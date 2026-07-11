"""
Agent基类 - 统一接口、LLM调用、Tool调用、状态上报

本模块定义了所有Agent的基类和工作流状态数据结构。
所有业务Agent（Planner、SimpleCoder、ComplexCoder、Tester）
和系统Agent（Constraint、Review）都应继承BaseAgent。

作者：成员C（wang123456-123456）
"""

# 导入抽象基类
from abc import ABC, abstractmethod
# 导入数据类装饰器
from dataclasses import dataclass, field
# 导入类型提示
from typing import Any, Callable, Optional
# 导入日志模块
import logging

# 导入LLM客户端
from models.llm import LLMClient

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class PipelineState:
    """
    工作流状态数据结构

    在整个Agent工作流中传递状态，包含用户输入、约束、代码、测试结果等。
    每个Agent接收state并返回修改后的state。

    属性说明：
        user_input: 用户输入的原始文本
        session_id: 会话ID，用于标识当前对话
        project: 项目名称，用于标识当前项目
        constraints: 检索到的约束列表
        constraint_summary: 约束摘要（由Constraint Agent生成）
        rag_context: RAG检索到的上下文
        memory_context: Memory上下文（global/project/task等层级）
        plan: 规划结果（由Planner Agent生成）
        code: 生成的代码（由Coder Agent生成）
        files_changed: 修改的文件列表
        test_results: 测试结果（由Tester Agent生成）
        review_result: 审查结果（由Review Agent生成）
        agent_history: Agent执行历史记录
        error: 错误信息（如果有）
        current_agent: 当前执行的Agent名称
        step_count: 当前执行步骤数
        max_steps: 最大步骤数限制
    """
    # 用户输入的原始文本
    user_input: str = ""
    # 会话ID，用于标识当前对话
    session_id: str = ""
    # 项目名称，用于标识当前项目
    project: str = ""
    # 检索到的约束列表
    constraints: list[str] = field(default_factory=list)
    # 约束摘要（由Constraint Agent生成）
    constraint_summary: str = ""
    # RAG检索到的上下文
    rag_context: str = ""
    # Memory上下文（global/project/task等层级）
    memory_context: dict = field(default_factory=dict)
    # 规划结果（由Planner Agent生成）
    plan: dict = field(default_factory=dict)
    # 生成的代码（由Coder Agent生成）
    code: str = ""
    # 修改的文件列表
    files_changed: list[dict] = field(default_factory=list)
    # 测试结果（由Tester Agent生成）
    test_results: dict = field(default_factory=dict)
    # 审查结果（由Review Agent生成）
    review_result: dict = field(default_factory=dict)
    # Agent执行历史记录
    agent_history: list[dict] = field(default_factory=list)
    # 错误信息（如果有）
    error: Optional[str] = None
    # 当前执行的Agent名称
    current_agent: str = ""
    # 当前执行步骤数
    step_count: int = 0
    # 最大步骤数限制
    max_steps: int = 50


class BaseAgent(ABC):
    """
    Agent基类

    所有Agent都应继承此类，并实现run()方法。
    提供LLM调用、Tool调用、状态上报等基础功能。

    子类必须定义：
        - name: Agent名称
        - description: Agent描述
        - run(): 执行逻辑

    子类可选覆盖：
        - model: 使用的LLM模型
        - temperature: 生成温度
        - system_prompt: 系统Prompt
        - permissions: 工具权限配置
    """

    # Agent名称（子类必须覆盖）
    name: str = "base"
    # Agent描述
    description: str = "基础Agent"
    # 使用的LLM模型
    model: str = "mimo-v2.5-pro"
    # 生成温度
    temperature: float = 0.1
    # 系统Prompt（子类应覆盖）
    system_prompt: str = ""
    # 工具权限配置
    permissions: dict = field(default_factory=lambda: {
        "read": "allow",
        "edit": "allow",
        "bash": "allow"
    })

    def __init__(self, llm_client: LLMClient):
        """
        初始化Agent

        Args:
            llm_client: LLM客户端实例
        """
        # LLM客户端
        self.llm = llm_client
        # 状态回调函数（用于SSE推送）
        self._status_callback: Optional[Callable] = None
        # ToolRegistry引用（由AgentManager注入）
        self._tool_registry = None
        # 日志记录器
        self.logger = logging.getLogger(f"agent.{self.name}")

    @abstractmethod
    async def run(self, state: PipelineState) -> PipelineState:
        """
        执行Agent逻辑（抽象方法，子类必须实现）

        Args:
            state: 当前工作流状态

        Returns:
            修改后的工作流状态
        """
        raise NotImplementedError

    async def call_llm(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """
        调用LLM

        Args:
            messages: 消息列表
            temperature: 温度参数（可选，默认使用Agent的temperature）
            max_tokens: 最大token数（可选）
            stream: 是否流式输出（当前未实现）

        Returns:
            LLM响应文本
        """
        # 使用指定温度或默认温度
        temp = temperature if temperature is not None else self.temperature

        try:
            # 调用LLM客户端
            response = await self.llm.chat(messages, temperature=temp, max_tokens=max_tokens)
            self.logger.debug(f"LLM call successful, response length: {len(response)}")
            return response
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    async def call_tool(self, tool_name: str, args: dict) -> Any:
        """
        调用Tool

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            工具执行结果

        Raises:
            RuntimeError: 如果ToolRegistry未注入
            PermissionError: 如果没有权限调用该工具
        """
        # 检查ToolRegistry是否已注入
        if self._tool_registry is None:
            raise RuntimeError(
                f"Agent '{self.name}' cannot call tool '{tool_name}': "
                "ToolRegistry not injected. Call set_tool_registry() first."
            )

        try:
            # 调用ToolRegistry执行工具
            result = await self._tool_registry.call(tool_name, args, self.permissions)
            self.logger.debug(f"Tool '{tool_name}' called successfully")
            return result
        except Exception as e:
            self.logger.error(f"Tool '{tool_name}' call failed: {e}")
            raise

    def set_tool_registry(self, tool_registry):
        """
        注入ToolRegistry

        Args:
            tool_registry: ToolRegistry实例
        """
        self._tool_registry = tool_registry
        self.logger.debug("ToolRegistry injected")

    def report_status(self, status: str, data: dict = None):
        """
        上报状态（SSE推送）

        Args:
            status: 状态文本（如 "running", "completed", "error"）
            data: 附加数据
        """
        # 构造状态消息
        status_msg = {
            "agent": self.name,
            "status": status,
            "data": data or {}
        }

        # 记录日志
        self.logger.info(f"Status: {status}, data: {data}")

        # 如果有回调函数，调用它
        if self._status_callback:
            try:
                self._status_callback(status_msg)
            except Exception as e:
                self.logger.error(f"Status callback failed: {e}")

    def set_status_callback(self, callback: Callable):
        """
        设置状态回调

        Args:
            callback: 回调函数，接收状态字典
        """
        self._status_callback = callback

    def add_to_history(self, state: PipelineState, action: str, result: Any):
        """
        添加到Agent历史记录

        Args:
            state: 当前工作流状态
            action: 执行的动作
            result: 执行结果
        """
        # 构造历史记录条目
        history_entry = {
            "agent": self.name,
            "action": action,
            "result": str(result)[:500]  # 限制长度
        }

        # 添加到历史记录
        state.agent_history.append(history_entry)

        # 记录日志
        self.logger.debug(f"Added to history: {action}")

    def check_step_limit(self, state: PipelineState) -> bool:
        """
        检查是否超过步骤限制

        Args:
            state: 当前工作流状态

        Returns:
            是否超过限制
        """
        return state.step_count >= state.max_steps

    def increment_step(self, state: PipelineState):
        """
        增加步骤计数

        Args:
            state: 当前工作流状态
        """
        state.step_count += 1
"""
Agent基类 - 统一接口、LLM调用、Tool调用、状态上报

本模块定义了所有Agent的基类和工作流状态数据结构。
所有业务Agent（Planner、SimpleCoder、ComplexCoder、Tester）
和系统Agent（Constraint、Review）都应继承BaseAgent。
"""

# 导入抽象基类
from abc import ABC, abstractmethod
# 导入数据类装饰器
from dataclasses import dataclass, field
# 导入类型提示
from typing import Any, Optional

# 导入LLM客户端
from models.llm import LLMClient


@dataclass
class PipelineState:
    """
    工作流状态数据结构

    在整个Agent工作流中传递状态，包含用户输入、约束、代码、测试结果等。
    每个Agent接收state并返回修改后的state。
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


class BaseAgent(ABC):
    """
    Agent基类

    所有Agent都应继承此类，并实现run()方法。
    提供LLM调用、Tool调用、状态上报等基础功能。
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
    permissions: dict = field(default_factory=dict)

    def __init__(self, llm_client: LLMClient):
        """
        初始化Agent

        Args:
            llm_client: LLM客户端实例
        """
        # LLM客户端
        self.llm = llm_client
        # 状态回调函数（用于SSE推送）
        self._status_callback = None

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
        # 调用LLM客户端
        return await self.llm.chat(messages, temperature=temp, max_tokens=max_tokens)

    async def call_tool(self, tool_name: str, args: dict) -> Any:
        """
        调用Tool（需要AgentManager注入ToolRegistry）

        Args:
            tool_name: 工具名称
            args: 工具参数

        Returns:
            工具执行结果
        """
        # 实际实现中，ToolRegistry会在AgentManager中注入
        raise NotImplementedError("Tool calling not implemented - need ToolRegistry injection")

    def report_status(self, status: str, data: dict = None):
        """
        上报状态（SSE推送）

        Args:
            status: 状态文本（如 "running", "completed", "error"）
            data: 附加数据
        """
        # 如果有回调函数，调用它
        if self._status_callback:
            self._status_callback({
                "agent": self.name,
                "status": status,
                "data": data or {}
            })

    def set_status_callback(self, callback):
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
        state.agent_history.append({
            "agent": self.name,
            "action": action,
            "result": str(result)[:500]  # 限制长度
        })
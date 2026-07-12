"""
Agent管理器 - 自动发现、注册、实例化、权限校验

本模块提供了Agent管理器，负责：
1. 自动扫描agents/目录，发现所有Agent
2. 注册和管理Agent实例
3. 权限校验后执行Agent
4. 管理Agent生命周期

作者：成员C（wang123456-123456）
"""

# 导入动态导入模块
import importlib
# 导入操作系统模块
import os
# 导入路径处理
from pathlib import Path
# 导入类型提示
from typing import Optional
# 导入日志模块
import logging

# 导入Agent基类和状态类
from agents.base import BaseAgent, PipelineState
# 导入LLM客户端
from models.llm import LLMClient

# 配置日志
logger = logging.getLogger(__name__)


class AgentManager:
    """
    Agent管理器

    管理所有Agent的注册、发现和执行。
    支持自动扫描目录并注册Agent。

    属性：
        llm_client: LLM客户端实例
        agents: Agent字典（name -> BaseAgent实例）
        _tool_registry: Tool注册中心（可选注入）
    """

    def __init__(self, llm_client: LLMClient):
        """
        初始化Agent管理器

        Args:
            llm_client: LLM客户端实例
        """
        # LLM客户端
        self.llm_client = llm_client
        # Agent字典：name -> BaseAgent实例
        self.agents: dict[str, BaseAgent] = {}
        # Tool注册中心（可选注入）
        self._tool_registry = None
        # 日志记录器
        self.logger = logger

        self.logger.info("AgentManager initialized")

    def set_tool_registry(self, tool_registry):
        """
        注入ToolRegistry

        Args:
            tool_registry: Tool注册中心实例
        """
        # 保存ToolRegistry引用
        self._tool_registry = tool_registry
        self.logger.info("ToolRegistry injected")

        # 给所有Agent注入ToolRegistry
        for agent_name, agent in self.agents.items():
            try:
                agent.set_tool_registry(tool_registry)
                self.logger.debug(f"ToolRegistry injected to agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to inject ToolRegistry to agent {agent_name}: {e}")

    def auto_discover(self, agents_dir: str = None):
        """
        自动扫描agents/目录，注册所有Agent

        Args:
            agents_dir: Agent目录路径（默认为当前文件所在目录）
        """
        # 如果未指定目录，使用当前文件所在目录
        if agents_dir is None:
            agents_dir = Path(__file__).parent

        self.logger.info(f"Auto-discovering agents in: {agents_dir}")

        # 遍历agents目录下的所有Python文件
        for file_path in Path(agents_dir).glob("*.py"):
            # 跳过__init__.py等私有文件
            if file_path.name.startswith("_"):
                continue

            # 跳过base.py和manager.py（不是Agent实现）
            if file_path.name in ["base.py", "manager.py"]:
                continue

            # 获取模块名称
            module_name = file_path.stem
            try:
                # 动态导入模块
                module = importlib.import_module(f"agents.{module_name}")
                self.logger.debug(f"Imported module: {module_name}")

                # 查找所有BaseAgent的子类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # 检查是否为BaseAgent的子类（但不是BaseAgent本身）
                    if (isinstance(attr, type) and
                        issubclass(attr, BaseAgent) and
                        attr is not BaseAgent):
                        # 实例化并注册
                        try:
                            agent = attr(self.llm_client)
                            self.register(agent)
                        except Exception as e:
                            self.logger.error(f"Failed to instantiate {attr_name}: {e}")
            except Exception as e:
                self.logger.error(f"Failed to import {module_name}: {e}")

    def register(self, agent: BaseAgent):
        """
        注册Agent

        Args:
            agent: Agent实例
        """
        # 检查是否已存在同名Agent
        if agent.name in self.agents:
            self.logger.warning(f"Overwriting existing agent: {agent.name}")

        # 将Agent添加到字典
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.description})")

        # 如果ToolRegistry已注入，给新Agent也注入
        if self._tool_registry is not None:
            try:
                agent.set_tool_registry(self._tool_registry)
            except Exception as e:
                self.logger.error(f"Failed to inject ToolRegistry to new agent {agent.name}: {e}")

    def get(self, name: str) -> Optional[BaseAgent]:
        """
        获取Agent实例

        Args:
            name: Agent名称

        Returns:
            Agent实例（如果存在）
        """
        return self.agents.get(name)

    def list_agents(self) -> list[str]:
        """
        列出所有已注册的Agent

        Returns:
            Agent名称列表
        """
        return list(self.agents.keys())

    def get_agent_info(self, name: str) -> dict:
        """
        获取Agent信息

        Args:
            name: Agent名称

        Returns:
            Agent信息字典
        """
        agent = self.get(name)
        if agent is None:
            return {}

        return {
            "name": agent.name,
            "description": agent.description,
            "model": agent.model,
            "temperature": agent.temperature,
            "permissions": agent.permissions
        }

    def get_all_agents_info(self) -> list[dict]:
        """
        获取所有Agent信息

        Returns:
            Agent信息列表
        """
        return [self.get_agent_info(name) for name in self.agents]

    async def run(self, name: str, state: PipelineState) -> PipelineState:
        """
        执行指定Agent

        Args:
            name: Agent名称
            state: 当前工作流状态

        Returns:
            修改后的工作流状态

        Raises:
            ValueError: 如果Agent不存在
            PermissionError: 如果Agent权限不足
        """
        # 获取Agent实例
        agent = self.get(name)
        if agent is None:
            raise ValueError(f"Agent not found: {name}")

        # 检查权限
        if not self._check_permissions(agent):
            raise PermissionError(f"Agent {name} lacks required permissions")

        # 更新状态中的当前Agent
        state.current_agent = name

        # 执行Agent
        self.logger.info(f"Running agent: {name}")
        try:
            result_state = await agent.run(state)
            self.logger.info(f"Agent {name} completed successfully")
            return result_state
        except Exception as e:
            self.logger.error(f"Agent {name} failed: {e}")
            raise

    def _check_permissions(self, agent: BaseAgent) -> bool:
        """
        检查Agent权限

        Args:
            agent: Agent实例

        Returns:
            是否有权限
        """
        # 基础权限检查（所有Agent都需要read权限）
        required_permissions = ["read"]
        for perm in required_permissions:
            if perm not in agent.permissions:
                self.logger.warning(f"Agent {agent.name} missing required permission: {perm}")
                return False
        return True

    def inject_callback_to_all(self, callback):
        """
        给所有Agent注入状态回调

        Args:
            callback: 回调函数
        """
        for agent_name, agent in self.agents.items():
            try:
                agent.set_status_callback(callback)
                self.logger.debug(f"Callback injected to agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to inject callback to agent {agent_name}: {e}")

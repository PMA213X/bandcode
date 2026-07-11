"""
Agent管理器 - 自动发现、注册、实例化、权限校验

本模块提供了Agent管理器，负责：
1. 自动扫描agents/目录，发现所有Agent
2. 注册和管理Agent实例
3. 权限校验后执行Agent
"""

# 导入动态导入模块
import importlib
# 导入操作系统模块
import os
# 导入路径处理
from pathlib import Path
# 导入类型提示
from typing import Optional

# 导入Agent基类和状态类
from agents.base import BaseAgent, PipelineState
# 导入LLM客户端
from models.llm import LLMClient


class AgentManager:
    """
    Agent管理器

    管理所有Agent的注册、发现和执行。
    支持自动扫描目录并注册Agent。
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

    def set_tool_registry(self, tool_registry):
        """
        注入ToolRegistry

        Args:
            tool_registry: Tool注册中心实例
        """
        # 保存ToolRegistry引用
        self._tool_registry = tool_registry
        # 给所有Agent注入ToolRegistry
        for agent in self.agents.values():
            # 为每个Agent设置call_tool方法
            agent.call_tool = lambda tool_name, args: tool_registry.call(
                tool_name, args, agent.permissions
            )

    def auto_discover(self, agents_dir: str = None):
        """
        自动扫描agents/目录，注册所有Agent

        Args:
            agents_dir: Agent目录路径（默认为当前文件所在目录）
        """
        # 如果未指定目录，使用当前文件所在目录
        if agents_dir is None:
            agents_dir = Path(__file__).parent

        # 遍历agents目录下的所有Python文件
        for file_path in Path(agents_dir).glob("*.py"):
            # 跳过__init__.py等私有文件
            if file_path.name.startswith("_"):
                continue

            # 获取模块名称
            module_name = file_path.stem
            try:
                # 动态导入模块
                module = importlib.import_module(f"agents.{module_name}")

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
                            print(f"Failed to instantiate {attr_name}: {e}")
            except Exception as e:
                print(f"Failed to import {module_name}: {e}")

    def register(self, agent: BaseAgent):
        """
        注册Agent

        Args:
            agent: Agent实例
        """
        # 将Agent添加到字典
        self.agents[agent.name] = agent
        print(f"Registered agent: {agent.name}")

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

    async def run(self, name: str, state: PipelineState) -> PipelineState:
        """
        执行指定Agent

        Args:
            name: Agent名称
            state: 当前工作流状态

        Returns:
            修改后的工作流状态
        """
        # 获取Agent实例
        agent = self.get(name)
        if agent is None:
            raise ValueError(f"Agent not found: {name}")

        # 检查权限
        if not self._check_permissions(agent):
            raise PermissionError(f"Agent {name} lacks required permissions")

        # 执行Agent
        return await agent.run(state)

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
                return False
        return True

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
            "permissions": agent.permissions
        }

"""
Tool注册中心 - 自动发现、注册、权限校验、执行

本模块提供了工具注册中心，负责：
1. 自动扫描tools/目录，发现所有工具
2. 注册和管理工具实例
3. 权限校验后执行工具
"""

# 导入动态导入模块
import importlib
# 导入路径处理
from pathlib import Path
# 导入类型提示
from typing import Optional

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class ToolRegistry:
    """
    Tool注册中心

    管理所有工具的注册、发现和执行。
    支持自动扫描目录并注册工具。
    """

    def __init__(self):
        """初始化注册中心"""
        # 工具字典：name -> Tool实例
        self.tools: dict[str, Tool] = {}

    def auto_discover(self, tools_dir: str = None):
        """
        自动扫描tools/目录，注册所有Tool

        Args:
            tools_dir: 工具目录路径（默认为当前文件所在目录）
        """
        # 如果未指定目录，使用当前文件所在目录
        if tools_dir is None:
            tools_dir = Path(__file__).parent

        # 遍历tools目录下的所有Python文件
        for file_path in Path(tools_dir).glob("*.py"):
            # 跳过__init__.py等私有文件
            if file_path.name.startswith("_"):
                continue

            # 获取模块名称
            module_name = file_path.stem
            try:
                # 动态导入模块
                module = importlib.import_module(f"tools.{module_name}")

                # 查找所有Tool的子类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # 检查是否为Tool的子类（但不是Tool本身）
                    if (isinstance(attr, type) and
                        issubclass(attr, Tool) and
                        attr is not Tool):
                        # 实例化并注册
                        try:
                            tool = attr()
                            self.register(tool)
                        except Exception as e:
                            print(f"Failed to instantiate {attr_name}: {e}")
            except Exception as e:
                print(f"Failed to import {module_name}: {e}")

        # 自动发现builtins子目录
        builtins_dir = Path(tools_dir) / "builtins"
        if builtins_dir.exists():
            self._discover_builtins(builtins_dir)

    def _discover_builtins(self, builtins_dir: Path):
        """
        发现builtins目录下的工具

        Args:
            builtins_dir: builtins目录路径
        """
        # 遍历builtins目录下的所有Python文件
        for file_path in builtins_dir.glob("*.py"):
            # 跳过__init__.py等私有文件
            if file_path.name.startswith("_"):
                continue

            # 获取模块名称
            module_name = file_path.stem
            try:
                # 动态导入模块
                module = importlib.import_module(f"tools.builtins.{module_name}")
                # 查找所有Tool的子类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # 检查是否为Tool的子类（但不是Tool本身）
                    if (isinstance(attr, type) and
                        issubclass(attr, Tool) and
                        attr is not Tool):
                        # 实例化并注册
                        try:
                            tool = attr()
                            self.register(tool)
                        except Exception as e:
                            print(f"Failed to instantiate {attr_name}: {e}")
            except Exception as e:
                print(f"Failed to import builtins.{module_name}: {e}")

    def register(self, tool: Tool):
        """
        注册工具

        Args:
            tool: 工具实例
        """
        # 将工具添加到字典
        self.tools[tool.name] = tool
        print(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[Tool]:
        """
        获取工具

        Args:
            name: 工具名称

        Returns:
            工具实例（如果存在）
        """
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        """
        列出所有工具

        Returns:
            工具名称列表
        """
        return list(self.tools.keys())

    async def call(self, name: str, args: dict, agent_permissions: dict) -> ToolResult:
        """
        调用工具，检查权限后执行

        Args:
            name: 工具名称
            args: 工具参数
            agent_permissions: Agent权限配置

        Returns:
            工具执行结果
        """
        # 获取工具实例
        tool = self.get(name)
        if tool is None:
            return ToolResult(success=False, error=f"Tool not found: {name}")

        # 检查权限
        if not self._check_permission(tool, agent_permissions):
            return ToolResult(
                success=False,
                error=f"Permission denied: agent lacks {tool.permission} permission"
            )

        # 验证参数
        if not tool.validate_params(**args):
            return ToolResult(success=False, error="Invalid parameters")

        # 执行工具
        try:
            return await tool.execute(**args)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _check_permission(self, tool: Tool, agent_permissions: dict) -> bool:
        """
        检查权限

        Args:
            tool: 工具实例
            agent_permissions: Agent权限配置

        Returns:
            是否有权限
        """
        # 获取工具所需权限
        tool_permission = tool.permission
        # 检查Agent是否有该权限
        if tool_permission in agent_permissions:
            return agent_permissions[tool_permission] == "allow"
        # 默认允许读取权限
        return tool_permission == "read"

    def get_tool_info(self, name: str) -> dict:
        """
        获取工具信息

        Args:
            name: 工具名称

        Returns:
            工具Schema
        """
        tool = self.get(name)
        if tool is None:
            return {}
        return tool.get_schema()

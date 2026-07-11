"""
Tool基类 - 定义工具接口

本模块定义了所有工具的基类和工具执行结果。
所有内置工具（read_file、write_file等）都应继承Tool。
"""

# 导入抽象基类
from abc import ABC, abstractmethod
# 导入数据类装饰器
from dataclasses import dataclass, field
# 导入类型提示
from typing import Any, Optional


@dataclass
class ToolResult:
    """
    工具执行结果

    封装工具执行的成功/失败状态、返回数据和错误信息。
    """
    # 执行是否成功
    success: bool
    # 返回数据（成功时）
    data: Any = None
    # 错误信息（失败时）
    error: Optional[str] = None


class Tool(ABC):
    """
    工具基类

    所有工具都应继承此类，并实现execute()方法。
    提供参数验证、Schema生成等基础功能。
    """

    # 工具名称（子类必须覆盖）
    name: str = "base"
    # 工具描述
    description: str = "基础工具"
    # 所需权限：read, write, bash, admin
    permission: str = "read"
    # 参数定义（JSON Schema格式）
    parameters: dict = field(default_factory=dict)

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        执行工具（抽象方法，子类必须实现）

        Args:
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        raise NotImplementedError

    def validate_params(self, **kwargs) -> bool:
        """
        验证参数

        Args:
            **kwargs: 工具参数

        Returns:
            参数是否有效
        """
        # 检查必需参数
        for param_name, param_info in self.parameters.items():
            if param_info.get("required", False):
                if param_name not in kwargs:
                    return False
        return True

    def get_schema(self) -> dict:
        """
        获取工具Schema

        Returns:
            工具的JSON Schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

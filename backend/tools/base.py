"""
Tool基类 - 定义工具接口

本模块定义了所有工具的基类和工具执行结果。
所有内置工具（read_file、write_file等）都应继承Tool。

作者：成员C（wang123456-123456）
"""

# 导入抽象基类
from abc import ABC, abstractmethod
# 导入数据类装饰器
from dataclasses import dataclass, field
# 导入类型提示
from typing import Any, Optional
# 导入日志模块
import logging

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """
    工具执行结果

    封装工具执行的成功/失败状态、返回数据和错误信息。

    属性：
        success: 执行是否成功
        data: 返回数据（成功时）
        error: 错误信息（失败时）
        execution_time: 执行时间（秒）
    """
    # 执行是否成功
    success: bool
    # 返回数据（成功时）
    data: Any = None
    # 错误信息（失败时）
    error: Optional[str] = None
    # 执行时间（秒）
    execution_time: Optional[float] = None


class Tool(ABC):
    """
    工具基类

    所有工具都应继承此类，并实现execute()方法。
    提供参数验证、Schema生成等基础功能。

    子类必须定义：
        - name: 工具名称
        - description: 工具描述
        - execute(): 执行逻辑

    子类可选覆盖：
        - permission: 所需权限（默认read）
        - parameters: 参数定义（JSON Schema格式）
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
                    logger.warning(f"Missing required parameter: {param_name}")
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

    def __str__(self) -> str:
        """字符串表示"""
        return f"Tool({self.name}): {self.description}"

    def __repr__(self) -> str:
        """调试表示"""
        return f"<Tool name={self.name} permission={self.permission}>"

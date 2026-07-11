"""
read_file工具 - 读取文件内容

本模块实现了文件读取工具，支持读取指定路径的文件内容。
"""

# 导入路径处理
from pathlib import Path

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class ReadFileTool(Tool):
    """
    读取文件内容工具

    读取指定文件的内容并返回。
    """

    # 工具名称
    name = "read_file"
    # 工具描述
    description = "读取指定文件的内容"
    # 所需权限：read
    permission = "read"
    # 参数定义
    parameters = {
        "file_path": {
            "type": "string",
            "description": "文件路径",
            "required": True
        },
        "encoding": {
            "type": "string",
            "description": "文件编码，默认utf-8",
            "required": False
        }
    }

    async def execute(self, file_path: str, encoding: str = "utf-8", **kwargs) -> ToolResult:
        """
        执行读取文件

        Args:
            file_path: 文件路径
            encoding: 文件编码（默认utf-8）

        Returns:
            文件内容或错误信息
        """
        try:
            # 创建Path对象
            path = Path(file_path)
            # 检查文件是否存在
            if not path.exists():
                return ToolResult(success=False, error=f"File not found: {file_path}")

            # 检查是否为文件（非目录）
            if not path.is_file():
                return ToolResult(success=False, error=f"Not a file: {file_path}")

            # 读取文件内容
            content = path.read_text(encoding=encoding)
            return ToolResult(success=True, data=content)
        except Exception as e:
            # 捕获异常并返回错误
            return ToolResult(success=False, error=str(e))

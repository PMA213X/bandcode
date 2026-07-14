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

    async def execute(self, file_path: str, encoding: str = "utf-8", workspace: str = "", **kwargs) -> ToolResult:
        try:
            path = self.resolve_path(file_path, workspace)
            if not path.exists():
                return ToolResult(success=False, error=f"File not found: {path}")
            if not path.is_file():
                return ToolResult(success=False, error=f"Not a file: {path}")
            content = path.read_text(encoding=encoding)
            return ToolResult(success=True, data=content)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
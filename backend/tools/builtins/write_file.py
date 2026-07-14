"""
write_file工具 - 写入或创建文件

本模块实现了文件写入工具，支持写入或创建指定路径的文件。
"""

# 导入路径处理
from pathlib import Path

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class WriteFileTool(Tool):
    """
    写入文件工具

    写入或创建指定文件。
    """

    # 工具名称
    name = "write_file"
    # 工具描述
    description = "写入或创建文件"
    # 所需权限：write
    permission = "write"
    # 参数定义
    parameters = {
        "file_path": {
            "type": "string",
            "description": "文件路径",
            "required": True
        },
        "content": {
            "type": "string",
            "description": "文件内容",
            "required": True
        },
        "encoding": {
            "type": "string",
            "description": "文件编码，默认utf-8",
            "required": False
        },
        "create_dirs": {
            "type": "boolean",
            "description": "是否自动创建目录，默认true",
            "required": False
        }
    }

    async def execute(
        self,
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True,
        workspace: str = "",
        **kwargs
    ) -> ToolResult:
        try:
            path = self.resolve_path(file_path, workspace)
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding=encoding)
            return ToolResult(success=True, data={"file_path": str(path), "bytes_written": len(content.encode(encoding))})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
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
        **kwargs
    ) -> ToolResult:
        """
        执行写入文件

        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码（默认utf-8）
            create_dirs: 是否自动创建目录（默认true）

        Returns:
            写入结果或错误信息
        """
        try:
            # 创建Path对象
            path = Path(file_path)

            # 自动创建目录
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件内容
            path.write_text(content, encoding=encoding)
            # 返回写入的字节数
            return ToolResult(success=True, data={"file_path": file_path, "bytes_written": len(content.encode(encoding))})
        except Exception as e:
            # 捕获异常并返回错误
            return ToolResult(success=False, error=str(e))

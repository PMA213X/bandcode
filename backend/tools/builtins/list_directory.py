"""
list_directory工具 - 列出目录结构

本模块实现了目录列表工具，支持列出指定目录的文件和子目录。
"""

# 导入路径处理
from pathlib import Path

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class ListDirectoryTool(Tool):
    """
    列出目录工具

    列出指定目录中的文件和子目录。
    """

    # 工具名称
    name = "list_directory"
    # 工具描述
    description = "列出目录中的文件和子目录"
    # 所需权限：read
    permission = "read"
    # 参数定义
    parameters = {
        "dir_path": {
            "type": "string",
            "description": "目录路径",
            "required": True
        },
        "recursive": {
            "type": "boolean",
            "description": "是否递归列出，默认false",
            "required": False
        },
        "max_depth": {
            "type": "integer",
            "description": "最大递归深度，默认3",
            "required": False
        }
    }

    async def execute(
        self,
        dir_path: str = ".",
        recursive: bool = False,
        max_depth: int = 3,
        workspace: str = "",
        **kwargs
    ) -> ToolResult:
        try:
            path = self.resolve_path(dir_path, workspace)
            if not path.exists():
                return ToolResult(success=False, error=f"Directory not found: {path}")
            if not path.is_dir():
                return ToolResult(success=False, error=f"Not a directory: {path}")
            result = []
            self._list_recursive(path, result, recursive, max_depth, 0)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def _list_recursive(
        self,
        path: Path,
        result: list,
        recursive: bool,
        max_depth: int,
        current_depth: int
    ):
        """
        递归列出目录

        Args:
            path: 当前目录路径
            result: 结果列表
            recursive: 是否递归
            max_depth: 最大递归深度
            current_depth: 当前递归深度
        """
        # 检查是否超过最大深度
        if current_depth > max_depth:
            return

        try:
            # 获取目录内容并排序（目录在前，文件在后）
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            # 遍历所有项目
            for item in items:
                # 构造项目信息
                item_info = {
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item)
                }
                # 添加到结果列表
                result.append(item_info)

                # 如果是目录且需要递归，继续递归
                if recursive and item.is_dir():
                    self._list_recursive(item, result, recursive, max_depth, current_depth + 1)
        except PermissionError:
            # 忽略权限错误
            pass
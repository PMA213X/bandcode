"""
search_project工具 - 全文搜索项目文件

本模块实现了项目文件搜索工具，支持在项目中搜索指定内容。
"""

# 导入路径处理
from pathlib import Path
# 导入正则表达式
import re

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class SearchProjectTool(Tool):
    """
    搜索项目工具

    在项目中搜索指定内容。
    """

    # 工具名称
    name = "search_project"
    # 工具描述
    description = "在项目中搜索指定内容"
    # 所需权限：read
    permission = "read"
    # 参数定义
    parameters = {
        "query": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        },
        "directory": {
            "type": "string",
            "description": "搜索目录（默认当前目录）",
            "required": False
        },
        "file_pattern": {
            "type": "string",
            "description": "文件匹配模式（如 *.py）",
            "required": False
        },
        "max_results": {
            "type": "integer",
            "description": "最大结果数（默认50）",
            "required": False
        }
    }

    async def execute(
        self,
        query: str,
        directory: str = ".",
        file_pattern: str = "*",
        max_results: int = 50,
        workspace: str = "",
        **kwargs
    ) -> ToolResult:
        try:
            path = self.resolve_path(directory, workspace)
            if not path.exists():
                return ToolResult(success=False, error=f"Directory not found: {path}")
            results = []
            pattern = re.compile(query, re.IGNORECASE)
            for file_path in path.rglob(file_pattern):
                if file_path.is_dir() or file_path.name.startswith("."):
                    continue
                if len(results) >= max_results:
                    break
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    matches = list(pattern.finditer(content))
                    if matches:
                        results.append({
                            "file": str(file_path),
                            "matches": len(matches),
                            "preview": content[:200]
                        })
                except Exception:
                    continue
            return ToolResult(success=True, data=results)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
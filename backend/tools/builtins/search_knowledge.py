"""
search_knowledge工具 - 搜索RAG知识库

本模块实现了知识库搜索工具，支持在知识库中搜索相关内容。
"""

# 导入路径处理
from pathlib import Path
# 导入正则表达式
import re

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class SearchKnowledgeTool(Tool):
    """
    搜索知识库工具

    在知识库中搜索相关内容。
    """

    # 工具名称
    name = "search_knowledge"
    # 工具描述
    description = "在知识库中搜索相关内容"
    # 所需权限：read
    permission = "read"
    # 参数定义
    parameters = {
        "query": {
            "type": "string",
            "description": "搜索关键词",
            "required": True
        },
        "knowledge_path": {
            "type": "string",
            "description": "知识库路径（默认knowledge）",
            "required": False
        },
        "max_results": {
            "type": "integer",
            "description": "最大结果数（默认10）",
            "required": False
        }
    }

    async def execute(
        self,
        query: str,
        knowledge_path: str = "knowledge",
        max_results: int = 10,
        **kwargs
    ) -> ToolResult:
        """
        执行搜索

        Args:
            query: 搜索关键词
            knowledge_path: 知识库路径
            max_results: 最大结果数

        Returns:
            搜索结果或错误信息
        """
        try:
            # 创建Path对象
            path = Path(knowledge_path)
            # 检查目录是否存在
            if not path.exists():
                return ToolResult(success=False, error=f"Knowledge path not found: {knowledge_path}")

            # 存储结果
            results = []
            # 编译正则表达式
            pattern = re.compile(query, re.IGNORECASE)

            # 遍历知识库文件
            for file_path in path.rglob("*.md"):
                # 检查结果数量
                if len(results) >= max_results:
                    break

                try:
                    # 读取文件内容
                    content = file_path.read_text(encoding="utf-8")
                    # 搜索匹配
                    matches = list(pattern.finditer(content))
                    if matches:
                        # 提取匹配的上下文
                        contexts = []
                        for match in matches[:3]:  # 最多3个上下文
                            start = max(0, match.start() - 100)
                            end = min(len(content), match.end() + 100)
                            context = content[start:end]
                            contexts.append(context)

                        # 添加到结果
                        results.append({
                            "file": str(file_path),
                            "matches": len(matches),
                            "contexts": contexts
                        })
                except Exception:
                    # 忽略读取错误
                    continue

            return ToolResult(success=True, data=results)

        except Exception as e:
            return ToolResult(success=False, error=str(e))

"""
Memory API
GET /api/memory - 获取 Memory 信息
"""
from fastapi import APIRouter
from typing import Optional

router = APIRouter(prefix="/memory", tags=["记忆"])


@router.get("")
async def get_memory(layer: Optional[str] = None):
    """
    获取 Memory 信息
    可选参数 layer: global/project/task/session/checkpoint/notes
    """
    # 模拟 Memory 数据（后续会对接 memory/store.py）
    memory_data = {
        "global": {"content": "# 全局记忆\n项目规范和配置信息"},
        "project": {"content": "# 项目记忆\n当前项目的状态和决策"},
        "task": {"content": "# 任务记忆\n当前任务的进度和上下文"},
        "session": {"content": "# 会话记忆\n当前会话的历史记录"},
        "checkpoint": {"content": "# 检查点\n最近的检查点快照"},
        "notes": {"content": "# 笔记\n开发者笔记"},
    }

    if layer:
        if layer not in memory_data:
            return {"code": -1, "data": None, "message": f"未知的 Memory 层：{layer}"}
        return {"code": 0, "data": memory_data[layer], "message": "ok"}

    return {"code": 0, "data": memory_data, "message": "ok"}


@router.get("/search")
async def search_memory(query: str, limit: int = 10):
    """
    搜索 Memory
    """
    # 模拟搜索结果（后续会对接 RAG 检索）
    results = [
        {"layer": "project", "content": f"找到与 '{query}' 相关的内容", "score": 0.95}
    ]
    return {"code": 0, "data": results[:limit], "message": "ok"}

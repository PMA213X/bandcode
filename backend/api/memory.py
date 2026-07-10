"""
Memory API
GET /api/memory - 获取 Memory 信息
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/memory", tags=["记忆"])


@router.get("")
async def get_memory(
    project: str = Query(..., description="项目名称"),
    layer: str = Query(..., description="Memory 层"),
):
    """
    获取 Memory 信息
    与前端 MemoryRequest 一致
    """
    # 模拟 Memory 数据（后续会对接 memory/store.py）
    memory_data = {
        "global": {"content": "# 全局记忆\n项目规范和配置信息", "updated_at": "2026-07-10T08:00:00"},
        "project": {"content": "# 项目记忆\n当前项目的状态和决策", "updated_at": "2026-07-10T08:30:00"},
        "task": {"content": "# 任务记忆\n当前任务的进度和上下文", "updated_at": "2026-07-10T08:45:00"},
        "session": {"content": "# 会话记忆\n当前会话的历史记录", "updated_at": "2026-07-10T08:55:00"},
        "checkpoint": {"content": "# 检查点\n最近的检查点快照", "updated_at": "2026-07-10T08:50:00"},
        "notes": {"content": "# 笔记\n开发者笔记", "updated_at": "2026-07-10T08:00:00"},
    }

    if layer not in memory_data:
        return {"code": -1, "data": None, "message": f"未知的 Memory 层：{layer}"}

    data = {
        "layer": layer,
        "content": memory_data[layer]["content"],
        "updated_at": memory_data[layer]["updated_at"],
    }
    return {"code": 0, "data": data, "message": "ok"}


@router.get("/search")
async def search_memory(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回数量"),
):
    """
    搜索 Memory
    """
    # 模拟搜索结果（后续会对接 RAG 检索）
    results = [
        {"layer": "project", "content": f"找到与 '{query}' 相关的内容", "score": 0.95}
    ]
    return {"code": 0, "data": results[:limit], "message": "ok"}

"""
Memory API 模块

本模块实现了记忆系统相关的 API 接口，包括：
1. 获取 Memory 信息 - GET /api/memory
2. 搜索 Memory - GET /api/memory/search
3. 获取最近记忆 - GET /api/memory/recent
4. 获取统计信息 - GET /api/memory/stats
5. 压缩会话 - POST /api/memory/compress
6. 清理过期会话 - POST /api/memory/clean

Memory 系统分为 6 层：
- global: 全局记忆（项目规范、配置信息）
- project: 项目记忆（项目状态、决策记录）
- task: 任务记忆（任务进度、上下文）
- session: 会话记忆（当前会话历史）
- checkpoint: 检查点（快照数据）
- notes: 笔记（开发者笔记）
"""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

from memory.manager import MemoryManager

router = APIRouter(prefix="/memory", tags=["记忆"])

# 全局 MemoryManager 实例
memory_manager = MemoryManager()


@router.get("")
async def get_memory(
    project: str = Query(..., description="项目名称"),
    layer: str = Query(..., description="Memory 层"),
):
    """
    获取 Memory 信息接口
    
    获取指定 Memory 层的内容。
    """
    memory_data = {
        "global": {
            "content": "# 全局记忆\n项目规范和配置信息",
            "updated_at": "2026-07-10T08:00:00"
        },
        "project": {
            "content": "# 项目记忆\n当前项目的状态和决策",
            "updated_at": "2026-07-10T08:30:00"
        },
        "task": {
            "content": "# 任务记忆\n当前任务的进度和上下文",
            "updated_at": "2026-07-10T08:45:00"
        },
        "session": {
            "content": "# 会话记忆\n当前会话的历史记录",
            "updated_at": "2026-07-10T08:55:00"
        },
        "checkpoint": {
            "content": "# 检查点\n最近的检查点快照",
            "updated_at": "2026-07-10T08:50:00"
        },
        "notes": {
            "content": "# 笔记\n开发者笔记",
            "updated_at": "2026-07-10T08:00:00"
        },
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
    type: Optional[str] = Query(None, description="条目类型过滤"),
):
    """
    搜索 Memory 接口
    
    根据关键词搜索 Memory 内容。
    """
    results = memory_manager.search(query, limit, type)
    return {"code": 200, "data": results, "message": "搜索成功"}


@router.get("/recent")
async def get_recent_memory(
    limit: int = Query(20, description="返回数量"),
    type: Optional[str] = Query(None, description="条目类型过滤"),
):
    """
    获取最近记忆接口
    
    获取最近的 Memory 条目。
    """
    results = memory_manager.get_recent(limit, type)
    return {"code": 200, "data": results, "message": "获取成功"}


@router.get("/stats")
async def get_memory_stats():
    """
    获取统计信息接口
    
    获取 Memory 系统的统计信息。
    """
    stats = memory_manager.get_stats()
    return {"code": 200, "data": stats, "message": "获取成功"}


@router.post("/compress")
async def compress_session(session_id: Optional[str] = None):
    """
    压缩会话接口
    
    压缩指定会话或当前会话的数据。
    """
    result = memory_manager.compress_session(session_id)
    return {"code": 200, "data": result, "message": "压缩完成"}


@router.post("/clean")
async def clean_old_sessions(max_age_days: int = Query(7, description="最大保留天数")):
    """
    清理过期会话接口
    
    清理超过指定天数的旧会话。
    """
    cleaned = memory_manager.clean_old_sessions(max_age_days)
    return {"code": 200, "data": {"cleaned": cleaned}, "message": "清理完成"}

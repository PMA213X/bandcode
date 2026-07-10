"""
Memory API 模块

本模块实现了记忆系统相关的 API 接口，包括：
1. 获取 Memory 信息 - GET /api/memory
2. 搜索 Memory - GET /api/memory/search

Memory 系统分为 6 层：
- global: 全局记忆（项目规范、配置信息）
- project: 项目记忆（项目状态、决策记录）
- task: 任务记忆（任务进度、上下文）
- session: 会话记忆（当前会话历史）
- checkpoint: 检查点（快照数据）
- notes: 笔记（开发者笔记）
"""

# 导入 FastAPI 路由和查询参数
from fastapi import APIRouter, Query
# 导入类型注解
from typing import Optional
# 导入时间处理模块
from datetime import datetime

# 创建路由器，prefix="/memory" 表示所有路由以 /memory 开头
# tags=["记忆"] 用于 API 文档分组
router = APIRouter(prefix="/memory", tags=["记忆"])


@router.get("")
async def get_memory(
    project: str = Query(..., description="项目名称"),
    layer: str = Query(..., description="Memory 层"),
):
    """
    获取 Memory 信息接口
    
    获取指定 Memory 层的内容。
    与前端 MemoryRequest 保持一致。
    
    Args:
        project: 项目名称（必填）
        layer: Memory 层名称（必填）
            - global: 全局记忆
            - project: 项目记忆
            - task: 任务记忆
            - session: 会话记忆
            - checkpoint: 检查点
            - notes: 笔记
    
    Returns:
        包含 Memory 内容的响应：
        - layer: Memory 层名称
        - content: Memory 内容
        - updated_at: 最后更新时间
    """
    # 模拟 Memory 数据（后续会对接 memory/store.py）
    # 每个 Memory 层都有内容和更新时间
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

    # 检查 Memory 层是否存在
    if layer not in memory_data:
        # 如果不存在，返回错误响应
        return {"code": -1, "data": None, "message": f"未知的 Memory 层：{layer}"}

    # 构建响应数据
    data = {
        "layer": layer,  # Memory 层名称
        "content": memory_data[layer]["content"],  # Memory 内容
        "updated_at": memory_data[layer]["updated_at"],  # 最后更新时间
    }
    # 返回统一格式的响应
    return {"code": 0, "data": data, "message": "ok"}


@router.get("/search")
async def search_memory(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, description="返回数量"),
):
    """
    搜索 Memory 接口
    
    根据关键词搜索 Memory 内容。
    后续会对接 RAG 检索系统。
    
    Args:
        query: 搜索关键词（必填）
        limit: 返回结果数量（默认为 10）
    
    Returns:
        包含搜索结果的响应：
        - 每个结果包含 layer（Memory 层）、content（内容）、score（相似度分数）
    """
    # 模拟搜索结果（后续会对接 RAG 检索）
    # 返回与查询关键词相关的 Memory 内容
    results = [
        {
            "layer": "project",  # Memory 层
            "content": f"找到与 '{query}' 相关的内容",  # 内容
            "score": 0.95  # 相似度分数（0-1）
        }
    ]
    # 返回统一格式的响应，限制返回数量
    return {"code": 0, "data": results[:limit], "message": "ok"}

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
from pathlib import Path

from memory.manager import MemoryManager

router = APIRouter(prefix="/memory", tags=["记忆"])

# 全局 MemoryManager 实例
memory_manager = MemoryManager()

# Memory 根目录
MEMORY_ROOT = Path(__file__).parent.parent.parent / "memory"


def _read_memory_file(layer: str, project: Optional[str] = None) -> dict:
    """读取指定层的 Memory 文件"""
    try:
        if layer == "global":
            file_path = MEMORY_ROOT / "global" / "MEMORY.md"
        elif layer == "project":
            if project:
                file_path = MEMORY_ROOT / "projects" / project / "MEMORY.md"
            else:
                file_path = MEMORY_ROOT / "projects" / "global" / "MEMORY.md"
        elif layer == "session":
            # 获取最新的 session
            sessions_dir = MEMORY_ROOT / "sessions"
            if sessions_dir.exists():
                sessions = sorted(sessions_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
                if sessions:
                    # 查找 session 中的 MEMORY.md 或 checkpoint.md
                    session_dir = sessions[0]
                    file_path = session_dir / "checkpoint.md"
                    if not file_path.exists():
                        file_path = session_dir / "MEMORY.md"
                else:
                    return {"content": "暂无会话记录", "updated_at": None}
            else:
                return {"content": "暂无会话记录", "updated_at": None}
        elif layer == "task":
            # 获取最新 session 的任务
            sessions_dir = MEMORY_ROOT / "sessions"
            if sessions_dir.exists():
                sessions = sorted(sessions_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
                if sessions:
                    tasks_dir = sessions[0] / "tasks"
                    if tasks_dir.exists():
                        task_files = list(tasks_dir.glob("*/progress.md"))
                        if task_files:
                            # 合并所有任务内容
                            contents = []
                            for tf in task_files[:5]:  # 最多显示5个任务
                                contents.append(tf.read_text(encoding="utf-8"))
                            content = "\n\n---\n\n".join(contents)
                            return {"content": content, "updated_at": datetime.now().isoformat()}
                return {"content": "暂无任务记录", "updated_at": None}
            else:
                return {"content": "暂无任务记录", "updated_at": None}
        elif layer == "checkpoint":
            sessions_dir = MEMORY_ROOT / "sessions"
            if sessions_dir.exists():
                sessions = sorted(sessions_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
                if sessions:
                    file_path = sessions[0] / "checkpoint.md"
                else:
                    return {"content": "暂无检查点", "updated_at": None}
            else:
                return {"content": "暂无检查点", "updated_at": None}
        elif layer == "notes":
            sessions_dir = MEMORY_ROOT / "sessions"
            if sessions_dir.exists():
                sessions = sorted(sessions_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
                if sessions:
                    file_path = sessions[0] / "notes.md"
                else:
                    return {"content": "暂无笔记", "updated_at": None}
            else:
                return {"content": "暂无笔记", "updated_at": None}
        else:
            return None

        if file_path and file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            updated_at = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            return {"content": content, "updated_at": updated_at}
        else:
            return {"content": f"暂无{layer}记忆内容", "updated_at": None}
    except Exception as e:
        return {"content": f"读取失败: {str(e)}", "updated_at": None}


@router.get("")
async def get_memory(
    project: Optional[str] = Query(None, description="项目名称"),
    layer: str = Query(..., description="Memory 层"),
):
    """
    获取 Memory 信息接口

    获取指定 Memory 层的内容。
    """
    valid_layers = ["global", "project", "task", "session", "checkpoint", "notes"]
    if layer not in valid_layers:
        return {"code": -1, "data": None, "message": f"未知的 Memory 层：{layer}"}

    result = _read_memory_file(layer, project)
    if result is None:
        return {"code": -1, "data": None, "message": f"读取 Memory 失败"}

    data = {
        "layer": layer,
        "content": result["content"],
        "updated_at": result["updated_at"],
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
    return {"code": 0, "data": results, "message": "搜索成功"}


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
    return {"code": 0, "data": results, "message": "获取成功"}


@router.get("/stats")
async def get_memory_stats():
    """
    获取统计信息接口
    
    获取 Memory 系统的统计信息。
    """
    stats = memory_manager.get_stats()
    return {"code": 0, "data": stats, "message": "获取成功"}


@router.post("/compress")
async def compress_session(session_id: Optional[str] = None):
    """
    压缩会话接口
    
    压缩指定会话或当前会话的数据。
    """
    result = memory_manager.compress_session(session_id)
    return {"code": 0, "data": result, "message": "压缩完成"}


@router.post("/clean")
async def clean_old_sessions(max_age_days: int = Query(7, description="最大保留天数")):
    """
    清理过期会话接口
    
    清理超过指定天数的旧会话。
    """
    cleaned = memory_manager.clean_old_sessions(max_age_days)
    return {"code": 0, "data": {"cleaned": cleaned}, "message": "清理完成"}

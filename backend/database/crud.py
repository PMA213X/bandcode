"""
CRUD 操作 — 用户、会话、消息、任务的增删改查

提供四个主要数据对象的完整 CRUD 接口:
- 会话 (Session): 管理用户交互会话的生命周期
- 消息 (Message): 存储对话历史
- 任务 (Task): 跟踪 Planner 拆解的子任务状态
- 快照 (Checkpoint): 记录文件变更用于回滚
"""
from __future__ import annotations
import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from .models import Database


# ==================== 会话操作 ====================

def create_session(db: Database, project: str) -> dict:
    """创建新会话"""
    session_id = f"session-{uuid4().hex[:12]}"
    db.execute(
        "INSERT INTO sessions (session_id, project) VALUES (?, ?)",
        (session_id, project)
    )
    db.commit()
    return {"session_id": session_id, "project": project, "status": "active"}


def get_session(db: Database, session_id: str) -> Optional[dict]:
    """获取会话信息"""
    return db.fetchone(
        "SELECT * FROM sessions WHERE session_id = ?",
        (session_id,)
    )


def list_sessions(db: Database, project: str, limit: int = 50) -> list[dict]:
    """列出项目的所有会话"""
    return db.fetchall(
        "SELECT * FROM sessions WHERE project = ? ORDER BY created_at DESC LIMIT ?",
        (project, limit)
    )


def update_session_status(db: Database, session_id: str, status: str) -> None:
    """更新会话状态"""
    db.execute(
        "UPDATE sessions SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
        (status, session_id)
    )
    db.commit()


# ==================== 消息操作 ====================

def create_message(
    db: Database,
    session_id: str,
    role: str,
    content: str,
    agent: str = None
) -> dict:
    """创建新消息"""
    db.execute(
        "INSERT INTO messages (session_id, role, agent, content) VALUES (?, ?, ?, ?)",
        (session_id, role, agent, content)
    )
    db.commit()
    return {"session_id": session_id, "role": role, "agent": agent, "content": content}


def get_messages(
    db: Database,
    session_id: str,
    limit: int = 50,
    offset: int = 0
) -> list[dict]:
    """获取会话的消息历史"""
    return db.fetchall(
        "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC LIMIT ? OFFSET ?",
        (session_id, limit, offset)
    )


def get_message_count(db: Database, session_id: str) -> int:
    """获取消息数量"""
    result = db.fetchone(
        "SELECT COUNT(*) as count FROM messages WHERE session_id = ?",
        (session_id,)
    )
    return result["count"] if result else 0


# ==================== 任务操作 ====================

def create_task(
    db: Database,
    session_id: str,
    title: str,
    description: str = None
) -> dict:
    """创建新任务"""
    task_id = f"task-{uuid4().hex[:8]}"
    db.execute(
        "INSERT INTO tasks (task_id, session_id, title, description) VALUES (?, ?, ?, ?)",
        (task_id, session_id, title, description)
    )
    db.commit()
    return {"task_id": task_id, "title": title, "status": "pending"}


def get_task(db: Database, task_id: str) -> Optional[dict]:
    """获取任务详情"""
    return db.fetchone(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task_id,)
    )


def list_tasks(db: Database, session_id: str, status: str = None) -> list[dict]:
    """列出会话的所有任务"""
    if status:
        return db.fetchall(
            "SELECT * FROM tasks WHERE session_id = ? AND status = ? ORDER BY created_at",
            (session_id, status)
        )
    return db.fetchall(
        "SELECT * FROM tasks WHERE session_id = ? ORDER BY created_at",
        (session_id,)
    )


def update_task_status(db: Database, task_id: str, status: str) -> None:
    """更新任务状态"""
    completed_at = datetime.now().isoformat() if status == "completed" else None
    db.execute(
        "UPDATE tasks SET status = ?, completed_at = ? WHERE task_id = ?",
        (status, completed_at, task_id)
    )
    db.commit()


# ==================== 快照操作 ====================

def create_checkpoint(
    db: Database,
    session_id: str,
    description: str,
    files_changed: list[str],
    snapshot_path: str
) -> dict:
    """创建文件快照"""
    checkpoint_id = f"cp-{uuid4().hex[:8]}"
    db.execute(
        "INSERT INTO checkpoints (checkpoint_id, session_id, description, files_changed, snapshot_path) "
        "VALUES (?, ?, ?, ?, ?)",
        (checkpoint_id, session_id, description, json.dumps(files_changed), snapshot_path)
    )
    db.commit()
    return {
        "checkpoint_id": checkpoint_id,
        "description": description,
        "files_changed": files_changed
    }


def get_latest_checkpoint(db: Database, session_id: str) -> Optional[dict]:
    """获取最新的快照"""
    row = db.fetchone(
        "SELECT * FROM checkpoints WHERE session_id = ? ORDER BY rowid DESC LIMIT 1",
        (session_id,)
    )
    if row and row.get("files_changed"):
        row["files_changed"] = json.loads(row["files_changed"])
    return row


def list_checkpoints(db: Database, session_id: str) -> list[dict]:
    """列出会话的所有快照"""
    rows = db.fetchall(
        "SELECT * FROM checkpoints WHERE session_id = ? ORDER BY created_at DESC",
        (session_id,)
    )
    for row in rows:
        if row.get("files_changed"):
            row["files_changed"] = json.loads(row["files_changed"])
    return rows

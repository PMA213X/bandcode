"""
数据库表结构定义

BandCode 使用 SQLite 存储会话、消息、任务、快照等运行时数据。
配置和 Memory 使用 Markdown/JSON 文件存储，不经过数据库。

表结构:
- sessions: 会话表，记录每次用户交互会话
- messages: 消息表，存储用户和 Agent 的对话内容
- tasks: 任务表，跟踪 Planner 拆解的子任务
- checkpoints: 快照表，记录文件变更用于回滚
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Optional

# SQL 建表语句
CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    agent TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    description TEXT,
    files_changed TEXT,
    snapshot_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""


class Database:
    """SQLite 数据库管理器"""

    def __init__(self, db_path: str = "bandcode.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """建立数据库连接"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_tables(self) -> None:
        """初始化所有表结构"""
        if not self.conn:
            self.connect()
        self.conn.executescript(CREATE_TABLES)
        self.conn.commit()

    def close(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行 SQL 语句"""
        if not self.conn:
            self.connect()
        return self.conn.execute(sql, params)

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[dict]:
        """查询单条记录"""
        cursor = self.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self, sql: str, params: tuple = ()) -> list[dict]:
        """查询多条记录"""
        cursor = self.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def commit(self) -> None:
        """提交事务"""
        if self.conn:
            self.conn.commit()

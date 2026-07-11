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
-- 会话表：记录每次用户交互会话的生命周期
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,          -- 会话唯一标识，格式 session-{hex}
    project TEXT NOT NULL,                -- 项目名称
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 更新时间
    status TEXT DEFAULT 'active'          -- 状态：active/completed/archived
);

-- 消息表：存储用户和Agent的对话内容
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- 自增主键
    session_id TEXT NOT NULL,             -- 所属会话ID
    role TEXT NOT NULL,                   -- 角色：user/assistant
    agent TEXT,                           -- Agent名称（可选，如planner/tester）
    content TEXT NOT NULL,                -- 消息内容
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- 任务表：跟踪Planner拆解的子任务状态
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,             -- 任务唯一标识，格式 task-{hex}
    session_id TEXT NOT NULL,             -- 所属会话ID
    title TEXT NOT NULL,                  -- 任务标题
    description TEXT,                     -- 任务描述（可选）
    status TEXT DEFAULT 'pending',        -- 状态：pending/in_progress/completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    completed_at TIMESTAMP,               -- 完成时间（可选）
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

-- 快照表：记录文件变更，用于Review失败时回滚
CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id TEXT PRIMARY KEY,       -- 快照唯一标识，格式 cp-{hex}
    session_id TEXT NOT NULL,             -- 所属会话ID
    description TEXT,                     -- 快照描述
    files_changed TEXT,                   -- 变更文件列表（JSON格式）
    snapshot_path TEXT,                   -- 快照存储路径
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""


class Database:
    """SQLite 数据库管理器

    封装了 SQLite 的基本操作，提供统一的数据库访问接口。
    支持自动连接、表初始化、查询执行等功能。
    """

    def __init__(self, db_path: str = "bandcode.db"):
        """初始化数据库管理器

        Args:
            db_path: 数据库文件路径，默认为当前目录下的 bandcode.db
        """
        self.db_path = Path(db_path)  # 数据库文件路径
        self.conn: Optional[sqlite3.Connection] = None  # 数据库连接对象

    def connect(self) -> sqlite3.Connection:
        """建立数据库连接

        使用 sqlite3.Row 作为行工厂，使得查询结果可以通过列名访问。
        """
        self.conn = sqlite3.connect(str(self.db_path))  # 创建连接
        self.conn.row_factory = sqlite3.Row  # 设置行工厂，支持列名访问
        return self.conn

    def init_tables(self) -> None:
        """初始化所有表结构

        执行 CREATE_TABLES 中的SQL语句，创建所需的4张表：
        sessions、messages、tasks、checkpoints
        """
        if not self.conn:
            self.connect()
        self.conn.executescript(CREATE_TABLES)  # 执行建表SQL
        self.conn.commit()  # 提交事务

    def close(self) -> None:
        """关闭数据库连接，释放资源"""
        if self.conn:
            self.conn.close()  # 关闭连接
            self.conn = None  # 清空连接引用

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行SQL语句

        Args:
            sql: SQL语句，支持参数占位符 ?
            params: SQL参数，用于防止SQL注入

        Returns:
            游标对象，可用于获取查询结果
        """
        if not self.conn:
            self.connect()  # 自动连接（懒加载）
        return self.conn.execute(sql, params)

    def fetchone(self, sql: str, params: tuple = ()) -> Optional[dict]:
        """查询单条记录

        Args:
            sql: SELECT查询语句
            params: 查询参数

        Returns:
            字典格式的记录，如果没有结果则返回None
        """
        cursor = self.execute(sql, params)  # 执行查询
        row = cursor.fetchone()  # 获取单条记录
        return dict(row) if row else None  # 转换为字典

    def fetchall(self, sql: str, params: tuple = ()) -> list[dict]:
        """查询多条记录

        Args:
            sql: SELECT查询语句
            params: 查询参数

        Returns:
            字典列表，每条记录对应一个字典
        """
        cursor = self.execute(sql, params)  # 执行查询
        return [dict(row) for row in cursor.fetchall()]  # 转换为字典列表

    def commit(self) -> None:
        """提交事务，将修改持久化到数据库"""
        if self.conn:
            self.conn.commit()

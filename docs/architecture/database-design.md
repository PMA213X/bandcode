# 数据库设计文档

> 模块：`backend/database/`
> 负责人：成员E
> 更新时间：2026-07-10

---

## 一、概述

BandCode 使用 **SQLite** 存储运行时数据（会话、消息、任务、快照）。

配置和 Memory 使用 Markdown/JSON 文件存储，不经过数据库。

**选型理由**：
- 零配置，无需安装数据库服务
- 单文件存储，便于备份和迁移
- 适合 CLI 工具的轻量级场景

## 二、表结构设计

### 2.1 sessions 表

存储用户交互会话的生命周期。

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    project TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'  -- active / completed / archived
);
```

| 字段 | 类型 | 说明 |
|------|------|------|
| session_id | TEXT | 会话唯一标识，格式 `session-{hex}` |
| project | TEXT | 项目名称 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| status | TEXT | 状态：active/completed/archived |

### 2.2 messages 表

存储用户和 Agent 的对话内容。

```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,           -- user / assistant
    agent TEXT,                   -- Agent 名称（planner/tester/...）
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| session_id | TEXT | 所属会话 |
| role | TEXT | 角色：user/assistant |
| agent | TEXT | Agent 名称（可选） |
| content | TEXT | 消息内容 |

### 2.3 tasks 表

跟踪 Planner 拆解的子任务状态。

```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',  -- pending / in_progress / completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

| 字段 | 类型 | 说明 |
|------|------|------|
| task_id | TEXT | 任务唯一标识，格式 `task-{hex}` |
| session_id | TEXT | 所属会话 |
| title | TEXT | 任务标题 |
| description | TEXT | 任务描述 |
| status | TEXT | 状态：pending/in_progress/completed |
| completed_at | TIMESTAMP | 完成时间 |

### 2.4 checkpoints 表

记录文件变更，用于回滚。

```sql
CREATE TABLE checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    description TEXT,
    files_changed TEXT,             -- JSON 格式的变更文件列表
    snapshot_path TEXT,             -- 快照文件路径
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
```

| 字段 | 类型 | 说明 |
|------|------|------|
| checkpoint_id | TEXT | 快照唯一标识，格式 `cp-{hex}` |
| session_id | TEXT | 所属会话 |
| description | TEXT | 快照描述 |
| files_changed | TEXT | 变更文件列表（JSON） |
| snapshot_path | TEXT | 快照存储路径 |

## 三、ER 关系

```
sessions 1───* messages
sessions 1───* tasks
sessions 1───* checkpoints
```

## 四、CRUD 操作

### 4.1 会话操作

```python
from database import crud

# 创建会话
session = crud.create_session(db, "my-project")

# 获取会话
session = crud.get_session(db, "session-abc123")

# 列出会话
sessions = crud.list_sessions(db, "my-project", limit=10)

# 更新状态
crud.update_session_status(db, "session-abc123", "completed")
```

### 4.2 消息操作

```python
# 创建消息
msg = crud.create_message(db, "session-123", "user", "帮我实现登录功能")

# 获取消息列表
messages = crud.get_messages(db, "session-123", limit=50)

# 获取消息数量
count = crud.get_message_count(db, "session-123")
```

### 4.3 任务操作

```python
# 创建任务
task = crud.create_task(db, "session-123", "实现登录API")

# 获取任务
task = crud.get_task(db, "task-abc123")

# 更新状态
crud.update_task_status(db, "task-abc123", "completed")
```

### 4.4 快照操作

```python
# 创建快照
cp = crud.create_checkpoint(
    db, "session-123", "修改前快照",
    ["src/auth.py"], "/tmp/snapshot"
)

# 获取最新快照
latest = crud.get_latest_checkpoint(db, "session-123")
```

## 五、文件结构

```
backend/database/
├── __init__.py      # 模块导出
├── models.py        # 数据库连接和表结构
└── crud.py          # CRUD 操作
```

## 六、测试

```bash
cd backend
pytest tests/test_database.py -v
```

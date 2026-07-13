# 成员E 答辩提示

## 你的角色
后端开发工程师 B

## 答辩要点

### 1. 数据库设计（2分钟）
- SQLite 表结构设计
- 主要表：用户表、会话表、对话日志表、知识库表
- 数据库索引优化

### 2. 数据管理（2分钟）
- 用户管理功能
- 对话日志记录
- 知识库管理接口

### 3. 测试（2分钟）
- 单元测试策略
- 测试覆盖率
- 测试结果

### 负责的源代码文件

- `backend/database/models.py` — 数据库表结构定义，SQLite 建表语句（sessions/messages/tasks/checkpoints）、Database 管理器类
- `backend/database/crud.py` — CRUD 操作，会话/消息/任务/快照的增删改查
- `backend/memory/manager.py` — Memory Manager，统一管理记忆系统（会话、对话、工具调用、决策、错误记录）
- `backend/memory/store.py` — 六层分层 Memory 存储管理器（global/project/task/session/checkpoint/notes）
- `backend/memory/builder.py` — Prompt Builder，将各层上下文组装为完整 Prompt
- `backend/memory/compressor.py` — 会话压缩器，自动压缩过长会话、清理过期会话
- `backend/memory/index.py` — Memory 索引，支持快速搜索（JSON 索引文件）
- `backend/memory/auto_recorder.py` — 自动记录器，记录对话、工具调用、代码变更、决策、错误
- `backend/api/memory.py` — Memory API，获取/搜索/压缩/清理记忆
- `backend/api/project.py` — 项目 API，初始化项目、获取项目状态
- `backend/api/tools.py` — 工具 API，获取工具列表、调用工具
- `backend/api/workspace.py` — 工作区 API，获取工作区信息、列出文件、路径验证

### 所需知识点

- SQLite 数据库（CREATE TABLE、外键、索引）
- Python sqlite3 模块（Connection、Cursor、Row Factory）
- 分层记忆架构设计（六层 Memory 层级）
- JSON 文件读写与索引设计
- Markdown 文件解析与生成
- 文件系统操作（pathlib、shutil）

### 可能的问题

**Q1: 为什么选择 SQLite 而不是 MySQL？**

A: SQLite 是嵌入式数据库，无需额外安装数据库服务，部署简单。项目使用 sqlite3 模块直接操作，通过 Database 类封装了 connect、execute、fetchone、fetchall 等方法，使用 sqlite3.Row 作为行工厂支持按列名访问。SQLite 适合中小规模应用，BandCode 作为 AI 编程助手，数据量不大（主要是会话、消息、任务、快照），SQLite 完全够用。同时 SQLite 支持外键约束（FOREIGN KEY），保证了 sessions-messages、sessions-tasks、sessions-checkpoints 之间的引用完整性。

**Q2: 如何处理数据库迁移？**

A: 项目采用 CREATE TABLE IF NOT EXISTS 语句实现简单的表结构管理。Database.init_tables 方法执行 CREATE_TABLES SQL 脚本，如果表已存在则跳过创建。这种设计适合项目早期阶段，表结构相对稳定。如果需要添加新字段，可以通过 ALTER TABLE 语句手动迁移。项目的核心数据（配置、Memory）使用 Markdown/JSON 文件存储在 .mimo 目录下，不经过数据库，这也降低了数据库迁移的复杂度。

**Q3: 如何保证数据一致性？**

A: 数据一致性通过以下方式保证：一是 SQLite 外键约束，messages、tasks、checkpoints 表都通过 FOREIGN KEY 引用 sessions 表的 session_id；二是 Database 类的 commit 方法确保事务提交；三是 Memory 系统使用文件存储，MemoryStore 的 _write_file 方法确保父目录存在后再写入；四是工作流状态 PipelineState 使用 dataclass 定义，字段类型明确，通过 to_dict/from_dict 方法序列化和反序列化，保证状态传递的一致性。

**Q4: 如何优化查询性能？**

A: 项目通过以下方式优化查询：一是 sessions 表使用 session_id 作为主键（TEXT PRIMARY KEY），查询会话时直接主键查找；二是 messages、tasks、checkpoints 表通过 session_id 外键关联，查询某会话的消息时使用 WHERE session_id = ? 过滤；三是 Database.fetchall 方法将结果转换为字典列表，方便上层使用；四是 MemoryStore 的 search_memory 方法实现了简单的文本搜索，search_all_layers 方法支持跨层搜索。对于当前数据规模，这些优化已经足够。

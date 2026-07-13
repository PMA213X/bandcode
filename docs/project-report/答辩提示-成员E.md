# 成员E 答辩提示

## 你的角色
后端开发工程师 B

## 答辩要点

### 1. 数据库设计（2分钟）
- SQLite 表结构：sessions、messages、tasks、checkpoints 四张核心表
- 外键约束保证引用完整性（messages/tasks/checkpoints → sessions）
- CREATE TABLE IF NOT EXISTS 策略，启动时自动建表

### 2. Memory 系统（2分钟）
- 六层分层记忆：global（全局）、project（项目）、task（任务）、session（会话）、checkpoint（快照）、notes（笔记）
- MemoryStore 统一管理六层存储，每层独立目录
- Prompt Builder 将各层上下文组装为完整 Prompt 送给 LLM

### 3. 数据管理（2分钟）
- Memory API：获取/搜索/压缩/清理记忆
- Project API：项目初始化、状态查询
- Workspace API：工作区信息、文件列表、路径验证

### 负责的源代码文件

- `backend/database/models.py` — 数据库表结构定义，SQLite 建表语句（sessions/messages/tasks/checkpoints）、Database 管理器类
- `backend/database/crud.py` — CRUD 操作，会话/消息/任务/快照的增删改查
- `backend/memory/manager.py` — Memory Manager，统一管理记忆系统（会话记录、工具调用、决策、错误记录）
- `backend/memory/store.py` — 六层分层 Memory 存储管理器（global/project/task/session/checkpoint/notes）
- `backend/memory/builder.py` — Prompt Builder，将各层上下文组装为完整 Prompt
- `backend/memory/compressor.py` — 会话压缩器，自动压缩过长会话、清理过期会话
- `backend/memory/index.py` — Memory 索引，JSON 索引文件支持快速搜索
- `backend/memory/auto_recorder.py` — 自动记录器，记录对话、工具调用、代码变更、决策、错误
- `backend/api/memory.py` — Memory API，获取/搜索/压缩/清理记忆接口
- `backend/api/project.py` — 项目 API，初始化项目、获取项目状态
- `backend/api/tools.py` — 工具 API，获取工具列表、调用工具
- `backend/api/workspace.py` — 工作区 API，获取工作区信息、列出文件、路径验证

### 所需知识点

- SQLite 数据库（CREATE TABLE、FOREIGN KEY、索引、sqlite3.Row）
- Python sqlite3 模块（Connection、Cursor、Row Factory、事务提交）
- 分层记忆架构设计（六层 Memory 层级、每层职责与存储方式）
- JSON 文件读写与索引设计
- Markdown 文件解析与生成（frontmatter、内容读写）
- 文件系统操作（pathlib、shutil、目录创建与文件写入）

### 可能的问题

**Q1: 为什么选择 SQLite 而不是 MySQL 或 PostgreSQL？**

A: SQLite 是嵌入式数据库，无需额外安装数据库服务，部署简单。项目使用 sqlite3 模块直接操作，通过 Database 类封装了 connect、execute、fetchone、fetchall 等方法，使用 sqlite3.Row 作为行工厂支持按列名访问。BandCode 作为 AI 编程助手，数据量不大（主要是会话、消息、任务、快照），SQLite 完全够用。同时 SQLite 支持外键约束（FOREIGN KEY），保证了表之间的引用完整性。

**Q2: Memory 为什么设计为六层？每层的职责是什么？**

A: 六层设计模拟了人类工作的记忆结构：global 层存储跨项目的用户偏好和反馈；project 层存储项目级架构决策和规则；task 层记录当前任务的进展和发现；session 层保存当前会话的对话上下文；checkpoint 层是会话的定期快照，防止上下文丢失；notes 层是自由格式的临时笔记。Prompt Builder 按需从各层提取上下文组装成完整 Prompt，既保证信息完整又避免超出 Token 限制。

**Q3: 如何保证数据一致性？**

A: 通过以下方式保证：一是 SQLite 外键约束，messages、tasks、checkpoints 表通过 FOREIGN KEY 引用 sessions 表的 session_id；二是 Database 类的 commit 方法确保事务提交；三是 Memory 系统使用文件存储，MemoryStore 的 _write_file 方法确保父目录存在后再写入；四是 PipelineState 使用 dataclass 定义，字段类型明确，通过 to_dict/from_dict 方法序列化和反序列化，保证状态传递的一致性。

**Q4: 如何优化查询性能？**

A: 项目通过以下方式优化：一是 sessions 表使用 session_id 作为主键（TEXT PRIMARY KEY），查询时直接主键查找；二是 messages、tasks、checkpoints 表通过 session_id 外键关联，查询某会话的消息时使用 WHERE session_id = ? 过滤；三是 Database.fetchall 方法将结果转换为字典列表，方便上层使用；四是 MemoryStore 的 search_memory 方法实现了基于 BM25 的文本搜索，search_all_layers 支持跨层搜索，JSON 索引文件加速检索。

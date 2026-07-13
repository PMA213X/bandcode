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

1. 为什么选择 SQLite 而不是 MySQL？
2. 如何处理数据库迁移？
3. 如何保证数据一致性？
4. 如何优化查询性能？

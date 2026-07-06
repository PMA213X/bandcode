# 成员E — 后端开发工程师B（数据与业务逻辑方向）开发规划

> 角色：后端开发工程师
> 核心职责：数据库设计、Memory系统、Workflow管线、Prompt Builder
> 分支：feature/backend-data

---

## 一、角色定位

成员E 负责后端的「数据与核心逻辑」：

- SQLite 数据库设计（表结构、CRUD操作）
- 分层 Memory 系统（六层记忆的读写、检索、更新）
- Workflow 工作流管线（8个节点的编排执行）
- Review 修正循环
- 快照管理（Checkpoint）
- Prompt Builder（上下文组装）

---

## 二、开发任务清单

### Phase 0：环境准备（第1天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| E-01 | 克隆仓库 | — | git clone + 切换到 feature/backend-data 分支 |
| E-02 | 安装依赖 | — | sqlite3、aiosqlite |
| E-03 | 阅读架构文档 | — | 熟悉Memory和Workflow设计 |

### Phase 1：数据库与Memory（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| E-04 | 数据库表结构 | `database/models.py` | sessions/messages/tasks/checkpoints表 |
| E-05 | CRUD操作 | `database/crud.py` | 用户、会话、消息、任务的增删改查 |
| E-06 | database模块初始化 | `database/__init__.py` | 模块导出 |
| E-07 | 数据库测试 | `tests/test_database.py` | 表创建、CRUD测试 |
| E-08 | Memory存储 | `memory/store.py` | 六层Memory的读写、检索、更新 |
| E-09 | memory模块初始化 | `memory/__init__.py` | 模块导出 |
| E-10 | Memory测试 | `tests/test_memory.py` | Memory读写测试 |

### Phase 1：Prompt Builder（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| E-11 | Prompt Builder | `memory/builder.py` | 组装完整Prompt（系统指令+约束+RAG+Memory+Agent+用户输入） |
| E-12 | Prompt Builder测试 | `tests/test_builder.py` | Prompt组装测试 |

### Phase 2：Workflow管线（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| E-13 | 状态数据结构 | `workflow/state.py` | PipelineState定义 |
| E-14 | 工作流管线 | `workflow/pipeline.py` | 8个节点顺序执行的主管线 |
| E-15 | Review循环 | `workflow/review_loop.py` | 自动修正循环逻辑 |
| E-16 | 快照管理 | `workflow/checkpoint.py` | 文件快照创建、恢复 |
| E-17 | workflow模块初始化 | `workflow/__init__.py` | 模块导出 |
| E-18 | Pipeline测试 | `tests/test_pipeline.py` | 工作流测试 |

### Phase 2：Memory压缩（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| E-19 | Memory压缩器 | `memory/compressor.py` | Session历史自动压缩为摘要 |
| E-20 | 压缩器测试 | `tests/test_compressor.py` | 压缩逻辑测试 |

### Phase 3：集成与完善（第9-11天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| E-21 | Pipeline集成测试 | — | 测试完整工作流 |
| E-22 | Memory集成测试 | — | 测试六层Memory联动 |
| E-23 | 数据迁移脚本 | — | 数据库初始化和迁移 |

### Phase 4-5：联调与优化（第12-16天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| E-24 | 端到端测试 | — | 完整流程测试 |
| E-25 | 性能优化 | — | 数据库查询优化、Memory缓存 |
| E-26 | 数据备份策略 | — | 数据库备份和恢复 |

---

## 三、技术要点

### 3.1 数据库表结构

```python
# database/models.py
import sqlite3

# SQL建表语句
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
    role TEXT NOT NULL,           -- 'user' / 'assistant'
    agent TEXT,                   -- Agent名称
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',  -- 'pending' / 'in_progress' / 'completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    description TEXT,
    files_changed TEXT,             -- JSON格式的变更文件列表
    snapshot_path TEXT,             -- 快照文件路径
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
"""
```

### 3.2 Memory存储核心逻辑

```python
# memory/store.py
from pathlib import Path

class MemoryStore:
    """分层Memory存储管理器"""

    def __init__(self, project_path: str):
        self.base_path = Path(project_path) / ".mimo"

    def get_memory(self, layer: str, session_id: str = None) -> str:
        """读取指定层级的Memory"""
        if layer == "global":
            return self._read_file(self.base_path / "global" / "MEMORY.md")
        elif layer == "project":
            return self._read_file(self.base_path / "project" / "MEMORY.md")
        elif layer == "task":
            return self._get_current_task_memory(session_id)
        elif layer == "session":
            return self._read_file(self.base_path / "sessions" / f"{session_id}.md")
        elif layer == "checkpoint":
            return self._get_latest_checkpoint(session_id)

    def update_memory(self, layer: str, content: str, session_id: str = None):
        """更新指定层级的Memory（追加写入）"""
        ...

    def search_memory(self, layer: str, query: str) -> list[str]:
        """在指定层级中搜索相关内容"""
        ...
```

### 3.3 PipelineState数据结构

```python
# workflow/state.py
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PipelineState:
    """贯穿整个工作流的状态数据结构"""

    # === 输入 ===
    user_input: str
    session_id: str
    project: str

    # === Constraint Agent输出 ===
    constraints: list[str] = field(default_factory=list)
    constraint_summary: str = ""

    # === RAG输出 ===
    rag_context: str = ""

    # === Memory上下文 ===
    memory_context: dict = field(default_factory=dict)

    # === Planner输出 ===
    plan: Optional[dict] = None

    # === 子Agent输出 ===
    agent_output: Optional[dict] = None

    # === Tester输出 ===
    test_result: Optional[dict] = None

    # === Review Agent输出 ===
    review_result: Optional[dict] = None

    # === 流程控制 ===
    current_step: str = "init"
    approval_pending: bool = False
    approval_result: Optional[bool] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    done: bool = False
```

### 3.4 Workflow管线核心逻辑

```python
# workflow/pipeline.py
async def run_pipeline(state: PipelineState) -> PipelineState:
    """主工作流管线"""

    # ① 约束检索
    if settings["开启约束智能检索"]:
        state = await node_constraint(state)

    # ② RAG检索
    state = await node_rag(state)

    # ③ Prompt构建
    state = await node_prompt_build(state)

    # ④ Planner调度
    state = await node_planner(state)

    # ⑤ 审批检查
    if settings["审批模式"]:
        state = await node_approval(state)
        if not state.approval_result:
            state.done = True
            return state

    # ⑥ 子Agent执行
    state = await node_subagent(state)

    # ⑦ Tester验证
    state = await node_tester(state)
    if state.test_result["status"] == "failed":
        state.error = "测试失败"
        state.done = True
        return state

    # ⑧ Review审查
    if settings["开启自动约束检查"]:
        state = await node_review_loop(state)

    # 更新Memory
    await update_memories(state)
    state.done = True
    return state
```

### 3.5 Prompt Builder核心逻辑

```python
# memory/builder.py
class PromptBuilder:
    """将各层上下文组装为完整Prompt"""

    def build(self, state: PipelineState, agent_prompt: str) -> list[dict]:
        messages = []

        # 1. System Prompt
        messages.append({"role": "system", "content": self._build_system_prompt()})

        # 2. 约束摘要
        if state.constraint_summary:
            messages.append({"role": "system", "content": f"[项目约束]\n{state.constraint_summary}"})

        # 3. RAG上下文
        if state.rag_context:
            messages.append({"role": "system", "content": f"[知识库参考]\n{state.rag_context}"})

        # 4. Memory各层级
        for layer in ["global", "project", "task", "checkpoint"]:
            content = state.memory_context.get(layer)
            if content:
                messages.append({"role": "system", "content": f"[{layer} Memory]\n{content}"})

        # 5. Agent专属Prompt
        messages.append({"role": "system", "content": f"[Agent指令]\n{agent_prompt}"})

        # 6. 用户输入
        messages.append({"role": "user", "content": state.user_input})

        return messages
```

---

## 四、AI Agent 使用指南

### 4.1 推荐配置

| 任务类型 | Agent | 模型 | 理由 |
|---------|-------|------|------|
| 数据库表结构设计 | general | mimo-v2.5-pro | 需要仔细设计关系 |
| Memory系统实现 | general | mimo-v2.5-pro | 六层Memory逻辑复杂 |
| Pipeline实现 | general | mimo-v2.5-pro | 工作流核心，需要Pro |
| Prompt Builder | general | mimo-v2.5-pro | Prompt组装逻辑 |
| CRUD实现 | general | mimo-v2.5 | 标准数据库操作 |
| Checkpoint实现 | general | mimo-v2.5 | 快照逻辑相对简单 |
| 代码探索 | explore | mimo-v2.5 | 查找相关模块 |

### 4.2 使用示例

**设计数据库表结构时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 database/models.py，定义SQLite数据库表结构。
要求：
1. sessions表：session_id、project、created_at、updated_at、status
2. messages表：id、session_id、role、agent、content、created_at
3. tasks表：task_id、session_id、title、description、status、created_at
4. checkpoints表：checkpoint_id、session_id、description、files_changed、snapshot_path
参考文件：doc1.md 第2.5节数据持久层
```

**实现Memory系统时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 memory/store.py，分层Memory存储管理器。
要求：
1. 支持六层Memory：global/project/task/session/checkpoint/notes
2. 实现 get_memory()、update_memory()、search_memory() 方法
3. update_memory() 使用追加写入，保留历史
4. search_memory() 支持关键词搜索
参考文件：doc1.md 第3.4节记忆机制
```

**实现Workflow管线时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 workflow/pipeline.py，主工作流管线。
要求：
1. 实现 run_pipeline() 主函数
2. 按顺序执行8个节点：约束检索→RAG→Prompt构建→Planner→审批→子Agent→Tester→Review
3. 每个节点通过 PipelineState 传递状态
4. 支持配置开关控制各节点
参考文件：doc1.md 第3.2节节点执行流程
```

---

## 五、文件所有权

### 5.1 主责文件

```
database/__init__.py            ← 创建
database/models.py              ← 主责
database/crud.py                ← 主责
memory/__init__.py              ← 创建
memory/store.py                 ← 主责
memory/compressor.py            ← 主责
memory/builder.py               ← 主责
workflow/__init__.py            ← 创建
workflow/state.py               ← 主责
workflow/pipeline.py            ← 主责
workflow/review_loop.py         ← 主责
workflow/checkpoint.py          ← 主责
tests/test_database.py          ← 主责
tests/test_memory.py            ← 主责
tests/test_builder.py           ← 主责
tests/test_pipeline.py          ← 主责
tests/test_compressor.py        ← 主责
```

### 5.2 协作文件

| 文件 | 协作人 | 协作内容 |
|------|--------|---------|
| agents/manager.py | 成员C | Pipeline调用Agent |
| models/llm.py | 成员B | Memory压缩需要LLM |
| config/loader.py | 成员D | 获取配置 |
| agents/*.md | 成员A | Agent Prompt定义 |

---

## 六、接口依赖

### 6.1 我依赖的接口

| 依赖方 | 依赖内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员B | models/llm.py | Phase 1 | LLM调用（压缩需要） |
| 成员C | agents/manager.py | Phase 1 | Agent调用入口 |
| 成员D | config/loader.py | Phase 1 | 配置加载 |
| 成员A | agents/*.md | Phase 1 | Agent Prompt定义 |

### 6.2 我提供的接口

| 接收方 | 提供内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员D | database/models.py | Phase 1 | 数据库表结构 |
| 成员D | database/crud.py | Phase 1 | CRUD操作 |
| 成员D | memory/store.py | Phase 2 | Memory读写 |
| 成员D | workflow/pipeline.py | Phase 2 | 工作流调用 |
| 成员B | memory/store.py | Phase 1 | Memory读写 |
| 成员C | memory/store.py | Phase 1 | Memory读写 |
| 成员C | memory/builder.py | Phase 2 | Prompt构建 |

---

## 七、交付物清单

| 阶段 | 交付物 | 验收标准 |
|------|--------|---------|
| Phase 0 | 环境就绪 | SQLite可正常操作 |
| Phase 1 | 数据库、Memory系统、Prompt Builder | 单元测试通过 |
| Phase 2 | Workflow管线、Review循环、Checkpoint | 工作流可完整运行 |
| Phase 3 | 集成测试通过 | 各模块联动正常 |
| Phase 4 | 端到端测试通过 | 完整流程正常 |
| Phase 5 | 性能优化完成 | 数据库查询<50ms |

---

## 八、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| 数据库设计不合理 | 后期重构 | 先设计ER图，评审后实现 |
| Memory检索效率低 | 响应延迟 | 增加索引、优化搜索算法 |
| Pipeline状态丢失 | 工作流异常 | 增加Checkpoint机制 |
| 并发读写冲突 | 数据不一致 | 使用事务和锁机制 |

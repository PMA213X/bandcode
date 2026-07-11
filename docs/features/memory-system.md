# Memory 系统文档

> 模块：`backend/memory/`
> 负责人：成员E
> 更新时间：2026-07-10

---

## 一、概述

BandCode 的 Memory 系统采用**六层分层架构**，从粗粒度到细粒度依次为：

| 层级 | 路径 | 用途 | 更新频率 |
|------|------|------|---------|
| global | `.mimo/global/MEMORY.md` | 编码偏好、通用规范 | 低 |
| project | `.mimo/project/MEMORY.md` | 架构决策、项目约定 | 中 |
| task | `.mimo/tasks/task-{id}.md` | 单任务目标、进展 | 每任务 |
| session | `.mimo/sessions/{session_id}.md` | 对话历史摘要 | 每会话 |
| checkpoint | `.mimo/checkpoints/` | 文件变更快照 | 按需 |
| notes | `.mimo/notes/NOTES.md` | TODO、灵感 | 任意 |

## 二、核心组件

### 2.1 MemoryStore

六层 Memory 的统一读写、检索、更新管理器。

**核心方法**：

```python
class MemoryStore:
    def get_memory(layer: str, session_id: str = None) -> str
    def update_memory(layer: str, content: str, session_id: str = None)
    def overwrite_memory(layer: str, content: str, session_id: str = None)
    def search_memory(layer: str, query: str) -> list[str]
    def search_all_layers(query: str) -> dict[str, list[str]]
    def get_all_layers() -> dict[str, str]
```

**使用示例**：

```python
store = MemoryStore("/path/to/project")

# 读取全局 Memory
global_mem = store.get_memory("global")

# 更新项目 Memory
store.update_memory("project", "## 架构决策\n- 使用 FastAPI")

# 搜索相关内容
results = store.search_memory("project", "FastAPI")
```

### 2.2 PromptBuilder

将各层上下文组装为完整 Prompt。

**Prompt 结构**：

```
1. System Prompt（全局系统指令）
2. 约束摘要（来自 Constraint Agent）
3. RAG 上下文（来自知识库检索）
4. Memory 各层级（global → project → task → checkpoint）
5. Agent 专属 Prompt
6. 用户输入
```

**使用示例**：

```python
builder = PromptBuilder()
messages = builder.build(
    user_input="帮我实现登录功能",
    agent_prompt="你是项目架构师...",
    constraint_summary="使用 JWT 认证",
    rag_context="[1] src/auth.py...",
    memory_context={"global": "偏好 Python", "project": "FastAPI"}
)
```

### 2.3 MemoryCompressor

Session 历史自动压缩为摘要。

**压缩策略**：
- 当消息数量超过阈值（默认 1000）时触发
- 保留最近 10 条消息的关键信息
- 支持 LLM 生成高质量摘要（可选）

## 三、Memory 自动更新策略

| 触发时机 | 更新的层级 | 更新内容 |
|---------|-----------|---------|
| Planner 做出架构决策 | Project | 决策记录 |
| 子 Agent 完成代码生成 | Task | 修改原因、涉及文件 |
| Review Agent 修正违规 | Global | 新发现的编码规范 |
| Tester 测试通过 | Checkpoint | 文件快照 + 变更列表 |
| 会话结束 | Session | 对话历史压缩摘要 |

## 四、文件结构

```
backend/memory/
├── __init__.py          # 模块导出
├── store.py             # MemoryStore 核心类
├── builder.py           # PromptBuilder 组装器
└── compressor.py        # MemoryCompressor 压缩器
```

## 五、测试

```bash
cd backend
pytest tests/test_memory.py -v
```

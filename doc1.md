# BandCode — 智能体项目立项与架构说明书

> **项目名称**：BandCode — 基于分层记忆与六智能体协作的 AI 编程助手
> **版本**：v1.0 | **日期**：2025-07-05 | **文档性质**：立项与架构设计（初稿）
> - 文档一：BandCode 项目立项与架构说明书（含项目概述、系统架构、Agent 工作流、API 规范、团队分工）
> - 文档二：系统整体架构图（文本描述，可转绘图工具）
> - 文档三：Agent 工作流设计图（感知→规划→行动完整流程）
> - 文档四：前后端 API 接口定义表（8 个接口的完整定义）
---

## 目录

- [文档一：项目立项与架构说明书](#文档一项目立项与架构说明书)
  - [一、项目概述](#一项目概述)
  - [二、系统架构设计](#二系统架构设计)
  - [三、智能体核心工作流设计](#三智能体核心工作流设计)
  - [四、API 接口规范](#四api-接口规范)
  - [五、团队 7 人角色分工与协作流](#五团队-7-人角色分工与协作流)
- [文档二：系统整体架构图](#文档二系统整体架构图)
- [文档三：Agent 工作流设计图](#文档三agent-工作流设计图)
- [文档四：前后端 API 接口定义表](#文档四前后端-api-接口定义表)

---

# 文档一：项目立项与架构说明书

---

## 一、项目概述

### 1.1 项目名称

**BandCode** — 基于分层 Memory、六智能体协作与 RAG 的 AI CLI 编程助手。

### 1.2 项目背景与目标

#### 背景

当前 AI 编程辅助工具普遍存在以下痛点：

| 痛点 | 现状 | BandCode 的解决思路 |
|---|---|---|
| **无项目记忆** | 每次对话独立，AI 不记得项目的架构决策、编码规范和历史上下文 | 六层分层 Memory 体系（Global → Project → Task → Session → Checkpoint → Notes），实现项目级长期记忆 |
| **上下文浪费** | 简单地将全部 Memory 塞入 Prompt，token 消耗大且干扰多 | Constraint Agent 智能检索，按用户意图精准筛选相关约束，而非全量注入 |
| **输出无审核** | AI 生成的代码无人检查是否违反项目规范，质量不可控 | Review Agent 形成"生成→检查→修正"闭环，自动审核并修正违规输出 |
| **工具不可扩展** | Agent 能力写死在代码中，新增功能需改源码 | Markdown 定义 Agent + JSON 定义 Tool，自动扫描注册，零代码扩展 |
| **流程不透明** | 用户不知道 AI 内部经历了哪些步骤、做了什么决策 | 六 Agent 流水线全程 SSE 推送，每一步可见可审批 |

#### 目标

BandCode 的核心目标是打造一个 **架构清晰、记忆持久、输出可控、全程透明** 的 AI 编程助手 CLI 工具，重点解决"AI 编程时不懂项目上下文"这一根本问题。

**具体目标**：

1. **实现分层 Memory 系统**：让 AI 在每次对话中自动感知项目的全局规范、当前任务目标和历史决策。
2. **实现约束智能检索**：通过 Constraint Agent 按需检索相关约束，将 token 消耗降低 50% 以上。
3. **实现生成-审查闭环**：通过 Review Agent 自动检查输出合规性，保证 AI 产出符合项目标准。
4. **实现 6 Agent 协作流水线**：从需求分析到代码生成、测试验证、约束审查，全流程自动化。
5. **实现全配置驱动**：Agent、Tool、Workflow 均通过 Markdown/JSON 配置，修改配置即改变系统行为。

### 1.3 核心功能矩阵

#### P0（必须实现）

| 编号 | 功能 | 说明 |
|---|---|---|
| P0-1 | 六 Agent 协作系统 | Planner / SimpleCoder / ComplexCoder / Tester 四个业务 Agent + Constraint / Review 两个系统 Agent |
| P0-2 | 分层 Memory 系统 | Global → Project → Task → Session → Checkpoint 五层记忆，Markdown 存储 |
| P0-3 | RAG 知识库检索 | 支持 knowledge/ 目录下文档的自动索引、向量检索、上下文注入 |
| P0-4 | Tool Calling | 8 个内置工具（文件读写、搜索、任务管理等），自动注册机制 |
| P0-5 | SSE 流式输出 | 全程 Server-Sent Events 推送 Agent 状态、代码生成、测试结果 |
| P0-6 | 前后端 CRUD | 用户管理、会话管理、历史记录保存、设置读写 |
| P0-7 | 中文 CLI 交互界面 | React + Ink 实现的命令行界面，所有设置项、日志、Prompt 均为中文 |
| P0-8 | 配置驱动架构 | settings.json + Agent Markdown 定义 + Tool JSON 定义，修改配置即改变行为 |

#### P1（进阶功能）

| 编号 | 功能 | 说明 |
|---|---|---|
| P1-1 | Constraint Agent 约束智能检索 | 每次提问前自动从 Memory 中筛选相关约束，减少 token 消耗 |
| P1-2 | Review Agent 生成-审查闭环 | 代码生成后自动检查约束合规性，违规则自动修正 |
| P1-3 | 自动修正循环 + 快照回滚 | Review 失败后自动重新生成，超过最大次数可回滚到修改前快照 |
| P1-4 | 自定义 Agent 注册 | 用户在 agents/ 目录下新增 Markdown 文件即可注册新 Agent |
| P1-5 | 审批模式 | 高风险操作（代码修改、bash 执行、Agent 切换）需用户确认 |
| P1-6 | Session 自动恢复与压缩 | 重启项目后自动恢复上次会话，长会话自动压缩摘要 |
| P1-7 | Git 提交建议 | 达到提交节点时自动生成 Commit Message |

---

## 二、系统架构设计

### 2.1 三层架构概览

BandCode 采用经典的三层架构设计：**前端交互层 → 后端业务层 → 大模型推理层**，辅以数据持久层进行状态存储。

```
┌─────────────────────────────────────────────────────────────┐
│                      前端交互层                              │
│           React 18 + Ink 4 + TypeScript + Axios              │
│    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│    │ 聊天界面  │ │ 设置面板  │ │ Agent状态 │ │ Memory 浏览  │  │
│    └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘  │
│         └────────────┴────────────┴──────────────┘           │
│                          │ SSE / Axios                       │
└──────────────────────────┼───────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                      后端业务层                               │
│                  Python 3.11 + FastAPI                        │
│    ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│    │ 路由与 API  │ │ Agent管理 │ │ 工作流引擎│ │ 设置管理   │  │
│    └─────┬──────┘ └────┬─────┘ └────┬─────┘ └─────┬──────┘  │
│          └─────────────┴────────────┴─────────────┘          │
│                          │                                   │
└──────────────────────────┼───────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                    大模型推理层                                │
│              OpenAI Compatible API (MiMo)                     │
│    ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│    │ 6 Agent    │ │ Prompt   │ │ RAG 检索  │ │ Tool 调用  │  │
│    │ 协作引擎   │ │ Builder  │ │ Engine   │ │ Registry   │  │
│    └────────────┘ └──────────┘ └──────────┘ └────────────┘  │
└──────────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────┐
│                    数据持久层                                  │
│    ┌──────────────┐ ┌──────────┐ ┌────────────────────────┐  │
│    │ ChromaDB     │ │ SQLite   │ │ JSON + Markdown 文件    │  │
│    │ (向量数据库)  │ │ (会话/   │ │ (配置 / Memory /       │  │
│    │              │ │  任务)    │ │  Agent / Tool 定义)    │  │
│    └──────────────┘ └──────────┘ └────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 前端交互层

**技术选型**：React 18 + Ink 4 + TypeScript + Axios

**选型理由**：

| 选项 | 选择原因 |
|---|---|
| React + Ink（而非 Vue/HTML） | CLI 界面需要终端渲染，Ink 是 React 的终端渲染器，组件化开发体验与 Web 一致 |
| TypeScript | 类型安全，IDE 提示完善，适合多人协作 |
| Axios | 成熟的 HTTP 客户端，支持拦截器、请求取消，SSE 兼容 |

**前端职责**：

| 模块 | 职责 |
|---|---|
| 聊天界面 (`Chat.tsx`) | 用户输入、消息列表、打字机流式输出展示 |
| 设置面板 (`Settings.tsx`) | 全中文设置项展示与修改，分 6 大类 39 项 |
| Agent 状态 (`AgentStatus.tsx`) | 实时显示当前运行的 Agent、进度、状态 |
| Memory 浏览 (`MemoryView.tsx`) | 查看各层 Memory 内容，支持手动编辑 |
| 审批弹窗 (`ApprovalDialog.tsx`) | Planner 切换子 Agent 或高风险操作时请求用户确认 |
| SSE Hook (`useSSE.ts`) | 封装 Server-Sent Events 连接、事件解析、状态管理 |

**界面布局**：

```
┌─ BandCode ──────────────────────────────────────────┐
│                                                      │
│  [Constraint] 检索相关约束... 3 条匹配 ✅             │
│  [Planner] 需求分析完成，任务拆解为 3 步               │
│  [审批] 即将委派 ComplexCoder 执行 API 开发 [Y/n]     │
│  [ComplexCoder] 正在编写 src/auth.py ...              │
│  [Tool] write_file → src/auth.py ✅                   │
│  [Tester] 运行测试... 5/5 通过 ✅                     │
│  [Review] 约束合规检查... 通过 ✅                      │
│  [Memory] 已更新 Task / Checkpoint                    │
│                                                      │
├──────────────────────────────────────────────────────┤
│  > _                                                 │
└──────────────────────────────────────────────────────┘
```

### 2.3 后端业务层

**技术选型**：Python 3.11 + FastAPI + asyncio

**选型理由**：

| 选项 | 选择原因 |
|---|---|
| FastAPI（而非 Flask/Django） | 原生 async/await 支持，SSE 流式响应内建支持，自动 OpenAPI 文档 |
| asyncio | 多 Agent 并发执行、LLM 异步调用、Tool 并行执行的基础 |
| OpenAI SDK | 统一 LLM 调用接口，兼容 MiMo / DeepSeek / Claude / Qwen 等所有 OpenAI Compatible 模型 |

**后端职责**：

| 模块 | 文件 | 职责 |
|---|---|---|
| 路由层 | `api/chat.py`, `api/settings.py`, ... | RESTful API 路由定义、请求校验、SSE 响应封装 |
| Agent 管理 | `agents/manager.py` | Agent 自动发现、注册、实例化、权限校验 |
| Agent 基类 | `agents/base.py` | 统一的 Agent 接口、LLM 调用、Tool 调用、状态上报 |
| 业务 Agent | `agents/planner.py` 等 | Planner / SimpleCoder / ComplexCoder / Tester 的具体实现 |
| 系统 Agent | `agents/constraint.py`, `agents/review.py` | Constraint / Review 两个系统级 Agent |
| 工作流引擎 | `workflow/pipeline.py` | 主管线：约束检索 → Prompt 构建 → Planner → 子 Agent → 测试 → 审查 |
| Review 循环 | `workflow/review_loop.py` | 自动修正循环，超过最大次数后回滚或询问用户 |
| 快照管理 | `workflow/checkpoint.py` | 文件快照创建、恢复，支持自动回滚 |
| Memory 管理 | `memory/store.py` | 分层 Memory 的读写、检索、更新 |
| Memory 压缩 | `memory/compressor.py` | Session 历史自动压缩为摘要 |
| Prompt 构建 | `memory/builder.py` | 将 System + 约束 + RAG + Memory + Agent + 用户输入组装为完整 Prompt |
| RAG 引擎 | `rag/indexer.py`, `rag/retriever.py` | 文档切分、向量索引、相似度检索 |
| Tool 管理 | `tools/registry.py` | Tool 自动发现、注册、权限校验、执行 |
| LLM 封装 | `models/llm.py` | OpenAI SDK 统一调用，支持流式/非流式 |
| Embedding | `models/embedding.py` | sentence-transformers 文本向量化 |
| 配置加载 | `config/loader.py` | settings.json + 项目 config.json 的加载与合并 |

**关于 LangChain 的说明**：

本项目**不使用 LangChain 框架**，而是采用自研的轻量级编排方案。原因如下：

| 对比维度 | LangChain | BandCode 自研方案 |
|---|---|---|
| 代码量 | LangChain 本身抽象层厚，引入后基础代码膨胀 | 项目总控 4000-6000 行，每行代码职责清晰 |
| 可理解性 | 框架内部链路长，答辩时难以讲清每个环节 | 自研 Agent、Pipeline、Tool 每个模块边界清晰 |
| 灵活性 | 需遵循 LangChain 的 Chain/Agent/Tool 抽象 | 完全自由设计，分层 Memory、六 Agent 流水线等均为自研 |
| 学习价值 | 使用框架 API 属于"调包" | 自研编排逻辑体现对 LLM 应用架构的深入理解 |

**等价功能映射**：

| LangChain 概念 | BandCode 自研等价实现 |
|---|---|
| `ChatOpenAI` | `models/llm.py` — OpenAI SDK 封装 |
| `PromptTemplate` | `memory/builder.py` — PromptBuilder |
| `create_react_agent` | `agents/base.py` + `agents/manager.py` — Agent 基类 + 调度器 |
| `@tool` | `tools/registry.py` — ToolRegistry + JSON 定义 |
| `VectorStore` | `rag/retriever.py` — ChromaDB 直接封装 |
| `Checkpointer` | `workflow/checkpoint.py` — 自研快照系统 |
| `StateGraph` | `workflow/pipeline.py` — Pipeline 管线编排 |
| `MemorySaver` | `memory/store.py` — 分层 Memory Store |

### 2.4 大模型推理层

**模型选型**：

| Agent | 模型 | 温度 | 选型理由 |
|---|---|---|---|
| Planner | mimo-v2.5-pro | 0.3 | 需要强推理能力，分析需求、拆解任务 |
| ComplexCoder | mimo-v2.5-pro | 0.1 | 低温度保证代码准确性，pro 模型处理复杂逻辑 |
| SimpleCoder | mimo-v2.5 | 0.2 | 简单任务不需要最强模型，节省成本 |
| Tester | mimo-v2.5 | 0 | 零温度保证测试判断的一致性和确定性 |
| Constraint Agent | mimo-v2.5 | 0.1 | 检索和筛选任务，不需要高创造性 |
| Review Agent | mimo-v2.5-pro | 0 | 零温度保证审核标准的一致性 |

**调用协议**：统一使用 OpenAI Compatible API

```python
# 所有模型通过同一接口调用，仅 base_url 和 model 不同
client = OpenAI(base_url=settings["Base URL"], api_key=settings["API Key"])
response = client.chat.completions.create(
    model=agent_config["model"],
    messages=prompt_messages,
    temperature=agent_config["temperature"],
    stream=True  # SSE 流式输出
)
```

**支持的模型**（通过修改配置即可切换）：

| 模型 | Base URL | 说明 |
|---|---|---|
| MiMo v2.5 Pro | api.mimo.example.com | 默认主力模型 |
| MiMo v2.5 | api.mimo.example.com | 轻量模型，用于简单任务 |
| DeepSeek Chat | api.deepseek.com | 备选 |
| Claude | api.anthropic.com | 备选（需适配） |
| Qwen | dashscope.aliyuncs.com | 备选 |

### 2.5 数据持久层

| 存储类型 | 技术 | 存储内容 | 说明 |
|---|---|---|---|
| 向量数据库 | ChromaDB | RAG 文档向量索引 | knowledge/ 目录下的文档经切分、向量化后存入 |
| 关系型数据库 | SQLite | 会话表、消息表、任务表、快照表 | 会话历史、任务索引、快照元数据 |
| 文件存储 | JSON + Markdown | 配置文件、Memory 文件、Agent 定义、Tool 定义 | 所有配置和 Memory 均为人类可读的文本文件 |

**不使用数据库存储配置和 Memory 的理由**：

- Markdown/JSON 文件可直接用编辑器查看和修改，降低调试门槛
- Memory 文件可在 Git 中追踪变更历史
- Agent/Tool 定义文件可直接复制到其他项目复用
- 减少数据库依赖，部署更简单

---

## 三、智能体核心工作流设计

### 3.1 六 Agent 架构总览

BandCode 采用 **2 系统级 + 4 业务级** 的六 Agent 协作架构：

| Agent | 类型 | 可见性 | 角色 | 触发方式 |
|---|---|---|---|---|
| Constraint Agent | 系统级 | 用户不可见 | 从 Memory 中智能检索相关约束 | 用户输入后自动触发 |
| Planner | 业务级 | 用户可见 | 需求分析、任务拆解、Agent 调度 | 主 Agent，直接接收用户输入 |
| SimpleCoder | 业务级 | 用户可见 | UI 修改、单文件、小 Bug | Planner 指派 |
| ComplexCoder | 业务级 | 用户可见 | API 开发、重构、架构调整 | Planner 指派 |
| Tester | 业务级 | 用户可见 | 编译检查、测试执行、静态分析 | Planner 指派 |
| Review Agent | 系统级 | 用户不可见 | 检查输出是否违反项目约束 | Tester 通过后自动触发 |

**完整调用链路**：

```
用户输入
   │
   ▼
Constraint Agent    ← 系统级，自动触发
   │
   ▼
Planner             ← 业务级，主调度
   │
   ├──▶ SimpleCoder     ← Planner 指派
   ├──▶ ComplexCoder    ← Planner 指派
   └──▶ Tester          ← Planner 指派
   │
   ▼
Review Agent        ← 系统级，自动触发
   │
   ├──▶ 通过 → 更新 Memory → 返回结果
   └──▶ 不通过 → 重新提交给 Planner 修正
                    │
                    └──▶ 循环最多 N 次
```

### 3.2 节点（Nodes）与状态（State）

BandCode 的工作流引擎采用 **Pipeline + 状态传递** 模式，等价于 LangGraph 的 StateGraph 设计。

#### 状态数据结构（PipelineState）

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class PipelineState:
    """贯穿整个工作流的状态数据结构"""

    # === 输入 ===
    user_input: str                          # 用户原始输入
    session_id: str                          # 会话 ID
    project: str                             # 当前项目名

    # === Constraint Agent 输出 ===
    constraints: list[str] = field(default_factory=list)   # 检索到的约束列表
    constraint_summary: str = ""                           # 约束摘要

    # === RAG 输出 ===
    rag_context: str = ""                                # RAG 检索到的知识库上下文

    # === Memory 上下文 ===
    memory_context: dict = field(default_factory=dict)
    # 结构: {"global": "...", "project": "...", "task": "...", "checkpoint": "..."}

    # === Planner 输出 ===
    plan: Optional[dict] = None
    # 结构: {"tasks": [...], "delegated_agent": "simple-coder", "reason": "..."}

    # === 子 Agent 输出 ===
    agent_output: Optional[dict] = None
    # 结构: {"agent": "complex-coder", "files_changed": [...], "code": "..."}

    # === Tester 输出 ===
    test_result: Optional[dict] = None
    # 结构: {"status": "passed", "tests": 5, "errors": [...]}

    # === Review Agent 输出 ===
    review_result: Optional[dict] = None
    # 结构: {"passed": bool, "violations": [...]}

    # === 流程控制 ===
    current_step: str = "init"           # 当前步骤名
    approval_pending: bool = False       # 是否等待用户审批
    approval_result: Optional[bool] = None  # 审批结果
    retry_count: int = 0                 # 修正循环计数
    max_retries: int = 3                 # 最大修正次数
    error: Optional[str] = None          # 错误信息
    done: bool = False                   # 流程是否结束
```

#### 节点定义

工作流由以下 **8 个节点** 顺序执行：

| 节点 | 函数名 | 输入状态 | 输出状态 | 说明 |
|---|---|---|---|---|
| ① 约束检索 | `node_constraint` | user_input, project | constraints, constraint_summary | Constraint Agent 从 Memory 中筛选相关约束 |
| ② RAG 检索 | `node_rag` | user_input | rag_context | 从 ChromaDB 检索相关知识库文档 |
| ③ Prompt 构建 | `node_prompt_build` | constraints, rag_context, memory_context | — | 将各层上下文组装为完整 Prompt |
| ④ Planner 调度 | `node_planner` | 完整 Prompt | plan | 需求分析、任务拆解、选择子 Agent |
| ⑤ 审批检查 | `node_approval` | plan | approval_pending, approval_result | 高风险操作请求用户确认 |
| ⑥ 子 Agent 执行 | `node_subagent` | plan | agent_output | SimpleCoder 或 ComplexCoder 执行代码生成 |
| ⑦ Tester 验证 | `node_tester` | agent_output | test_result | 编译检查、测试执行、静态分析 |
| ⑧ Review 审查 | `node_review` | agent_output, constraints | review_result | 检查输出是否违反项目约束 |

#### 节点执行流程

```python
async def run_pipeline(state: PipelineState) -> PipelineState:
    """主工作流管线"""

    # ① 约束检索（可关闭）
    if settings["开启约束智能检索"]:
        state = await node_constraint(state)

    # ② RAG 检索
    state = await node_rag(state)

    # ③ Prompt 构建
    state = await node_prompt_build(state)

    # ④ Planner 调度
    state = await node_planner(state)

    # ⑤ 审批检查（可关闭）
    if settings["审批模式"]:
        state = await node_approval(state)
        if not state.approval_result:
            state.done = True
            return state

    # ⑥ 子 Agent 执行
    state = await node_subagent(state)

    # ⑦ Tester 验证
    state = await node_tester(state)
    if state.test_result["status"] == "failed":
        state.error = "测试失败"
        state.done = True
        return state

    # ⑧ Review 审查（可关闭）
    if settings["开启自动约束检查"]:
        state = await node_review_loop(state)

    # 更新 Memory
    await update_memories(state)
    state.done = True
    return state
```

### 3.3 工具集（Tools）

BandCode 内置 **8 个工具**，通过 ToolRegistry 统一管理。

#### 工具注册机制

```python
class Tool:
    """工具基类"""
    name: str              # 工具名称
    description: str       # 工具描述
    permission: str        # 所需权限 (read / edit / bash / ...)
    parameters: dict       # JSON Schema 参数定义

    async def execute(self, args: dict) -> ToolResult:
        """执行工具"""
        ...

class ToolRegistry:
    """工具注册中心"""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def auto_discover(self, tools_dir: str):
        """自动扫描 tools/ 目录，注册所有 JSON 定义的工具"""
        for file in Path(tools_dir).glob("*.json"):
            config = json.loads(file.read_text())
            tool = Tool.from_config(config)
            self.tools[tool.name] = tool

    async def call(self, name: str, args: dict, agent_permissions: dict) -> ToolResult:
        """调用工具，检查权限后执行"""
        tool = self.tools.get(name)
        if not tool:
            return ToolResult(success=False, error=f"工具 {name} 不存在")
        if agent_permissions.get(tool.permission) != "allow":
            return ToolResult(success=False, error=f"权限不足: {tool.permission}")
        return await tool.execute(args)
```

#### 内置工具详细定义

| 工具名 | 说明 | 所需权限 | 输入参数 | 输出 |
|---|---|---|---|---|
| `read_file` | 读取指定路径的文件内容 | read | `path: string` (文件路径) | 文件内容文本 |
| `write_file` | 写入或创建文件 | edit | `path: string`, `content: string` | 写入成功/失败 |
| `list_directory` | 列出目录结构 | read | `path: string`, `depth: int` (可选) | 目录树文本 |
| `search_project` | 全文搜索项目文件 | read | `query: string`, `file_pattern: string` (可选) | 匹配结果列表 |
| `search_knowledge` | 搜索 RAG 知识库 | read | `query: string`, `top_k: int` (可选) | 相关文档片段 |
| `create_task` | 创建新任务 | todowrite | `title: string`, `description: string` | 任务 ID |
| `update_memory` | 写入或更新 Memory | edit | `layer: string`, `content: string` | 更新成功/失败 |
| `finish_task` | 标记任务完成 | todowrite | `task_id: string`, `summary: string` | 完成成功/失败 |

#### Tool 调用示例（LLM 输出格式）

```json
{
  "tool_calls": [
    {
      "tool": "write_file",
      "args": {
        "path": "src/auth.py",
        "content": "from fastapi import APIRouter\n..."
      }
    }
  ]
}
```

#### 工具权限矩阵

不同 Agent 拥有不同的工具权限：

| 权限 | Planner | SimpleCoder | ComplexCoder | Tester |
|---|---|---|---|---|
| read | allow | allow | allow | allow |
| edit | allow | allow | allow | **deny** |
| bash | allow | allow | allow | allow |
| todoread | allow | allow | allow | allow |
| todowrite | allow | allow | allow | allow |
| websearch | allow | allow | allow | allow |
| codesearch | allow | allow | allow | allow |
| skill | allow | — | — | — |

**关键约束**：Tester 的 edit 权限为 deny，禁止修改任何代码文件。

### 3.4 记忆机制（Memory）

#### 分层 Memory 架构

BandCode 设计了 **六层 Memory**，从粗粒度到细粒度依次为：

```
┌─────────────────────────────┐
│   Global Memory (全局)       │  编码偏好、通用规范、技术栈偏好
│   .mimo/global/MEMORY.md    │  更新频率：低
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│   Project Memory (项目)      │  架构决策、模块说明、项目约定
│   .mimo/project/MEMORY.md   │  更新频率：中
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│   Task Memory (任务)         │  单任务目标、进展、决策
│   .mimo/tasks/task-{id}.md  │  更新频率：每任务
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│   Session Memory (会话)      │  对话历史摘要
│   .mimo/sessions/           │  更新频率：每会话
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│   Checkpoint (快照)          │  文件变更列表、快照摘要
│   .mimo/checkpoints/        │  更新频率：按需
└──────────┬──────────────────┘
           ▼
┌─────────────────────────────┐
│   Notes (备忘)               │  TODO、临时记录、灵感
│   .mimo/notes/              │  更新频率：任意
└─────────────────────────────┘
```

#### 会话隔离

每个 Session 通过唯一的 `session_id` 隔离，等价于 LangChain 的 `thread_id`：

```python
class MemoryStore:
    """分层 Memory 存储管理器"""

    def __init__(self, project_path: str):
        self.base_path = Path(project_path) / ".mimo"

    def get_memory(self, layer: str, session_id: str = None) -> str:
        """读取指定层级的 Memory"""
        if layer == "global":
            return (self.base_path / "global" / "MEMORY.md").read_text()
        elif layer == "project":
            return (self.base_path / "project" / "MEMORY.md").read_text()
        elif layer == "task":
            return self._get_current_task_memory(session_id)
        elif layer == "session":
            return (self.base_path / "sessions" / f"{session_id}.md").read_text()
        elif layer == "checkpoint":
            return self._get_latest_checkpoint(session_id)

    def update_memory(self, layer: str, content: str, session_id: str = None):
        """更新指定层级的 Memory"""
        # 追加写入，保留历史
        ...

    def search_memory(self, layer: str, query: str) -> list[str]:
        """在指定层级中搜索与 query 相关的内容"""
        # 用于 Constraint Agent 的检索
        ...
```

#### Memory 自动更新策略

| 触发时机 | 更新的 Memory 层 | 更新内容 |
|---|---|---|
| Planner 做出架构决策 | Project Memory | 决策记录 |
| 子 Agent 完成代码生成 | Task Memory | 修改原因、涉及文件、变更摘要 |
| Review Agent 修正违规 | Global Memory | 新发现的编码规范 |
| Tester 测试通过 | Checkpoint | 文件快照 + 变更列表 |
| 会话结束 | Session Memory | 对话历史压缩摘要 |

#### Memory 文件示例

**Project Memory** (`project/MEMORY.md`)：

```markdown
# 项目 Memory

## 架构决策
- 前端使用 React + Ink CLI 框架
- 后端使用 Python + FastAPI，不使用 LangChain
- 通信使用 SSE 流式传输
- 数据持久层：ChromaDB（向量）+ SQLite（关系）+ JSON/Markdown（配置）

## 编码规范
- 所有注释使用简体中文
- 函数命名使用 snake_case
- 类命名使用 PascalCase
- 每个模块必须有 __init__.py

## 模块说明
- agents/: Agent 定义与调度
- memory/: 分层 Memory 管理
- rag/: 向量检索
- workflow/: 工作流管线
- tools/: 工具注册与执行
```

**Task Memory** (`tasks/task-001.md`)：

```markdown
# 任务：实现用户登录功能

## 目标
实现 JWT 认证的用户登录 API

## 涉及文件
- src/auth.py (新增)
- src/models/user.py (新增)
- tests/test_auth.py (新增)

## 决策记录
- 密码使用 bcrypt 加密，rounds=12
- Token 有效期 24 小时
- 使用 HS256 算法签名

## 状态
✅ 已完成
```

### 3.5 Prompt Builder 详细设计

Prompt Builder 负责将各层上下文组装成最终发送给 LLM 的完整 Prompt：

```python
class PromptBuilder:
    """将各层上下文组装为完整 Prompt"""

    def build(self, state: PipelineState, agent_prompt: str) -> list[dict]:
        """构建完整的消息列表"""
        messages = []

        # 1. System Prompt（全局系统指令）
        messages.append({
            "role": "system",
            "content": self._build_system_prompt()
        })

        # 2. 约束摘要（来自 Constraint Agent）
        if state.constraint_summary:
            messages.append({
                "role": "system",
                "content": f"[项目约束]\n{state.constraint_summary}"
            })

        # 3. RAG 上下文
        if state.rag_context:
            messages.append({
                "role": "system",
                "content": f"[知识库参考]\n{state.rag_context}"
            })

        # 4. Memory 各层级
        for layer in ["global", "project", "task", "checkpoint"]:
            content = state.memory_context.get(layer)
            if content:
                messages.append({
                    "role": "system",
                    "content": f"[{layer} Memory]\n{content}"
                })

        # 5. Agent 专属 Prompt
        messages.append({
            "role": "system",
            "content": f"[Agent 指令]\n{agent_prompt}"
        })

        # 6. 用户输入
        messages.append({
            "role": "user",
            "content": state.user_input
        })

        return messages
```

**最终 Prompt 结构示意**：

```
┌──────────────────────────────────┐
│  [系统指令]                       │  全局系统规则
│  你是 BandCode AI 编程助手...     │
├──────────────────────────────────┤
│  [项目约束]                       │  ← Constraint Agent 输出
│  - 使用 JWT 认证                  │
│  - 密码使用 bcrypt 加密           │
│  - API 返回格式: {code,data,msg}  │
├──────────────────────────────────┤
│  [知识库参考]                     │  ← RAG 检索结果
│  [1] src/auth.py: JWT 模块...    │
│  [2] docs/api.md: API 规范...    │
├──────────────────────────────────┤
│  [global Memory]                 │  ← 全局记忆
│  偏好 Python 3.11+, 类型注解...   │
├──────────────────────────────────┤
│  [project Memory]                │  ← 项目记忆
│  FastAPI + SQLAlchemy 架构...    │
├──────────────────────────────────┤
│  [task Memory]                   │  ← 任务记忆
│  当前任务：用户登录功能...        │
├──────────────────────────────────┤
│  [Agent 指令]                     │  ← Agent 专属 Prompt
│  你是项目架构师与项目经理...      │
├──────────────────────────────────┤
│  [用户输入]                       │  ← 用户原始输入
│  帮我实现用户登录功能             │
└──────────────────────────────────┘
```

### 3.6 Agent 详细设计

#### ① Constraint Agent（约束检索智能体）

**类型**：系统级，用户不可见
**触发**：每次用户输入后自动触发（可通过开关关闭）
**模型**：mimo-v2.5，温度 0.1

```python
class ConstraintAgent:
    """约束检索智能体 — 从 Memory 中筛选与当前问题相关的约束"""

    async def run(self, state: PipelineState) -> PipelineState:
        # 1. 解析用户意图
        intent = await self.llm.classify(state.user_input)

        # 2. 检索各层 Memory
        global_results = self.memory.search_memory("global", intent)
        project_results = self.memory.search_memory("project", intent)
        task_results = self.memory.search_memory("task", intent)

        # 3. 去重 + 排序
        all_constraints = self.deduplicate_and_rank(
            global_results, project_results, task_results, top_k=10
        )

        # 4. 生成约束摘要
        summary = await self.llm.summarize(all_constraints)

        state.constraints = all_constraints
        state.constraint_summary = summary
        return state
```

**SSE 推送事件**：

```json
{"event": "agent_start", "data": {"agent": "constraint", "status": "检索相关约束..."}}
{"event": "constraint_result", "data": {"count": 3, "summary": "当前任务需遵循认证规范和 API 格式约定"}}
```

#### ② Planner Agent（规划调度智能体）

**类型**：业务级，主调度（primary）
**模型**：mimo-v2.5-pro，温度 0.3，步骤上限 20

**职责**：
1. 接收用户需求 + 约束摘要 + RAG 上下文
2. 需求分析与任务拆解
3. 风险评估与影响范围分析
4. 选择子 Agent（SimpleCoder / ComplexCoder）
5. **请求用户审批**（审批模式开启时）
6. 委派子 Agent 执行
7. 委派 Tester 验证

**审批机制**：

以下行为发生前必须暂停并请求用户确认：

| 行为 | 审批内容 |
|---|---|
| 切换子 Agent | 输出委派的 Agent 名称、原因 |
| 开始代码修改 | 输出修改计划、涉及文件 |
| 执行 bash/git 操作 | 输出具体命令 |
| 进入测试流程 | 输出测试范围 |

**SSE 推送事件**：

```json
{"event": "agent_start", "data": {"agent": "planner", "status": "分析需求..."}}
{"event": "plan", "data": {"tasks": ["1.创建User模型", "2.实现登录API", "3.编写测试"], "delegated_agent": "complex-coder"}}
{"event": "approval_required", "data": {"plan": "...", "agent": "complex-coder", "reason": "涉及API开发"}}
```

#### ③ SimpleCoder Agent（简单编码智能体）

**类型**：业务级，子 Agent（subagent）
**模型**：mimo-v2.5，温度 0.2

**适用场景**：UI 修改、配置调整、单文件修改、小型 Bug 修复

**自动升级条件**（应建议转交 ComplexCoder）：
- 涉及超过 2 个文件
- 修改超过 300 行代码
- 涉及架构调整

#### ④ ComplexCoder Agent（复杂编码智能体）

**类型**：业务级，子 Agent（subagent）
**模型**：mimo-v2.5-pro，温度 0.1

**适用场景**：核心业务逻辑、API 开发、架构调整、跨模块重构

**硬约束**：
- 必须主动输出完整代码，不得只描述方案
- 完成后记录：修改原因、涉及模块、涉及文件、文档更新建议

#### ⑤ Tester Agent（测试验证智能体）

**类型**：业务级，子 Agent（subagent）
**模型**：mimo-v2.5，温度 0，步骤上限 10

**硬约束**：
- **edit 权限：deny** — 禁止修改任何代码文件
- 禁止自动修复
- 失败时必须停止执行并等待用户确认

**输出格式**：

```json
{
  "status": "failed",
  "tests_total": 5,
  "tests_passed": 3,
  "errors": [
    {
      "file": "src/auth.py",
      "line": 42,
      "error": "NameError: name 'jwt' is not defined",
      "suggestion": "请在文件顶部添加 import jwt"
    }
  ]
}
```

#### ⑥ Review Agent（约束审查智能体）

**类型**：系统级，用户不可见
**触发**：Tester 通过后自动触发（可通过开关关闭）
**模型**：mimo-v2.5-pro，温度 0

```python
class ReviewAgent:
    """约束审查智能体 — 检查输出是否违反项目约束"""

    async def run(self, state: PipelineState) -> PipelineState:
        violations = []

        # 1. 检查是否违反 Memory 约束
        for constraint in state.constraints:
            if not await self.check_compliance(state.agent_output, constraint):
                violations.append({
                    "constraint": constraint,
                    "severity": "high",
                    "detail": "..."
                })

        # 2. 检查编码规范
        code_violations = await self.check_code_style(
            state.agent_output["files_changed"]
        )
        violations.extend(code_violations)

        # 3. 检查 Prompt 规则
        prompt_violations = await self.check_prompt_rules(state.agent_output)
        violations.extend(prompt_violations)

        state.review_result = {
            "passed": len(violations) == 0,
            "violations": violations
        }
        return state
```

#### Review 修正循环

```python
async def node_review_loop(state: PipelineState) -> PipelineState:
    """Review + 自动修正循环"""
    for attempt in range(state.max_retries):
        state = await review_agent.run(state)

        if state.review_result["passed"]:
            return state  # ✅ 审查通过

        if not settings["自动修正"]:
            # 不自动修正，报告给用户
            state.error = f"审查未通过: {state.review_result['violations']}"
            return state

        # 自动修正：将违规信息反馈给主 Agent 重新生成
        state.user_input = (
            f"请修正以下违规项：\n"
            + "\n".join(f"- {v['detail']}" for v in state.review_result["violations"])
        )
        state.retry_count += 1

        # 重新执行子 Agent
        state = await node_subagent(state)
        state = await node_tester(state)

        if state.test_result["status"] == "failed":
            break

    # 超过最大修正次数
    if settings["修正失败自动回滚"]:
        await checkpoint_manager.restore(state.session_id)
        state.error = "修正失败，已自动回滚到修改前状态"
    else:
        state.error = f"已达最大修正次数({state.max_retries})，请手动处理"

    return state
```

### 3.7 完整 Workflow 配置开关

| 开关名称 | 默认值 | 关闭后行为 |
|---|---|---|
| 开启约束智能检索 | 开 | 跳过 Constraint Agent，直接注入全部 Memory |
| 开启自动约束检查 | 开 | 跳过 Review Agent，生成后直接返回 |
| 自动修正 | 开 | Review 失败只报告，不自动重新生成 |
| 最大修正次数 | 3 | — |
| 修正失败自动回滚 | 开 | 失败后需手动处理，不自动回滚 |
| 自动更新文档 | 开 | 代码修改后不自动更新相关文档 |
| 自动更新 Memory | 开 | 不自动写入 Memory |
| Git 提交建议 | 开 | 不自动生成 Commit Message |
| 审批模式 | 开 | Planner 不请求审批，直接执行 |

---

## 四、API 接口规范

### 4.1 接口总览

| 序号 | 方法 | 路径 | 说明 | 关联前端组件 |
|---|---|---|---|---|
| 1 | POST | `/api/users/create` | 创建/初始化用户 | 初始化流程 |
| 2 | POST | `/api/chat/stream` | 流式聊天（SSE） | Chat.tsx |
| 3 | GET | `/api/chat/history` | 获取聊天历史 | Chat.tsx |
| 4 | POST | `/api/project/init` | 初始化项目 | 初始化流程 |
| 5 | GET | `/api/settings` | 获取全部设置 | Settings.tsx |
| 6 | POST | `/api/settings` | 更新设置 | Settings.tsx |
| 7 | GET | `/api/memory` | 获取指定层级 Memory | MemoryView.tsx |
| 8 | POST | `/api/tools/call` | 手动调用 Tool | 调试面板 |

### 4.2 核心接口详细定义

#### 接口 1：创建用户

```
POST /api/users/create
```

**请求体**：

```json
{
  "username": "developer_01",
  "preferences": {
    "language": "zh-CN",
    "theme": "dark"
  }
}
```

**响应**：

```json
{
  "code": 200,
  "data": {
    "user_id": "u_abc123",
    "username": "developer_01",
    "created_at": "2025-07-05T10:00:00Z"
  },
  "message": "用户创建成功"
}
```

#### 接口 2：流式聊天（SSE）

```
POST /api/chat/stream
Content-Type: application/json
Accept: text/event-stream
```

**请求体**：

```json
{
  "session_id": "session-abc123",
  "project": "my-project",
  "message": "帮我实现用户登录功能",
  "options": {
    "agent": "auto",
    "workflow": "auto"
  }
}
```

**响应**（SSE 流）：

```
event: agent_start
data: {"agent": "constraint", "status": "检索相关约束..."}

event: constraint_result
data: {"constraints": ["使用JWT认证", "密码bcrypt加密", "API格式统一"], "summary": "..."}

event: agent_start
data: {"agent": "planner", "status": "分析需求..."}

event: plan
data: {"tasks": ["1.创建User模型", "2.实现登录API", "3.编写测试"], "delegated_agent": "complex-coder"}

event: approval_required
data: {"plan": "...", "agent": "complex-coder", "reason": "涉及API开发，需要complex-coder处理"}

event: approval_response
data: {"approved": true}

event: agent_start
data: {"agent": "complex-coder", "status": "编写代码..."}

event: tool_call
data: {"tool": "write_file", "args": {"path": "src/auth.py"}}

event: code
data: {"file": "src/auth.py", "content": "from fastapi import APIRouter\n..."}

event: agent_start
data: {"agent": "tester", "status": "运行测试..."}

event: test_result
data: {"status": "passed", "tests": 5, "coverage": "82%"}

event: agent_start
data: {"agent": "review", "status": "检查约束合规..."}

event: review_result
data: {"status": "passed", "violations": []}

event: memory_update
data: {"layers": ["task", "checkpoint"], "message": "已更新 Memory"}

event: done
data: {"session_id": "session-abc123", "summary": "用户登录功能已完成"}
```

#### 接口 3：获取聊天历史

```
GET /api/chat/history?session_id=session-abc123&limit=50&offset=0
```

**响应**：

```json
{
  "code": 200,
  "data": {
    "session_id": "session-abc123",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "帮我实现用户登录功能",
        "created_at": "2025-07-05T10:00:00Z"
      },
      {
        "id": 2,
        "role": "assistant",
        "agent": "planner",
        "content": "分析需求，拆解为3个任务...",
        "created_at": "2025-07-05T10:00:05Z"
      }
    ],
    "total": 12,
    "has_more": false
  },
  "message": "查询成功"
}
```

#### 接口 4：初始化项目

```
POST /api/project/init
```

**请求体**：

```json
{
  "project_name": "my-project",
  "path": "/home/user/projects/my-project",
  "language": "python",
  "framework": "fastapi"
}
```

**响应**：

```json
{
  "code": 200,
  "data": {
    "project": "my-project",
    "mimo_dir": "/home/user/projects/my-project/.mimo",
    "structure": {
      "global/MEMORY.md": "created",
      "project/MEMORY.md": "created",
      "tasks/": "created",
      "sessions/": "created",
      "checkpoints/": "created",
      "notes/": "created",
      "config.json": "created"
    }
  },
  "message": "项目初始化完成"
}
```

#### 接口 5：获取设置

```
GET /api/settings
```

**响应**：

```json
{
  "code": 200,
  "data": {
    "模型设置": {
      "默认模型": "xiaomi-tokenplan/mimo-v2.5-pro",
      "Base URL": "https://api.mimo.example.com/v1",
      "API Key": "sk-****",
      "Planner 模型": "xiaomi-tokenplan/mimo-v2.5-pro",
      "SimpleCoder 模型": "xiaomi-tokenplan/mimo-v2.5",
      "ComplexCoder 模型": "xiaomi-tokenplan/mimo-v2.5-pro",
      "Tester 模型": "xiaomi-tokenplan/mimo-v2.5"
    },
    "Agent 设置": { ... },
    "Memory 设置": { ... },
    "Workflow 设置": { ... },
    "RAG 设置": { ... },
    "Tool 设置": { ... }
  },
  "message": "查询成功"
}
```

#### 接口 6：更新设置

```
POST /api/settings
```

**请求体**：

```json
{
  "section": "Workflow 设置",
  "key": "最大修正次数",
  "value": 5
}
```

**响应**：

```json
{
  "code": 200,
  "data": {
    "section": "Workflow 设置",
    "key": "最大修正次数",
    "old_value": 3,
    "new_value": 5
  },
  "message": "设置已更新"
}
```

#### 接口 7：获取 Memory

```
GET /api/memory?project=my-project&layer=project
```

**响应**：

```json
{
  "code": 200,
  "data": {
    "layer": "project",
    "content": "# 项目 Memory\n\n## 架构决策\n- 前端使用 React + Ink...",
    "updated_at": "2025-07-05T10:00:00Z"
  },
  "message": "查询成功"
}
```

#### 接口 8：调用工具

```
POST /api/tools/call
```

**请求体**：

```json
{
  "tool": "read_file",
  "args": {
    "path": "src/main.py"
  }
}
```

**响应**：

```json
{
  "code": 200,
  "data": {
    "tool": "read_file",
    "success": true,
    "result": "import fastapi\n\napp = fastapi.FastAPI()\n..."
  },
  "message": "工具执行成功"
}
```

---

## 五、团队 7 人角色分工与协作流

### 5.1 角色分配

| 角色 | 人数 | 负责人 | 核心职责 |
|---|---|---|---|
| 组长 / 项目经理 | 1 人 | 成员 A | 需求拆解、架构图绘制、优先级排序、测试验收、答辩 PPT |
| AI 开发工程师 | 2 人 | 成员 B、成员 C | Agent 编排、Prompt 优化、RAG、Tool 开发 |
| 后端开发工程师 | 2 人 | 成员 D、成员 E | FastAPI 框架、RESTful 接口、数据库、SSE 流式输出 |
| 前端开发工程师 | 2 人 | 成员 F、成员 G | React Ink CLI 界面、SSE 消费、设置面板 |

### 5.2 各角色详细分工

#### 组长 / 项目经理（成员 A）

| 职责 | 具体任务 |
|---|---|
| 需求管理 | 将项目需求拆解为 P0 / P1 优先级，制定 Sprint 计划 |
| 架构设计 | 绘制系统架构图、Agent 工作流设计图 |
| 质量把控 | 每个 Phase 完成后进行验收测试 |
| 协调沟通 | 组织每日站会，协调前后端联调 |
| 文档输出 | 主笔本架构说明书，制作答辩 PPT |
| Git 管理 | 分支策略制定，Code Review |

#### AI 开发工程师 A（成员 B）— RAG 与知识库方向

| 职责 | 具体任务 |
|---|---|
| RAG 引擎 | 实现 `rag/indexer.py`、`rag/retriever.py`、`rag/chunker.py` |
| Embedding 集成 | 接入 sentence-transformers，对接 ChromaDB |
| Constraint Agent | 实现 `agents/constraint.py`，完成 Memory 智能检索逻辑 |
| Prompt 优化 | 调试各 Agent 的 Prompt，优化输出质量 |
| 知识库管理 | 整理 knowledge/ 目录下的文档，测试索引效果 |

#### AI 开发工程师 B（成员 C）— Agent 编排方向

| 职责 | 具体任务 |
|---|---|
| Agent 基类 | 实现 `agents/base.py`、`agents/manager.py` |
| 业务 Agent | 实现 Planner / SimpleCoder / ComplexCoder / Tester 四个 Agent |
| Review Agent | 实现 `agents/review.py`，完成约束审查逻辑 |
| Tool 系统 | 实现 `tools/registry.py`，开发 8 个内置工具 |
| Agent 调试 | 单元测试每个 Agent 的输入输出 |

#### 后端开发工程师 A（成员 D）— 框架与通信方向

| 职责 | 具体任务 |
|---|---|
| FastAPI 框架 | 搭建 `main.py`，注册路由，配置 CORS |
| API 路由 | 实现 `api/chat.py`、`api/settings.py`、`api/memory.py`、`api/project.py`、`api/tools.py` |
| SSE 流式输出 | 实现 SSE 事件推送机制，处理 Agent 状态、代码、测试结果的实时推送 |
| 配置管理 | 实现 `config/loader.py`，处理 settings.json 的读写 |

#### 后端开发工程师 B（成员 E）— 数据与业务逻辑方向

| 职责 | 具体任务 |
|---|---|
| 数据库设计 | 设计 SQLite 表结构（sessions / messages / tasks / checkpoints） |
| CRUD 业务 | 实现用户管理、会话管理、历史记录等业务逻辑 |
| Memory 存储 | 实现 `memory/store.py`、`memory/compressor.py` |
| Workflow 管线 | 实现 `workflow/pipeline.py`、`workflow/review_loop.py`、`workflow/checkpoint.py` |
| Prompt Builder | 实现 `memory/builder.py`，组装完整 Prompt |

#### 前端开发工程师 A（成员 F）— 界面设计方向

| 职责 | 具体任务 |
|---|---|
| CLI 框架 | 搭建 React Ink 项目结构，配置 TypeScript |
| 聊天界面 | 实现 `Chat.tsx`：消息列表、输入框、打字机效果 |
| 设置面板 | 实现 `Settings.tsx`：全中文 6 大类 39 项设置 |
| 样式设计 | 终端色彩方案、布局排版、状态图标 |

#### 前端开发工程师 B（成员 G）— 数据对接方向

| 职责 | 具体任务 |
|---|---|
| API 对接 | 实现 `services/api.ts`：Axios 封装，请求/响应处理 |
| SSE 消费 | 实现 `hooks/useSSE.ts`：SSE 连接管理、事件解析、状态更新 |
| Agent 状态 | 实现 `AgentStatus.tsx`：实时显示当前运行的 Agent |
| Memory 浏览 | 实现 `MemoryView.tsx`：各层 Memory 内容展示 |
| 审批交互 | 实现 `ApprovalDialog.tsx`：审批确认弹窗 |

### 5.3 协作流程

```
                    ┌─────────────────┐
                    │   组长 (成员A)    │
                    │  需求拆解 / 架构  │
                    │  验收 / 答辩PPT   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ AI 组 (2人)   │ │ 后端组 (2人)  │ │ 前端组 (2人)  │
    │              │ │              │ │              │
    │ B: RAG/约束   │ │ D: 框架/SSE  │ │ F: 界面设计  │
    │ C: Agent/Tool│ │ E: DB/Workflow│ │ G: API对接   │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                     ┌──────┴──────┐
                     │  联调与集成   │
                     │ (每 Phase)   │
                     └─────────────┘
```

**协作节奏**：

| 频率 | 活动 | 参与者 |
|---|---|---|
| 每日 | 站会（15 分钟） | 全员 |
| 每 Phase 结束 | 验收测试 | 组长 + 各组代表 |
| 每周 | 代码 Review | 组长 + AI 组 |
| 联调阶段 | 前后端联调 | 后端组 + 前端组 |
| 项目收尾 | 集成测试 + 文档整理 | 全员 |

---

# 文档二：系统整体架构图

> 以下为 BandCode 系统整体架构的文本描述，可直接使用绘图工具（draw.io / ProcessOn / Figma）绘制。

## 2.1 系统整体架构图

```
╔══════════════════════════════════════════════════════════════════════════╗
║                        BandCode 系统整体架构                             ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  ┌──────────────────────────────────────────────────────────────────┐  ║
║  │                    前端交互层 (Frontend)                          │  ║
║  │                  React 18 + Ink 4 + TypeScript                    │  ║
║  │                                                                  │  ║
║  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌─────────────────┐  │  ║
║  │  │  Chat.tsx  │ │Settings   │ │AgentStatus│ │  MemoryView.tsx │  │  ║
║  │  │ 聊天界面   │ │.tsx       │ │.tsx       │ │  Memory 浏览    │  │  ║
║  │  │ 输入/输出  │ │ 设置面板   │ │ Agent状态  │ │  各层Memory查看 │  │  ║
║  │  │ 流式展示   │ │ 全中文    │ │ 实时显示   │ │  手动编辑      │  │  ║
║  │  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └───────┬─────────┘  │  ║
║  │        │             │             │               │             │  ║
║  │        └──────┬──────┴──────┬──────┴───────┬───────┘             │  ║
║  │               │             │              │                     │  ║
║  │  ┌────────────┴───┐ ┌──────┴──────┐ ┌────┴──────────────┐      │  ║
║  │  │ useSSE.ts      │ │ api.ts      │ │ApprovalDialog.tsx │      │  ║
║  │  │ SSE 流式Hook   │ │ Axios封装   │ │  审批确认弹窗      │      │  ║
║  │  └────────┬───────┘ └──────┬──────┘ └────┬──────────────┘      │  ║
║  └───────────┼────────────────┼──────────────┼──────────────────────┘  ║
║              │  SSE (Server-Sent Events)     │  HTTP (Axios)          ║
║              └────────────────┼──────────────┘                         ║
║                               │                                        ║
║  ┌────────────────────────────┼────────────────────────────────────┐   ║
║  │                    后端业务层 (Backend)                          │   ║
║  │                  Python 3.11 + FastAPI                          │   ║
║  │                            │                                    │   ║
║  │  ┌─────────────────────────┼──────────────────────────────────┐ │   ║
║  │  │              API 路由层 (api/)                              │ │   ║
║  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │ │   ║
║  │  │  │chat.py   │ │settings  │ │memory.py │ │project.py    │  │ │   ║
║  │  │  │/chat/    │ │.py       │ │/memory   │ │/project/     │  │ │   ║
║  │  │  │stream    │ │/settings │ │          │ │init          │  │ │   ║
║  │  │  │/history  │ │GET/POST  │ │GET       │ │POST          │  │ │   ║
║  │  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘  │ │   ║
║  │  └───────┼────────────┼────────────┼──────────────┼───────────┘ │   ║
║  │          │            │            │              │             │   ║
║  │  ┌───────┴────────────┴────────────┴──────────────┴───────────┐ │   ║
║  │  │              业务逻辑层                                      │ │   ║
║  │  │                                                             │ │   ║
║  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │ │   ║
║  │  │  │ Agent 管理    │  │ Workflow 引擎 │  │ 设置管理         │  │ │   ║
║  │  │  │ manager.py    │  │ pipeline.py   │  │ config/loader.py│  │ │   ║
║  │  │  │ 自动发现/注册  │  │ 主管线编排    │  │ JSON读写        │  │ │   ║
║  │  │  └──────┬───────┘  └──────┬───────┘  └──────────────────┘  │ │   ║
║  │  │         │                 │                                 │ │   ║
║  │  └─────────┼─────────────────┼─────────────────────────────────┘ │   ║
║  └────────────┼─────────────────┼───────────────────────────────────┘   ║
║               │                 │                                       ║
║  ┌────────────┼─────────────────┼───────────────────────────────────┐   ║
║  │            │     大模型推理层 (AI Agent)                           │   ║
║  │            │                                                      │   ║
║  │  ┌─────────┴───────────────────────────────────────────────────┐  │   ║
║  │  │                    6 Agent 协作引擎                          │  │   ║
║  │  │                                                             │  │   ║
║  │  │   系统级 Agent（用户不可见）                                  │  │   ║
║  │  │   ┌─────────────────┐      ┌──────────────────┐            │  │   ║
║  │  │   │ Constraint Agent │      │  Review Agent    │            │  │   ║
║  │  │   │ 约束检索智能体    │      │  约束审查智能体    │            │  │   ║
║  │  │   │ Memory → 约束筛选 │      │  输出 → 合规检查  │            │  │   ║
║  │  │   └─────────────────┘      └──────────────────┘            │  │   ║
║  │  │                                                             │  │   ║
║  │  │   业务级 Agent（用户可见）                                    │  │   ║
║  │  │   ┌──────────┐ ┌──────────────┐ ┌──────────────┐           │  │   ║
║  │  │   │ Planner   │ │ SimpleCoder  │ │ComplexCoder  │           │  │   ║
║  │  │   │ 规划调度   │ │ 简单编码     │ │ 复杂编码     │           │  │   ║
║  │  │   └──────────┘ └──────────────┘ └──────────────┘           │  │   ║
║  │  │   ┌──────────┐                                             │  │   ║
║  │  │   │ Tester   │                                             │  │   ║
║  │  │   │ 测试验证  │                                             │  │   ║
║  │  │   └──────────┘                                             │  │   ║
║  │  └─────────────────────────────────────────────────────────────┘  │   ║
║  │                                                                   │   ║
║  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐  │   ║
║  │  │ Prompt Builder│  │ RAG 引擎      │  │ Tool Registry         │  │   ║
║  │  │ 上下文组装    │  │ 索引/检索     │  │ 自动发现/注册/执行     │  │   ║
║  │  └──────────────┘  └──────────────┘  └────────────────────────┘  │   ║
║  │                                                                   │   ║
║  │  ┌──────────────┐  ┌──────────────────────────────────────────┐  │   ║
║  │  │ LLM 封装     │  │ OpenAI Compatible API (MiMo)             │  │   ║
║  │  │ llm.py       │  │ base_url + api_key + model → 统一调用     │  │   ║
║  │  └──────────────┘  └──────────────────────────────────────────┘  │   ║
║  └───────────────────────────────────────────────────────────────────┘   ║
║                               │                                         ║
║  ┌────────────────────────────┼─────────────────────────────────────┐   ║
║  │                    数据持久层 (Storage)                            │   ║
║  │                                                                   │   ║
║  │  ┌───────────────┐  ┌───────────────┐  ┌──────────────────────┐  │   ║
║  │  │ ChromaDB       │  │ SQLite         │  │ JSON + Markdown 文件│  │   ║
║  │  │ 向量数据库      │  │ 关系型数据库    │  │ 配置/Memory/Agent   │  │   ║
║  │  │ RAG文档索引     │  │ 会话/消息/任务  │  │ Tool定义            │  │   ║
║  │  └───────────────┘  └───────────────┘  └──────────────────────┘  │   ║
║  └───────────────────────────────────────────────────────────────────┘   ║
║                                                                        ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

# 文档三：Agent 工作流设计图

> 以下为 BandCode 六 Agent 协作工作流的详细设计，可使用绘图工具绘制。

## 3.1 Agent 工作流全景图

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    BandCode Agent 工作流设计图                           ║
║                    (大模型感知 → 规划 → 行动逻辑)                         ║
╚══════════════════════════════════════════════════════════════════════════╝

                           ┌──────────────┐
                           │   用户输入    │
                           │  (自然语言)   │
                           └──────┬───────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ① 感知阶段 (Perception)                             │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Constraint Agent                              │   │
│   │                  (约束检索智能体 · 系统级)                        │   │
│   │                                                                 │   │
│   │   输入: 用户输入 + 当前项目                                       │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  Step 1: 解析用户意图                                      │ │   │
│   │   │          LLM 分类 → 意图标签                               │ │   │
│   │   │                                                           │ │   │
│   │   │  Step 2: 检索各层 Memory                                   │ │   │
│   │   │          ┌──────────────┐                                 │ │   │
│   │   │          │ Global Memory │──→ 通用编码规范                 │ │   │
│   │   │          └──────────────┘                                 │ │   │
│   │   │          ┌──────────────┐                                 │ │   │
│   │   │          │Project Memory │──→ 架构决策、模块说明           │ │   │
│   │   │          └──────────────┘                                 │ │   │
│   │   │          ┌──────────────┐                                 │ │   │
│   │   │          │ Task Memory   │──→ 当前任务上下文               │ │   │
│   │   │          └──────────────┘                                 │ │   │
│   │   │                                                           │ │   │
│   │   │  Step 3: 去重 + 排序 + 截断 (top_k=10)                    │ │   │
│   │   │                                                           │ │   │
│   │   │  Step 4: 生成约束摘要                                      │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   │                                                                 │   │
│   │   输出: constraints[] + constraint_summary                      │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
│                                        │                                │
│   ┌────────────────────────────────────┴────────────────────────────┐   │
│   │                    RAG 检索                                      │   │
│   │                                                                 │   │
│   │   输入: 用户输入                                                 │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  用户输入 → Embedding 向量化                                │ │   │
│   │   │       ↓                                                    │ │   │
│   │   │  ChromaDB 相似度检索 (top_k=5)                              │ │   │
│   │   │       ↓                                                    │ │   │
│   │   │  返回: 相关文档片段 + 来源元数据                             │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   │                                                                 │   │
│   │   输出: rag_context (格式化文档片段)                              │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
│                                        │                                │
│   ┌────────────────────────────────────┴────────────────────────────┐   │
│   │                    Prompt Builder                                │   │
│   │                                                                 │   │
│   │   组装完整 Prompt:                                               │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  [系统指令] + [项目约束] + [知识库参考] +                  │ │   │
│   │   │  [global Memory] + [project Memory] + [task Memory] +     │ │   │
│   │   │  [checkpoint Memory] + [Agent 指令] + [用户输入]           │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   │                                                                 │   │
│   │   输出: 完整 Prompt (messages[])                                 │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
└────────────────────────────────────────┼────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ② 规划阶段 (Planning)                               │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                       Planner Agent                              │   │
│   │                   (规划调度智能体 · 业务级)                       │   │
│   │                                                                 │   │
│   │   输入: 完整 Prompt (含约束 + RAG + Memory)                      │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  Step 1: 需求分析                                          │ │   │
│   │   │          - 理解用户目标                                     │ │   │
│   │   │          - 识别技术要点                                     │ │   │
│   │   │                                                           │ │   │
│   │   │  Step 2: 任务拆解                                          │ │   │
│   │   │          - 拆分为可执行的子任务                              │ │   │
│   │   │          - 确定执行顺序                                     │ │   │
│   │   │                                                           │ │   │
│   │   │  Step 3: 风险评估                                          │ │   │
│   │   │          - 影响范围分析                                     │ │   │
│   │   │          - 识别潜在冲突                                     │ │   │
│   │   │                                                           │ │   │
│   │   │  Step 4: Agent 选择                                        │ │   │
│   │   │          ┌─────────────────────────────────────────────┐  │ │   │
│   │   │          │  任务类型        → 委派 Agent                │  │ │   │
│   │   │          │  ─────────────────────────────────────────  │  │ │   │
│   │   │          │  UI/配置/单文件  → SimpleCoder              │  │ │   │
│   │   │          │  API/重构/架构   → ComplexCoder             │  │ │   │
│   │   │          │  测试/验证       → Tester                   │  │ │   │
│   │   │          └─────────────────────────────────────────────┘  │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   │                                                                 │   │
│   │   输出: plan + delegated_agent + reason                         │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
│                                        │                                │
│   ┌────────────────────────────────────┴────────────────────────────┐   │
│   │                    审批检查 (Approval)                           │   │
│   │                                                                 │   │
│   │   条件: settings["审批模式"] == true                              │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  需要审批的操作:                                            │ │   │
│   │   │  - 切换子 Agent                                            │ │   │
│   │   │  - 开始代码修改                                            │ │   │
│   │   │  - 执行 bash/git 操作                                      │ │   │
│   │   │  - 进入测试流程                                            │ │   │
│   │   │                                                           │ │   │
│   │   │  ┌─────────┐    ┌─────────┐                               │ │   │
│   │   │  │ 用户确认 │    │ 用户拒绝 │                               │ │   │
│   │   │  │   Y     │    │   N     │                               │ │   │
│   │   │  │ → 继续  │    │ → 取消  │                               │ │   │
│   │   │  └─────────┘    └─────────┘                               │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
└────────────────────────────────────────┼────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ③ 行动阶段 (Action)                                 │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    子 Agent 执行                                 │   │
│   │                                                                 │   │
│   │   ┌──────────────────┐  ┌──────────────────┐                    │   │
│   │   │  SimpleCoder     │  │  ComplexCoder    │                    │   │
│   │   │                  │  │                  │                    │   │
│   │   │  适用:           │  │  适用:           │                    │   │
│   │   │  - UI 修改       │  │  - API 开发      │                    │   │
│   │   │  - 配置调整      │  │  - 架构调整      │                    │   │
│   │   │  - 单文件修改    │  │  - 跨模块重构    │                    │   │
│   │   │  - 小型 Bug      │  │  - 核心业务逻辑  │                    │   │
│   │   │                  │  │                  │                    │   │
│   │   │  模型: mimo-v2.5 │  │  模型: mimo-pro  │                    │   │
│   │   │  温度: 0.2       │  │  温度: 0.1       │                    │   │
│   │   └────────┬─────────┘  └────────┬─────────┘                    │   │
│   │            │                     │                              │   │
│   │            └──────────┬──────────┘                              │   │
│   │                       │                                         │   │
│   │                       ▼                                         │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  Tool Calling (工具调用)                                   │ │   │
│   │   │                                                           │ │   │
│   │   │  Agent 调用 → ToolRegistry 权限检查 → 工具执行             │ │   │
│   │   │                                                           │ │   │
│   │   │  可用工具:                                                  │ │   │
│   │   │  ┌────────────┐ ┌────────────┐ ┌──────────────┐          │ │   │
│   │   │  │ read_file  │ │write_file  │ │list_directory│          │ │   │
│   │   │  └────────────┘ └────────────┘ └──────────────┘          │ │   │
│   │   │  ┌────────────┐ ┌────────────┐ ┌──────────────┐          │ │   │
│   │   │  │search_     │ │search_     │ │ create_task  │          │ │   │
│   │   │  │project     │ │knowledge   │ │              │          │ │   │
│   │   │  └────────────┘ └────────────┘ └──────────────┘          │ │   │
│   │   │  ┌────────────┐ ┌────────────┐                           │ │   │
│   │   │  │update_     │ │finish_task │                           │ │   │
│   │   │  │memory      │ │            │                           │ │   │
│   │   │  └────────────┘ └────────────┘                           │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   │                                                                 │   │
│   │   输出: agent_output (files_changed, code, summary)             │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
│                                        │                                │
│                                        ▼                                │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Tester Agent                                  │   │
│   │                  (测试验证智能体 · 业务级)                        │   │
│   │                                                                 │   │
│   │   硬约束: edit 权限 = deny (禁止修改代码)                        │   │
│   │   模型: mimo-v2.5, 温度: 0                                      │   │
│   │                                                                 │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  Step 1: 编译检查 (如有编译步骤)                            │ │   │
│   │   │  Step 2: 单元测试执行                                      │ │   │
│   │   │  Step 3: 静态分析                                          │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   │                                                                 │   │
│   │   输出: test_result {status, tests, errors}                     │   │
│   │                                                                 │   │
│   │   ┌────────────────────────────────────────────┐                │   │
│   │   │  status == "passed"  → 继续到 Review       │                │   │
│   │   │  status == "failed"  → 停止，报告错误      │                │   │
│   │   └────────────────────────────────────────────┘                │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
└────────────────────────────────────────┼────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     ④ 审查阶段 (Review)                                 │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    Review Agent                                  │   │
│   │                 (约束审查智能体 · 系统级)                         │   │
│   │                                                                 │   │
│   │   条件: settings["开启自动约束检查"] == true                       │   │
│   │   模型: mimo-v2.5-pro, 温度: 0                                  │   │
│   │                                                                 │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │  检查维度:                                                  │ │   │
│   │   │                                                           │ │   │
│   │   │  1. Memory 约束合规                                        │ │   │
│   │   │     输出是否违反 Global/Project Memory 中的规范？           │ │   │
│   │   │                                                           │ │   │
│   │   │  2. 编码规范检查                                           │ │   │
│   │   │     命名规范、注释规范、代码风格是否一致？                  │ │   │
│   │   │                                                           │ │   │
│   │   │  3. Prompt 规则检查                                        │ │   │
│   │   │     是否遵循 Agent Prompt 中的硬约束？                      │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   │                                                                 │   │
│   │   输出: review_result {passed, violations[]}                    │   │
│   └────────────────────────────────────┬────────────────────────────┘   │
│                                        │                                │
│                                        ▼                                │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    修正循环 (Review Loop)                        │   │
│   │                                                                 │   │
│   │   ┌─────────────────────────────────────────────────────────┐   │   │
│   │   │                                                         │   │   │
│   │   │     ┌───────────┐     ┌───────────────────────┐        │   │   │
│   │   │     │ Review    │────→│ passed?               │        │   │   │
│   │   │     │ 检查约束   │     │                       │        │   │   │
│   │   │     └───────────┘     │ YES → ⑤ 更新阶段      │        │   │   │
│   │   │           ↑           │                       │        │   │   │
│   │   │           │           │ NO  → 自动修正？       │        │   │   │
│   │   │           │           │       │               │        │   │   │
│   │   │           │           │  ┌────┴────┐          │        │   │   │
│   │   │           │           │  │ 开启    │ 关闭     │        │   │   │
│   │   │           │           │  │         │          │        │   │   │
│   │   │           │           │  │ 重新生成 │ 报告用户 │        │   │   │
│   │   │           │           │  └────┬────┘          │        │   │   │
│   │   │           │           │       │               │        │   │   │
│   │   │           └───────────│───────┘               │        │   │   │
│   │   │                       │                       │        │   │   │
│   │   │                       │ retry_count < max?    │        │   │   │
│   │   │                       │ YES → 重新执行子Agent  │        │   │   │
│   │   │                       │ NO  → ⑥ 失败处理      │        │   │   │
│   │   │                       └───────────────────────┘        │   │   │
│   │   │                                                         │   │   │
│   │   │   最大修正次数: settings["最大修正次数"] (默认 3)        │   │   │
│   │   └─────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────┬────────────────────────────────┘
                                         │
                            ┌────────────┴────────────┐
                            │                         │
                            ▼                         ▼
┌────────────────────────────────┐  ┌─────────────────────────────────────┐
│     ⑤ 成功路径 (Success)       │  │     ⑥ 失败路径 (Failure)            │
│                                │  │                                     │
│  ┌──────────────────────────┐  │  │  ┌───────────────────────────────┐  │
│  │ 更新 Memory               │  │  │  │ 修正失败自动回滚？             │  │
│  │                          │  │  │  │                               │  │
│  │ - Task Memory            │  │  │  │  YES → 回滚到 Checkpoint      │  │
│  │ - Checkpoint (快照)      │  │  │  │        恢复修改前状态           │  │
│  │ - Project Memory (按需)  │  │  │  │                               │  │
│  │ - Session Memory         │  │  │  │  NO  → 询问用户               │  │
│  └──────────┬───────────────┘  │  │  │        是否恢复修改前？         │  │
│             │                  │  │  │        YES → 回滚              │  │
│             ▼                  │  │  │        NO  → 保持现状           │  │
│  ┌──────────────────────────┐  │  │  └───────────────────────────────┘  │
│  │ Git 提交建议 (可选)       │  │  │                                     │
│  │ 自动生成 Commit Message  │  │  └─────────────────────────────────────┘
│  └──────────┬───────────────┘  │
│             │                  │
│             ▼                  │
│  ┌──────────────────────────┐  │
│  │ SSE 推送完成事件          │  │
│  │ event: done              │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

---

# 文档四：前后端 API 接口定义表

## 4.1 接口总览表

| 序号 | 方法 | 路径 | 说明 | 请求格式 | 响应格式 | 关联前端组件 |
|---|---|---|---|---|---|---|
| 1 | POST | `/api/users/create` | 创建/初始化用户 | JSON | JSON | 初始化流程 |
| 2 | POST | `/api/chat/stream` | 流式聊天 | JSON | SSE | Chat.tsx |
| 3 | GET | `/api/chat/history` | 获取聊天历史 | Query Params | JSON | Chat.tsx |
| 4 | POST | `/api/project/init` | 初始化项目 | JSON | JSON | 初始化流程 |
| 5 | GET | `/api/settings` | 获取全部设置 | — | JSON | Settings.tsx |
| 6 | POST | `/api/settings` | 更新设置 | JSON | JSON | Settings.tsx |
| 7 | GET | `/api/memory` | 获取 Memory | Query Params | JSON | MemoryView.tsx |
| 8 | POST | `/api/tools/call` | 调用工具 | JSON | JSON | 调试面板 |

---

## 4.2 接口 1：创建用户

```
POST /api/users/create
```

**请求头**：

| Header | 值 |
|---|---|
| Content-Type | application/json |

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| username | string | 是 | 用户名 |
| preferences | object | 否 | 用户偏好设置 |
| preferences.language | string | 否 | 语言偏好，默认 "zh-CN" |
| preferences.theme | string | 否 | 主题偏好，默认 "dark" |

**请求示例**：

```json
{
  "username": "developer_01",
  "preferences": {
    "language": "zh-CN",
    "theme": "dark"
  }
}
```

**响应体**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| data.user_id | string | 用户 ID |
| data.username | string | 用户名 |
| data.created_at | string | 创建时间 (ISO 8601) |
| message | string | 提示信息 |

**响应示例**：

```json
{
  "code": 200,
  "data": {
    "user_id": "u_abc123",
    "username": "developer_01",
    "created_at": "2025-07-05T10:00:00Z"
  },
  "message": "用户创建成功"
}
```

**错误码**：

| code | 说明 |
|---|---|
| 200 | 成功 |
| 400 | 参数错误 |
| 409 | 用户名已存在 |

---

## 4.3 接口 2：流式聊天

```
POST /api/chat/stream
```

**请求头**：

| Header | 值 |
|---|---|
| Content-Type | application/json |
| Accept | text/event-stream |

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| session_id | string | 是 | 会话 ID |
| project | string | 是 | 项目名称 |
| message | string | 是 | 用户消息 |
| options | object | 否 | 选项 |
| options.agent | string | 否 | 指定 Agent，默认 "auto" |
| options.workflow | string | 否 | 指定工作流，默认 "auto" |

**请求示例**：

```json
{
  "session_id": "session-abc123",
  "project": "my-project",
  "message": "帮我实现用户登录功能",
  "options": {
    "agent": "auto",
    "workflow": "auto"
  }
}
```

**SSE 事件定义**：

| 事件名 | data 字段 | 说明 |
|---|---|---|
| `agent_start` | `{agent: string, status: string}` | Agent 开始执行 |
| `constraint_result` | `{constraints: string[], summary: string}` | 约束检索结果 |
| `plan` | `{tasks: string[], delegated_agent: string}` | Planner 任务计划 |
| `approval_required` | `{plan: string, agent: string, reason: string}` | 请求用户审批 |
| `approval_response` | `{approved: boolean}` | 审批结果 |
| `tool_call` | `{tool: string, args: object}` | 工具调用 |
| `code` | `{file: string, content: string}` | 代码生成 |
| `test_result` | `{status: string, tests: number, errors: object[]}` | 测试结果 |
| `review_result` | `{status: string, violations: object[]}` | 审查结果 |
| `memory_update` | `{layers: string[], message: string}` | Memory 更新 |
| `error` | `{code: string, message: string}` | 错误 |
| `done` | `{session_id: string, summary: string}` | 流程完成 |

**SSE 事件流示例**：

```
event: agent_start
data: {"agent": "constraint", "status": "检索相关约束..."}

event: constraint_result
data: {"constraints": ["使用JWT认证", "密码bcrypt加密"], "summary": "需遵循认证规范"}

event: agent_start
data: {"agent": "planner", "status": "分析需求..."}

event: plan
data: {"tasks": ["1.创建User模型", "2.实现登录API", "3.编写测试"], "delegated_agent": "complex-coder"}

event: approval_required
data: {"plan": "创建User模型→实现登录API→编写测试", "agent": "complex-coder", "reason": "涉及API开发"}

event: agent_start
data: {"agent": "complex-coder", "status": "编写代码..."}

event: tool_call
data: {"tool": "write_file", "args": {"path": "src/auth.py"}}

event: code
data: {"file": "src/auth.py", "content": "from fastapi import APIRouter\n..."}

event: agent_start
data: {"agent": "tester", "status": "运行测试..."}

event: test_result
data: {"status": "passed", "tests": 5, "errors": []}

event: agent_start
data: {"agent": "review", "status": "检查约束合规..."}

event: review_result
data: {"status": "passed", "violations": []}

event: memory_update
data: {"layers": ["task", "checkpoint"], "message": "已更新 Task Memory 和 Checkpoint"}

event: done
data: {"session_id": "session-abc123", "summary": "用户登录功能已完成，涉及3个文件"}
```

---

## 4.4 接口 3：获取聊天历史

```
GET /api/chat/history
```

**Query 参数**：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| session_id | string | 是 | 会话 ID |
| limit | int | 否 | 返回条数，默认 50 |
| offset | int | 否 | 偏移量，默认 0 |

**请求示例**：

```
GET /api/chat/history?session_id=session-abc123&limit=50&offset=0
```

**响应体**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| data.session_id | string | 会话 ID |
| data.messages | array | 消息列表 |
| data.messages[].id | int | 消息 ID |
| data.messages[].role | string | 角色: user / assistant / system |
| data.messages[].agent | string | 产出 Agent（仅 assistant） |
| data.messages[].content | string | 消息内容 |
| data.messages[].created_at | string | 创建时间 |
| data.total | int | 总条数 |
| data.has_more | boolean | 是否有更多 |
| message | string | 提示信息 |

**响应示例**：

```json
{
  "code": 200,
  "data": {
    "session_id": "session-abc123",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "agent": null,
        "content": "帮我实现用户登录功能",
        "created_at": "2025-07-05T10:00:00Z"
      },
      {
        "id": 2,
        "role": "assistant",
        "agent": "planner",
        "content": "分析需求，拆解为3个任务...",
        "created_at": "2025-07-05T10:00:05Z"
      }
    ],
    "total": 12,
    "has_more": false
  },
  "message": "查询成功"
}
```

---

## 4.5 接口 4：初始化项目

```
POST /api/project/init
```

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| project_name | string | 是 | 项目名称 |
| path | string | 是 | 项目路径 |
| language | string | 否 | 主要语言，如 "python" |
| framework | string | 否 | 使用框架，如 "fastapi" |

**请求示例**：

```json
{
  "project_name": "my-project",
  "path": "/home/user/projects/my-project",
  "language": "python",
  "framework": "fastapi"
}
```

**响应体**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| data.project | string | 项目名称 |
| data.mimo_dir | string | .mimo 目录路径 |
| data.structure | object | 创建的文件/目录列表 |
| message | string | 提示信息 |

**响应示例**：

```json
{
  "code": 200,
  "data": {
    "project": "my-project",
    "mimo_dir": "/home/user/projects/my-project/.mimo",
    "structure": {
      "global/MEMORY.md": "created",
      "project/MEMORY.md": "created",
      "tasks/": "created",
      "sessions/": "created",
      "checkpoints/": "created",
      "notes/": "created",
      "config.json": "created"
    }
  },
  "message": "项目初始化完成"
}
```

---

## 4.6 接口 5：获取设置

```
GET /api/settings
```

**请求参数**：无

**响应体**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| data | object | 全部设置（6 大类） |
| data["模型设置"] | object | 模型相关配置 |
| data["Agent 设置"] | object | Agent 相关配置 |
| data["Memory 设置"] | object | Memory 相关配置 |
| data["Workflow 设置"] | object | Workflow 开关配置 |
| data["RAG 设置"] | object | RAG 相关配置 |
| data["Tool 设置"] | object | Tool 权限配置 |
| message | string | 提示信息 |

**响应示例**：

```json
{
  "code": 200,
  "data": {
    "模型设置": {
      "默认模型": "xiaomi-tokenplan/mimo-v2.5-pro",
      "Base URL": "https://api.mimo.example.com/v1",
      "API Key": "sk-****",
      "Planner 模型": "xiaomi-tokenplan/mimo-v2.5-pro",
      "SimpleCoder 模型": "xiaomi-tokenplan/mimo-v2.5",
      "ComplexCoder 模型": "xiaomi-tokenplan/mimo-v2.5-pro",
      "Tester 模型": "xiaomi-tokenplan/mimo-v2.5"
    },
    "Agent 设置": {
      "自动发现 Agent": true,
      "默认 Planner": "planner",
      "Agent 最大步骤": 20,
      "Agent 超时时间": 300
    },
    "Memory 设置": {
      "自动更新 Global": true,
      "自动更新 Project": true,
      "自动更新 Task": true,
      "自动更新 Checkpoint": true,
      "自动恢复 Session": true,
      "自动压缩 Session": true
    },
    "Workflow 设置": {
      "开启约束智能检索": true,
      "开启自动约束检查": true,
      "自动修正": true,
      "最大修正次数": 3,
      "修正失败自动回滚": true,
      "自动更新文档": true,
      "自动更新 Memory": true,
      "Git 提交建议": true,
      "审批模式": true
    },
    "RAG 设置": {
      "知识库目录": "./knowledge",
      "自动索引": true,
      "TopK": 5,
      "Chunk 大小": 512,
      "重叠长度": 64,
      "Embedding 模型": "all-MiniLM-L6-v2"
    },
    "Tool 设置": {
      "文件读取": true,
      "文件写入": true,
      "Bash": true,
      "搜索项目": true,
      "搜索知识库": true,
      "更新 Memory": true,
      "创建 Task": true
    }
  },
  "message": "查询成功"
}
```

---

## 4.7 接口 6：更新设置

```
POST /api/settings
```

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| section | string | 是 | 设置类别名 |
| key | string | 是 | 设置项名 |
| value | any | 是 | 新值 |

**请求示例**：

```json
{
  "section": "Workflow 设置",
  "key": "最大修正次数",
  "value": 5
}
```

**响应体**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| data.section | string | 设置类别 |
| data.key | string | 设置项 |
| data.old_value | any | 旧值 |
| data.new_value | any | 新值 |
| message | string | 提示信息 |

**响应示例**：

```json
{
  "code": 200,
  "data": {
    "section": "Workflow 设置",
    "key": "最大修正次数",
    "old_value": 3,
    "new_value": 5
  },
  "message": "设置已更新"
}
```

**错误码**：

| code | 说明 |
|---|---|
| 200 | 成功 |
| 400 | 参数错误（section/key 不存在） |
| 422 | 值类型不匹配 |

---

## 4.8 接口 7：获取 Memory

```
GET /api/memory
```

**Query 参数**：

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| project | string | 是 | 项目名称 |
| layer | string | 是 | Memory 层级: global / project / task / session / checkpoint / notes |
| session_id | string | 否 | 会话 ID（layer=session 时必填） |
| task_id | string | 否 | 任务 ID（layer=task 时可选） |

**请求示例**：

```
GET /api/memory?project=my-project&layer=project
```

**响应体**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| data.layer | string | Memory 层级 |
| data.content | string | Memory 内容（Markdown） |
| data.updated_at | string | 最后更新时间 |
| message | string | 提示信息 |

**响应示例**：

```json
{
  "code": 200,
  "data": {
    "layer": "project",
    "content": "# 项目 Memory\n\n## 架构决策\n- 前端使用 React + Ink CLI 框架\n- 后端使用 Python + FastAPI\n\n## 编码规范\n- 所有注释使用简体中文\n- 函数命名使用 snake_case",
    "updated_at": "2025-07-05T10:00:00Z"
  },
  "message": "查询成功"
}
```

---

## 4.9 接口 8：调用工具

```
POST /api/tools/call
```

**请求体**：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| tool | string | 是 | 工具名称 |
| args | object | 是 | 工具参数 |

**请求示例**：

```json
{
  "tool": "read_file",
  "args": {
    "path": "src/main.py"
  }
}
```

**响应体**：

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 状态码 |
| data.tool | string | 工具名称 |
| data.success | boolean | 是否成功 |
| data.result | any | 工具执行结果 |
| data.error | string | 错误信息（失败时） |
| message | string | 提示信息 |

**响应示例（成功）**：

```json
{
  "code": 200,
  "data": {
    "tool": "read_file",
    "success": true,
    "result": "import fastapi\n\napp = fastapi.FastAPI()\n..."
  },
  "message": "工具执行成功"
}
```

**响应示例（失败）**：

```json
{
  "code": 200,
  "data": {
    "tool": "read_file",
    "success": false,
    "result": null,
    "error": "文件不存在: src/not_exist.py"
  },
  "message": "工具执行失败"
}
```

**可用工具参数速查**：

| 工具 | 参数 | 说明 |
|---|---|---|
| `read_file` | `{path: string}` | 读取文件 |
| `write_file` | `{path: string, content: string}` | 写入文件 |
| `list_directory` | `{path: string, depth?: int}` | 列出目录 |
| `search_project` | `{query: string, file_pattern?: string}` | 搜索项目 |
| `search_knowledge` | `{query: string, top_k?: int}` | 搜索知识库 |
| `create_task` | `{title: string, description: string}` | 创建任务 |
| `update_memory` | `{layer: string, content: string}` | 更新 Memory |
| `finish_task` | `{task_id: string, summary: string}` | 完成任务 |

---


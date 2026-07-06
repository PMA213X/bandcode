# BandCode 开发规划

> 版本：v1.0 | 日期：2026-07-06 | 适用范围：7人团队全员

---

## 一、项目结构总览

```
bandcode/
├── frontend/                    # 前端交互层
│   ├── src/
│   │   ├── components/          # UI 组件
│   │   │   ├── Chat.tsx         # 聊天界面
│   │   │   ├── Settings.tsx     # 设置面板
│   │   │   ├── AgentStatus.tsx  # Agent 状态
│   │   │   ├── MemoryView.tsx   # Memory 浏览
│   │   │   └── ApprovalDialog.tsx # 审批弹窗
│   │   ├── hooks/
│   │   │   └── useSSE.ts        # SSE 流式 Hook
│   │   ├── services/
│   │   │   └── api.ts           # Axios 封装
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                     # 后端业务层
│   ├── api/                     # API 路由层
│   │   ├── chat.py              # 聊天接口
│   │   ├── settings.py          # 设置接口
│   │   ├── memory.py            # Memory 接口
│   │   ├── project.py           # 项目接口
│   │   └── tools.py             # 工具接口
│   ├── agents/                  # Agent 模块
│   │   ├── base.py              # Agent 基类
│   │   ├── manager.py           # Agent 管理器
│   │   ├── planner.py           # Planner Agent
│   │   ├── simple_coder.py      # SimpleCoder Agent
│   │   ├── complex_coder.py     # ComplexCoder Agent
│   │   ├── tester.py            # Tester Agent
│   │   ├── constraint.py        # Constraint Agent
│   │   └── review.py            # Review Agent
│   ├── memory/                  # Memory 模块
│   │   ├── store.py             # Memory 存储
│   │   ├── compressor.py        # Memory 压缩
│   │   └── builder.py           # Prompt Builder
│   ├── rag/                     # RAG 模块
│   │   ├── indexer.py           # 文档索引
│   │   ├── retriever.py         # 向量检索
│   │   └── chunker.py           # 文档切分
│   ├── workflow/                # 工作流模块
│   │   ├── pipeline.py          # 主管线
│   │   ├── review_loop.py       # Review 循环
│   │   └── checkpoint.py        # 快照管理
│   ├── tools/                   # 工具模块
│   │   ├── registry.py          # 工具注册中心
│   │   └── builtins/            # 内置工具
│   ├── models/                  # 模型封装
│   │   ├── llm.py               # LLM 调用
│   │   └── embedding.py         # Embedding
│   ├── config/                  # 配置
│   │   └── loader.py            # 配置加载
│   ├── database/                # 数据库
│   │   ├── models.py            # 表结构
│   │   └── crud.py              # CRUD 操作
│   ├── main.py                  # FastAPI 入口
│   └── requirements.txt
│
├── agents/                      # Agent 定义（Markdown）
│   ├── planner.md
│   ├── simple-coder.md
│   ├── complex-coder.md
│   ├── tester.md
│   ├── constraint.md
│   └── review.md
│
├── tools/                       # Tool 定义（JSON）
│   ├── read_file.json
│   ├── write_file.json
│   ├── list_directory.json
│   ├── search_project.json
│   ├── search_knowledge.json
│   ├── create_task.json
│   ├── update_memory.json
│   └── finish_task.json
│
├── knowledge/                   # RAG 知识库
│   └── docs/
│
├── .mimo/                       # Memory 存储
│   ├── global/MEMORY.md
│   ├── project/MEMORY.md
│   ├── tasks/
│   ├── sessions/
│   ├── checkpoints/
│   ├── notes/
│   └── config.json
│
├── settings.json                # 全局设置
└── docs/                        # 项目文档
```

---

## 二、总体开发规划

### 2.1 阶段划分

| 阶段 | 名称 | 时间 | 目标 | 交付物 |
|------|------|------|------|--------|
| Phase 0 | 项目初始化 | 第1天 | 环境搭建、分支策略、基础框架 | 项目骨架、开发环境 |
| Phase 1 | 核心基础 | 第2-4天 | 后端框架、数据库、LLM封装、Agent基类 | 可运行的后端服务 |
| Phase 2 | Agent 开发 | 第5-8天 | 6个Agent、Tool系统、Memory系统 | Agent可独立调用 |
| Phase 3 | 工作流集成 | 第9-11天 | Pipeline、RAG、Review循环 | 完整工作流可运行 |
| Phase 4 | 前端开发 | 第5-11天 | CLI界面、SSE消费、所有组件 | 可交互的前端界面 |
| Phase 5 | 联调测试 | 第12-14天 | 前后端联调、端到端测试 | 可演示的完整系统 |
| Phase 6 | 收尾优化 | 第15-16天 | 性能优化、文档整理、答辩准备 | 最终交付版本 |

### 2.2 并行开发策略

```
Phase 0 (第1天)
  └─ 全员：环境搭建 + Git 规范 + 分支创建

Phase 1 (第2-4天) ─────────────────────────────────────────
  ├─ 后端D：FastAPI框架 + API路由 + SSE机制
  ├─ 后端E：SQLite表结构 + CRUD + 配置加载
  ├─ AI-B：LLM封装 + Embedding集成 + ChromaDB
  ├─ AI-C：Agent基类 + Agent管理器 + Agent定义文件
  ├─ 前端F：React Ink项目搭建 + 基础组件骨架
  └─ 前端G：Axios封装 + SSE Hook基础实现

Phase 2 (第5-8天) ─────────────────────────────────────────
  ├─ 后端D：完善API路由 + SSE事件推送
  ├─ 后端E：Memory存储 + Prompt Builder
  ├─ AI-B：Constraint Agent + RAG引擎 + 知识库
  ├─ AI-C：Planner/SimpleCoder/ComplexCoder/Tester + Tool系统
  ├─ 前端F：Chat.tsx + Settings.tsx 完整实现
  └─ 前端G：AgentStatus + MemoryView + ApprovalDialog

Phase 3 (第9-11天) ────────────────────────────────────────
  ├─ 后端D：API完善 + 错误处理
  ├─ 后端E：Pipeline + Review循环 + Checkpoint
  ├─ AI-B：Review Agent + Constraint优化
  ├─ AI-C：Agent调试 + Tool调试
  ├─ 前端F：UI优化 + 样式调整
  └─ 前端G：SSE完整对接 + 状态管理

Phase 4 (第12-14天) ───────────────────────────────────────
  └─ 全员：前后端联调 + 端到端测试 + Bug修复

Phase 5 (第15-16天) ───────────────────────────────────────
  └─ 全员：性能优化 + 文档完善 + 答辩准备
```

### 2.3 分支策略

| 分支 | 负责人 | 内容 |
|------|--------|------|
| main | 成员A | 生产就绪代码 |
| develop | 成员A | 开发集成分支 |
| feature/backend-api | 成员D | 后端框架与API |
| feature/backend-data | 成员E | 数据库与业务逻辑 |
| feature/ai-rag | 成员B | RAG与Constraint Agent |
| feature/ai-agent | 成员C | Agent与Tool系统 |
| feature/frontend-ui | 成员F | 前端界面组件 |
| feature/frontend-data | 成员G | 前端数据对接 |

---

## 三、成员A — 组长/项目经理

### 3.1 角色定位

- 需求管理、架构设计、质量把控、协调沟通
- 不直接参与核心代码开发，负责验收和集成

### 3.2 开发内容

| 任务 | 说明 | 优先级 |
|------|------|--------|
| 项目初始化 | 创建仓库、配置分支策略、搭建项目骨架 | P0 |
| 配置文件 | 创建 settings.json、.mimo/ 目录结构 | P0 |
| Agent定义文件 | 编写 agents/*.md（6个Agent的Prompt定义） | P0 |
| Tool定义文件 | 编写 tools/*.json（8个工具的参数定义） | P0 |
| 知识库整理 | 整理 knowledge/ 目录下的文档 | P1 |
| 验收测试 | 每个Phase完成后进行验收 | P0 |
| 文档维护 | 更新 docs/ 下的文档 | P0 |
| 答辩PPT | 制作项目答辩材料 | P1 |

### 3.3 AI Agent 使用建议

**主要使用：`general` + `mimo-v2.5-pro`**

使用场景：

| 场景 | Agent | 模型 | 说明 |
|------|-------|------|------|
| 编写Agent定义文件 | general | mimo-v2.5-pro | 需要高质量的Prompt设计 |
| 编写Tool定义文件 | general | mimo-v2.5 | JSON格式，相对简单 |
| 验收测试 | general | mimo-v2.5 | 运行测试、检查输出 |
| 文档编写 | general | mimo-v2.5 | 文档整理 |
| 架构分析 | explore | mimo-v2.5 | 查看代码结构 |

### 3.4 文件所有权

```
agents/planner.md           ← 编写
agents/simple-coder.md      ← 编写
agents/complex-coder.md     ← 编写
agents/tester.md            ← 编写
agents/constraint.md        ← 编写（与成员B协作）
agents/review.md            ← 编写（与成员C协作）
tools/*.json                ← 编写
settings.json               ← 编写
.mimo/config.json           ← 编写
knowledge/                  ← 维护
docs/                       ← 维护
```

---

## 四、成员B — AI开发工程师A（RAG与知识库方向）

### 4.1 角色定位

- RAG 引擎开发、Embedding 集成、Constraint Agent 实现
- 负责知识库的索引、检索、上下文注入

### 4.2 开发内容

| 任务 | 文件 | 说明 | 优先级 |
|------|------|------|--------|
| LLM封装 | `models/llm.py` | OpenAI SDK统一流式/非流式调用 | P0 |
| Embedding封装 | `models/embedding.py` | sentence-transformers文本向量化 | P0 |
| RAG文档切分 | `rag/chunker.py` | 文档按段落/句子切分 | P0 |
| RAG索引器 | `rag/indexer.py` | 文档切分→向量化→存入ChromaDB | P0 |
| RAG检索器 | `rag/retriever.py` | ChromaDB相似度检索 | P0 |
| Constraint Agent | `agents/constraint.py` | Memory智能检索、约束筛选 | P0 |
| Review Agent | `agents/review.py` | 约束审查逻辑（与成员C协作） | P1 |
| 知识库测试 | `tests/test_rag.py` | RAG索引和检索的单元测试 | P1 |

### 4.3 AI Agent 使用建议

**主要使用：`general` + `mimo-v2.5-pro`**

使用场景：

| 场景 | Agent | 模型 | 说明 |
|------|-------|------|------|
| 实现LLM封装 | general | mimo-v2.5-pro | 涉及异步流式处理，复杂度高 |
| 实现RAG引擎 | general | mimo-v2.5-pro | 向量检索逻辑，需要精确实现 |
| 实现Constraint Agent | general | mimo-v2.5-pro | Agent逻辑复杂，需要Pro模型 |
| 单元测试 | general | mimo-v2.5 | 测试代码相对简单 |
| 代码探索 | explore | mimo-v2.5 | 查找相关模块代码 |

### 4.4 文件所有权

```
models/llm.py               ← 主责
models/embedding.py          ← 主责
rag/chunker.py               ← 主责
rag/indexer.py               ← 主责
rag/retriever.py             ← 主责
agents/constraint.py         ← 主责
agents/review.py             ← 协助成员C
tests/test_rag.py            ← 主责
tests/test_constraint.py     ← 主责
```

### 4.5 接口依赖

| 依赖方 | 依赖内容 | 说明 |
|--------|---------|------|
| 成员A | agents/constraint.md | Constraint Agent的Prompt定义 |
| 成员C | agents/base.py | Agent基类，Constraint需继承 |
| 成员E | memory/store.py | Memory存储，Constraint需调用 |
| 成员D | config/loader.py | 配置加载，获取模型设置 |

---

## 五、成员C — AI开发工程师B（Agent编排方向）

### 5.1 角色定位

- Agent 基类与管理器、业务Agent实现、Tool系统开发
- 负责Agent的调度、注册、权限管理

### 5.2 开发内容

| 任务 | 文件 | 说明 | 优先级 |
|------|------|------|--------|
| Agent基类 | `agents/base.py` | 统一Agent接口、LLM调用、Tool调用、状态上报 | P0 |
| Agent管理器 | `agents/manager.py` | Agent自动发现、注册、实例化、权限校验 | P0 |
| Planner Agent | `agents/planner.py` | 需求分析、任务拆解、Agent调度 | P0 |
| SimpleCoder Agent | `agents/simple_coder.py` | UI修改、单文件、小Bug | P0 |
| ComplexCoder Agent | `agents/complex_coder.py` | API开发、重构、架构调整 | P0 |
| Tester Agent | `agents/tester.py` | 编译检查、测试执行、静态分析 | P0 |
| Tool基类 | `tools/base.py` | Tool基类定义 | P0 |
| Tool注册中心 | `tools/registry.py` | Tool自动发现、注册、权限校验、执行 | P0 |
| 内置工具实现 | `tools/builtins/*.py` | 8个内置工具的具体实现 | P0 |
| Agent单元测试 | `tests/test_agents.py` | 每个Agent的输入输出测试 | P1 |

### 5.3 AI Agent 使用建议

**主要使用：`general` + `mimo-v2.5-pro`**

使用场景：

| 场景 | Agent | 模型 | 说明 |
|------|-------|------|------|
| 实现Agent基类 | general | mimo-v2.5-pro | 核心架构，需要高质量 |
| 实现Planner | general | mimo-v2.5-pro | 复杂的调度逻辑 |
| 实现Tool系统 | general | mimo-v2.5-pro | 注册、权限、执行机制 |
| 实现SimpleCoder | general | mimo-v2.5 | 相对简单的Agent |
| 实现Tester | general | mimo-v2.5 | 测试Agent逻辑 |
| 调试Agent | general | mimo-v2.5 | 单元测试 |
| 代码探索 | explore | mimo-v2.5 | 查找相关模块 |

### 5.4 文件所有权

```
agents/base.py               ← 主责
agents/manager.py            ← 主责
agents/planner.py            ← 主责
agents/simple_coder.py       ← 主责
agents/complex_coder.py      ← 主责
agents/tester.py             ← 主责
agents/review.py             ← 主责（与成员B协作）
tools/base.py                ← 主责
tools/registry.py            ← 主责
tools/builtins/*.py          ← 主责
tests/test_agents.py         ← 主责
tests/test_tools.py          ← 主责
```

### 5.5 接口依赖

| 依赖方 | 依赖内容 | 说明 |
|--------|---------|------|
| 成员A | agents/*.md | 所有Agent的Prompt定义 |
| 成员A | tools/*.json | 所有Tool的参数定义 |
| 成员B | models/llm.py | LLM调用封装 |
| 成员E | memory/store.py | Memory读写 |
| 成员E | memory/builder.py | Prompt构建 |

---

## 六、成员D — 后端开发工程师A（框架与通信方向）

### 6.1 角色定位

- FastAPI 框架搭建、API 路由实现、SSE 流式输出
- 负责后端服务的骨架和通信机制

### 6.2 开发内容

| 任务 | 文件 | 说明 | 优先级 |
|------|------|------|--------|
| FastAPI入口 | `main.py` | 搭建FastAPI应用、注册路由、配置CORS | P0 |
| 聊天API | `api/chat.py` | /chat/stream (SSE) + /chat/history | P0 |
| 设置API | `api/settings.py` | GET/POST /settings | P0 |
| Memory API | `api/memory.py` | GET /memory | P0 |
| 项目API | `api/project.py` | POST /project/init | P0 |
| 工具API | `api/tools.py` | POST /tools/call | P0 |
| 用户API | `api/users.py` | POST /users/create | P0 |
| SSE机制 | `api/sse.py` | SSE事件推送封装 | P0 |
| 配置加载 | `config/loader.py` | settings.json读写 | P0 |
| API测试 | `tests/test_api.py` | API接口测试 | P1 |

### 6.3 AI Agent 使用建议

**主要使用：`general` + `mimo-v2.5-pro`**

使用场景：

| 场景 | Agent | 模型 | 说明 |
|------|-------|------|------|
| 搭建FastAPI框架 | general | mimo-v2.5-pro | 框架搭建需要Pro模型 |
| 实现SSE机制 | general | mimo-v2.5-pro | 异步流式处理较复杂 |
| 实现API路由 | general | mimo-v2.5 | CRUD接口相对标准 |
| 配置加载 | general | mimo-v2.5 | JSON读写简单 |
| API测试 | general | mimo-v2.5 | 测试代码 |

### 6.4 文件所有权

```
main.py                      ← 主责
api/chat.py                  ← 主责
api/settings.py              ← 主责
api/memory.py                ← 主责
api/project.py               ← 主责
api/tools.py                 ← 主责
api/users.py                 ← 主责
api/sse.py                   ← 主责
config/loader.py             ← 主责
tests/test_api.py            ← 主责
requirements.txt             ← 主责
```

### 6.5 接口依赖

| 依赖方 | 依赖内容 | 说明 |
|--------|---------|------|
| 成员E | database/models.py | 数据库表结构 |
| 成员E | database/crud.py | CRUD操作 |
| 成员E | memory/store.py | Memory读写（间接） |
| 成员C | agents/manager.py | Agent调用入口 |
| 成员E | workflow/pipeline.py | 工作流调用入口 |

---

## 七、成员E — 后端开发工程师B（数据与业务逻辑方向）

### 7.1 角色定位

- 数据库设计、Memory系统、Workflow管线、Prompt Builder
- 负责数据持久化和核心业务逻辑

### 7.2 开发内容

| 任务 | 文件 | 说明 | 优先级 |
|------|------|------|--------|
| 数据库表结构 | `database/models.py` | sessions/messages/tasks/checkpoints表 | P0 |
| CRUD操作 | `database/crud.py` | 用户、会话、消息、任务的增删改查 | P0 |
| Memory存储 | `memory/store.py` | 分层Memory的读写、检索、更新 | P0 |
| Memory压缩 | `memory/compressor.py` | Session历史自动压缩为摘要 | P1 |
| Prompt Builder | `memory/builder.py` | 组装完整Prompt | P0 |
| 工作流管线 | `workflow/pipeline.py` | 主管线：8个节点顺序执行 | P0 |
| Review循环 | `workflow/review_loop.py` | 自动修正循环 | P0 |
| 快照管理 | `workflow/checkpoint.py` | 文件快照创建、恢复 | P0 |
| PipelineState | `workflow/state.py` | 状态数据结构定义 | P0 |
| 业务测试 | `tests/test_workflow.py` | 工作流测试 | P1 |

### 7.3 AI Agent 使用建议

**主要使用：`general` + `mimo-v2.5-pro`**

使用场景：

| 场景 | Agent | 模型 | 说明 |
|------|-------|------|------|
| 设计数据库表结构 | general | mimo-v2.5-pro | 需要仔细设计关系 |
| 实现Memory系统 | general | mimo-v2.5-pro | 六层Memory逻辑复杂 |
| 实现Pipeline | general | mimo-v2.5-pro | 工作流核心，需要Pro |
| 实现Prompt Builder | general | mimo-v2.5-pro | Prompt组装逻辑 |
| 实现CRUD | general | mimo-v2.5 | 标准数据库操作 |
| 实现Checkpoint | general | mimo-v2.5 | 快照逻辑相对简单 |
| 代码探索 | explore | mimo-v2.5 | 查找相关模块 |

### 7.4 文件所有权

```
database/models.py           ← 主责
database/crud.py             ← 主责
database/__init__.py         ← 主责
memory/store.py              ← 主责
memory/compressor.py         ← 主责
memory/builder.py            ← 主责
memory/__init__.py           ← 主责
workflow/pipeline.py         ← 主责
workflow/review_loop.py      ← 主责
workflow/checkpoint.py       ← 主责
workflow/state.py            ← 主责
workflow/__init__.py         ← 主责
tests/test_workflow.py       ← 主责
tests/test_memory.py         ← 主责
```

### 7.5 接口依赖

| 依赖方 | 依赖内容 | 说明 |
|--------|---------|------|
| 成员B | models/llm.py | LLM调用（Memory压缩需要） |
| 成员C | agents/manager.py | Agent调用（Pipeline需要） |
| 成员D | config/loader.py | 配置加载 |
| 成员A | agents/*.md | Agent Prompt定义 |

---

## 八、成员F — 前端开发工程师A（界面设计方向）

### 8.1 角色定位

- React Ink CLI 框架搭建、UI 组件实现、样式设计
- 负责用户看到的所有界面元素

### 8.2 开发内容

| 任务 | 文件 | 说明 | 优先级 |
|------|------|------|--------|
| CLI框架搭建 | `frontend/` | React Ink + TypeScript项目初始化 | P0 |
| 聊天界面 | `components/Chat.tsx` | 消息列表、输入框、打字机效果 | P0 |
| 设置面板 | `components/Settings.tsx` | 全中文6大类39项设置 | P0 |
| 布局组件 | `components/Layout.tsx` | 整体布局框架 | P0 |
| 样式系统 | `styles/` | 终端色彩方案、状态图标 | P0 |
| 状态管理 | `store/` | 全局状态管理 | P1 |
| 组件测试 | `tests/` | UI组件测试 | P1 |

### 8.3 AI Agent 使用建议

**主要使用：`general` + `mimo-v2.5`**

使用场景：

| 场景 | Agent | 模型 | 说明 |
|------|-------|------|------|
| 搭建Ink项目 | general | mimo-v2.5 | 项目初始化 |
| 实现Chat组件 | general | mimo-v2.5 | UI组件开发 |
| 实现Settings组件 | general | mimo-v2.5 | 表单组件 |
| 样式设计 | general | mimo-v2.5 | CSS/样式代码 |
| 组件测试 | general | mimo-v2.5 | 测试代码 |
| 参考示例 | explore | mimo-v2.5 | 查找Ink示例 |

### 8.4 文件所有权

```
frontend/src/components/Chat.tsx        ← 主责
frontend/src/components/Settings.tsx    ← 主责
frontend/src/components/Layout.tsx      ← 主责
frontend/src/styles/                    ← 主责
frontend/src/store/                     ← 主责
frontend/package.json                   ← 主责
frontend/tsconfig.json                  ← 主责
```

### 8.5 接口依赖

| 依赖方 | 依赖内容 | 说明 |
|--------|---------|------|
| 成员G | services/api.ts | API调用封装 |
| 成员G | hooks/useSSE.ts | SSE数据流 |
| 成员D | API接口定义 | 接口格式 |

---

## 九、成员G — 前端开发工程师B（数据对接方向）

### 9.1 角色定位

- API 对接、SSE 消费、数据驱动组件
- 负责前端与后端的所有数据交互

### 9.2 开发内容

| 任务 | 文件 | 说明 | 优先级 |
|------|------|------|--------|
| Axios封装 | `services/api.ts` | HTTP请求封装、拦截器、错误处理 | P0 |
| SSE Hook | `hooks/useSSE.ts` | SSE连接管理、事件解析、状态更新 | P0 |
| Agent状态 | `components/AgentStatus.tsx` | 实时显示当前运行的Agent | P0 |
| Memory浏览 | `components/MemoryView.tsx` | 各层Memory内容展示 | P0 |
| 审批弹窗 | `components/ApprovalDialog.tsx` | 审批确认弹窗 | P0 |
| 类型定义 | `types/` | TypeScript类型定义 | P0 |
| 数据测试 | `tests/` | 数据层测试 | P1 |

### 9.3 AI Agent 使用建议

**主要使用：`general` + `mimo-v2.5`**

使用场景：

| 场景 | Agent | 模型 | 说明 |
|------|-------|------|------|
| 实现Axios封装 | general | mimo-v2.5 | HTTP封装 |
| 实现SSE Hook | general | mimo-v2.5 | SSE处理逻辑 |
| 实现AgentStatus | general | mimo-v2.5 | 状态展示组件 |
| 实现MemoryView | general | mimo-v2.5 | 数据展示组件 |
| 实现ApprovalDialog | general | mimo-v2.5 | 弹窗组件 |
| 参考SSE示例 | explore | mimo-v2.5 | 查找SSE实现参考 |

### 9.4 文件所有权

```
frontend/src/services/api.ts           ← 主责
frontend/src/hooks/useSSE.ts           ← 主责
frontend/src/components/AgentStatus.tsx ← 主责
frontend/src/components/MemoryView.tsx  ← 主责
frontend/src/components/ApprovalDialog.tsx ← 主责
frontend/src/types/                    ← 主责
```

### 9.5 接口依赖

| 依赖方 | 依赖内容 | 说明 |
|--------|---------|------|
| 成员D | API接口定义 | 8个接口的请求/响应格式 |
| 成员D | SSE事件格式 | SSE事件类型和数据结构 |
| 成员F | 组件基础 | Layout、样式系统 |

---

## 十、协作接口矩阵

### 10.1 前后端接口约定

| 接口 | 后端负责人 | 前端负责人 | 联调时间 |
|------|-----------|-----------|---------|
| POST /api/chat/stream | 成员D | 成员G | Phase 4 |
| GET /api/chat/history | 成员D | 成员G | Phase 4 |
| GET/POST /api/settings | 成员D | 成员F | Phase 4 |
| GET /api/memory | 成员D | 成员G | Phase 4 |
| POST /api/project/init | 成员D | 成员F | Phase 4 |
| POST /api/users/create | 成员D | 成员F | Phase 4 |
| POST /api/tools/call | 成员D | 成员G | Phase 4 |

### 10.2 模块依赖图

```
成员A (配置/定义)
  │
  ├──→ 成员B (RAG/Constraint)
  │      │
  │      └──→ 成员E (Memory/Workflow)
  │
  ├──→ 成员C (Agent/Tool)
  │      │
  │      └──→ 成员E (Memory/Workflow)
  │
  ├──→ 成员D (API/SSE)
  │      │
  │      └──→ 成员G (前端数据对接)
  │
  └──→ 成员F (前端UI)
         │
         └──→ 成员G (前端数据对接)
```

---

## 十一、每日站会模板

```
日期：YYYY-MM-DD
参与人：全员

## 成员A
- 昨天：
- 今天：
- 阻塞：

## 成员B
- 昨天：
- 今天：
- 阻塞：

## 成员C
- 昨天：
- 今天：
- 阻塞：

## 成员D
- 昨天：
- 今天：
- 阻塞：

## 成员E
- 昨天：
- 今天：
- 阻塞：

## 成员F
- 昨天：
- 今天：
- 阻塞：

## 成员G
- 昨天：
- 今天：
- 阻塞：
```

---

## 十二、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| Agent调试困难 | 延期 | 先Mock LLM返回，再对接真实模型 |
| SSE兼容性问题 | 前后端联调受阻 | 提前验证SSE方案，准备WebSocket备选 |
| ChromaDB安装问题 | RAG功能延期 | 准备简单的内存向量检索备选方案 |
| 前后端接口不一致 | 联调效率低 | 先定义OpenAPI文档，前后端并行开发 |
| 成员进度不均 | 集成困难 | 每日站会同步，及时调整分工 |

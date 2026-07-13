# 成员A 答辩提示

## 你的角色
项目经理 / 组长

## 答辩要点

### 1. 项目整体介绍（2分钟）
- BandCode 定位：基于分层记忆与六智能体协作的 AI 编程助手 CLI 工具
- 技术栈概览：Python 3.11 + FastAPI 后端，React 18 + TypeScript + Tailwind CSS 前端，MiMo v2.5 Pro 大模型
- 核心能力：8 节点 Pipeline 工作流、六层 Memory 系统、8 个内置工具、12 种 SSE 事件类型

### 2. 项目管理经验（2分钟）
- 7 人团队分工：项目经理、RAG 开发、Agent 开发、后端 ×2、前端 ×2
- 敏捷开发流程：需求分析 → 架构设计 → 模块开发 → 集成测试 → 迭代优化
- 协作方式：Git 分支管理、接口先行（先定义 API 契约再并行开发）、定期 Code Review

### 3. 架构设计（2分钟）
- 分层架构：API 层 → Agent 层 → Tool 层 → Memory 层 → Database 层
- 六智能体协作：Planner、SimpleCoder、ComplexCoder、Tester、Constraint、Review
- Pipeline 8 节点：从用户输入到最终输出的完整处理链路
- 配置驱动：agents/*.md 定义 Agent 行为，tools/*.json 定义工具元数据

### 负责的源代码文件

- `backend/main.py` — 应用入口，FastAPI 实例创建、CORS 配置、路由注册、启动/关闭事件
- `backend/config/` — 配置管理，JSON 配置文件读写、系统参数管理、环境变量处理
- `backend/api/errors.py` — 全局错误处理，自定义异常类、register_error_handlers 统一异常捕获
- `backend/api/middleware.py` — 中间件，SecurityHeadersMiddleware 安全头、RequestLoggingMiddleware 请求日志
- `backend/workflow/` — Pipeline 工作流引擎，8 节点流程控制、PipelineState 状态管理、Agent 调度

### 所需知识点

- FastAPI 应用生命周期（lifespan、startup/shutdown 事件）
- CORS 跨域配置（CORSMiddleware、allow_origins、allow_methods）
- Python logging 日志系统（日志级别、格式化、Handler）
- Pydantic 数据验证（BaseModel、Field、validator）
- JSON 配置文件管理（读写、默认值、环境变量覆盖）
- 项目分层架构设计（关注点分离、依赖注入）

### 可能的问题

**Q1: 为什么选择 FastAPI 作为后端框架？**

A: FastAPI 是异步优先的 Python Web 框架，原生支持 async/await，与项目中大量异步操作（SSE 流式输出、AsyncOpenAI 调用、数据库操作）配合良好。FastAPI 自动生成 OpenAPI 文档（Swagger UI），方便前后端联调。相比 Django 更轻量、启动快，适合 API 服务场景；相比 Flask 原生支持类型验证（集成 Pydantic），开发效率更高。

**Q2: 如何保证项目的代码质量？**

A: 从四个维度保障：一是类型安全，全项目使用 Python 类型注解 + Pydantic 数据验证，API 请求和响应都有严格的数据模型；二是分层架构，API 层、Agent 层、Tool 层、Memory 层职责清晰，降低耦合；三是统一错误处理，通过 register_error_handlers 全局捕获异常，返回标准化错误响应；四是日志系统，RequestLoggingMiddleware 记录所有请求日志，便于排查问题。

**Q3: 项目如何处理并发请求？**

A: FastAPI 基于 Uvicorn（ASGI 服务器）运行，天然支持异步并发。项目中 LLM 调用使用 AsyncOpenAI 异步客户端，数据库操作使用 async/await，SSE 流式输出通过 asyncio.Queue 在处理函数和事件生成器之间传递数据。多个用户可以同时发起聊天请求，每个请求独立处理，互不阻塞。

**Q4: 项目的核心创新点是什么？**

A: 三个核心创新：一是六智能体协作架构，不同 Agent（Planner 规划、SimpleCoder/ComplexCoder 编码、Tester 测试、Constraint 约束检查、Review 代码审查）分工协作，模拟真实开发团队；二是六层分层记忆系统（global/project/task/session/checkpoint/notes），让 AI 能跨会话保持上下文；三是配置驱动设计，Agent 行为通过 Markdown 文件定义、工具通过 JSON 元数据注册，新增 Agent 或工具无需修改核心代码。

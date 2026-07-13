# 成员D 答辩提示

## 你的角色
后端开发工程师 A

## 答辩要点

### 1. API 设计（2分钟）
- RESTful API 设计规范
- 主要接口：对话、会话管理、知识库管理
- SSE 流式输出实现

### 2. 后端架构（2分钟）
- FastAPI 框架选择理由
- 异步处理机制
- 错误处理和日志系统

### 3. 系统集成（2分钟）
- 如何与 AI 模块集成
- 如何与前端通信
- 如何处理并发请求

### 负责的源代码文件

- `backend/api/chat.py` — 聊天 API，流式聊天接口（SSE）、聊天历史接口、LLM 调用集成
- `backend/api/sse.py` — SSE 事件推送封装，12 种事件类型定义、Pydantic 事件模型、连接管理器、事件生成器
- `backend/api/users.py` — 用户 API，创建用户、获取用户列表
- `backend/api/settings.py` — 设置 API，获取/更新系统配置
- `backend/api/test.py` — 模型测试 API，测试模型连接、流式输出测试
- `backend/models/llm.py` — LLM 客户端封装，AsyncOpenAI 调用、流式/非流式对话、错误处理
- `backend/models/requests.py` — 请求数据模型，Pydantic Field 验证
- `backend/models/responses.py` — 响应数据模型，统一响应格式

### 所需知识点

- FastAPI 路由系统（APIRouter、prefix、tags）
- Server-Sent Events（SSE）原理与实现（sse-starlette、EventSourceResponse）
- Pydantic BaseModel 数据验证（Field、validator）
- OpenAI Python SDK（AsyncOpenAI、chat.completions.create）
- 异步编程（asyncio.Queue、asyncio.create_task、async for）
- RESTful API 设计规范

### 可能的问题

**Q1: 为什么选择 FastAPI 而不是 Django？**

A: FastAPI 是异步优先的 Python Web 框架，原生支持 async/await 语法，与 AsyncOpenAI 等异步 SDK 配合良好。项目需要 SSE 流式输出，FastAPI 通过 sse-starlette 库可以方便地实现 EventSourceResponse。FastAPI 自动生成 OpenAPI 文档（Swagger UI），方便前后端联调。相比 Django 的 MTV 架构，FastAPI 更轻量，启动速度快，适合 API 服务场景。项目使用 Pydantic BaseModel 进行请求验证，FastAPI 原生集成 Pydantic。

**Q2: SSE 和 WebSocket 的区别？**

A: SSE（Server-Sent Events）是单向通信（服务器→客户端），基于 HTTP 协议，适合服务器向客户端推送实时数据的场景。WebSocket 是双向通信，适合需要客户端频繁向服务器发送数据的场景。本项目选择 SSE 的原因是：聊天场景主要是服务器向客户端推送 AI 回复和 Agent 状态，单向通信完全够用；SSE 基于 HTTP，天然支持跨域、代理、负载均衡；实现简单，通过 sse-starlette 库的 EventSourceResponse 即可实现，前端使用 EventSource API 接收。

**Q3: 如何保证 API 安全性？**

A: 项目在多个层面保障安全性：一是全局中间件 SecurityHeadersMiddleware 添加安全响应头（如 X-Content-Type-Options、X-Frame-Options 等）；二是 RequestLoggingMiddleware 记录所有请求日志，便于审计和问题追踪；三是全局异常处理器 register_error_handlers 统一捕获异常，避免泄露内部错误信息；四是 CORS 中间件配置了跨域策略；五是 LLMClient 对 API 错误进行了分类处理（AuthenticationError、APIStatusError 等），返回用户友好的错误消息。

**Q4: 如何进行 API 测试？**

A: 项目提供了多种测试方式：一是 ModelTest 组件（/api/test 接口），可以测试模型连接和流式输出，验证 LLM API 是否正常工作；二是 FastAPI 自带的 Swagger UI（访问 /docs），可以直接在浏览器中测试所有 API 接口；三是聊天接口支持通过 GET 参数传递 session_id、project、message，方便 curl 或前端直接调用；四是所有 API 返回统一格式 {code, data, message}，便于自动化测试脚本验证响应格式。

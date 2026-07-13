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

1. 为什么选择 FastAPI 而不是 Django？
2. SSE 和 WebSocket 的区别？
3. 如何保证 API 安全性？
4. 如何进行 API 测试？

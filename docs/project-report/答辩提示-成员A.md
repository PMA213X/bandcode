# 成员A 答辩提示

## 你的角色
组长/项目经理

## 答辩要点

### 1. 项目整体介绍（2分钟）
- 项目背景：熏掌门是武夷山非遗食品品牌
- 解决问题：客服效率低、响应慢、回答不一致
- 技术方案：LangChain + LangGraph + RAG

### 2. 项目管理经验（2分钟）
- 如何分工：7人团队，AI/后端/前端三组
- 如何协调：每日站会、代码审查
- 遇到的挑战：如何解决

### 3. 架构设计（2分钟）
- 三层架构：界面层、应用层、数据层
- 技术选型理由
- 模块划分

### 负责的源代码文件

- `backend/main.py` — 后端服务入口，FastAPI 应用创建、CORS 配置、中间件注册、路由注册
- `backend/config/loader.py` — 配置加载器，settings.json 读写、单例模式、默认配置定义
- `backend/config/logging.py` — 日志系统，中文格式化器、日志级别配置
- `backend/api/errors.py` — 全局错误处理，错误码定义、AppException、异常处理器注册
- `backend/api/middleware.py` — 中间件，请求日志、安全响应头
- `backend/workflow/pipeline.py` — 工作流主管线，8 节点编排、Review 修正循环
- `backend/workflow/state.py` — 工作流状态数据结构定义
- `backend/workflow/checkpoint.py` — 文件快照管理器
- `backend/workflow/review_loop.py` — Review 修正循环逻辑

### 所需知识点

- FastAPI 应用框架（创建实例、路由注册、中间件链）
- CORS 跨域资源共享配置
- Python logging 模块（Formatter、Handler、Logger）
- Pydantic 数据验证模型
- JSON 配置文件读写与单例模式
- 项目架构设计（三层架构：界面层、应用层、数据层）

### 可能的问题

**Q1: 为什么选择 LangChain 而不是自研？**

A: LangChain 是成熟的 LLM 应用开发框架，提供了 PromptTemplate、RetrievalQA、AgentExecutor 等丰富组件，可以快速搭建 RAG 和 Agent 系统。自研框架需要大量开发时间且稳定性无法保证。LangChain 社区活跃、文档完善，遇到问题容易找到解决方案，同时与 LangGraph 配合良好，支持复杂的状态流转和多 Agent 编排。

**Q2: 如何保证回答准确性？**

A: 通过 RAG 技术将知识库文档向量化后存入 ChromaDB，用户提问时先检索相关文档片段作为上下文注入 Prompt，减少大模型幻觉。同时设置了 Top-K 相似度检索策略，返回最相关的文档片段。知识库内容来自官方产品文档和客服标准话术，确保信息权威性。

**Q3: 如何处理并发请求？**

A: 后端基于 FastAPI 框架，天然支持异步并发处理。聊天接口使用 asyncio.create_task() 启动后台任务处理 Agent 工作流，通过 asyncio.Queue 在处理函数和 SSE 生成器之间传递事件，不会阻塞主线程。LLM 调用使用 AsyncOpenAI 异步客户端，支持高并发场景。

**Q4: 项目有什么创新点？**

A: 主要创新点有三个：一是采用六层分层记忆架构（global/project/task/session/checkpoint/notes），让 Agent 具备长期记忆能力；二是 8 节点工作流管线设计（约束检索→RAG→Prompt 构建→Planner→审批→子 Agent→Tester→Review），实现了完整的代码生成质量保障闭环；三是 Review 修正循环机制，当审查发现违规时自动反馈给 Planner 重新生成，最多重试 3 次。

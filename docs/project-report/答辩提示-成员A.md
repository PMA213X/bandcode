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

1. 为什么选择 LangChain 而不是自研？
2. 如何保证回答准确性？
3. 如何处理并发请求？
4. 项目有什么创新点？

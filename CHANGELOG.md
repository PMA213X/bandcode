# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/) 规范。

## [0.1.0] - 2026-07-12

### 新增

- **Agent 系统**
  - Planner Agent：需求分析、任务拆解、Agent 调度
  - SimpleCoder Agent：简单编码任务
  - ComplexCoder Agent：复杂编码任务
  - Tester Agent：测试验证
  - Constraint Agent：约束检索
  - Review Agent：约束审查

- **Tool 系统**
  - read_file：读取文件
  - write_file：写入文件
  - list_directory：列出目录
  - search_project：搜索项目
  - search_knowledge：搜索知识库
  - create_task：创建任务
  - update_memory：更新 Memory
  - finish_task：完成任务

- **后端**
  - FastAPI 框架
  - 8 个 RESTful API 接口
  - SSE 流式推送
  - SQLite 数据库
  - ChromaDB 向量数据库
  - Memory 分层系统
  - Workflow 管线

- **前端**
  - React + Ink CLI 界面
  - Chat 组件
  - Layout 组件
  - Settings 组件
  - Agent 状态显示
  - Memory 浏览
  - 审批弹窗

- **RAG 引擎**
  - 文档切分
  - 向量索引
  - 相似度检索

- **文档**
  - 项目架构文档
  - API 接口文档
  - 功能模块文档
  - 团队成员文档

### 修复

- 无

## [0.0.1] - 2026-07-06

### 新增

- 项目初始化
- 文档开发规范
- Git 提交规范

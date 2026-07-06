# 2026-07-06 添加开发规划文档

## 修改原因

为7人团队制定详细的开发分工和AI Agent使用指南，确保多人协作有序进行。

## 涉及文件

- docs/development-plan.md（新增）
- docs/changes/2026-07-06-add-development-plan.md（新增）

## 涉及模块

- 文档系统

## 变更内容

新增完整的开发规划文档，包含：

1. 项目结构总览
2. 总体开发规划（6个阶段）
3. 成员A — 组长/项目经理（配置文件、Agent/Tool定义）
4. 成员B — AI开发工程师A（RAG、Constraint Agent、LLM封装）
5. 成员C — AI开发工程师B（Agent基类、Tool系统、业务Agent）
6. 成员D — 后端开发工程师A（FastAPI框架、API路由、SSE）
7. 成员E — 后端开发工程师B（数据库、Memory、Workflow）
8. 成员F — 前端开发工程师A（CLI框架、UI组件、样式）
9. 成员G — 前端开发工程师B（API对接、SSE消费、数据组件）
10. 协作接口矩阵
11. 风险与应对措施

每位成员包含：角色定位、开发内容、AI Agent使用建议、文件所有权、接口依赖。

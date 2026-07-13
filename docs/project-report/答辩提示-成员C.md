# 成员C 答辩提示

## 你的角色
AI 开发工程师 B（Agent 方向）

## 答辩要点

### 1. LangGraph 状态图设计（2分钟）
- 状态图结构：意图识别 → 条件路由 → 处理节点 → 回答生成
- AgentState 定义：messages, intent, context, tool_result
- 节点设计：意图识别、RAG检索、工具调用、直接对话

### 2. 意图识别实现（2分钟）
- 基于 LLM 的意图分类
- 意图类型：产品咨询、订单查询、产品推荐、闲聊
- 路由逻辑：根据意图选择处理节点

### 3. 工具调用设计（2分钟）
- 工具定义：query_order, search_product, recommend_product
- Function Calling 机制
- 工具结果与回答生成的整合

### 可能的问题

1. 为什么选择 LangGraph 而不是自研状态机？
2. 意图识别的准确率如何保证？
3. 如何处理工具调用失败？
4. 如何扩展新的意图类型？

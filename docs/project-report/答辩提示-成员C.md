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

### 负责的源代码文件

- `backend/agents/base.py` — Agent 基类，BaseAgent 抽象类、PipelineState 状态结构、LLM 调用、Tool 调用、状态上报
- `backend/agents/manager.py` — Agent 管理器，自动发现、注册、权限校验、Agent 生命周期管理
- `backend/agents/planner.py` — Planner Agent，需求分析、任务拆解、Agent 调度
- `backend/agents/complex_coder.py` — ComplexCoder Agent，复杂编码任务处理
- `backend/agents/simple_coder.py` — SimpleCoder Agent，简单编码任务处理
- `backend/agents/tester.py` — Tester Agent，编译检查、测试执行、静态分析
- `backend/agents/constraint.py` — Constraint Agent，从 Memory 检索约束
- `backend/agents/review.py` — Review Agent，约束审查、违规检测
- `backend/tools/base.py` — Tool 基类，ToolResult 数据结构、参数验证、Schema 生成
- `backend/tools/registry.py` — Tool 注册中心，自动发现、权限校验、工具执行
- `backend/tools/builtins/` — 8 个内置工具实现（read_file、write_file、list_directory 等）
- `agents/*.md` — 6 个 Agent 提示词文件（planner、constraint、review、simple-coder、complex-coder、tester）
- `tools/*.json` — 8 个 Tool 定义文件（JSON Schema 格式）

### 所需知识点

- LangGraph 状态图设计（StateGraph、节点、条件路由）
- Python ABC 抽象基类与 @abstractmethod
- Agent 架构模式（ReAct、Plan-and-Execute）
- Function Calling / Tool Use 机制
- 动态模块发现（importlib、Path.glob）
- 权限控制模型（read/edit/bash 权限分级）

### 可能的问题

1. 为什么选择 LangGraph 而不是自研状态机？
2. 意图识别的准确率如何保证？
3. 如何处理工具调用失败？
4. 如何扩展新的意图类型？

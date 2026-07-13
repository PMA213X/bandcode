# 成员C 答辩提示

## 你的角色
AI 开发工程师 B（Agent 方向）

## 答辩要点

### 1. Agent 架构设计（2分钟）
- 六智能体：Planner（规划）、SimpleCoder（简单编码）、ComplexCoder（复杂编码）、Tester（测试）、Constraint（约束检查）、Review（代码审查）
- ABC 抽象基类设计，统一 Agent 接口
- 配置驱动：agents/*.md 定义每个 Agent 的系统提示词和行为

### 2. Pipeline 工作流（2分钟）
- 8 节点 Pipeline：用户输入 → 意图识别 → RAG 检索 → Agent 选择 → Agent 执行 → 工具调用 → 结果整合 → 输出
- PipelineState 状态对象贯穿整个流程
- 节点间数据传递与状态管理

### 3. 工具调用设计（2分钟）
- 8 个内置工具：read_file、write_file、list_dir、run_command、search_code、edit_file、ask_user、finish
- tools/*.json 定义工具元数据（名称、描述、参数 schema）
- Function Calling 机制：Agent 生成工具调用 → 执行 → 结果回传

### 负责的源代码文件

- `backend/agents/` — Agent 实现，抽象基类 BaseAgent、六个具体 Agent（Planner/SimpleCoder/ComplexCoder/Tester/Constraint/Review）、Agent 工厂
- `backend/tools/` — 工具系统，BaseTool 抽象基类、八个内置工具实现、工具注册与发现机制
- `agents/*.md` — Agent 配置文件，每个 Agent 的系统提示词、行为定义、可用工具列表
- `tools/*.json` — 工具元数据，工具名称、描述、参数 JSON Schema、权限配置

### 所需知识点

- ABC 抽象基类（abc.ABC、@abstractmethod）
- Agent 架构模式（ReAct、Function Calling、Tool Use）
- OpenAI Function Calling 协议（tool_choice、tools 参数、function call 响应）
- 动态模块发现（importlib、inspect、自动注册）
- 权限控制（Agent 可用工具白名单、工具执行权限）
- 设计模式（工厂模式、策略模式、模板方法模式）

### 可能的问题

**Q1: 为什么不用 LangGraph 而是自己实现 Agent 框架？**

A: LangGraph 是通用的 Agent 编排框架，功能强大但引入较重的依赖。BandCode 的 Agent 逻辑相对明确（六角色分工 + Pipeline 流转），自研框架可以精确控制每个环节：自定义 PipelineState 状态流转、按 Agent 角色分配工具白名单、通过 Markdown 配置文件灵活定义 Agent 行为。自研的好处是轻量、可控、易于调试，团队对每一行代码都有完全理解。

**Q2: 如何保证多个 Agent 的协作效率？**

A: 通过三个机制保障：一是 Pipeline 顺序执行，8 个节点按序流转，避免 Agent 间冲突；二是 Agent 选择策略，根据用户意图和任务复杂度自动选择合适的 Agent（如简单问题用 SimpleCoder，复杂重构用 ComplexCoder）；三是共享 PipelineState，所有 Agent 读写同一个状态对象，信息传递透明。Constraint Agent 在关键节点检查约束条件，Review Agent 在输出前做最终审查。

**Q3: 如何处理工具调用失败？**

A: 工具调用失败时有三层容错：一是工具层，每个 Tool 实现都有 try-catch，捕获 FileNotFoundError、PermissionError 等具体异常，返回结构化的错误信息（success=False + error message）；二是 Agent 层，BaseAgent 解析工具执行结果，如果失败则将错误信息反馈给 LLM，让 LLM 决定重试或换方案；三是 Pipeline 层，PipelineState 记录执行历史，Pipeline 超时或异常时可以回溯定位问题。

**Q4: 如何扩展新的 Agent 或工具？**

A: 扩展 Agent：在 agents/ 目录下新增 .md 配置文件（定义系统提示词和可用工具），然后在 backend/agents/ 下实现对应的 Agent 类继承 BaseAgent，最后在 Agent 工厂中注册即可。扩展工具：在 tools/ 目录下新增 .json 元数据文件，在 backend/tools/ 下实现工具类继承 BaseTool，工具系统通过动态发现机制自动注册。整个过程不需要修改 Pipeline 核心代码。

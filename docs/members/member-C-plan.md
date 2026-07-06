# 成员C — AI开发工程师B（Agent编排方向）开发规划

> 角色：AI 开发工程师
> 核心职责：Agent 基类与管理器、业务 Agent 实现、Tool 系统开发
> 分支：feature/ai-agent

---

## 一、角色定位

成员C 负责项目的「决策与执行层」能力：

- Agent 基类（统一接口、LLM调用、Tool调用、状态上报）
- Agent 管理器（自动发现、注册、实例化、权限校验）
- 6个业务Agent的具体实现（Planner/SimpleCoder/ComplexCoder/Tester）
- Tool 基类与注册中心
- 8个内置工具的具体实现

---

## 二、开发任务清单

### Phase 0：环境准备（第1天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| C-01 | 克隆仓库 | — | git clone + 切换到 feature/ai-agent 分支 |
| C-02 | 安装依赖 | — | 确认Python环境、依赖包 |
| C-03 | 阅读架构文档 | — | 熟悉Agent/Tool设计规范 |

### Phase 1：基础框架开发（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| C-04 | Agent基类 | `agents/base.py` | 统一Agent接口、LLM调用、Tool调用、状态上报 |
| C-05 | Agent管理器 | `agents/manager.py` | 自动发现、注册、实例化、权限校验 |
| C-06 | agents模块初始化 | `agents/__init__.py` | 模块导出 |
| C-07 | Agent基类测试 | `tests/test_agent_base.py` | 测试基类接口 |
| C-08 | Agent管理器测试 | `tests/test_agent_manager.py` | 测试注册和调度 |
| C-09 | Tool基类 | `tools/base.py` | Tool基类定义 |
| C-10 | Tool注册中心 | `tools/registry.py` | 自动发现、注册、权限校验、执行 |
| C-11 | tools模块初始化 | `tools/__init__.py` | 模块导出 |
| C-12 | Tool系统测试 | `tests/test_tool_registry.py` | 测试注册和执行 |

### Phase 2：业务Agent实现（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| C-13 | Planner Agent | `agents/planner.py` | 需求分析、任务拆解、Agent调度 |
| C-14 | SimpleCoder Agent | `agents/simple_coder.py` | UI修改、单文件、小Bug |
| C-15 | ComplexCoder Agent | `agents/complex_coder.py` | API开发、重构、架构调整 |
| C-16 | Tester Agent | `agents/tester.py` | 编译检查、测试执行、静态分析 |
| C-17 | Review Agent | `agents/review.py` | 约束审查（与成员B协作） |
| C-18 | Agent单元测试 | `tests/test_agents.py` | 所有Agent的输入输出测试 |

### Phase 2：内置工具实现（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| C-19 | read_file工具 | `tools/builtins/read_file.py` | 读取文件内容 |
| C-20 | write_file工具 | `tools/builtins/write_file.py` | 写入或创建文件 |
| C-21 | list_directory工具 | `tools/builtins/list_directory.py` | 列出目录结构 |
| C-22 | search_project工具 | `tools/builtins/search_project.py` | 全文搜索项目文件 |
| C-23 | search_knowledge工具 | `tools/builtins/search_knowledge.py` | 搜索RAG知识库 |
| C-24 | create_task工具 | `tools/builtins/create_task.py` | 创建新任务 |
| C-25 | update_memory工具 | `tools/builtins/update_memory.py` | 写入或更新Memory |
| C-26 | finish_task工具 | `tools/builtins/finish_task.py` | 标记任务完成 |
| C-27 | builtins模块初始化 | `tools/builtins/__init__.py` | 模块导出 |
| C-28 | Tool单元测试 | `tests/test_tools.py` | 所有工具的测试 |

### Phase 3：集成与调试（第9-11天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| C-29 | Agent集成测试 | — | 测试Agent在Pipeline中的表现 |
| C-30 | Tool集成测试 | — | 测试Tool调用链路 |
| C-31 | Agent调试优化 | — | 优化Prompt、调整参数 |
| C-32 | 权限矩阵验证 | — | 验证各Agent的Tool权限正确 |

### Phase 4-5：联调与优化（第12-16天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| C-33 | 端到端测试 | — | 完整工作流测试 |
| C-34 | Agent性能优化 | — | 减少不必要的LLM调用 |
| C-35 | Prompt迭代 | — | 根据测试结果优化Prompt |

---

## 三、技术要点

### 3.1 Agent基类核心接口

```python
# agents/base.py
class BaseAgent:
    """Agent基类"""

    name: str                    # Agent名称
    model: str                   # 使用的模型
    temperature: float           # 温度参数
    permissions: dict            # 工具权限
    system_prompt: str           # 系统Prompt

    async def run(self, state: PipelineState) -> PipelineState:
        """执行Agent逻辑"""
        raise NotImplementedError

    async def call_llm(self, messages: list, stream: bool = False):
        """调用LLM"""
        ...

    async def call_tool(self, tool_name: str, args: dict):
        """调用Tool"""
        ...

    def report_status(self, status: str, data: dict = None):
        """上报状态（SSE推送）"""
        ...
```

### 3.2 Agent管理器核心接口

```python
# agents/manager.py
class AgentManager:
    """Agent管理器"""

    def __init__(self):
        self.agents: dict[str, BaseAgent] = {}

    def auto_discover(self, agents_dir: str):
        """自动扫描agents/目录，注册所有Agent"""
        ...

    def register(self, agent: BaseAgent):
        """注册Agent"""
        ...

    def get(self, name: str) -> BaseAgent:
        """获取Agent实例"""
        ...

    async def run(self, name: str, state: PipelineState) -> PipelineState:
        """执行指定Agent"""
        ...
```

### 3.3 Tool注册中心核心接口

```python
# tools/registry.py
class ToolRegistry:
    """Tool注册中心"""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def auto_discover(self, tools_dir: str):
        """自动扫描tools/目录，注册所有Tool"""
        ...

    async def call(self, name: str, args: dict, agent_permissions: dict) -> ToolResult:
        """调用工具，检查权限后执行"""
        ...
```

### 3.4 Planner Agent核心逻辑

```python
# agents/planner.py
class PlannerAgent(BaseAgent):
    """规划调度智能体"""

    async def run(self, state: PipelineState) -> PipelineState:
        # 1. 需求分析
        analysis = await self.analyze_requirement(state)

        # 2. 任务拆解
        tasks = await self分解_tasks(analysis)

        # 3. 选择子Agent
        delegated_agent = self.select_agent(tasks)

        # 4. 输出计划
        state.plan = {
            "tasks": tasks,
            "delegated_agent": delegated_agent,
            "reason": "..."
        }
        return state
```

### 3.5 Tester Agent硬约束

```python
# agents/tester.py
class TesterAgent(BaseAgent):
    """测试验证智能体"""

    permissions = {
        "read": "allow",
        "edit": "deny",      # 关键：禁止修改代码
        "bash": "allow",
        ...
    }

    async def run(self, state: PipelineState) -> PipelineState:
        # 1. 编译检查
        # 2. 单元测试执行
        # 3. 静态分析
        # 禁止自动修复，失败必须报告
        ...
```

---

## 四、AI Agent 使用指南

### 4.1 推荐配置

| 任务类型 | Agent | 模型 | 理由 |
|---------|-------|------|------|
| Agent基类实现 | general | mimo-v2.5-pro | 核心架构，需要高质量 |
| Planner实现 | general | mimo-v2.5-pro | 复杂的调度逻辑 |
| Tool系统实现 | general | mimo-v2.5-pro | 注册、权限机制 |
| SimpleCoder实现 | general | mimo-v2.5 | 相对简单的Agent |
| Tester实现 | general | mimo-v2.5 | 测试Agent逻辑 |
| 内置工具实现 | general | mimo-v2.5 | 标准CRUD操作 |
| 单元测试 | general | mimo-v2.5 | 测试代码 |
| 代码探索 | explore | mimo-v2.5 | 查找相关模块 |

### 4.2 使用示例

**实现Agent基类时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 agents/base.py，定义所有Agent的统一基类。
要求：
1. 包含 name、model、temperature、permissions、system_prompt 属性
2. 实现 run() 抽象方法
3. 实现 call_llm() 方法，封装LLM调用
4. 实现 call_tool() 方法，封装Tool调用
5. 实现 report_status() 方法，用于SSE推送
参考文件：doc1.md 第3.2节状态数据结构
```

**实现Planner Agent时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 agents/planner.py，规划调度智能体。
要求：
1. 继承 agents/base.py 的 BaseAgent
2. 实现需求分析、任务拆解、Agent选择逻辑
3. 输出 plan + delegated_agent + reason
4. 支持审批模式（暂停等待用户确认）
参考文件：doc1.md 第3.6节Planner Agent设计
```

**实现Tool系统时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 tools/base.py 和 tools/registry.py。
要求：
1. Tool基类：name、description、permission、parameters、execute()
2. ToolRegistry：auto_discover()、register()、call()
3. call()方法需要检查权限
参考文件：doc1.md 第3.3节工具集设计
```

---

## 五、文件所有权

### 5.1 主责文件

```
agents/__init__.py              ← 创建
agents/base.py                  ← 主责
agents/manager.py               ← 主责
agents/planner.py               ← 主责
agents/simple_coder.py          ← 主责
agents/complex_coder.py         ← 主责
agents/tester.py                ← 主责
agents/review.py                ← 主责（与成员B协作）
tools/__init__.py               ← 创建
tools/base.py                   ← 主责
tools/registry.py               ← 主责
tools/builtins/__init__.py      ← 创建
tools/builtins/read_file.py     ← 主责
tools/builtins/write_file.py    ← 主责
tools/builtins/list_directory.py    ← 主责
tools/builtins/search_project.py    ← 主责
tools/builtins/search_knowledge.py  ← 主责
tools/builtins/create_task.py       ← 主责
tools/builtins/update_memory.py     ← 主责
tools/builtins/finish_task.py       ← 主责
tests/test_agent_base.py        ← 主责
tests/test_agent_manager.py     ← 主责
tests/test_agents.py            ← 主责
tests/test_tool_registry.py     ← 主责
tests/test_tools.py             ← 主责
```

### 5.2 协作文件

| 文件 | 协作人 | 协作内容 |
|------|--------|---------|
| agents/review.py | 成员B | 约束检查逻辑由成员B实现 |
| models/llm.py | 成员B | 调用LLM封装 |
| memory/store.py | 成员E | 调用Memory存储 |
| memory/builder.py | 成员E | 调用Prompt构建 |
| agents/*.md | 成员A | Prompt定义 |

---

## 六、接口依赖

### 6.1 我依赖的接口

| 依赖方 | 依赖内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员A | agents/*.md | Phase 1 | 所有Agent的Prompt定义 |
| 成员A | tools/*.json | Phase 1 | 所有Tool的参数定义 |
| 成员B | models/llm.py | Phase 1 | LLM调用封装 |
| 成员E | memory/store.py | Phase 1 | Memory读写 |
| 成员E | memory/builder.py | Phase 2 | Prompt构建 |

### 6.2 我提供的接口

| 接收方 | 提供内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员D | agents/manager.py | Phase 1 | Agent调用入口 |
| 成员E | agents/manager.py | Phase 2 | Pipeline调用Agent |
| 成员B | agents/base.py | Phase 1 | Agent基类 |
| 成员G | agents/manager.py | Phase 4 | 前端调用Agent状态 |

---

## 七、交付物清单

| 阶段 | 交付物 | 验收标准 |
|------|--------|---------|
| Phase 0 | 环境就绪 | 开发环境正常 |
| Phase 1 | Agent基类、Agent管理器、Tool系统 | 单元测试通过 |
| Phase 2 | 6个Agent、8个内置工具 | 所有Agent可独立调用，Tool可执行 |
| Phase 3 | 集成测试通过 | Agent在Pipeline中正常运行 |
| Phase 4 | 端到端测试通过 | 完整工作流正常 |
| Phase 5 | 性能优化完成 | Agent响应时间合理 |

---

## 八、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| Agent Prompt效果差 | 输出质量低 | 迭代优化Prompt |
| Tool权限配置错误 | 安全风险 | 严格测试权限矩阵 |
| Agent调度混乱 | 工作流异常 | 完善错误处理和日志 |
| LLM输出格式不稳定 | 解析失败 | 增加格式校验和重试 |

# Agent 系统文档

> 模块：`backend/agents/`
> 负责人：成员C（AI开发工程师B）
> 更新时间：2026-07-11

---

## 一、概述

Agent 系统是 BandCode 项目的核心模块，负责智能体的管理和调度。所有 Agent 都继承自 `BaseAgent` 基类，通过 `AgentManager` 进行统一管理。

BandCode 采用 **2系统级 + 4业务级** 的六Agent协作架构，实现从需求分析到代码生成、测试验证、约束审查的全流程自动化。

### Agent类型

| 类型 | Agent | 可见性 | 说明 |
|------|-------|--------|------|
| 系统级 | Constraint Agent | 用户不可见 | 从Memory中智能检索相关约束 |
| 系统级 | Review Agent | 用户不可见 | 检查输出是否违反项目约束 |
| 业务级 | Planner | 用户可见 | 需求分析、任务拆解、Agent调度 |
| 业务级 | SimpleCoder | 用户可见 | UI修改、单文件、小Bug |
| 业务级 | ComplexCoder | 用户可见 | API开发、架构调整、跨模块重构 |
| 业务级 | Tester | 用户可见 | 编译检查、测试执行、静态分析 |

---

## 二、架构

```
BaseAgent (基类)
├── PlannerAgent (规划调度)
├── SimpleCoderAgent (简单编码)
├── ComplexCoderAgent (复杂编码)
├── TesterAgent (测试验证)
├── ConstraintAgent (约束检索)
└── ReviewAgent (约束审查)

AgentManager (管理器)
├── auto_discover() - 自动发现
├── register() - 注册Agent
├── get() - 获取Agent
├── run() - 执行Agent
└── set_tool_registry() - 注入工具注册中心
```

---

## 三、核心组件

### 3.1 BaseAgent（Agent基类）

所有Agent的基类，定义统一接口。

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| name | str | Agent名称 |
| description | str | Agent描述 |
| model | str | 使用的LLM模型 |
| temperature | float | 生成温度 |
| system_prompt | str | 系统Prompt |
| permissions | dict | 工具权限配置 |

**核心方法**：

```python
class BaseAgent(ABC):
    async def run(self, state: PipelineState) -> PipelineState:
        """执行Agent逻辑（抽象方法）"""
        raise NotImplementedError

    async def call_llm(self, messages, temperature=None, max_tokens=None):
        """调用LLM"""
        ...

    async def call_tool(self, tool_name, args):
        """调用Tool"""
        ...

    def report_status(self, status, data=None):
        """上报状态（SSE推送）"""
        ...

    def add_to_history(self, state, action, result):
        """添加历史记录"""
        ...
```

**示例**：

```python
from agents.base import BaseAgent, PipelineState

class MyAgent(BaseAgent):
    name = "my-agent"
    description = "自定义Agent"
    model = "mimo-v2.5"
    temperature = 0.1
    permissions = {"read": "allow", "edit": "allow"}

    async def run(self, state: PipelineState) -> PipelineState:
        # 实现Agent逻辑
        return state
```

### 3.2 AgentManager（Agent管理器）

管理所有Agent的注册、发现和执行。

**核心方法**：

```python
class AgentManager:
    def auto_discover(self, agents_dir=None):
        """自动扫描agents/目录，注册所有Agent"""
        ...

    def register(self, agent):
        """注册Agent"""
        ...

    def get(self, name) -> Optional[BaseAgent]:
        """获取Agent实例"""
        ...

    def list_agents(self) -> list[str]:
        """列出所有Agent"""
        ...

    async def run(self, name, state) -> PipelineState:
        """执行指定Agent"""
        ...

    def set_tool_registry(self, tool_registry):
        """注入ToolRegistry"""
        ...
```

**使用示例**：

```python
from agents.manager import AgentManager
from models.llm import LLMClient

# 创建LLM客户端
llm = LLMClient(base_url="...", api_key="...", model="...")

# 创建Agent管理器
manager = AgentManager(llm_client=llm)

# 自动发现Agent
manager.auto_discover()

# 执行Agent
state = PipelineState(user_input="帮我实现登录功能")
result = await manager.run("planner", state)
```

### 3.3 PipelineState（工作流状态）

贯穿整个工作流的状态数据结构。

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| user_input | str | 用户输入 |
| session_id | str | 会话ID |
| project | str | 项目名称 |
| constraints | list | 约束列表 |
| constraint_summary | str | 约束摘要 |
| rag_context | str | RAG上下文 |
| memory_context | dict | Memory上下文 |
| plan | dict | 规划结果 |
| code | str | 生成的代码 |
| files_changed | list | 修改的文件列表 |
| test_results | dict | 测试结果 |
| review_result | dict | 审查结果 |
| agent_history | list | Agent执行历史 |
| error | str | 错误信息 |

---

## 四、Agent详细设计

### 4.1 PlannerAgent（规划调度智能体）

**职责**：
- 需求分析：理解用户需求
- 任务拆解：将复杂任务分解为子任务
- Agent调度：选择合适的子Agent执行

**配置**：
- 模型：mimo-v2.5-pro
- 温度：0.3
- 权限：read, edit, bash

**审批机制**：
- 切换子Agent时需用户确认
- 代码修改前需用户确认
- bash操作前需用户确认

**输出格式**：

```json
{
  "plan": [...],
  "delegated_agent": "simple-coder|complex-coder",
  "reason": "选择原因"
}
```

### 4.2 SimpleCoderAgent（简单编码智能体）

**职责**：
- UI修改：样式调整、布局优化
- 配置调整：配置文件参数修改
- 单文件修改：单个文件内的代码变更
- 小型Bug修复：简单的逻辑修复

**配置**：
- 模型：mimo-v2.5
- 温度：0.2
- 权限：read, edit, bash

**自动升级条件**：
- 超过2个文件需要修改
- 超过300行代码变更
- 涉及架构调整

### 4.3 ComplexCoderAgent（复杂编码智能体）

**职责**：
- 核心业务逻辑：关键业务流程的实现
- API开发：接口设计与实现
- 架构调整：模块重构、依赖关系调整
- 跨模块重构：涉及多个模块的代码重构

**配置**：
- 模型：mimo-v2.5-pro
- 温度：0.1
- 权限：read, edit, bash

**硬约束**：
- 必须输出完整代码，不得省略
- 完成后记录修改原因、涉及模块、涉及文件

### 4.4 TesterAgent（测试验证智能体）

**职责**：
- 编译检查：检查代码语法和类型
- 单元测试：运行单元测试
- 静态分析：代码质量检查

**配置**：
- 模型：mimo-v2.5
- 温度：0
- 权限：read（禁止edit和bash）

**硬约束**：
- edit权限 = deny：禁止修改任何代码文件
- 禁止自动修复：发现问题后仅报告

### 4.5 ConstraintAgent（约束检索智能体）

**职责**：
- 解析用户意图
- 检索各层Memory
- 去重+排序
- 生成约束摘要

**配置**：
- 模型：mimo-v2.5
- 温度：0.1
- 权限：read

**触发方式**：每次用户输入后自动触发

### 4.6 ReviewAgent（约束审查智能体）

**职责**：
- 检查代码是否违反约束
- 检查文件修改是否合规
- 生成审查报告

**配置**：
- 模型：mimo-v2.5-pro
- 温度：0
- 权限：read

**检查维度**：
- Memory约束合规
- 编码规范
- Prompt规则

**修正循环**：
- 最多重试3次
- 超过3次标记为失败

---

## 五、权限矩阵

| 权限 | Planner | SimpleCoder | ComplexCoder | Tester |
|------|---------|-------------|--------------|--------|
| read | allow | allow | allow | allow |
| edit | allow | allow | allow | **deny** |
| bash | allow | allow | allow | allow |

---

## 六、使用流程

### 6.1 初始化

```python
from agents.manager import AgentManager
from models.llm import LLMClient

# 创建LLM客户端
llm = LLMClient(
    base_url="https://api.example.com/v1",
    api_key="your-api-key",
    model="mimo-v2.5-pro"
)

# 创建Agent管理器
manager = AgentManager(llm_client=llm)

# 自动发现Agent
manager.auto_discover()
```

### 6.2 执行单个Agent

```python
from agents.base import PipelineState

# 创建初始状态
state = PipelineState(
    user_input="帮我实现用户登录功能",
    session_id="session_123",
    project="my_project"
)

# 执行Planner Agent
result = await manager.run("planner", state)

# 获取规划结果
print(result.plan)
```

### 6.3 执行工作流

```python
# 执行Constraint Agent获取约束
state = await manager.run("constraint", state)

# 执行Planner Agent进行规划
state = await manager.run("planner", state)

# 根据规划结果执行编码Agent
if state.plan.get("delegated_agent") == "simple-coder":
    state = await manager.run("simple-coder", state)
elif state.plan.get("delegated_agent") == "complex-coder":
    state = await manager.run("complex-coder", state)

# 执行Tester Agent进行测试
state = await manager.run("tester", state)

# 执行Review Agent进行审查
state = await manager.run("review", state)
```

---

## 七、文件结构

```
backend/agents/
├── __init__.py          # 模块导出
├── base.py              # BaseAgent 基类
├── manager.py           # AgentManager 管理器
├── planner.py           # Planner Agent
├── simple_coder.py      # SimpleCoder Agent
├── complex_coder.py     # ComplexCoder Agent
├── tester.py            # Tester Agent
├── constraint.py        # Constraint Agent
└── review.py            # Review Agent
```

---

## 八、Prompt定义文件

```
agents/
├── planner.md           # Planner Prompt定义
├── simple-coder.md      # SimpleCoder Prompt定义
├── complex-coder.md     # ComplexCoder Prompt定义
├── tester.md            # Tester Prompt定义
├── constraint.md        # Constraint Prompt定义
└── review.md            # Review Prompt定义
```

---

## 九、测试

```bash
cd backend
pytest tests/test_agents.py -v
```

测试覆盖：
- PipelineState 创建和使用
- BaseAgent 抽象类
- 所有Agent的运行流程
- AgentManager的注册、获取、执行

---

## 作者

成员C（wang123456-123456）- AI开发工程师B（Agent编排方向）

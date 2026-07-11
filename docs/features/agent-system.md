# Agent 系统

## 概述

Agent 系统是 BandCode 项目的核心模块，负责智能体的管理和调度。所有 Agent 都继承自 `BaseAgent` 基类，通过 `AgentManager` 进行统一管理。

## 架构

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

## 核心组件

### 1. BaseAgent 基类

所有 Agent 的基类，提供统一接口。

**属性：**
- `name`: Agent名称
- `description`: Agent描述
- `model`: 使用的LLM模型
- `temperature`: 生成温度
- `permissions`: 工具权限配置

**方法：**
- `run(state)`: 执行Agent逻辑（抽象方法）
- `call_llm(messages)`: 调用LLM
- `call_tool(tool_name, args)`: 调用Tool
- `report_status(status, data)`: 上报状态
- `add_to_history(state, action, result)`: 添加历史记录

**示例：**
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

### 2. AgentManager 管理器

管理所有 Agent 的注册、发现和执行。

**方法：**
- `auto_discover(agents_dir)`: 自动扫描目录，注册所有Agent
- `register(agent)`: 注册Agent
- `get(name)`: 获取Agent实例
- `list_agents()`: 列出所有Agent
- `run(name, state)`: 执行指定Agent
- `set_tool_registry(tool_registry)`: 注入ToolRegistry

**示例：**
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

### 3. PipelineState 状态

工作流状态数据结构，在整个Agent工作流中传递。

**属性：**
- `user_input`: 用户输入
- `session_id`: 会话ID
- `project`: 项目名称
- `constraints`: 约束列表
- `constraint_summary`: 约束摘要
- `rag_context`: RAG上下文
- `memory_context`: Memory上下文
- `plan`: 规划结果
- `code`: 生成的代码
- `files_changed`: 修改的文件列表
- `test_results`: 测试结果
- `review_result`: 审查结果
- `agent_history`: Agent执行历史
- `error`: 错误信息
- `current_agent`: 当前Agent名称
- `step_count`: 步骤计数
- `max_steps`: 最大步骤数

## Agent 类型

### 1. PlannerAgent (规划调度智能体)

**职责：**
- 需求分析：理解用户需求
- 任务拆解：将复杂任务分解为子任务
- Agent调度：选择合适的子Agent执行

**配置：**
- 模型：mimo-v2.5-pro
- 温度：0.3
- 权限：read, edit, bash

### 2. SimpleCoderAgent (简单编码智能体)

**职责：**
- UI修改：样式调整、布局优化
- 配置调整：配置文件参数修改
- 单文件修改：单个文件内的代码变更
- 小型Bug修复：简单的逻辑修复

**配置：**
- 模型：mimo-v2.5
- 温度：0.2
- 权限：read, edit, bash
- 升级阈值：2个文件或300行代码

### 3. ComplexCoderAgent (复杂编码智能体)

**职责：**
- 核心业务逻辑：关键业务流程的实现
- API开发：接口设计与实现
- 架构调整：模块重构、依赖关系调整
- 跨模块重构：涉及多个模块的代码重构

**配置：**
- 模型：mimo-v2.5-pro
- 温度：0.1
- 权限：read, edit, bash

### 4. TesterAgent (测试验证智能体)

**职责：**
- 编译检查：检查代码语法和类型
- 单元测试：运行单元测试
- 静态分析：代码质量检查

**配置：**
- 模型：mimo-v2.5
- 温度：0
- 权限：read（禁止edit和bash）

**硬约束：**
- 禁止修改任何代码文件
- 禁止自动修复问题

### 5. ConstraintAgent (约束检索智能体)

**职责：**
- 从Memory中智能检索相关约束
- 去重和排序
- 生成约束摘要

**配置：**
- 模型：mimo-v2.5
- 温度：0.1
- 权限：read

### 6. ReviewAgent (约束审查智能体)

**职责：**
- 检查代码是否违反约束
- 检查文件修改是否合规
- 生成审查报告

**配置：**
- 模型：mimo-v2.5
- 温度：0
- 权限：read

## 使用流程

### 1. 初始化

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

### 2. 执行单个Agent

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

### 3. 执行工作流

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

## 测试

运行单元测试：
```bash
python -m pytest tests/test_agents.py -v
```

测试覆盖：
- PipelineState 创建和使用
- BaseAgent 抽象类
- 所有Agent的运行流程
- AgentManager的注册、获取、执行

## 作者

成员C（wang123456-123456）- AI开发工程师B（Agent编排方向）

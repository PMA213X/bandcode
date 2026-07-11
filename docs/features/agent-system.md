# Agent 系统文档

> 模块：`backend/agents/`
> 负责人：成员C（AI开发工程师B）
> 更新时间：2026-07-11

---

## 一、概述

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

## 二、核心组件

### 2.1 BaseAgent（Agent基类）

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
```

### 2.2 AgentManager（Agent管理器）

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

    async def run(self, name, state) -> PipelineState:
        """执行指定Agent"""
        ...
```

**使用示例**：

```python
from agents.manager import AgentManager
from models.llm import LLMClient

llm = LLMClient()
manager = AgentManager(llm)
manager.auto_discover()

# 执行Planner
result = await manager.run("planner", state)
```

---

## 三、Agent详细设计

### 3.1 Planner Agent（规划调度智能体）

**职责**：
- 需求分析：理解用户需求
- 任务拆解：将复杂任务分解为子任务
- Agent调度：选择合适的子Agent执行

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

### 3.2 SimpleCoder Agent（简单编码智能体）

**适用场景**：
- UI修改：样式调整、布局优化
- 配置调整：配置文件参数修改
- 单文件修改：单个文件内的代码变更
- 小型Bug修复：简单的逻辑修复

**自动升级条件**：
- 超过2个文件需要修改
- 超过300行代码变更
- 涉及架构调整

### 3.3 ComplexCoder Agent（复杂编码智能体）

**适用场景**：
- 核心业务逻辑：关键业务流程的实现
- API开发：接口设计与实现
- 架构调整：模块重构、依赖关系调整
- 跨模块重构：涉及多个模块的代码重构

**硬约束**：
- 必须输出完整代码，不得省略
- 完成后记录修改原因、涉及模块、涉及文件

### 3.4 Tester Agent（测试验证智能体）

**职责**：
- 编译检查：检查代码语法和类型
- 单元测试：运行单元测试
- 静态分析：代码质量检查

**硬约束**：
- edit权限 = deny：禁止修改任何代码文件
- 禁止自动修复：发现问题后仅报告

### 3.5 Constraint Agent（约束检索智能体）

**职责**：
- 解析用户意图
- 检索各层Memory
- 去重+排序
- 生成约束摘要

**触发方式**：每次用户输入后自动触发

### 3.6 Review Agent（约束审查智能体）

**检查维度**：
- Memory约束合规
- 编码规范
- Prompt规则

**修正循环**：
- 最多重试3次
- 超过3次标记为失败

---

## 四、权限矩阵

| 权限 | Planner | SimpleCoder | ComplexCoder | Tester |
|------|---------|-------------|--------------|--------|
| read | allow | allow | allow | allow |
| edit | allow | allow | allow | **deny** |
| bash | allow | allow | allow | allow |

---

## 五、文件结构

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

## 六、Prompt定义文件

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

## 七、测试

```bash
cd backend
pytest tests/test_agents.py -v
```

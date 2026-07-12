# Tool 系统文档

> 模块：`backend/tools/`
> 负责人：成员C（AI开发工程师B）
> 更新时间：2026-07-11

---

## 一、概述

Tool 系统是 BandCode 项目的工具模块，负责提供各种工具供 Agent 使用。所有 Tool 都继承自 `Tool` 基类，通过 `ToolRegistry` 进行统一管理。

BandCode 内置 **8个工具**，通过 ToolRegistry 统一管理。Agent通过Tool调用实现文件操作、搜索、任务管理等能力。

### 工具列表

| 工具名 | 说明 | 所需权限 |
|--------|------|----------|
| read_file | 读取指定路径的文件内容 | read |
| write_file | 写入或创建文件 | edit |
| list_directory | 列出目录结构 | read |
| search_project | 全文搜索项目文件 | read |
| search_knowledge | 搜索RAG知识库 | read |
| create_task | 创建新任务 | todowrite |
| update_memory | 写入或更新Memory | edit |
| finish_task | 标记任务完成 | todowrite |

---

## 二、架构

```
Tool (基类)
├── ReadFileTool (读取文件)
├── WriteFileTool (写入文件)
├── ListDirectoryTool (列出目录)
├── SearchProjectTool (搜索项目)
├── CreateTaskTool (创建任务)
├── FinishTaskTool (完成任务)
├── SearchKnowledgeTool (搜索知识库)
└── UpdateMemoryTool (更新Memory)

ToolRegistry (注册中心)
├── auto_discover() - 自动发现
├── register() - 注册工具
├── get() - 获取工具
├── call() - 调用工具
└── list_tools() - 列出工具
```

---

## 三、核心组件

### 3.1 Tool（工具基类）

所有工具的基类，提供统一接口。

**核心属性**：

| 属性 | 类型 | 说明 |
|------|------|------|
| name | str | 工具名称 |
| description | str | 工具描述 |
| permission | str | 所需权限 |
| parameters | dict | 参数定义（JSON Schema格式） |

**核心方法**：

```python
class Tool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具（抽象方法）"""
        raise NotImplementedError

    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        ...

    def get_schema(self) -> dict:
        """获取工具Schema"""
        ...
```

**示例**：

```python
from tools.base import Tool, ToolResult

class MyTool(Tool):
    name = "my_tool"
    description = "自定义工具"
    permission = "read"
    parameters = {
        "param1": {
            "type": "string",
            "description": "参数1",
            "required": True
        }
    }

    async def execute(self, param1: str, **kwargs) -> ToolResult:
        # 实现工具逻辑
        return ToolResult(success=True, data={"result": param1})
```

### 3.2 ToolResult（工具执行结果）

```python
@dataclass
class ToolResult:
    success: bool      # 执行是否成功
    data: Any = None   # 返回数据（成功时）
    error: str = None  # 错误信息（失败时）
```

### 3.3 ToolRegistry（工具注册中心）

管理所有工具的注册、发现和执行。

**核心方法**：

```python
class ToolRegistry:
    def auto_discover(self, tools_dir=None):
        """自动扫描tools/目录，注册所有Tool"""
        ...

    def register(self, tool):
        """注册工具"""
        ...

    def get(self, name) -> Optional[Tool]:
        """获取工具"""
        ...

    def list_tools(self) -> list[str]:
        """列出所有工具"""
        ...

    async def call(self, name, args, agent_permissions) -> ToolResult:
        """调用工具，检查权限后执行"""
        ...

    def get_tool_info(self, name) -> dict:
        """获取工具信息"""
        ...
```

**使用示例**：

```python
from tools.registry import ToolRegistry

# 创建注册中心
registry = ToolRegistry()

# 自动发现工具
registry.auto_discover()

# 列出所有工具
print(registry.list_tools())

# 调用工具
result = await registry.call(
    "read_file",
    {"file_path": "test.txt"},
    {"read": "allow"}
)
```

---

## 四、内置工具详细定义

### 4.1 read_file

读取指定路径的文件内容。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 文件路径 |

**返回**：文件内容文本

**示例**：

```python
result = await registry.call(
    "read_file",
    {"file_path": "src/main.py"},
    {"read": "allow"}
)
```

### 4.2 write_file

写入或创建文件。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 文件路径 |
| content | string | 是 | 文件内容 |

**返回**：写入成功/失败

**示例**：

```python
result = await registry.call(
    "write_file",
    {"file_path": "output.txt", "content": "Hello World"},
    {"write": "allow"}
)
```

### 4.3 list_directory

列出目录结构。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| path | string | 是 | 目录路径 |
| depth | integer | 否 | 递归深度，默认1 |

**返回**：目录树文本

**示例**：

```python
result = await registry.call(
    "list_directory",
    {"dir_path": "src", "recursive": True},
    {"read": "allow"}
)
```

### 4.4 search_project

全文搜索项目文件。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 搜索关键词 |
| file_pattern | string | 否 | 文件模式过滤，默认"*" |

**返回**：匹配结果列表

**示例**：

```python
result = await registry.call(
    "search_project",
    {"query": "def login", "file_pattern": "*.py"},
    {"read": "allow"}
)
```

### 4.5 search_knowledge

搜索RAG知识库。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 搜索查询 |
| top_k | integer | 否 | 返回结果数量，默认5 |

**返回**：相关文档片段

**示例**：

```python
result = await registry.call(
    "search_knowledge",
    {"query": "JWT认证"},
    {"read": "allow"}
)
```

### 4.6 create_task

创建新任务。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 任务标题 |
| description | string | 否 | 任务描述 |

**返回**：任务ID

**示例**：

```python
result = await registry.call(
    "create_task",
    {"title": "实现登录功能", "priority": "high"},
    {"write": "allow"}
)
```

### 4.7 update_memory

写入或更新Memory。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| layer | string | 是 | Memory层级：global/project/task/session/checkpoint |
| content | string | 是 | Memory内容 |

**返回**：更新成功/失败

**示例**：

```python
result = await registry.call(
    "update_memory",
    {"key": "login_rule", "value": "使用JWT认证", "memory_type": "project"},
    {"write": "allow"}
)
```

### 4.8 finish_task

标记任务完成。

**参数**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |
| summary | string | 否 | 完成摘要 |

**返回**：完成成功/失败

**示例**：

```python
result = await registry.call(
    "finish_task",
    {"task_id": "task_123", "result": "已完成"},
    {"write": "allow"}
)
```

---

## 五、权限系统

工具权限与Agent权限配合使用：

| 权限 | 说明 | 典型用途 |
|------|------|---------|
| read | 读取权限 | 读取文件、搜索、列出目录 |
| edit/write | 写入权限 | 写入文件、创建任务、更新Memory |
| bash | 执行权限 | 执行Shell命令 |
| todowrite | 任务写入权限 | 创建任务、完成任务 |

**权限检查流程**：

```
Agent调用Tool → ToolRegistry检查权限 → 权限通过 → 执行工具
                                    → 权限不足 → 返回错误
```

1. Agent调用工具时，传入Agent的权限配置
2. ToolRegistry检查工具所需权限
3. 如果Agent有该权限且为allow，则允许执行
4. 否则返回权限拒绝错误

---

## 六、参数定义文件

工具参数通过JSON Schema定义：

```
tools/
├── read_file.json
├── write_file.json
├── list_directory.json
├── search_project.json
├── search_knowledge.json
├── create_task.json
├── update_memory.json
└── finish_task.json
```

**JSON Schema示例**：

```json
{
  "name": "read_file",
  "description": "读取指定路径的文件内容",
  "permission": "read",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "文件路径"
      }
    },
    "required": ["path"]
  }
}
```

---

## 七、使用流程

### 7.1 初始化

```python
from tools.registry import ToolRegistry

# 创建注册中心
registry = ToolRegistry()

# 自动发现工具
registry.auto_discover()
```

### 7.2 注入到AgentManager

```python
from agents.manager import AgentManager

# 创建Agent管理器
manager = AgentManager(llm_client=llm)

# 注入ToolRegistry
manager.set_tool_registry(registry)
```

### 7.3 Agent调用工具

```python
from agents.base import BaseAgent, PipelineState

class MyAgent(BaseAgent):
    name = "my-agent"

    async def run(self, state: PipelineState) -> PipelineState:
        # 调用读取文件工具
        result = await self.call_tool("read_file", {"file_path": "config.json"})

        if result.success:
            # 处理文件内容
            content = result.data
            # ...

        return state
```

---

## 八、文件结构

```
backend/tools/
├── __init__.py          # 模块导出
├── base.py              # Tool基类和ToolResult
├── registry.py          # ToolRegistry注册中心
└── builtins/            # 内置工具实现
    ├── __init__.py
    ├── read_file.py
    ├── write_file.py
    ├── list_directory.py
    ├── search_project.py
    ├── search_knowledge.py
    ├── create_task.py
    ├── update_memory.py
    └── finish_task.py
```

---

## 九、测试

```bash
cd backend
pytest tests/test_tools.py -v
```

测试覆盖：
- ToolResult 创建和使用
- Tool 基类
- 所有工具的执行
- ToolRegistry的注册、获取、调用
- 权限检查

---

## 作者

成员C（wang123456-123456）- AI开发工程师B（Agent编排方向）

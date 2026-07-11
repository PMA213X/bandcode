# Tool 系统

## 概述

Tool 系统是 BandCode 项目的工具模块，负责提供各种工具供 Agent 使用。所有 Tool 都继承自 `Tool` 基类，通过 `ToolRegistry` 进行统一管理。

## 架构

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

## 核心组件

### 1. Tool 基类

所有工具的基类，提供统一接口。

**属性：**
- `name`: 工具名称
- `description`: 工具描述
- `permission`: 所需权限（read, write, bash, admin）
- `parameters`: 参数定义（JSON Schema格式）

**方法：**
- `execute(**kwargs)`: 执行工具（抽象方法）
- `validate_params(**kwargs)`: 验证参数
- `get_schema()`: 获取工具Schema

**示例：**
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

### 2. ToolRegistry 注册中心

管理所有工具的注册、发现和执行。

**方法：**
- `auto_discover(tools_dir)`: 自动扫描目录，注册所有工具
- `register(tool)`: 注册工具
- `get(name)`: 获取工具实例
- `list_tools()`: 列出所有工具
- `call(name, args, agent_permissions)`: 调用工具
- `get_tool_info(name)`: 获取工具信息

**示例：**
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

### 3. ToolResult 结果

工具执行结果。

**属性：**
- `success`: 执行是否成功
- `data`: 返回数据（成功时）
- `error`: 错误信息（失败时）
- `execution_time`: 执行时间（秒）

## 工具类型

### 1. ReadFileTool (读取文件)

**功能：** 读取指定文件的内容

**参数：**
- `file_path` (string, required): 文件路径
- `encoding` (string, optional): 文件编码，默认utf-8

**权限：** read

**示例：**
```python
result = await registry.call(
    "read_file",
    {"file_path": "src/main.py"},
    {"read": "allow"}
)
```

### 2. WriteFileTool (写入文件)

**功能：** 写入或创建文件

**参数：**
- `file_path` (string, required): 文件路径
- `content` (string, required): 文件内容
- `encoding` (string, optional): 文件编码，默认utf-8
- `create_dirs` (boolean, optional): 是否自动创建目录，默认true

**权限：** write

**示例：**
```python
result = await registry.call(
    "write_file",
    {"file_path": "output.txt", "content": "Hello World"},
    {"write": "allow"}
)
```

### 3. ListDirectoryTool (列出目录)

**功能：** 列出目录中的文件和子目录

**参数：**
- `dir_path` (string, required): 目录路径
- `recursive` (boolean, optional): 是否递归列出，默认false
- `max_depth` (integer, optional): 最大递归深度，默认3

**权限：** read

**示例：**
```python
result = await registry.call(
    "list_directory",
    {"dir_path": "src", "recursive": True},
    {"read": "allow"}
)
```

### 4. SearchProjectTool (搜索项目)

**功能：** 在项目中搜索指定内容

**参数：**
- `query` (string, required): 搜索关键词
- `directory` (string, optional): 搜索目录，默认当前目录
- `file_pattern` (string, optional): 文件匹配模式，默认*
- `max_results` (integer, optional): 最大结果数，默认50

**权限：** read

**示例：**
```python
result = await registry.call(
    "search_project",
    {"query": "def login", "file_pattern": "*.py"},
    {"read": "allow"}
)
```

### 5. CreateTaskTool (创建任务)

**功能：** 创建新的任务

**参数：**
- `title` (string, required): 任务标题
- `description` (string, optional): 任务描述
- `priority` (string, optional): 优先级（low/medium/high）
- `assigned_to` (string, optional): 分配给谁

**权限：** write

**示例：**
```python
result = await registry.call(
    "create_task",
    {"title": "实现登录功能", "priority": "high"},
    {"write": "allow"}
)
```

### 6. FinishTaskTool (完成任务)

**功能：** 标记任务完成

**参数：**
- `task_id` (string, required): 任务ID
- `result` (string, optional): 任务结果

**权限：** write

**示例：**
```python
result = await registry.call(
    "finish_task",
    {"task_id": "task_123", "result": "已完成"},
    {"write": "allow"}
)
```

### 7. SearchKnowledgeTool (搜索知识库)

**功能：** 在知识库中搜索相关内容

**参数：**
- `query` (string, required): 搜索关键词
- `knowledge_path` (string, optional): 知识库路径，默认knowledge
- `max_results` (integer, optional): 最大结果数，默认10

**权限：** read

**示例：**
```python
result = await registry.call(
    "search_knowledge",
    {"query": "JWT认证"},
    {"read": "allow"}
)
```

### 8. UpdateMemoryTool (更新Memory)

**功能：** 写入或更新Memory

**参数：**
- `key` (string, required): Memory键
- `value` (string, required): Memory值
- `memory_type` (string, optional): Memory类型（global/project/task/session）

**权限：** write

**示例：**
```python
result = await registry.call(
    "update_memory",
    {"key": "login_rule", "value": "使用JWT认证", "memory_type": "project"},
    {"write": "allow"}
)
```

## 权限系统

工具权限与Agent权限配合使用：

| 权限 | 说明 | 典型用途 |
|------|------|---------|
| read | 读取权限 | 读取文件、搜索、列出目录 |
| write | 写入权限 | 写入文件、创建任务、更新Memory |
| bash | 执行权限 | 执行Shell命令 |
| admin | 管理权限 | 管理操作 |

**权限检查流程：**
1. Agent调用工具时，传入Agent的权限配置
2. ToolRegistry检查工具所需权限
3. 如果Agent有该权限且为allow，则允许执行
4. 否则返回权限拒绝错误

## 使用流程

### 1. 初始化

```python
from tools.registry import ToolRegistry

# 创建注册中心
registry = ToolRegistry()

# 自动发现工具
registry.auto_discover()
```

### 2. 注入到AgentManager

```python
from agents.manager import AgentManager

# 创建Agent管理器
manager = AgentManager(llm_client=llm)

# 注入ToolRegistry
manager.set_tool_registry(registry)
```

### 3. Agent调用工具

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

## 测试

运行单元测试：
```bash
python -m pytest tests/test_tools.py -v
```

测试覆盖：
- ToolResult 创建和使用
- Tool 基类
- 所有工具的执行
- ToolRegistry的注册、获取、调用
- 权限检查

## 作者

成员C（wang123456-123456）- AI开发工程师B（Agent编排方向）

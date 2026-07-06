# 成员D — 后端开发工程师A（框架与通信方向）开发规划

> 角色：后端开发工程师
> 核心职责：FastAPI 框架搭建、API 路由实现、SSE 流式输出、配置管理
> 分支：feature/backend-api

---

## 一、角色定位

成员D 负责后端服务的「骨架与通信」：

- FastAPI 应用框架搭建
- 8个 RESTful API 路由实现
- SSE (Server-Sent Events) 流式推送机制
- 配置文件加载与管理
- 中间件、CORS、错误处理

---

## 二、开发任务清单

### Phase 0：环境准备（第1天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| D-01 | 克隆仓库 | — | git clone + 切换到 feature/backend-api 分支 |
| D-02 | 创建Python环境 | — | python -m venv venv |
| D-03 | 安装依赖 | `requirements.txt` | fastapi、uvicorn、sse-starlette |
| D-04 | 验证FastAPI | — | 测试FastAPI基本运行 |

### Phase 1：框架搭建（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| D-05 | FastAPI入口 | `main.py` | 创建FastAPI应用、注册路由、配置CORS |
| D-06 | 配置加载 | `config/loader.py` | settings.json读写、项目config.json合并 |
| D-07 | config模块初始化 | `config/__init__.py` | 模块导出 |
| D-08 | SSE封装 | `api/sse.py` | SSE事件推送封装、事件类型定义 |
| D-09 | API模块初始化 | `api/__init__.py` | 路由注册 |
| D-10 | 框架测试 | `tests/test_main.py` | 测试FastAPI启动和基本路由 |

### Phase 1：API路由实现（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| D-11 | 用户API | `api/users.py` | POST /api/users/create |
| D-12 | 聊天API | `api/chat.py` | POST /api/chat/stream (SSE) + GET /api/chat/history |
| D-13 | 设置API | `api/settings.py` | GET/POST /api/settings |
| D-14 | Memory API | `api/memory.py` | GET /api/memory |
| D-15 | 项目API | `api/project.py` | POST /api/project/init |
| D-16 | 工具API | `api/tools.py` | POST /api/tools/call |
| D-17 | API测试 | `tests/test_api.py` | 所有API接口测试 |

### Phase 2：SSE完善（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| D-18 | SSE事件类型完善 | `api/sse.py` | agent_start/plan/code/test_result/done等 |
| D-19 | SSE连接管理 | — | 连接池、心跳、断线重连 |
| D-20 | SSE集成测试 | — | 测试完整SSE流程 |

### Phase 3：完善与优化（第9-11天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| D-21 | 错误处理 | — | 全局异常处理、错误码定义 |
| D-22 | 请求校验 | — | Pydantic模型校验 |
| D-23 | 日志系统 | — | 结构化日志 |
| D-24 | API文档 | — | OpenAPI文档完善 |

### Phase 4-5：联调与优化（第12-16天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| D-25 | 前后端联调 | — | 配合前端调试所有接口 |
| D-26 | 性能优化 | — | 异步优化、连接池 |
| D-27 | 安全加固 | — | 输入校验、SQL注入防护 |

---

## 三、技术要点

### 3.1 FastAPI入口

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BandCode", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from api.chat import router as chat_router
from api.settings import router as settings_router
# ...

app.include_router(chat_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
```

### 3.2 SSE流式输出

```python
# api/sse.py
from sse_starlette.sse import EventSourceResponse

async def sse_generator(event_queue: asyncio.Queue):
    """SSE事件生成器"""
    while True:
        event = await event_queue.get()
        if event is None:
            break
        yield {
            "event": event["type"],
            "data": json.dumps(event["data"], ensure_ascii=False)
        }

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    event_queue = asyncio.Queue()

    # 启动后台任务处理Agent工作流
    asyncio.create_task(process_chat(request, event_queue))

    return EventSourceResponse(sse_generator(event_queue))
```

### 3.3 SSE事件类型

```python
# api/sse.py
class SSEEventType:
    AGENT_START = "agent_start"          # Agent开始执行
    CONSTRAINT_RESULT = "constraint_result"  # 约束检索结果
    PLAN = "plan"                        # Planner输出计划
    APPROVAL_REQUIRED = "approval_required"  # 需要审批
    APPROVAL_RESPONSE = "approval_response"  # 审批响应
    TOOL_CALL = "tool_call"              # Tool调用
    CODE = "code"                        # 代码生成
    TEST_RESULT = "test_result"          # 测试结果
    REVIEW_RESULT = "review_result"      # 审查结果
    MEMORY_UPDATE = "memory_update"      # Memory更新
    DONE = "done"                        # 完成
    ERROR = "error"                      # 错误
```

### 3.4 配置加载

```python
# config/loader.py
import json
from pathlib import Path

class ConfigLoader:
    """配置加载器"""

    def __init__(self, settings_path: str = "settings.json"):
        self.settings_path = Path(settings_path)
        self.settings = self.load_settings()

    def load_settings(self) -> dict:
        """加载全局设置"""
        if self.settings_path.exists():
            return json.loads(self.settings_path.read_text(encoding="utf-8"))
        return self.get_default_settings()

    def get(self, section: str, key: str, default=None):
        """获取配置项"""
        return self.settings.get(section, {}).get(key, default)

    def update(self, section: str, key: str, value):
        """更新配置项"""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save()

    def save(self):
        """保存配置"""
        self.settings_path.write_text(
            json.dumps(self.settings, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
```

---

## 四、AI Agent 使用指南

### 4.1 推荐配置

| 任务类型 | Agent | 模型 | 理由 |
|---------|-------|------|------|
| FastAPI框架搭建 | general | mimo-v2.5-pro | 框架搭建需要Pro模型 |
| SSE机制实现 | general | mimo-v2.5-pro | 异步流式处理较复杂 |
| API路由实现 | general | mimo-v2.5 | CRUD接口相对标准 |
| 配置加载 | general | mimo-v2.5 | JSON读写简单 |
| API测试 | general | mimo-v2.5 | 测试代码 |
| 代码探索 | explore | mimo-v2.5 | 查找相关模块 |

### 4.2 使用示例

**搭建FastAPI框架时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 main.py，搭建FastAPI应用框架。
要求：
1. 创建FastAPI应用实例
2. 配置CORS中间件
3. 注册所有API路由
4. 配置静态文件服务
5. 添加全局异常处理
参考文件：doc1.md 第2.3节后端业务层设计
```

**实现SSE机制时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 api/sse.py，封装SSE事件推送机制。
要求：
1. 定义所有SSE事件类型
2. 实现SSE事件生成器
3. 支持异步队列推送
4. 处理连接断开
参考文件：doc1.md 第4.2节接口2的SSE响应格式
```

**实现API路由时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：实现 api/chat.py，包含聊天相关接口。
要求：
1. POST /api/chat/stream - 流式聊天（SSE）
2. GET /api/chat/history - 获取聊天历史
3. 使用Pydantic模型校验请求
4. 返回统一格式 {code, data, message}
参考文件：doc1.md 第4.2节接口2和接口3定义
```

---

## 五、文件所有权

### 5.1 主责文件

```
main.py                         ← 主责
requirements.txt                ← 主责
config/__init__.py              ← 创建
config/loader.py                ← 主责
api/__init__.py                 ← 创建
api/sse.py                      ← 主责
api/chat.py                     ← 主责
api/settings.py                 ← 主责
api/memory.py                   ← 主责
api/project.py                  ← 主责
api/tools.py                    ← 主责
api/users.py                    ← 主责
tests/test_main.py              ← 主责
tests/test_api.py               ← 主责
```

### 5.2 协作文件

| 文件 | 协作人 | 协作内容 |
|------|--------|---------|
| database/models.py | 成员E | 数据库表结构 |
| database/crud.py | 成员E | CRUD操作 |
| agents/manager.py | 成员C | Agent调用入口 |
| workflow/pipeline.py | 成员E | 工作流调用 |

---

## 六、接口依赖

### 6.1 我依赖的接口

| 依赖方 | 依赖内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员E | database/models.py | Phase 1 | 数据库表结构 |
| 成员E | database/crud.py | Phase 1 | CRUD操作 |
| 成员E | memory/store.py | Phase 2 | Memory读写 |
| 成员C | agents/manager.py | Phase 1 | Agent调用入口 |
| 成员E | workflow/pipeline.py | Phase 2 | 工作流调用 |

### 6.2 我提供的接口

| 接收方 | 提供内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员F | API接口定义 | Phase 1 | 8个接口的请求/响应格式 |
| 成员G | API接口定义 | Phase 1 | 8个接口的请求/响应格式 |
| 成员G | SSE事件格式 | Phase 1 | SSE事件类型和数据结构 |
| 全员 | config/loader.py | Phase 1 | 配置加载 |

---

## 七、交付物清单

| 阶段 | 交付物 | 验收标准 |
|------|--------|---------|
| Phase 0 | 环境就绪 | FastAPI可正常启动 |
| Phase 1 | FastAPI框架、8个API路由、配置加载 | 所有API可访问，返回正确格式 |
| Phase 2 | SSE完整实现 | 流式推送正常工作 |
| Phase 3 | 错误处理、日志、文档 | 系统健壮性提升 |
| Phase 4 | 联调通过 | 前后端完整交互 |
| Phase 5 | 性能优化完成 | API响应时间<200ms |

---

## 八、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| SSE兼容性问题 | 流式输出异常 | 准备WebSocket备选方案 |
| 并发性能不足 | 响应延迟 | 使用uvicorn多worker |
| 接口格式不一致 | 联调困难 | 先定义OpenAPI文档 |
| 依赖模块未完成 | 开发受阻 | Mock依赖接口，先测试框架 |

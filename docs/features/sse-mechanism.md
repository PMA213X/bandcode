# SSE 机制文档

> 模块：backend/api/sse.py  
> 负责人：成员D（后端-A）  
> 最后更新：2026-07-10

---

## 一、概述

Server-Sent Events (SSE) 是一种服务器向客户端推送数据的技术。BandCode 使用 SSE 实现实时状态更新和流式响应。

### 技术对比

| 特性 | SSE | WebSocket |
|------|-----|-----------|
| 方向 | 单向（服务器→客户端） | 双向 |
| 协议 | HTTP | WS/WSS |
| 复杂度 | 简单 | 复杂 |
| 适用场景 | 状态推送、日志流 | 实时交互 |

---

## 二、事件类型

BandCode 定义了 12 种 SSE 事件类型：

| 事件类型 | 说明 | 触发时机 |
|----------|------|----------|
| agent_start | Agent 开始执行 | Agent 启动时 |
| constraint_result | 约束检索结果 | Constraint Agent 完成检索 |
| plan | Planner 输出计划 | Planner Agent 生成计划 |
| approval_required | 需要审批 | 高风险操作前 |
| approval_response | 审批响应 | 用户确认后 |
| tool_call | Tool 调用 | Agent 调用工具 |
| code | 代码生成 | Agent 生成代码 |
| test_result | 测试结果 | Tester Agent 完成测试 |
| review_result | 审查结果 | Review Agent 完成审查 |
| memory_update | Memory 更新 | Memory 系统更新 |
| done | 完成 | 任务完成 |
| error | 错误 | 发生错误 |

---

## 三、连接管理

### 连接池

```python
class ConnectionManager:
    """SSE 连接管理器"""
    
    def __init__(self):
        self.connections: Dict[str, SSEConnection] = {}
    
    def create_connection(self, session_id: str) -> SSEConnection:
        """创建新连接"""
        ...
    
    def remove_connection(self, connection_id: str) -> None:
        """移除连接"""
        ...
```

### 心跳机制

连接管理器支持心跳检测，用于：
- 检测连接是否存活
- 清理无效连接
- 统计活跃连接数

---

## 四、事件推送

### 推送函数

```python
async def push_agent_start(event_queue, agent, status):
    """推送 Agent 开始事件"""
    data = AgentStartEvent(agent=agent, status=status).model_dump()
    await push_event(event_queue, SSEEventType.AGENT_START, data)

async def push_code(event_queue, file, content):
    """推送代码生成事件"""
    data = CodeEvent(file=file, content=content).model_dump()
    await push_event(event_queue, SSEEventType.CODE, data)

async def push_done(event_queue, session_id, summary):
    """推送完成事件"""
    data = DoneEvent(session_id=session_id, summary=summary).model_dump()
    await push_event(event_queue, SSEEventType.DONE, data)
    await event_queue.put(None)  # 结束信号
```

---

## 五、事件生成器

```python
async def sse_generator(event_queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """
    SSE 事件生成器
    
    从队列中读取事件并生成 SSE 格式的响应
    """
    while True:
        event = await event_queue.get()
        if event is None:
            break
        yield f"event: {event.event_type}\ndata: {json.dumps(event.data)}\n\n"
```

---

## 六、前端消费

```typescript
// 前端 SSE Hook
const eventSource = new EventSource('/api/chat/stream?...');

// 监听所有事件类型
SSE_EVENT_TYPES.forEach((type) => {
  eventSource.addEventListener(type, (e: MessageEvent) => {
    const data = JSON.parse(e.data);
    // 处理事件...
  });
});
```

---

## 七、相关文件

- `backend/api/sse.py` - SSE 事件封装
- `backend/api/chat.py` - 聊天接口（使用 SSE）
- `frontend/src/hooks/useSSE.ts` - 前端 SSE Hook
- `frontend/src/types/api.ts` - 事件类型定义

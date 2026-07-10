"""
SSE (Server-Sent Events) 事件推送封装
定义事件类型和事件生成器
"""
import json
import asyncio
from typing import AsyncGenerator, Any


class SSEEventType:
    """SSE 事件类型定义"""

    AGENT_START = "agent_start"  # Agent 开始执行
    CONSTRAINT_RESULT = "constraint_result"  # 约束检索结果
    PLAN = "plan"  # Planner 输出计划
    APPROVAL_REQUIRED = "approval_required"  # 需要审批
    APPROVAL_RESPONSE = "approval_response"  # 审批响应
    TOOL_CALL = "tool_call"  # Tool 调用
    CODE = "code"  # 代码生成
    TEST_RESULT = "test_result"  # 测试结果
    REVIEW_RESULT = "review_result"  # 审查结果
    MEMORY_UPDATE = "memory_update"  # Memory 更新
    DONE = "done"  # 完成
    ERROR = "error"  # 错误


class SSEEvent:
    """SSE 事件对象"""

    def __init__(self, event_type: str, data: Any):
        self.event_type = event_type
        self.data = data

    def to_dict(self) -> dict:
        return {"event": self.event_type, "data": self.data}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


async def sse_generator(event_queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """
    SSE 事件生成器
    从队列中读取事件并生成 SSE 格式的响应
    """
    while True:
        event = await event_queue.get()
        if event is None:
            break
        yield f"event: {event.event_type}\ndata: {json.dumps(event.data, ensure_ascii=False)}\n\n"


async def push_event(
    event_queue: asyncio.Queue, event_type: str, data: Any
) -> None:
    """推送事件到队列"""
    event = SSEEvent(event_type, data)
    await event_queue.put(event)


async def push_agent_start(
    event_queue: asyncio.Queue, agent_name: str, task: str
) -> None:
    """推送 Agent 开始事件"""
    await push_event(
        event_queue,
        SSEEventType.AGENT_START,
        {"agent": agent_name, "task": task, "status": "running"},
    )


async def push_plan(event_queue: asyncio.Queue, plan: dict) -> None:
    """推送计划事件"""
    await push_event(event_queue, SSEEventType.PLAN, plan)


async def push_code(
    event_queue: asyncio.Queue, file_path: str, content: str
) -> None:
    """推送代码生成事件"""
    await push_event(
        event_queue, SSEEventType.CODE, {"file": file_path, "content": content}
    )


async def push_test_result(
    event_queue: asyncio.Queue, result: dict
) -> None:
    """推送测试结果事件"""
    await push_event(event_queue, SSEEventType.TEST_RESULT, result)


async def push_done(event_queue: asyncio.Queue, message: str) -> None:
    """推送完成事件"""
    await push_event(event_queue, SSEEventType.DONE, {"message": message})
    await event_queue.put(None)  # 结束信号


async def push_error(event_queue: asyncio.Queue, error: str) -> None:
    """推送错误事件"""
    await push_event(event_queue, SSEEventType.ERROR, {"error": error})
    await event_queue.put(None)  # 结束信号

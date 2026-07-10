"""
聊天 API
GET /api/chat/stream - 流式聊天（SSE）
GET /api/chat/history - 获取聊天历史
"""
import asyncio
import json
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from sse_starlette.sse import EventSourceResponse
from api.sse import (
    SSEEventType,
    sse_generator,
    push_agent_start,
    push_constraint_result,
    push_plan,
    push_tool_call,
    push_code,
    push_test_result,
    push_review_result,
    push_memory_update,
    push_done,
    push_error,
)

router = APIRouter(prefix="/chat", tags=["聊天"])


class ChatStreamRequest(BaseModel):
    """聊天流式请求"""

    session_id: str
    project: str
    message: str
    options: Optional[dict] = None


class ChatMessage(BaseModel):
    """聊天消息"""

    id: int
    role: str  # user / assistant
    agent: Optional[str] = None
    content: str
    created_at: str


# 临时存储（后续会对接数据库）
chat_history: dict[str, List[dict]] = {}


async def process_chat(
    session_id: str, project: str, message: str, event_queue: asyncio.Queue
):
    """处理聊天请求（模拟 Agent 工作流）"""
    try:
        # 1. 推送 Agent 开始事件
        await push_agent_start(event_queue, "constraint", "running")

        # 模拟约束检索
        await asyncio.sleep(0.3)
        await push_constraint_result(
            event_queue,
            constraints=["代码必须使用中文注释", "API 返回统一格式 {code, data, message}"],
            summary="找到 2 条相关约束",
        )

        # 2. 推送 Planner 开始
        await push_agent_start(event_queue, "planner", "running")
        await asyncio.sleep(0.3)

        # 3. 推送计划事件
        await push_plan(
            event_queue,
            tasks=["分析用户需求", "检索相关约束", "生成代码方案", "执行代码生成"],
            delegated_agent="complex_coder",
        )

        # 4. 推送 ComplexCoder 开始
        await push_agent_start(event_queue, "complex_coder", "running")
        await asyncio.sleep(0.5)

        # 5. 推送 Tool 调用
        await push_tool_call(event_queue, "write_file", {"path": "output.py"})

        # 6. 推送代码生成
        await push_code(
            event_queue,
            file="output.py",
            content=f"# 处理消息: {message}\nprint('Hello from BandCode!')",
        )

        # 7. 推送 Tester 开始
        await push_agent_start(event_queue, "tester", "running")
        await asyncio.sleep(0.3)

        # 8. 推送测试结果
        await push_test_result(
            event_queue, status="passed", tests_total=1, tests_passed=1
        )

        # 9. 推送 Review 结果
        await push_review_result(event_queue, status="passed", violations=[])

        # 10. 推送 Memory 更新
        await push_memory_update(
            event_queue, layers=["session", "checkpoint"], message="已更新会话记忆"
        )

        # 11. 推送完成事件
        await push_done(event_queue, session_id, f"已处理消息：{message}")

        # 保存到历史
        if session_id not in chat_history:
            chat_history[session_id] = []

        chat_history[session_id].append(
            {
                "id": len(chat_history[session_id]),
                "role": "user",
                "content": message,
                "created_at": "2026-07-10T08:55:00",
            }
        )
        chat_history[session_id].append(
            {
                "id": len(chat_history[session_id]),
                "role": "assistant",
                "agent": "complex_coder",
                "content": f"已处理：{message}",
                "created_at": "2026-07-10T08:55:01",
            }
        )

    except Exception as e:
        await push_error(event_queue, str(e))


@router.get("/stream")
async def chat_stream(
    session_id: str = Query(..., description="会话ID"),
    project: str = Query(..., description="项目名称"),
    message: str = Query(..., description="用户消息"),
):
    """
    流式聊天接口（SSE）
    前端通过 GET 请求，参数通过 URL 查询字符串传递
    """
    event_queue: asyncio.Queue = asyncio.Queue()

    # 启动后台任务处理 Agent 工作流
    asyncio.create_task(process_chat(session_id, project, message, event_queue))

    return EventSourceResponse(sse_generator(event_queue))


@router.get("/history")
async def get_chat_history(
    session_id: str = Query("default", description="会话ID"),
    limit: int = Query(50, description="返回数量"),
    offset: int = Query(0, description="偏移量"),
):
    """
    获取聊天历史
    """
    history = chat_history.get(session_id, [])
    total = len(history)
    paginated = history[offset : offset + limit]
    has_more = offset + limit < total

    return {
        "code": 0,
        "data": {
            "session_id": session_id,
            "messages": paginated,
            "total": total,
            "has_more": has_more,
        },
        "message": "ok",
    }

"""
聊天 API
POST /api/chat/stream - 流式聊天（SSE）
GET /api/chat/history - 获取聊天历史
"""
import asyncio
import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from sse_starlette.sse import EventSourceResponse
from api.sse import (
    SSEEventType,
    sse_generator,
    push_agent_start,
    push_plan,
    push_done,
    push_error,
)

router = APIRouter(prefix="/chat", tags=["聊天"])


class ChatRequest(BaseModel):
    """聊天请求"""

    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatMessage(BaseModel):
    """聊天消息"""

    id: str
    role: str  # user / assistant
    content: str
    timestamp: str


# 临时存储（后续会对接数据库）
chat_history: dict[str, List[dict]] = {}


async def process_chat(request: ChatRequest, event_queue: asyncio.Queue):
    """处理聊天请求（模拟 Agent 工作流）"""
    try:
        # 1. 推送 Agent 开始事件
        await push_agent_start(event_queue, "planner", "分析用户需求")

        # 模拟处理延迟
        await asyncio.sleep(0.5)

        # 2. 推送计划事件
        await push_plan(
            event_queue,
            {
                "steps": [
                    "分析用户需求",
                    "检索相关约束",
                    "生成代码方案",
                    "执行代码生成",
                ]
            },
        )

        await asyncio.sleep(0.5)

        # 3. 模拟代码生成
        await push_agent_start(event_queue, "complex_coder", "生成代码")

        # 4. 推送完成事件
        await push_done(event_queue, f"已处理消息：{request.message}")

        # 保存到历史
        session_id = request.session_id or "default"
        if session_id not in chat_history:
            chat_history[session_id] = []

        chat_history[session_id].append(
            {"role": "user", "content": request.message, "id": f"msg_{len(chat_history[session_id])}"}
        )
        chat_history[session_id].append(
            {
                "role": "assistant",
                "content": f"已处理：{request.message}",
                "id": f"msg_{len(chat_history[session_id])}",
            }
        )

    except Exception as e:
        await push_error(event_queue, str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    流式聊天接口（SSE）
    """
    event_queue: asyncio.Queue = asyncio.Queue()

    # 启动后台任务处理 Agent 工作流
    asyncio.create_task(process_chat(request, event_queue))

    return EventSourceResponse(sse_generator(event_queue))


@router.get("/history")
async def get_chat_history(session_id: str = "default"):
    """
    获取聊天历史
    """
    history = chat_history.get(session_id, [])
    return {"code": 0, "data": history, "message": "ok"}

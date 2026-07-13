"""
聊天 API 模块

本模块实现了聊天相关的 API 接口，包括：
1. 流式聊天接口（SSE） - 通过 Server-Sent Events 实现实时流式响应
2. 聊天历史接口 - 获取指定会话的聊天记录

聊天流程：
1. 用户发送消息
2. 后端启动 Agent 工作流
3. 通过 SSE 实时推送 Agent 执行状态
4. 前端实时显示执行进度
"""

# 导入异步编程模块
import asyncio
# 导入 JSON 序列化模块
import json
# 导入日志模块
import logging
# 导入时间模块
from datetime import datetime
# 导入 FastAPI 路由和查询参数
from fastapi import APIRouter, Query
# 导入 Pydantic 数据验证模型
from pydantic import BaseModel
# 导入类型注解
from typing import Optional, List
# 导入 SSE 响应类
from sse_starlette.sse import EventSourceResponse
# 导入自定义 SSE 事件推送函数
from api.sse import (
    SSEEventType,  # SSE 事件类型
    sse_generator,  # SSE 事件生成器
    push_agent_start,  # 推送 Agent 开始事件
    push_constraint_result,  # 推送约束检索结果
    push_plan,  # 推送计划事件
    push_tool_call,  # 推送工具调用事件
    push_code,  # 推送代码生成事件
    push_test_result,  # 推送测试结果事件
    push_review_result,  # 推送审查结果事件
    push_memory_update,  # 推送 Memory 更新事件
    push_text,  # 推送 LLM 流式文本事件
    push_done,  # 推送完成事件
    push_error,  # 推送错误事件
)
# 导入 Memory Manager
from memory.manager import MemoryManager
# 导入配置加载器
from config.loader import get_config
# 导入 LLM 客户端
from models.llm import LLMClient

logger = logging.getLogger("bandcode.chat")

# 创建路由器，prefix="/chat" 表示所有路由以 /chat 开头
# tags=["聊天"] 用于 API 文档分组
router = APIRouter(prefix="/chat", tags=["聊天"])

# 全局 MemoryManager 实例
memory_manager = MemoryManager()


class ChatStreamRequest(BaseModel):
    """
    聊天流式请求模型
    
    定义了流式聊天接口的请求参数
    注意：实际使用的是 GET 请求，参数通过 URL 查询字符串传递
    """
    session_id: str  # 会话 ID，用于标识一个聊天会话
    project: str  # 项目名称
    message: str  # 用户发送的消息
    options: Optional[dict] = None  # 可选参数，如指定 Agent、工作流等


class ChatMessage(BaseModel):
    """
    聊天消息模型
    
    定义了单条聊天消息的数据结构
    """
    id: int  # 消息 ID
    role: str  # 消息角色: "user"（用户）或 "assistant"（助手）
    agent: Optional[str] = None  # 处理消息的 Agent 名称
    content: str  # 消息内容
    created_at: str  # 创建时间


# 临时存储聊天历史（后续会对接数据库）
# key 为 session_id，value 为消息列表
chat_history: dict[str, List[dict]] = {}


def _build_llm_client(agent_name: str = "default") -> LLMClient:
    """根据配置构建 LLM 客户端"""
    config = get_config()
    model_settings = config.get_section("模型设置")
    base_url = model_settings.get("Base URL", "")
    api_key = model_settings.get("API Key", "")

    model_map = {
        "planner": model_settings.get("Planner 模型", model_settings.get("默认模型", "")),
        "complex_coder": model_settings.get("ComplexCoder 模型", model_settings.get("默认模型", "")),
        "simple_coder": model_settings.get("SimpleCoder 模型", model_settings.get("默认模型", "")),
        "tester": model_settings.get("Tester 模型", model_settings.get("默认模型", "")),
        "default": model_settings.get("默认模型", ""),
    }
    model = model_map.get(agent_name, model_map["default"])

    return LLMClient(base_url=base_url, api_key=api_key, model=model)


def _get_chat_history_messages(session_id: str) -> List[dict]:
    """将会话历史转换为 LLM 消息格式"""
    history = chat_history.get(session_id, [])
    messages = []
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    return messages


async def process_chat(
    session_id: str, project: str, message: str, event_queue: asyncio.Queue
):
    """
    处理聊天请求 - 调用 LLM API 生成回复

    Args:
        session_id: 会话 ID
        project: 项目名称
        message: 用户消息
        event_queue: SSE 事件队列
    """
    try:
        # ========== 记录用户消息到历史 ==========
        if session_id not in chat_history:
            chat_history[session_id] = []

        chat_history[session_id].append({
            "id": len(chat_history[session_id]),
            "role": "user",
            "content": message,
            "created_at": datetime.now().isoformat(),
        })

        # ========== 记录用户消息到 Memory ==========
        memory_manager.record_conversation("user", message)

        # ========== 第1步：Constraint Agent 检索约束 ==========
        await push_agent_start(event_queue, "constraint", "running")
        await push_constraint_result(
            event_queue,
            constraints=["代码必须使用中文注释", "API 返回统一格式 {code, data, message}"],
            summary="找到 2 条相关约束",
        )

        # ========== 第2步：Planner Agent 分析需求 ==========
        await push_agent_start(event_queue, "planner", "running")
        await push_plan(
            event_queue,
            tasks=["分析用户需求", "生成回复"],
            delegated_agent="complex_coder",
        )

        # ========== 第3步：调用 LLM 生成回复 ==========
        await push_agent_start(event_queue, "complex_coder", "running")

        llm_client = _build_llm_client("complex_coder")
        llm_messages = _get_chat_history_messages(session_id)

        full_response = ""
        try:
            async for chunk in llm_client.chat_stream(llm_messages):
                full_response += chunk
                await push_text(event_queue, chunk, agent="complex_coder")
        except Exception as llm_error:
            logger.error(f"LLM 调用失败: {llm_error}")
            await push_error(event_queue, f"LLM 调用失败: {str(llm_error)}")
            return

        # ========== 第4步：记录助手回复到历史 ==========
        chat_history[session_id].append({
            "id": len(chat_history[session_id]),
            "role": "assistant",
            "agent": "complex_coder",
            "content": full_response,
            "created_at": datetime.now().isoformat(),
        })

        # ========== 第5步：更新 Memory ==========
        memory_manager.record_conversation("assistant", full_response, agent="complex_coder")
        await push_memory_update(
            event_queue, layers=["session", "checkpoint"], message="已更新会话记忆"
        )

        # ========== 第6步：完成 ==========
        await push_done(event_queue, session_id, f"已处理消息：{message}")

    except Exception as e:
        logger.exception(f"处理聊天请求失败: {e}")
        await push_error(event_queue, str(e))


@router.get("/stream")
async def chat_stream(
    session_id: str = Query(..., description="会话ID"),
    project: str = Query(..., description="项目名称"),
    message: str = Query(..., description="用户消息"),
):
    """
    流式聊天接口（SSE）
    
    这是聊天的核心接口，使用 Server-Sent Events 实现实时流式响应。
    
    工作流程：
    1. 前端通过 GET 请求发送消息
    2. 后端创建事件队列
    3. 启动后台任务处理 Agent 工作流
    4. 返回 SSE 响应，前端实时接收事件
    
    Args:
        session_id: 会话 ID（必填）
        project: 项目名称（必填）
        message: 用户消息（必填）
    
    Returns:
        EventSourceResponse: SSE 响应对象
    """
    # 创建事件队列，用于在处理函数和 SSE 生成器之间传递事件
    event_queue: asyncio.Queue = asyncio.Queue()

    # 启动后台任务处理 Agent 工作流
    # asyncio.create_task() 会立即返回，不会阻塞当前请求
    asyncio.create_task(process_chat(session_id, project, message, event_queue))

    # 返回 SSE 响应
    # sse_generator() 会从事件队列中读取事件并生成 SSE 格式的响应
    return EventSourceResponse(sse_generator(event_queue))


@router.get("/history")
async def get_chat_history(
    session_id: Optional[str] = Query(None, description="会话ID，不传则返回会话列表"),
    limit: int = Query(50, description="返回数量"),
    offset: int = Query(0, description="偏移量"),
):
    """
    获取聊天历史接口

    不传 session_id 时返回会话列表，传入时返回该会话的消息。
    """
    if session_id is None:
        # 返回会话列表
        sessions = []
        for sid, messages in chat_history.items():
            last_message = messages[-1]["content"] if messages else None
            sessions.append({
                "session_id": sid,
                "created_at": messages[0]["created_at"] if messages else "",
                "message_count": len(messages),
                "last_message": last_message,
            })
        # 按创建时间倒序
        sessions.sort(key=lambda s: s["created_at"], reverse=True)
        return {
            "code": 0,
            "data": {"sessions": sessions},
            "message": "ok",
        }

    # 返回指定会话的消息
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


@router.delete("/history")
async def delete_chat_history(
    session_id: str = Query(..., description="要删除的会话ID"),
):
    """删除指定会话的聊天历史"""
    if session_id in chat_history:
        del chat_history[session_id]
    return {"code": 0, "data": None, "message": "ok"}

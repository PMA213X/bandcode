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
    push_done,  # 推送完成事件
    push_error,  # 推送错误事件
)
# 导入 Memory Manager
from memory.manager import MemoryManager

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


async def process_chat(
    session_id: str, project: str, message: str, event_queue: asyncio.Queue
):
    """
    处理聊天请求（模拟 Agent 工作流）
    
    这是聊天处理的核心函数，模拟了完整的 Agent 工作流：
    1. Constraint Agent - 检索相关约束
    2. Planner Agent - 分析需求、生成计划
    3. ComplexCoder Agent - 生成代码
    4. Tester Agent - 运行测试
    5. Review Agent - 审查代码
    6. Memory 更新 - 更新会话记忆
    
    Args:
        session_id: 会话 ID
        project: 项目名称
        message: 用户消息
        event_queue: SSE 事件队列
    """
    try:
        # ========== 记录用户消息到 Memory ==========
        memory_manager.record_conversation("user", message)

        # ========== 第1步：Constraint Agent 检索约束 ==========
        # 推送 Agent 开始事件
        await push_agent_start(event_queue, "constraint", "running")
        # 模拟约束检索延迟
        await asyncio.sleep(0.3)
        # 推送约束检索结果
        await push_constraint_result(
            event_queue,
            constraints=["代码必须使用中文注释", "API 返回统一格式 {code, data, message}"],
            summary="找到 2 条相关约束",
        )

        # ========== 第2步：Planner Agent 生成计划 ==========
        # 推送 Planner 开始事件
        await push_agent_start(event_queue, "planner", "running")
        # 模拟计划生成延迟
        await asyncio.sleep(0.3)
        # 推送计划事件，包含任务列表和委派的 Agent
        await push_plan(
            event_queue,
            tasks=["分析用户需求", "检索相关约束", "生成代码方案", "执行代码生成"],
            delegated_agent="complex_coder",
        )

        # ========== 第3步：ComplexCoder Agent 生成代码 ==========
        # 推送 ComplexCoder 开始事件
        await push_agent_start(event_queue, "complex_coder", "running")
        # 模拟代码生成延迟
        await asyncio.sleep(0.5)
        # 推送工具调用事件
        await push_tool_call(event_queue, "write_file", {"path": "output.py"})
        # 推送代码生成事件
        await push_code(
            event_queue,
            file="output.py",
            content=f"# 处理消息: {message}\nprint('Hello from BandCode!')",
        )

        # ========== 第4步：Tester Agent 运行测试 ==========
        # 推送 Tester 开始事件
        await push_agent_start(event_queue, "tester", "running")
        # 模拟测试执行延迟
        await asyncio.sleep(0.3)
        # 推送测试结果事件
        await push_test_result(
            event_queue, status="passed", tests_total=1, tests_passed=1
        )

        # ========== 第5步：Review Agent 审查代码 ==========
        # 推送审查结果事件
        await push_review_result(event_queue, status="passed", violations=[])

        # ========== 第6步：更新 Memory ==========
        # 推送 Memory 更新事件
        await push_memory_update(
            event_queue, layers=["session", "checkpoint"], message="已更新会话记忆"
        )

        # ========== 第7步：完成 ==========
        # 推送完成事件，同时会发送结束信号（None）
        await push_done(event_queue, session_id, f"已处理消息：{message}")

        # ========== 记录助手回复到 Memory ==========
        memory_manager.record_conversation("assistant", f"已处理：{message}", agent="complex_coder")

        # ========== 保存聊天历史 ==========
        # 如果会话不存在，创建新的会话
        if session_id not in chat_history:
            chat_history[session_id] = []

        # 添加用户消息到历史
        chat_history[session_id].append(
            {
                "id": len(chat_history[session_id]),  # 消息 ID
                "role": "user",  # 用户角色
                "content": message,  # 消息内容
                "created_at": "2026-07-10T08:55:00",  # 创建时间
            }
        )
        # 添加助手回复到历史
        chat_history[session_id].append(
            {
                "id": len(chat_history[session_id]),  # 消息 ID
                "role": "assistant",  # 助手角色
                "agent": "complex_coder",  # 处理消息的 Agent
                "content": f"已处理：{message}",  # 回复内容
                "created_at": "2026-07-10T08:55:01",  # 创建时间
            }
        )

    except Exception as e:
        # 如果发生错误，推送错误事件
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
    session_id: str = Query("default", description="会话ID"),
    limit: int = Query(50, description="返回数量"),
    offset: int = Query(0, description="偏移量"),
):
    """
    获取聊天历史接口
    
    获取指定会话的聊天记录，支持分页。
    
    Args:
        session_id: 会话 ID（默认为 "default"）
        limit: 返回的消息数量（默认为 50）
        offset: 偏移量（默认为 0）
    
    Returns:
        包含聊天历史的响应：
        - session_id: 会话 ID
        - messages: 消息列表
        - total: 消息总数
        - has_more: 是否还有更多消息
    """
    # 获取指定会话的聊天历史，如果不存在返回空列表
    history = chat_history.get(session_id, [])
    # 计算消息总数
    total = len(history)
    # 分页获取消息
    paginated = history[offset : offset + limit]
    # 判断是否还有更多消息
    has_more = offset + limit < total

    # 返回统一格式的响应
    return {
        "code": 0,  # 状态码，0 表示成功
        "data": {
            "session_id": session_id,  # 会话 ID
            "messages": paginated,  # 消息列表
            "total": total,  # 消息总数
            "has_more": has_more,  # 是否还有更多消息
        },
        "message": "ok",  # 提示信息
    }

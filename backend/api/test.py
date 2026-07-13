"""
模型测试 API 模块

本模块实现了模型测试相关的 API 接口，包括：
1. 测试模型连接 - POST /api/test/model
2. 获取模型信息 - GET /api/test/model/info
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from config.loader import get_config
from models.llm import LLMClient

logger = logging.getLogger("bandcode.test")

router = APIRouter(prefix="/test", tags=["测试"])


class TestModelRequest(BaseModel):
    """测试模型请求模型"""
    message: str = "你好，请简单介绍一下自己。"
    model: Optional[str] = None  # 可选指定模型


def _build_test_llm_client(model: Optional[str] = None) -> LLMClient:
    """构建测试用的 LLM 客户端"""
    config = get_config()
    # 重新加载配置以确保使用最新的设置
    config.reload()
    model_settings = config.get_section("模型设置")
    base_url = model_settings.get("Base URL", "")
    api_key = model_settings.get("API Key", "")
    
    if model:
        model_name = model
    else:
        model_name = model_settings.get("默认模型", "")
    
    logger.info(f"构建测试 LLM 客户端: base_url={base_url}, model={model_name}, api_key={'***' if api_key else '(空)'}")
    
    return LLMClient(base_url=base_url, api_key=api_key, model=model_name)


@router.post("/model")
async def test_model(request: TestModelRequest):
    """
    测试模型连接接口
    
    发送一条测试消息给 AI 模型，检查是否能正常响应。
    
    Args:
        request: 测试请求，包含测试消息和可选的模型名称
    
    Returns:
        包含测试结果的响应：
        - success: 是否成功
        - response: 模型回复内容
        - latency: 响应时间（毫秒）
        - model: 使用的模型名称
    """
    start_time = datetime.now()
    logger.info(f"收到模型测试请求: message={request.message[:50]}..., model={request.model}")
    
    try:
        # 构建 LLM 客户端
        llm_client = _build_test_llm_client(request.model)
        
        # 构建测试消息
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        # 调用模型
        logger.info(f"开始调用模型: {llm_client.model}")
        response = await llm_client.chat(messages)
        
        # 计算延迟
        latency = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"模型调用成功: latency={latency:.2f}ms")
        
        return {
            "code": 0,
            "data": {
                "success": True,
                "response": response,
                "latency": round(latency, 2),
                "model": llm_client.model,
                "base_url": llm_client.base_url,
            },
            "message": "测试成功",
        }
        
    except Exception as e:
        logger.error(f"模型测试失败: {e}")
        latency = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "code": -1,
            "data": {
                "success": False,
                "response": None,
                "latency": round(latency, 2),
                "error": str(e),
            },
            "message": f"测试失败: {str(e)}",
        }


@router.get("/model/info")
async def get_model_info():
    """
    获取模型信息接口
    
    返回当前配置的模型信息。
    """
    config = get_config()
    model_settings = config.get_section("模型设置")
    
    return {
        "code": 0,
        "data": {
            "default_model": model_settings.get("默认模型", ""),
            "base_url": model_settings.get("Base URL", ""),
            "planner_model": model_settings.get("Planner 模型", ""),
            "simple_coder_model": model_settings.get("SimpleCoder 模型", ""),
            "complex_coder_model": model_settings.get("ComplexCoder 模型", ""),
            "tester_model": model_settings.get("Tester 模型", ""),
        },
        "message": "ok",
    }


@router.post("/model/stream")
async def test_model_stream(request: TestModelRequest):
    """
    测试模型流式输出接口
    
    发送一条测试消息给 AI 模型，以 SSE 流式返回响应。
    """
    from sse_starlette.sse import EventSourceResponse
    from api.sse import SSEEvent, SSEEventType, sse_generator
    
    event_queue = asyncio.Queue()
    
    async def process_test():
        try:
            llm_client = _build_test_llm_client(request.model)
            messages = [{"role": "user", "content": request.message}]
            
            full_response = ""
            async for chunk in llm_client.chat_stream(messages):
                full_response += chunk
                event = SSEEvent(SSEEventType.TEXT, {"content": chunk})
                await event_queue.put(event)
            
            # 发送完成事件
            done_event = SSEEvent(SSEEventType.DONE, {
                "session_id": "test",
                "summary": f"测试完成，模型: {llm_client.model}"
            })
            await event_queue.put(done_event)
            await event_queue.put(None)
            
        except Exception as e:
            logger.error(f"流式测试失败: {e}")
            error_event = SSEEvent(SSEEventType.ERROR, {"message": str(e)})
            await event_queue.put(error_event)
            await event_queue.put(None)
    
    asyncio.create_task(process_test())
    return EventSourceResponse(sse_generator(event_queue))

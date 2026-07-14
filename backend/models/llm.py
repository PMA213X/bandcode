"""LLM统一封装模块，支持流式和非流式调用"""

import logging
from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI, APIStatusError, APIConnectionError, AuthenticationError

logger = logging.getLogger("bandcode.llm")


class LLMClient:
    """OpenAI兼容的LLM客户端封装"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        # 确保 base_url 以 / 结尾，openai 库会自动拼接 /chat/completions
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.base_url:
            raise ValueError("Base URL 不能为空，请在设置中配置 API Base URL")
        if not self.api_key:
            raise ValueError("API Key 不能为空，请在设置中配置 API Key")
        if not self.model:
            raise ValueError("模型名称不能为空，请在设置中配置默认模型")
        
        logger.info(f"初始化 LLM 客户端: base_url={self.base_url}, model={self.model}")
        
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=timeout,
            max_retries=max_retries
        )

    def _handle_error(self, e: Exception) -> str:
        """将 API 错误转换为用户友好的错误消息"""
        if isinstance(e, AuthenticationError):
            return f"API Key 无效或已过期，请检查设置中的 API Key 配置 (模型: {self.model})"
        elif isinstance(e, APIStatusError):
            status = e.status_code
            if status == 404:
                return (
                    f"API 端点不存在 (404)。请检查:\n"
                    f"  1. Base URL 是否正确 (当前: {self.base_url})\n"
                    f"  2. 模型名称是否正确 (当前: {self.model})\n"
                    f"  3. API 服务是否支持 OpenAI 兼容接口"
                )
            elif status == 401:
                return "API Key 无效 (401)，请检查设置中的 API Key 配置"
            elif status == 429:
                return "API 请求频率超限 (429)，请稍后再试"
            elif status == 500:
                return f"API 服务器内部错误 (500)，请联系 API 提供方"
            else:
                return f"API 请求失败 (HTTP {status}): {e.message}"
        elif isinstance(e, APIConnectionError):
            return f"无法连接到 API 服务器 ({self.base_url})，请检查网络连接和 Base URL 配置"
        else:
            return f"LLM 调用失败: {type(e).__name__}: {str(e)}"

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> str:
        """非流式对话，返回完整响应"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        try:
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            error_msg = self._handle_error(e)
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[str, None]:
        """流式对话，逐块返回响应"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        try:
            stream = await self.client.chat.completions.create(**kwargs)
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            error_msg = self._handle_error(e)
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ):
        """带工具调用的对话，返回完整的 completion 对象（支持 function calling）"""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if tools:
            kwargs["tools"] = tools

        try:
            response = await self.client.chat.completions.create(**kwargs)
            return response
        except Exception as e:
            error_msg = self._handle_error(e)
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

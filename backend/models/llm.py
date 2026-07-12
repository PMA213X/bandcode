"""LLM统一封装模块，支持流式和非流式调用"""

from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI


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
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )

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

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

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

        stream = await self.client.chat.completions.create(**kwargs)
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

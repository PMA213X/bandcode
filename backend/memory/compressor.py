"""
Memory 压缩器 — Session 历史自动压缩为摘要

当对话历史过长时，自动压缩旧消息为摘要，保留关键信息。
"""
from __future__ import annotations
from typing import Optional


class MemoryCompressor:
    """Memory 压缩器"""

    def __init__(self, llm_client=None, threshold: int = 1000):
        """
        Args:
            llm_client: LLM 客户端，用于生成摘要
            threshold: 触发压缩的消息数量阈值
        """
        self.llm_client = llm_client
        self.threshold = threshold

    def should_compress(self, message_count: int) -> bool:
        """判断是否需要压缩"""
        return message_count > self.threshold

    async def compress(self, messages: list[dict]) -> str:
        """
        将消息列表压缩为摘要

        Args:
            messages: 消息列表 [{"role": "user/assistant", "content": "..."}]

        Returns:
            压缩后的摘要文本
        """
        if not messages:
            return ""

        # 提取关键信息
        key_points = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                key_points.append(f"用户请求: {content[:200]}")
            elif role == "assistant":
                # 只保留前 100 字符
                key_points.append(f"助手回复: {content[:100]}...")

        # 如果有 LLM 客户端，使用 LLM 生成摘要
        if self.llm_client:
            return await self._llm_summarize(key_points)

        # 否则使用简单的拼接方式
        return self._simple_summarize(key_points)

    def _simple_summarize(self, key_points: list[str]) -> str:
        """简单拼接摘要"""
        summary_lines = ["## 会话历史摘要\n"]
        for i, point in enumerate(key_points[-10:], 1):  # 只保留最近 10 条
            summary_lines.append(f"{i}. {point}")
        return "\n".join(summary_lines)

    async def _llm_summarize(self, key_points: list[str]) -> str:
        """使用 LLM 生成摘要"""
        prompt = (
            "请将以下对话历史压缩为简洁的摘要，保留关键信息：\n\n"
            + "\n".join(key_points)
            + "\n\n摘要："
        )

        try:
            response = await self.llm_client.chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            return response.get("content", self._simple_summarize(key_points))
        except Exception:
            return self._simple_summarize(key_points)

    def estimate_tokens(self, text: str) -> int:
        """估算文本的 token 数量（粗略估算）"""
        # 中文约 1.5 字符/token，英文约 4 字符/token
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)

"""
Prompt Builder — 将各层上下文组装为完整 Prompt

Prompt 结构:
1. System Prompt（全局系统指令）
2. 约束摘要（来自 Constraint Agent）
3. RAG 上下文（来自知识库检索）
4. Memory 各层级（global → project → task → checkpoint）
5. Agent 专属 Prompt
6. 用户输入
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptMessage:
    """Prompt 消息结构"""
    role: str  # "system" / "user"
    content: str


class PromptBuilder:
    """将各层上下文组装为完整 Prompt"""

    def __init__(self, system_prompt: str = None):
        self.system_prompt = system_prompt or (
            "你是 BandCode AI 编程助手，基于分层记忆与六智能体协作的 AI 编程工具。"
            "请根据项目约束和上下文，提供准确、规范的代码和建议。"
        )

    def build(
        self,
        user_input: str,
        agent_prompt: str = None,
        constraint_summary: str = None,
        rag_context: str = None,
        memory_context: dict = None,
    ) -> list[PromptMessage]:
        """
        构建完整的消息列表

        Args:
            user_input: 用户原始输入
            agent_prompt: Agent 专属 Prompt
            constraint_summary: 约束摘要（来自 Constraint Agent）
            rag_context: RAG 检索到的知识库上下文
            memory_context: Memory 各层级内容 {"global": ..., "project": ..., ...}

        Returns:
            消息列表
        """
        messages = []

        # 1. System Prompt（全局系统指令）
        messages.append(PromptMessage(role="system", content=self.system_prompt))

        # 2. 约束摘要（来自 Constraint Agent）
        if constraint_summary:
            messages.append(PromptMessage(
                role="system",
                content=f"[项目约束]\n{constraint_summary}"
            ))

        # 3. RAG 上下文
        if rag_context:
            messages.append(PromptMessage(
                role="system",
                content=f"[知识库参考]\n{rag_context}"
            ))

        # 4. Memory 各层级
        if memory_context:
            for layer in ["global", "project", "task", "checkpoint"]:
                content = memory_context.get(layer)
                if content:
                    messages.append(PromptMessage(
                        role="system",
                        content=f"[{layer} Memory]\n{content}"
                    ))

        # 5. Agent 专属 Prompt
        if agent_prompt:
            messages.append(PromptMessage(
                role="system",
                content=f"[Agent 指令]\n{agent_prompt}"
            ))

        # 6. 用户输入
        messages.append(PromptMessage(role="user", content=user_input))

        return messages

    def build_for_agent(
        self,
        agent_name: str,
        agent_prompt: str,
        user_input: str,
        state=None,
    ) -> list[PromptMessage]:
        """为指定 Agent 构建 Prompt"""
        constraint_summary = state.constraint_summary if state else None
        rag_context = state.rag_context if state else None
        memory_context = state.memory_context if state else None

        return self.build(
            user_input=user_input,
            agent_prompt=agent_prompt,
            constraint_summary=constraint_summary,
            rag_context=rag_context,
            memory_context=memory_context,
        )

    def messages_to_dicts(self, messages: list[PromptMessage]) -> list[dict]:
        """将消息列表转换为 OpenAI API 格式"""
        return [{"role": m.role, "content": m.content} for m in messages]

"""Constraint Agent - 从Memory中智能检索相关约束"""

import re
from dataclasses import dataclass, field
from typing import Optional

from models.llm import LLMClient


@dataclass
class PipelineState:
    """工作流状态数据结构（简化版，完整版由成员E实现）"""
    user_input: str = ""
    session_id: str = ""
    project: str = ""
    constraints: list[str] = field(default_factory=list)
    constraint_summary: str = ""
    rag_context: str = ""
    memory_context: dict = field(default_factory=dict)


class ConstraintAgent:
    """约束检索智能体 - 从Memory中筛选与当前问题相关的约束"""

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.max_constraints = 10

    async def run(self, state: PipelineState) -> PipelineState:
        """执行约束检索"""
        # 1. 解析用户意图
        intent = await self._parse_intent(state.user_input)

        # 2. 检索各层Memory（实际实现需要调用成员E的memory/store.py）
        # 这里提供接口，具体实现依赖成员E的MemoryStore
        all_constraints = await self._search_constraints(intent, state)

        # 3. 去重 + 排序
        unique_constraints = self._deduplicate(all_constraints)
        ranked_constraints = self._rank_by_relevance(unique_constraints, intent)

        # 4. 取top_k
        top_constraints = ranked_constraints[:self.max_constraints]

        # 5. 生成约束摘要
        summary = await self._generate_summary(top_constraints)

        state.constraints = top_constraints
        state.constraint_summary = summary
        return state

    async def _parse_intent(self, user_input: str) -> str:
        """使用LLM解析用户意图"""
        messages = [
            {"role": "system", "content": "你是一个意图分析器。请从用户输入中提取核心意图，用简短的关键词描述。"},
            {"role": "user", "content": f"用户输入：{user_input}\n\n请提取核心意图关键词："}
        ]
        intent = await self.llm.chat(messages, temperature=0.1)
        return intent.strip()

    async def _search_constraints(self, intent: str, state: PipelineState) -> list[str]:
        """搜索相关约束（需要集成MemoryStore）"""
        # TODO: 集成成员E的MemoryStore
        # 当前返回模拟数据
        constraints = []

        # 搜索global memory
        if "global" in state.memory_context:
            constraints.extend(self._filter_relevant(state.memory_context["global"], intent))

        # 搜索project memory
        if "project" in state.memory_context:
            constraints.extend(self._filter_relevant(state.memory_context["project"], intent))

        # 搜索task memory
        if "task" in state.memory_context:
            constraints.extend(self._filter_relevant(state.memory_context["task"], intent))

        return constraints

    def _tokenize(self, text: str) -> set[str]:
        """分词函数，支持中英文混合"""
        # 提取英文单词
        english_words = set(re.findall(r'[a-zA-Z]+', text.lower()))
        # 提取中文字符（连续的）
        chinese_chars = set(re.findall(r'[\u4e00-\u9fff]+', text))
        return english_words | chinese_chars

    def _filter_relevant(self, content: str, intent: str) -> list[str]:
        """过滤相关内容"""
        lines = content.split("\n")
        relevant = []
        intent_tokens = self._tokenize(intent)

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            line_tokens = self._tokenize(line)
            # 如果有交集，认为相关
            if intent_tokens & line_tokens:
                relevant.append(line)

        return relevant

    def _deduplicate(self, constraints: list[str]) -> list[str]:
        """去重"""
        seen = set()
        unique = []
        for c in constraints:
            if c not in seen:
                seen.add(c)
                unique.append(c)
        return unique

    def _rank_by_relevance(self, constraints: list[str], intent: str) -> list[str]:
        """按相关性排序"""
        intent_tokens = self._tokenize(intent)

        def score(c):
            c_tokens = self._tokenize(c)
            return len(intent_tokens & c_tokens)

        return sorted(constraints, key=score, reverse=True)

    async def _generate_summary(self, constraints: list[str]) -> str:
        """使用LLM生成约束摘要"""
        if not constraints:
            return "未找到相关约束"

        constraints_text = "\n".join(f"- {c}" for c in constraints)
        messages = [
            {"role": "system", "content": "你是一个约束摘要生成器。请将以下约束整理成简洁的摘要。"},
            {"role": "user", "content": f"约束列表：\n{constraints_text}\n\n请生成摘要："}
        ]
        summary = await self.llm.chat(messages, temperature=0.1)
        return summary.strip()

"""Constraint Agent - 从Memory中智能检索相关约束"""

import re
from dataclasses import dataclass, field
from typing import Optional

from models.llm import LLMClient
# 导入统一的PipelineState定义
from agents.base import BaseAgent, PipelineState


class ConstraintAgent(BaseAgent):
    """约束检索智能体 - 从Memory中筛选与当前问题相关的约束"""

    # Agent名称
    name = "constraint"
    # Agent描述
    description = "约束检索智能体"
    # 使用的模型
    model = "mimo-v2.5"
    # 生成温度
    temperature = 0.1
    # 工具权限
    permissions = {
        "read": "allow",
        "edit": "deny",
        "bash": "deny"
    }

    def __init__(self, llm_client: LLMClient):
        # 调用父类初始化
        super().__init__(llm_client)
        # 最大约束数量
        self.max_constraints = 10

    async def run(self, state: PipelineState) -> PipelineState:
        """
        执行约束检索

        Args:
            state: 当前工作流状态

        Returns:
            修改后的工作流状态
        """
        # 上报状态：开始执行
        self.report_status("running", {"step": "解析用户意图"})

        try:
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

            # 更新状态
            state.constraints = top_constraints
            state.constraint_summary = summary

            # 记录到历史
            self.add_to_history(state, "constraint_search", {
                "constraints_found": len(top_constraints)
            })

            # 上报状态：完成
            self.report_status("completed", {
                "constraints_count": len(top_constraints)
            })

            return state

        except Exception as e:
            # 上报错误
            state.error = str(e)
            self.report_status("failed", {"error": str(e)})
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

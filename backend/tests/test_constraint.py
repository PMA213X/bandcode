"""Constraint Agent单元测试"""

import pytest
from agents.constraint import ConstraintAgent, PipelineState


class MockLLMClient:
    """模拟LLM客户端"""

    def __init__(self):
        self.call_count = 0

    async def chat(self, messages, temperature=0.1):
        self.call_count += 1
        # 根据提示返回模拟响应
        prompt = messages[-1]["content"]
        if "意图" in prompt:
            return "用户认证 登录"
        elif "摘要" in prompt:
            return "需要遵循JWT认证规范和密码加密要求"
        return "模拟响应"


class TestConstraintAgent:
    """Constraint Agent测试"""

    def setup_method(self):
        self.llm = MockLLMClient()
        self.agent = ConstraintAgent(llm_client=self.llm)

    @pytest.mark.asyncio
    async def test_run_basic(self):
        """测试基本运行流程"""
        state = PipelineState(
            user_input="帮我实现用户登录功能",
            memory_context={
                "global": "使用JWT认证\n密码使用bcrypt加密",
                "project": "API返回格式统一"
            }
        )

        result = await self.agent.run(state)

        assert result.constraints is not None
        assert result.constraint_summary != ""

    @pytest.mark.asyncio
    async def test_empty_memory(self):
        """测试空Memory情况"""
        state = PipelineState(user_input="测试输入")

        result = await self.agent.run(state)

        assert result.constraint_summary == "未找到相关约束"

    def test_deduplicate(self):
        """测试去重功能"""
        constraints = ["约束A", "约束B", "约束A", "约束C", "约束B"]
        unique = self.agent._deduplicate(constraints)
        assert unique == ["约束A", "约束B", "约束C"]

    def test_rank_by_relevance(self):
        """测试相关性排序"""
        constraints = ["使用Python开发", "JWT认证规范", "FastAPI框架"]
        intent = "JWT 认证"
        ranked = self.agent._rank_by_relevance(constraints, intent)
        # JWT认证规范应该排在前面（包含JWT和认证两个词）
        assert "JWT" in ranked[0] or "认证" in ranked[0]

    def test_filter_relevant(self):
        """测试相关性过滤"""
        content = "使用JWT认证\n密码使用bcrypt加密\nFastAPI框架"
        intent = "JWT 认证"
        relevant = self.agent._filter_relevant(content, intent)
        assert len(relevant) > 0
        assert any("JWT" in r for r in relevant)

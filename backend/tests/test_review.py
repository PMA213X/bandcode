"""Review Agent单元测试"""

import pytest
from agents.review import ReviewAgent, ReviewResult


class MockLLMClient:
    """模拟LLM客户端"""

    async def chat(self, messages, temperature=0):
        # 返回无违规的响应
        return "[]"


class TestReviewAgent:
    """Review Agent测试"""

    def setup_method(self):
        self.llm = MockLLMClient()
        self.agent = ReviewAgent(llm_client=self.llm)

    @pytest.mark.asyncio
    async def test_check_compliance_pass(self):
        """测试合规检查通过"""
        agent_output = {"code": "print('hello')", "files_changed": []}
        constraints = ["使用UTF-8编码"]

        result = await self.agent.check_compliance(agent_output, constraints)

        assert isinstance(result, ReviewResult)
        assert result.passed is True
        assert result.violations == []

    @pytest.mark.asyncio
    async def test_check_compliance_no_constraints(self):
        """测试无约束情况"""
        agent_output = {"code": "print('hello')"}

        result = await self.agent.check_compliance(agent_output, [])

        assert result.passed is True

    def test_check_file_compliance(self):
        """测试文件合规检查"""
        files_changed = [
            {"path": "src/main.py", "action": "modify"},
            {"path": "settings.json", "action": "modify"}
        ]
        constraints = ["禁止修改配置文件"]

        result = self.agent._check_file_compliance(files_changed, constraints)

        assert len(result) == 1
        assert "settings.json" in result[0]["detail"]

    def test_generate_summary_pass(self):
        """测试通过摘要生成"""
        summary = self.agent._generate_summary(True, [])
        assert summary == "约束合规检查通过"

    def test_generate_summary_fail(self):
        """测试失败摘要生成"""
        violations = [
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "medium"}
        ]
        summary = self.agent._generate_summary(False, violations)
        assert "1个高严重性违规" in summary
        assert "2个中严重性违规" in summary

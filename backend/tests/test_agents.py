"""
Agent模块单元测试

测试所有Agent的输入输出和基本功能。

作者：成员C（wang123456-123456）
"""

import pytest
from agents.base import BaseAgent, PipelineState
from agents.manager import AgentManager
from agents.planner import PlannerAgent
from agents.simple_coder import SimpleCoderAgent
from agents.complex_coder import ComplexCoderAgent
from agents.tester import TesterAgent


class MockLLMClient:
    """模拟LLM客户端"""

    def __init__(self):
        self.call_count = 0

    async def chat(self, messages, temperature=0.1, max_tokens=None):
        self.call_count += 1
        # 根据提示返回模拟响应
        prompt = messages[-1]["content"]

        # 模拟JSON响应
        if "需求分析" in prompt or "分析需求" in prompt:
            return '{"intent": "用户登录", "complexity": "medium", "scope": "认证模块", "constraints": [], "estimated_steps": 3}'
        elif "拆解任务" in prompt:
            return '[{"step": 1, "description": "实现登录API", "assigned_agent": "simple-coder", "estimated_complexity": "low"}]'
        elif "任务分析" in prompt:
            return '{"files": ["src/auth/login.py"], "type": "logic", "estimated_lines": 100, "complexity": "low"}'
        elif "代码生成" in prompt or "生成代码" in prompt:
            return 'def login(username, password):\n    return {"status": "success"}'
        elif "架构分析" in prompt:
            return '{"modules": ["auth"], "dependencies": ["database"], "design": "使用JWT", "risks": []}'
        elif "方案设计" in prompt:
            return '{"approach": "JWT认证", "files": ["auth.py"], "steps": ["创建token"], "considerations": []}'
        elif "编译检查" in prompt:
            return '{"success": true, "errors": [], "warnings": []}'
        elif "单元测试" in prompt:
            return '{"total": 5, "passed": 5, "failed": 0, "errors": []}'
        elif "静态分析" in prompt:
            return '{"quality_score": 90, "issues": [], "suggestions": [], "metrics": {"complexity": "low", "maintainability": "good"}}'
        return "模拟响应"


class TestPipelineState:
    """PipelineState测试"""

    def test_create_default(self):
        """测试默认创建"""
        state = PipelineState()
        assert state.user_input == ""
        assert state.session_id == ""
        assert state.step_count == 0
        assert state.max_steps == 50

    def test_create_with_values(self):
        """测试带值创建"""
        state = PipelineState(
            user_input="测试输入",
            session_id="123",
            project="test_project"
        )
        assert state.user_input == "测试输入"
        assert state.session_id == "123"
        assert state.project == "test_project"

    def test_agent_history(self):
        """测试Agent历史记录"""
        state = PipelineState()
        state.agent_history.append({"agent": "test", "action": "run", "result": "success"})
        assert len(state.agent_history) == 1


class TestBaseAgent:
    """BaseAgent测试"""

    def test_cannot_instantiate(self):
        """测试不能直接实例化抽象类"""
        llm = MockLLMClient()
        with pytest.raises(TypeError):
            BaseAgent(llm)


class TestPlannerAgent:
    """PlannerAgent测试"""

    def setup_method(self):
        self.llm = MockLLMClient()
        self.agent = PlannerAgent(llm_client=self.llm)

    def test_agent_info(self):
        """测试Agent信息"""
        assert self.agent.name == "planner"
        assert self.agent.description == "规划调度智能体"
        assert self.agent.model == "mimo-v2.5-pro"

    @pytest.mark.asyncio
    async def test_run(self):
        """测试运行流程"""
        state = PipelineState(user_input="帮我实现用户登录功能")
        result = await self.agent.run(state)

        assert result.plan is not None
        assert "tasks" in result.plan
        assert "delegated_agent" in result.plan

    def test_extract_json(self):
        """测试JSON提取"""
        # 测试直接JSON
        text = '{"key": "value"}'
        result = self.agent._extract_json(text)
        assert result == {"key": "value"}

        # 测试带代码块的JSON
        text = '```json\n{"key": "value"}\n```'
        result = self.agent._extract_json(text)
        assert result == {"key": "value"}

    def test_select_agent(self):
        """测试Agent选择"""
        tasks = [{"assigned_agent": "complex-coder", "estimated_complexity": "high"}]
        analysis = {"complexity": "high"}
        agent, reason = self.agent._select_agent(tasks, analysis)
        assert agent == "complex-coder"


class TestSimpleCoderAgent:
    """SimpleCoderAgent测试"""

    def setup_method(self):
        self.llm = MockLLMClient()
        self.agent = SimpleCoderAgent(llm_client=self.llm)

    def test_agent_info(self):
        """测试Agent信息"""
        assert self.agent.name == "simple-coder"
        assert self.agent.description == "简单编码智能体"
        assert self.agent.model == "mimo-v2.5"

    @pytest.mark.asyncio
    async def test_run(self):
        """测试运行流程"""
        state = PipelineState(user_input="修改登录按钮颜色")
        result = await self.agent.run(state)

        assert result.code is not None
        assert result.error is None

    def test_should_upgrade(self):
        """测试升级判断"""
        # 低复杂度，不应该升级
        analysis = {"files": ["test.py"], "estimated_lines": 50, "complexity": "low"}
        assert self.agent._should_upgrade(analysis) == False

        # 高复杂度，应该升级
        analysis = {"files": ["a.py", "b.py", "c.py"], "estimated_lines": 500, "complexity": "high"}
        assert self.agent._should_upgrade(analysis) == True


class TestComplexCoderAgent:
    """ComplexCoderAgent测试"""

    def setup_method(self):
        self.llm = MockLLMClient()
        self.agent = ComplexCoderAgent(llm_client=self.llm)

    def test_agent_info(self):
        """测试Agent信息"""
        assert self.agent.name == "complex-coder"
        assert self.agent.description == "复杂编码智能体"
        assert self.agent.model == "mimo-v2.5-pro"

    @pytest.mark.asyncio
    async def test_run(self):
        """测试运行流程"""
        state = PipelineState(user_input="重构认证模块")
        result = await self.agent.run(state)

        assert result.code is not None
        assert result.error is None


class TestTesterAgent:
    """TesterAgent测试"""

    def setup_method(self):
        self.llm = MockLLMClient()
        self.agent = TesterAgent(llm_client=self.llm)

    def test_agent_info(self):
        """测试Agent信息"""
        assert self.agent.name == "tester"
        assert self.agent.description == "测试验证智能体"
        assert self.agent.model == "mimo-v2.5"
        assert self.agent.permissions["edit"] == "deny"

    @pytest.mark.asyncio
    async def test_run(self):
        """测试运行流程"""
        state = PipelineState(code="def test(): pass")
        result = await self.agent.run(state)

        assert result.test_results is not None
        assert "status" in result.test_results

    @pytest.mark.asyncio
    async def test_run_no_code(self):
        """测试无代码情况"""
        state = PipelineState()
        result = await self.agent.run(state)

        assert result.test_results is not None

    def test_generate_report(self):
        """测试报告生成"""
        compile_result = {"success": True, "errors": []}
        test_result = {"total": 5, "passed": 5, "failed": 0, "errors": []}
        analysis_result = {"quality_score": 90, "issues": [], "suggestions": []}

        report = self.agent._generate_report(compile_result, test_result, analysis_result)
        assert report["status"] == "passed"

    def test_generate_report_failed(self):
        """测试失败报告生成"""
        compile_result = {"success": False, "errors": ["语法错误"]}
        test_result = {"total": 0, "passed": 0, "failed": 0, "errors": []}
        analysis_result = {"quality_score": 0, "issues": [], "suggestions": []}

        report = self.agent._generate_report(compile_result, test_result, analysis_result)
        assert report["status"] == "failed"


class TestAgentManager:
    """AgentManager测试"""

    def setup_method(self):
        self.llm = MockLLMClient()
        self.manager = AgentManager(llm_client=self.llm)

    def test_register(self):
        """测试注册Agent"""
        agent = PlannerAgent(llm_client=self.llm)
        self.manager.register(agent)
        assert "planner" in self.manager.list_agents()

    def test_get(self):
        """测试获取Agent"""
        agent = PlannerAgent(llm_client=self.llm)
        self.manager.register(agent)

        retrieved = self.manager.get("planner")
        assert retrieved is not None
        assert retrieved.name == "planner"

    def test_get_not_found(self):
        """测试获取不存在的Agent"""
        retrieved = self.manager.get("nonexistent")
        assert retrieved is None

    def test_list_agents(self):
        """测试列出Agent"""
        agent1 = PlannerAgent(llm_client=self.llm)
        agent2 = SimpleCoderAgent(llm_client=self.llm)
        self.manager.register(agent1)
        self.manager.register(agent2)

        agents = self.manager.list_agents()
        assert "planner" in agents
        assert "simple-coder" in agents

    def test_get_agent_info(self):
        """测试获取Agent信息"""
        agent = PlannerAgent(llm_client=self.llm)
        self.manager.register(agent)

        info = self.manager.get_agent_info("planner")
        assert info["name"] == "planner"
        assert info["description"] == "规划调度智能体"

    @pytest.mark.asyncio
    async def test_run(self):
        """测试运行Agent"""
        agent = PlannerAgent(llm_client=self.llm)
        self.manager.register(agent)

        state = PipelineState(user_input="测试输入")
        result = await self.manager.run("planner", state)

        assert result.plan is not None

    @pytest.mark.asyncio
    async def test_run_not_found(self):
        """测试运行不存在的Agent"""
        state = PipelineState(user_input="测试输入")
        with pytest.raises(ValueError):
            await self.manager.run("nonexistent", state)

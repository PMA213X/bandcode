"""
Planner Agent - 规划调度智能体

本模块实现了规划调度智能体，负责：
1. 需求分析：理解用户需求，结合Constraint Agent提供的约束
2. 任务拆解：将复杂任务分解为可执行的子任务
3. Agent调度：根据任务特征选择合适的子Agent执行
"""

# 导入数据类
from dataclasses import dataclass, field
# 导入类型提示
from typing import Optional

# 导入Agent基类
from agents.base import BaseAgent, PipelineState
# 导入LLM客户端
from models.llm import LLMClient


class PlannerAgent(BaseAgent):
    """
    规划调度智能体

    负责需求分析、任务拆解和Agent调度。
    """

    # Agent名称
    name = "planner"
    # Agent描述
    description = "规划调度智能体"
    # 使用的模型
    model = "mimo-v2.5-pro"
    # 生成温度
    temperature = 0.3
    # 工具权限
    permissions = {
        "read": "allow",
        "edit": "allow",
        "bash": "allow"
    }

    def __init__(self, llm_client: LLMClient):
        """
        初始化Planner Agent

        Args:
            llm_client: LLM客户端实例
        """
        # 调用父类初始化
        super().__init__(llm_client)
        # 最大步骤数
        self.max_steps = 20

    async def run(self, state: PipelineState) -> PipelineState:
        """
        执行规划调度

        Args:
            state: 当前工作流状态

        Returns:
            修改后的工作流状态
        """
        # 上报状态：开始执行
        self.report_status("running", {"step": "需求分析"})

        try:
            # 1. 需求分析
            analysis = await self._analyze_requirement(state)

            # 2. 任务拆解
            tasks = await self._decompose_tasks(analysis, state)

            # 3. 选择子Agent
            delegated_agent, reason = self._select_agent(tasks)

            # 4. 输出计划
            state.plan = {
                "tasks": tasks,
                "delegated_agent": delegated_agent,
                "reason": reason
            }

            # 记录到历史
            self.add_to_history(state, "planning", state.plan)

            # 上报状态：完成
            self.report_status("completed", {"plan": state.plan})

            return state

        except Exception as e:
            # 上报错误
            state.error = str(e)
            self.report_status("failed", {"error": str(e)})
            return state

    async def _analyze_requirement(self, state: PipelineState) -> str:
        """
        分析用户需求

        Args:
            state: 当前工作流状态

        Returns:
            需求分析结果
        """
        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个需求分析器。请分析用户需求，结合提供的约束，输出结构化的需求分析。

输出格式：
{
    "intent": "用户核心意图",
    "complexity": "low|medium|high",
    "scope": "影响范围描述",
    "constraints": ["相关约束列表"]
}"""
            },
            {
                "role": "user",
                "content": f"""用户需求：{state.user_input}

约束摘要：
{state.constraint_summary}

请分析需求："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0.3)
        return response

    async def _decompose_tasks(self, analysis: str, state: PipelineState) -> list[dict]:
        """
        拆解任务

        Args:
            analysis: 需求分析结果
            state: 当前工作流状态

        Returns:
            任务列表
        """
        # 构造Prompt
        messages = [
            {
                "role": "system",
                "content": """你是一个任务拆解器。请将需求分析结果拆解为可执行的子任务。

输出格式：
[
    {
        "step": 1,
        "description": "步骤描述",
        "assigned_agent": "simple-coder|complex-coder|tester",
        "estimated_complexity": "low|medium|high"
    }
]"""
            },
            {
                "role": "user",
                "content": f"""需求分析：
{analysis}

请拆解任务："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0.3)

        # 解析响应（简化处理）
        # 实际实现中应该使用JSON解析
        tasks = [
            {
                "step": 1,
                "description": "分析需求并制定计划",
                "assigned_agent": "planner",
                "estimated_complexity": "low"
            }
        ]

        return tasks

    def _select_agent(self, tasks: list[dict]) -> tuple[str, str]:
        """
        选择子Agent

        Args:
            tasks: 任务列表

        Returns:
            (Agent名称, 选择原因)
        """
        # 根据任务复杂度选择Agent
        # 简单任务：simple-coder
        # 复杂任务：complex-coder
        # 测试任务：tester

        # 默认选择simple-coder
        return "simple-coder", "默认选择：简单编码任务"
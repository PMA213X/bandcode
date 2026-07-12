"""
Planner Agent - 规划调度智能体

本模块实现了规划调度智能体，负责：
1. 需求分析：理解用户需求，结合Constraint Agent提供的约束
2. 任务拆解：将复杂任务分解为可执行的子任务
3. Agent调度：根据任务特征选择合适的子Agent执行

作者：成员C（wang123456-123456）
"""

# 导入JSON解析
import json
# 导入正则表达式
import re
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
            self.logger.info(f"需求分析完成: {analysis.get('intent', 'N/A')}")

            # 2. 任务拆解
            tasks = await self._decompose_tasks(analysis, state)
            self.logger.info(f"任务拆解完成: {len(tasks)} 个子任务")

            # 3. 选择子Agent
            delegated_agent, reason = self._select_agent(tasks, analysis)
            self.logger.info(f"选择Agent: {delegated_agent}, 原因: {reason}")

            # 4. 输出计划
            state.plan = {
                "tasks": tasks,
                "delegated_agent": delegated_agent,
                "reason": reason,
                "analysis": analysis
            }

            # 记录到历史
            self.add_to_history(state, "planning", state.plan)

            # 上报状态：完成
            self.report_status("completed", {"plan": state.plan})

            return state

        except Exception as e:
            # 上报错误
            self.logger.error(f"规划调度失败: {e}")
            state.error = str(e)
            self.report_status("failed", {"error": str(e)})
            return state

    def _extract_json(self, text: str) -> dict:
        """
        从LLM响应中提取JSON

        Args:
            text: LLM响应文本

        Returns:
            解析后的JSON字典
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取```json ... ```格式
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取{ ... }格式
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # 解析失败返回默认值
        return {}

    async def _analyze_requirement(self, state: PipelineState) -> dict:
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

输出格式（JSON）：
{
    "intent": "用户核心意图",
    "complexity": "low|medium|high",
    "scope": "影响范围描述",
    "constraints": ["相关约束列表"],
    "estimated_steps": 3
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

        # 解析响应
        analysis = self._extract_json(response)

        # 设置默认值
        if not analysis:
            analysis = {
                "intent": state.user_input[:100],
                "complexity": "medium",
                "scope": "待分析",
                "constraints": [],
                "estimated_steps": 3
            }

        return analysis

    async def _decompose_tasks(self, analysis: dict, state: PipelineState) -> list[dict]:
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

输出格式（JSON数组）：
[
    {
        "step": 1,
        "description": "步骤描述",
        "assigned_agent": "simple-coder|complex-coder|tester",
        "estimated_complexity": "low|medium|high"
    }
]

Agent选择规则：
- simple-coder：UI修改、配置调整、单文件修改、小型Bug修复
- complex-coder：核心业务逻辑、API开发、架构调整、跨模块重构
- tester：编译检查、单元测试、静态分析"""
            },
            {
                "role": "user",
                "content": f"""需求分析：
{json.dumps(analysis, ensure_ascii=False, indent=2)}

请拆解任务："""
            }
        ]

        # 调用LLM
        response = await self.call_llm(messages, temperature=0.3)

        # 解析响应
        tasks = self._extract_json(response)

        # 如果解析失败，返回默认任务
        if not isinstance(tasks, list) or len(tasks) == 0:
            tasks = [
                {
                    "step": 1,
                    "description": "分析需求并制定计划",
                    "assigned_agent": "planner",
                    "estimated_complexity": "low"
                }
            ]

        return tasks

    def _select_agent(self, tasks: list[dict], analysis: dict) -> tuple[str, str]:
        """
        选择子Agent

        Args:
            tasks: 任务列表
            analysis: 需求分析结果

        Returns:
            (Agent名称, 选择原因)
        """
        # 获取第一个任务的指定Agent
        if tasks and len(tasks) > 0:
            first_task = tasks[0]
            assigned_agent = first_task.get("assigned_agent", "simple-coder")
            complexity = first_task.get("estimated_complexity", "medium")

            # 验证Agent名称
            valid_agents = ["simple-coder", "complex-coder", "tester"]
            if assigned_agent in valid_agents:
                reason = f"任务复杂度: {complexity}, 选择 {assigned_agent}"
                return assigned_agent, reason

        # 根据整体复杂度选择
        overall_complexity = analysis.get("complexity", "medium")
        if overall_complexity == "high":
            return "complex-coder", "高复杂度任务，需要复杂编码智能体"
        elif overall_complexity == "low":
            return "simple-coder", "低复杂度任务，使用简单编码智能体"
        else:
            return "simple-coder", "默认选择：简单编码任务"

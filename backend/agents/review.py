"""Review Agent - 约束合规检查（成员B协助实现约束检查部分）"""

import fnmatch
import json
from dataclasses import dataclass, field
from typing import Optional

from models.llm import LLMClient
# 导入统一的PipelineState定义
from agents.base import BaseAgent, PipelineState


@dataclass
class ReviewResult:
    """审查结果"""
    passed: bool
    violations: list[dict] = field(default_factory=list)
    summary: str = ""


class ReviewAgent(BaseAgent):
    """约束审查智能体 - 检查输出是否违反项目约束"""

    # Agent名称
    name = "review"
    # Agent描述
    description = "约束审查智能体"
    # 使用的模型
    model = "mimo-v2.5"
    # 生成温度
    temperature = 0
    # 工具权限
    permissions = {
        "read": "allow",
        "edit": "deny",
        "bash": "deny"
    }

    def __init__(self, llm_client: LLMClient):
        # 调用父类初始化
        super().__init__(llm_client)

    async def run(self, state: PipelineState) -> PipelineState:
        """
        执行约束审查

        Args:
            state: 当前工作流状态

        Returns:
            修改后的工作流状态
        """
        # 上报状态：开始执行
        self.report_status("running", {"step": "约束合规检查"})

        try:
            # 构造agent_output
            agent_output = {
                "code": state.code,
                "files_changed": state.files_changed
            }

            # 执行合规检查
            result = await self.check_compliance(agent_output, state.constraints)

            # 更新状态
            state.review_result = {
                "passed": result.passed,
                "violations": result.violations,
                "summary": result.summary
            }

            # 记录到历史
            self.add_to_history(state, "review", state.review_result)

            # 上报状态：完成
            self.report_status("completed", state.review_result)

            return state

        except Exception as e:
            # 上报错误
            state.error = str(e)
            self.report_status("failed", {"error": str(e)})
            return state

    async def check_compliance(
        self,
        agent_output: dict,
        constraints: list[str]
    ) -> ReviewResult:
        """检查输出是否符合约束"""
        violations = []

        # 1. 检查代码是否违反约束
        if "code" in agent_output:
            code_violations = await self._check_code_compliance(
                agent_output["code"],
                constraints
            )
            violations.extend(code_violations)

        # 2. 检查文件修改是否合规
        if "files_changed" in agent_output:
            file_violations = self._check_file_compliance(
                agent_output["files_changed"],
                constraints
            )
            violations.extend(file_violations)

        passed = len(violations) == 0
        summary = self._generate_summary(passed, violations)

        return ReviewResult(
            passed=passed,
            violations=violations,
            summary=summary
        )

    async def _check_code_compliance(
        self,
        code: str,
        constraints: list[str]
    ) -> list[dict]:
        """检查代码是否符合约束"""
        violations = []

        if not constraints:
            return violations

        # 使用LLM进行代码审查
        constraints_text = "\n".join(f"- {c}" for c in constraints)
        messages = [
            {"role": "system", "content": """你是一个代码审查器。请检查代码是否违反以下约束。
返回JSON格式的违规列表，如果没有违规返回空数组。
格式：[{"constraint": "违反的约束", "detail": "具体违规描述", "severity": "high/medium/low"}]"""},
            {"role": "user", "content": f"约束：\n{constraints_text}\n\n代码：\n{code}\n\n请检查违规："}
        ]

        response = await self.llm.chat(messages, temperature=0)

        # 解析响应（实际应使用JSON解析）
        try:
            # 尝试提取JSON部分
            if "[" in response and "]" in response:
                start = response.index("[")
                end = response.rindex("]") + 1
                violations = json.loads(response[start:end])
        except (json.JSONDecodeError, ValueError):
            pass

        return violations

    def _check_file_compliance(
        self,
        files_changed: list[dict],
        constraints: list[str]
    ) -> list[dict]:
        """检查文件修改是否合规"""
        violations = []

        # 检查是否修改了禁止修改的文件
        forbidden_patterns = ["settings.json", ".env", "*.key", "*.pem"]

        for file_info in files_changed:
            file_path = file_info.get("path", "")
            for pattern in forbidden_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    violations.append({
                        "constraint": "禁止修改敏感文件",
                        "detail": f"尝试修改禁止的文件: {file_path}",
                        "severity": "high"
                    })

        return violations

    def _generate_summary(self, passed: bool, violations: list[dict]) -> str:
        """生成审查摘要"""
        if passed:
            return "约束合规检查通过"

        high_count = sum(1 for v in violations if v.get("severity") == "high")
        medium_count = sum(1 for v in violations if v.get("severity") == "medium")
        low_count = sum(1 for v in violations if v.get("severity") == "low")

        parts = []
        if high_count:
            parts.append(f"{high_count}个高严重性违规")
        if medium_count:
            parts.append(f"{medium_count}个中严重性违规")
        if low_count:
            parts.append(f"{low_count}个低严重性违规")

        return f"发现{'、'.join(parts)}，需要修正"

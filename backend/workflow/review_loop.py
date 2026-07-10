"""
Review 修正循环 — 自动修正循环逻辑

当 Review Agent 发现违规时:
1. 将违规信息反馈给 Planner
2. Planner 重新生成代码
3. 重复直到通过或达到最大修正次数
4. 超过最大次数可回滚到修改前快照
"""
from __future__ import annotations
from typing import Optional, Callable, Any

from .state import PipelineState


class ReviewLoop:
    """Review 修正循环管理器"""

    def __init__(
        self,
        max_retries: int = 3,
        auto_fix: bool = True,
        auto_rollback: bool = True,
        on_fix_callback: Callable = None,
    ):
        """
        Args:
            max_retries: 最大修正次数
            auto_fix: 是否自动修正
            auto_rollback: 修正失败是否自动回滚
            on_fix_callback: 修正回调函数
        """
        self.max_retries = max_retries
        self.auto_fix = auto_fix
        self.auto_rollback = auto_rollback
        self.on_fix_callback = on_fix_callback

    async def run(
        self,
        state: PipelineState,
        review_fn: Callable,
        fix_fn: Callable,
        rollback_fn: Callable = None,
    ) -> PipelineState:
        """
        执行 Review 修正循环

        Args:
            state: 当前工作流状态
            review_fn: Review 函数 (state) -> state
            fix_fn: 修正函数 (state) -> state
            rollback_fn: 回滚函数 (state) -> state (可选)

        Returns:
            修正后的状态
        """
        for attempt in range(self.max_retries):
            # 执行 Review
            state = await review_fn(state)

            # Review 通过
            if state.review_result and state.review_result.get("passed", True):
                return state

            # 不自动修正，直接返回
            if not self.auto_fix:
                state.error = (
                    f"Review 未通过: {state.review_result.get('violations', [])}"
                )
                return state

            # 准备修正
            violations = state.review_result.get("violations", [])
            fix_prompt = self._build_fix_prompt(violations)

            # 将修正请求反馈给上游
            state.user_input = fix_prompt
            state.retry_count += 1

            # 执行修正
            state = await fix_fn(state)

            # 检查 Tester 是否通过
            if state.test_result and state.test_result.get("status") == "failed":
                break

            # 回调通知
            if self.on_fix_callback:
                await self.on_fix_callback(state, attempt + 1)

        # 达到最大修正次数
        if self.auto_rollback and rollback_fn:
            state = await rollback_fn(state)
            state.error = "修正失败，已自动回滚到修改前状态"
        else:
            state.error = f"已达最大修正次数({self.max_retries})，请手动处理"

        return state

    def _build_fix_prompt(self, violations: list[dict]) -> str:
        """构建修正提示词"""
        lines = ["请修正以下违规项："]
        for v in violations:
            constraint = v.get("constraint", "")
            detail = v.get("detail", "")
            severity = v.get("severity", "")
            lines.append(f"- [{severity}] {constraint}: {detail}")
        return "\n".join(lines)


class ReviewResult:
    """Review 结果数据类"""

    def __init__(self, passed: bool, violations: list[dict] = None):
        self.passed = passed
        self.violations = violations or []

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "violations": self.violations,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewResult":
        return cls(
            passed=data.get("passed", True),
            violations=data.get("violations", []),
        )

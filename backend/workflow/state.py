"""
PipelineState — 贯穿整个工作流的状态数据结构

等价于 LangGraph 的 StateGraph 设计，通过状态传递实现节点间通信。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PipelineState:
    """贯穿整个工作流的状态数据结构"""

    # === 输入 ===
    user_input: str = ""
    session_id: str = ""
    project: str = ""

    # === Constraint Agent 输出 ===
    constraints: list[str] = field(default_factory=list)
    constraint_summary: str = ""

    # === RAG 输出 ===
    rag_context: str = ""

    # === Memory 上下文 ===
    memory_context: dict = field(default_factory=dict)
    # 结构: {"global": "...", "project": "...", "task": "...", "checkpoint": "..."}

    # === Planner 输出 ===
    plan: Optional[dict] = None
    # 结构: {"tasks": [...], "delegated_agent": "simple-coder", "reason": "..."}

    # === 子 Agent 输出 ===
    agent_output: Optional[dict] = None
    # 结构: {"agent": "complex-coder", "files_changed": [...], "code": "..."}

    # === Tester 输出 ===
    test_result: Optional[dict] = None
    # 结构: {"status": "passed", "tests": 5, "errors": [...]}

    # === Review Agent 输出 ===
    review_result: Optional[dict] = None
    # 结构: {"passed": bool, "violations": [...]}

    # === 流程控制 ===
    current_step: str = "init"
    approval_pending: bool = False
    approval_result: Optional[bool] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    done: bool = False

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "user_input": self.user_input,
            "session_id": self.session_id,
            "project": self.project,
            "constraints": self.constraints,
            "constraint_summary": self.constraint_summary,
            "rag_context": self.rag_context,
            "memory_context": self.memory_context,
            "plan": self.plan,
            "agent_output": self.agent_output,
            "test_result": self.test_result,
            "review_result": self.review_result,
            "current_step": self.current_step,
            "approval_pending": self.approval_pending,
            "approval_result": self.approval_result,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error": self.error,
            "done": self.done,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PipelineState":
        """从字典创建状态"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

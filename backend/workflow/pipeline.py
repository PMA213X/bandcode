"""
工作流管线 — 主管线，8个节点顺序执行

节点执行顺序:
1. 约束检索 (Constraint Agent)
2. RAG 检索
3. Prompt 构建
4. Planner 调度
5. 审批检查
6. 子 Agent 执行
7. Tester 验证
8. Review 审查
"""
from __future__ import annotations
import asyncio
from typing import Callable, Optional, Any

from .state import PipelineState


# 工作流配置默认值
DEFAULT_CONFIG = {
    "开启约束智能检索": True,
    "开启自动约束检查": True,
    "自动修正": True,
    "最大修正次数": 3,
    "修正失败自动回滚": True,
    "自动更新文档": True,
    "Git提交建议": True,
    "审批模式": True,
}


class Pipeline:
    """主工作流管线"""

    def __init__(self, config: dict = None):
        self.config = config or DEFAULT_CONFIG.copy()
        self.nodes: list[Callable] = []
        self._init_default_nodes()

    def _init_default_nodes(self) -> None:
        """初始化默认节点列表"""
        self.nodes = [
            self.node_constraint,
            self.node_rag,
            self.node_prompt_build,
            self.node_planner,
            self.node_approval,
            self.node_subagent,
            self.node_tester,
            self.node_review,
        ]

    # ==================== 节点函数 ====================

    async def node_constraint(self, state: PipelineState) -> PipelineState:
        """节点1: 约束检索 — Constraint Agent 从 Memory 中筛选相关约束"""
        if not self.config.get("开启约束智能检索", True):
            return state

        state.current_step = "constraint"
        # TODO: 调用 Constraint Agent
        # constraint_agent = AgentManager.get("constraint")
        # state = await constraint_agent.run(state)
        return state

    async def node_rag(self, state: PipelineState) -> PipelineState:
        """节点2: RAG 检索 — 从 ChromaDB 检索相关知识库文档"""
        state.current_step = "rag"
        # TODO: 调用 RAG 检索器
        # retriever = RAGRetriever(...)
        # state.rag_context = await retriever.search(state.user_input)
        return state

    async def node_prompt_build(self, state: PipelineState) -> PipelineState:
        """节点3: Prompt 构建 — 将各层上下文组装为完整 Prompt"""
        state.current_step = "prompt_build"
        # TODO: 调用 Prompt Builder
        # builder = PromptBuilder()
        # state.messages = builder.build(...)
        return state

    async def node_planner(self, state: PipelineState) -> PipelineState:
        """节点4: Planner 调度 — 需求分析、任务拆解、选择子 Agent"""
        state.current_step = "planner"
        # TODO: 调用 Planner Agent
        # planner = AgentManager.get("planner")
        # state = await planner.run(state)
        return state

    async def node_approval(self, state: PipelineState) -> PipelineState:
        """节点5: 审批检查 — 高风险操作请求用户确认"""
        if not self.config.get("审批模式", True):
            return state

        state.current_step = "approval"
        state.approval_pending = True
        # TODO: 通过 SSE 发送审批请求，等待用户响应
        # await sse.send("approval_required", {...})
        # state.approval_result = await wait_for_approval()
        # state.approval_pending = False
        return state

    async def node_subagent(self, state: PipelineState) -> PipelineState:
        """节点6: 子 Agent 执行 — SimpleCoder 或 ComplexCoder 执行代码生成"""
        state.current_step = "subagent"

        # 确定使用哪个子 Agent
        agent_name = "simple-coder"
        if state.plan and "delegated_agent" in state.plan:
            agent_name = state.plan["delegated_agent"]

        # TODO: 调用子 Agent
        # agent = AgentManager.get(agent_name)
        # state = await agent.run(state)
        return state

    async def node_tester(self, state: PipelineState) -> PipelineState:
        """节点7: Tester 验证 — 编译检查、测试执行、静态分析"""
        state.current_step = "tester"
        # TODO: 调用 Tester Agent
        # tester = AgentManager.get("tester")
        # state = await tester.run(state)
        return state

    async def node_review(self, state: PipelineState) -> PipelineState:
        """节点8: Review 审查 — 检查输出是否违反项目约束"""
        if not self.config.get("开启自动约束检查", True):
            return state

        state.current_step = "review"
        # TODO: 调用 Review Agent
        # review = AgentManager.get("review")
        # state = await review.run(state)
        return state

    # ==================== 主管线执行 ====================

    async def run(self, state: PipelineState) -> PipelineState:
        """执行主管线"""
        for node in self.nodes:
            if state.done or state.error:
                break

            try:
                state = await node(state)
            except Exception as e:
                state.error = f"节点 {node.__name__} 执行失败: {str(e)}"
                break

        return state

    async def run_with_review_loop(self, state: PipelineState) -> PipelineState:
        """执行主管线（带 Review 修正循环）"""
        for attempt in range(state.max_retries):
            state = await self.run()

            # 如果 Review 失败且开启了自动修正
            if (
                state.review_result
                and not state.review_result.get("passed", True)
                and self.config.get("自动修正", True)
            ):
                state.retry_count += 1
                # 将违规信息反馈给 Planner 重新生成
                violations = state.review_result.get("violations", [])
                state.user_input = (
                    f"请修正以下违规项：\n"
                    + "\n".join(f"- {v.get('detail', '')}" for v in violations)
                )
                continue

            break

        return state

    # ==================== 配置管理 ====================

    def update_config(self, key: str, value: Any) -> None:
        """更新配置项"""
        self.config[key] = value

    def get_config(self, key: str, default=None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)

import type {
  SSEEvent,
  SSEEventType,
  AgentStartEvent,
  ConstraintResultEvent,
  PlanEvent,
  ApprovalRequiredEvent,
  ToolCallEvent,
  CodeEvent,
  TestResultEvent,
  ReviewResultEvent,
  MemoryUpdateEvent,
  DoneEvent,
  ErrorEvent,
} from "../types";

export function isAgentStart(event: SSEEvent): event is SSEEvent & { data: AgentStartEvent } {
  return event.type === "agent_start";
}

export function isConstraintResult(event: SSEEvent): event is SSEEvent & { data: ConstraintResultEvent } {
  return event.type === "constraint_result";
}

export function isPlan(event: SSEEvent): event is SSEEvent & { data: PlanEvent } {
  return event.type === "plan";
}

export function isApprovalRequired(event: SSEEvent): event is SSEEvent & { data: ApprovalRequiredEvent } {
  return event.type === "approval_required";
}

export function isToolCall(event: SSEEvent): event is SSEEvent & { data: ToolCallEvent } {
  return event.type === "tool_call";
}

export function isCode(event: SSEEvent): event is SSEEvent & { data: CodeEvent } {
  return event.type === "code";
}

export function isTestResult(event: SSEEvent): event is SSEEvent & { data: TestResultEvent } {
  return event.type === "test_result";
}

export function isReviewResult(event: SSEEvent): event is SSEEvent & { data: ReviewResultEvent } {
  return event.type === "review_result";
}

export function isMemoryUpdate(event: SSEEvent): event is SSEEvent & { data: MemoryUpdateEvent } {
  return event.type === "memory_update";
}

export function isDone(event: SSEEvent): event is SSEEvent & { data: DoneEvent } {
  return event.type === "done";
}

export function isError(event: SSEEvent): event is SSEEvent & { data: ErrorEvent } {
  return event.type === "error";
}

const EVENT_LABELS: Record<SSEEventType, string> = {
  agent_start: "Agent 启动",
  constraint_result: "约束检索",
  plan: "任务规划",
  approval_required: "等待审批",
  approval_response: "审批响应",
  tool_call: "工具调用",
  code: "代码生成",
  test_result: "测试结果",
  review_result: "审查结果",
  memory_update: "记忆更新",
  done: "完成",
  error: "错误",
};

export function getEventLabel(type: SSEEventType): string {
  return EVENT_LABELS[type] || type;
}

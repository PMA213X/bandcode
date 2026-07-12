// 导入所有 SSE 事件类型定义
import type {
  SSEEvent,                  // SSE 事件通用接口
  SSEEventType,              // SSE 事件类型枚举
  AgentStartEvent,           // Agent 启动事件数据
  ConstraintResultEvent,     // 约束检索结果事件数据
  PlanEvent,                 // 计划事件数据
  ApprovalRequiredEvent,     // 审批请求事件数据
  ToolCallEvent,             // 工具调用事件数据
  CodeEvent,                 // 代码生成事件数据
  TestResultEvent,           // 测试结果事件数据
  ReviewResultEvent,         // 审查结果事件数据
  MemoryUpdateEvent,         // Memory 更新事件数据
  DoneEvent,                 // 完成事件数据
  ErrorEvent,                // 错误事件数据
} from "../types";

/**
 * SSE 事件类型守卫函数集合
 * 使用 TypeScript 类型谓词（type predicate）实现类型窄化
 * 在运行时检查事件类型，同时在编译时提供类型安全
 */

/**
 * 判断是否为 Agent 启动事件
 * @param event - SSE 事件对象
 * @returns 类型谓词，表明 data 是否为 AgentStartEvent
 */
export function isAgentStart(event: SSEEvent): event is SSEEvent & { data: AgentStartEvent } {
  return event.type === "agent_start";
}

/**
 * 判断是否为约束检索结果事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isConstraintResult(event: SSEEvent): event is SSEEvent & { data: ConstraintResultEvent } {
  return event.type === "constraint_result";
}

/**
 * 判断是否为计划事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isPlan(event: SSEEvent): event is SSEEvent & { data: PlanEvent } {
  return event.type === "plan";
}

/**
 * 判断是否为审批请求事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isApprovalRequired(event: SSEEvent): event is SSEEvent & { data: ApprovalRequiredEvent } {
  return event.type === "approval_required";
}

/**
 * 判断是否为工具调用事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isToolCall(event: SSEEvent): event is SSEEvent & { data: ToolCallEvent } {
  return event.type === "tool_call";
}

/**
 * 判断是否为代码生成事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isCode(event: SSEEvent): event is SSEEvent & { data: CodeEvent } {
  return event.type === "code";
}

/**
 * 判断是否为测试结果事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isTestResult(event: SSEEvent): event is SSEEvent & { data: TestResultEvent } {
  return event.type === "test_result";
}

/**
 * 判断是否为审查结果事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isReviewResult(event: SSEEvent): event is SSEEvent & { data: ReviewResultEvent } {
  return event.type === "review_result";
}

/**
 * 判断是否为 Memory 更新事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isMemoryUpdate(event: SSEEvent): event is SSEEvent & { data: MemoryUpdateEvent } {
  return event.type === "memory_update";
}

/**
 * 判断是否为完成事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isDone(event: SSEEvent): event is SSEEvent & { data: DoneEvent } {
  return event.type === "done";
}

/**
 * 判断是否为错误事件
 * @param event - SSE 事件对象
 * @returns 类型谓词
 */
export function isError(event: SSEEvent): event is SSEEvent & { data: ErrorEvent } {
  return event.type === "error";
}

/**
 * SSE 事件类型中文标签映射
 * 用于在界面上显示事件的中文名称
 */
const EVENT_LABELS: Record<SSEEventType, string> = {
  agent_start: "Agent 启动",        // Agent 开始执行任务
  constraint_result: "约束检索",    // Constraint Agent 检索结果
  plan: "任务规划",                 // Planner 输出任务计划
  approval_required: "等待审批",    // 需要用户确认高风险操作
  approval_response: "审批响应",    // 用户的审批响应
  tool_call: "工具调用",            // Agent 调用工具
  code: "代码生成",                 // Agent 生成代码
  test_result: "测试结果",          // Tester 测试结果
  review_result: "审查结果",        // Review Agent 审查结果
  memory_update: "记忆更新",        // Memory 层级更新
  done: "完成",                     // 任务完成
  error: "错误",                    // 发生错误
};

/**
 * 获取事件类型的中文标签
 * @param type - SSE 事件类型
 * @returns 中文标签，如果没有映射则返回原类型名
 */
export function getEventLabel(type: SSEEventType): string {
  return EVENT_LABELS[type] || type;
}

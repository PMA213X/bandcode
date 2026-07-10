// === 通用 API 响应格式 ===

export interface ApiResponse<T> {
  code: number;
  data: T;
  message: string;
}

// === 用户相关 ===

export interface CreateUserRequest {
  username: string;
  preferences?: {
    language?: string;
    theme?: string;
  };
}

export interface CreateUserResponse {
  user_id: string;
  username: string;
  created_at: string;
}

// === 聊天相关 ===

export interface ChatStreamRequest {
  session_id: string;
  project: string;
  message: string;
  options?: {
    agent?: string;
    workflow?: string;
  };
}

export interface ChatHistoryRequest {
  session_id: string;
  limit?: number;
  offset?: number;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  agent?: string;
  content: string;
  created_at: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessage[];
  total: number;
  has_more: boolean;
}

// === 项目相关 ===

export interface ProjectInitRequest {
  project_name: string;
  path: string;
  language?: string;
  framework?: string;
}

export interface ProjectInitResponse {
  project: string;
  mimo_dir: string;
  structure: Record<string, string>;
}

// === 设置相关 ===

export interface SettingsResponse {
  模型设置: Record<string, string>;
  "Agent 设置": Record<string, any>;
  "Memory 设置": Record<string, any>;
  "Workflow 设置": Record<string, any>;
  "RAG 设置": Record<string, any>;
  "Tool 设置": Record<string, any>;
}

export interface UpdateSettingsRequest {
  section: string;
  key: string;
  value: any;
}

export interface UpdateSettingsResponse {
  section: string;
  key: string;
  old_value: any;
  new_value: any;
}

// === Memory 相关 ===

export interface MemoryRequest {
  project: string;
  layer: string;
}

export interface MemoryResponse {
  layer: string;
  content: string;
  updated_at: string;
}

// === 工具相关 ===

export interface ToolCallRequest {
  tool: string;
  args: Record<string, any>;
}

export interface ToolCallResponse {
  tool: string;
  success: boolean;
  result: string;
}

// === SSE 事件类型 ===

export type SSEEventType =
  | "agent_start"
  | "constraint_result"
  | "plan"
  | "approval_required"
  | "approval_response"
  | "tool_call"
  | "code"
  | "test_result"
  | "review_result"
  | "memory_update"
  | "done"
  | "error";

export interface AgentStartEvent {
  agent: string;
  status: string;
}

export interface ConstraintResultEvent {
  constraints: string[];
  summary: string;
}

export interface PlanEvent {
  tasks: string[];
  delegated_agent: string;
}

export interface ApprovalRequiredEvent {
  plan: string;
  agent: string;
  reason: string;
}

export interface ToolCallEvent {
  tool: string;
  args: Record<string, any>;
}

export interface CodeEvent {
  file: string;
  content: string;
}

export interface TestResultEvent {
  status: "passed" | "failed";
  tests_total: number;
  tests_passed: number;
  errors?: Array<{
    file: string;
    line: number;
    error: string;
    suggestion: string;
  }>;
}

export interface ReviewResultEvent {
  status: "passed" | "failed";
  violations: Array<{
    constraint: string;
    severity: string;
    detail: string;
  }>;
}

export interface MemoryUpdateEvent {
  layers: string[];
  message: string;
}

export interface DoneEvent {
  session_id: string;
  summary: string;
}

export interface ErrorEvent {
  message: string;
}

export type SSEEventData =
  | AgentStartEvent
  | ConstraintResultEvent
  | PlanEvent
  | ApprovalRequiredEvent
  | ToolCallEvent
  | CodeEvent
  | TestResultEvent
  | ReviewResultEvent
  | MemoryUpdateEvent
  | DoneEvent
  | ErrorEvent;

export interface SSEEvent {
  type: SSEEventType;
  data: SSEEventData;
}

/**
 * BandCode 前端 API 类型定义
 * 定义所有与后端通信的请求/响应数据结构
 * 与后端 Pydantic 模型保持一致
 */

// ============================================================
// 通用 API 响应格式
// ============================================================

/**
 * 统一 API 响应格式
 * 所有后端接口都返回此格式
 * @type T - 响应数据的类型
 */
export interface ApiResponse<T> {
  code: number;    // 状态码：0 表示成功，非 0 表示错误
  data: T;         // 响应数据，类型由泛型 T 决定
  message: string; // 响应消息
}

// ============================================================
// 用户相关类型
// ============================================================

/**
 * 创建用户请求体
 * POST /api/users/create
 */
export interface CreateUserRequest {
  username: string;    // 用户名
  preferences?: {      // 用户偏好设置（可选）
    language?: string; // 语言偏好（如 zh-CN）
    theme?: string;    // 主题偏好（如 dark/light）
  };
}

/**
 * 创建用户响应数据
 */
export interface CreateUserResponse {
  user_id: string;     // 用户 ID
  username: string;    // 用户名
  created_at: string;  // 创建时间（ISO 8601 格式）
}

// ============================================================
// 聊天相关类型
// ============================================================

/**
 * 流式聊天请求体
 * POST /api/chat/stream（SSE）
 */
export interface ChatStreamRequest {
  session_id: string;  // 会话 ID
  project: string;     // 项目名称
  message: string;     // 用户消息
  options?: {          // 可选配置
    agent?: string;    // 指定 Agent（auto 为自动选择）
    workflow?: string; // 指定工作流
  };
}

/**
 * 聊天历史请求参数
 * GET /api/chat/history
 */
export interface ChatHistoryRequest {
  session_id: string;  // 会话 ID
  limit?: number;      // 返回数量限制
  offset?: number;     // 偏移量（分页）
}

/**
 * 聊天消息对象
 */
export interface ChatMessage {
  id: number;            // 消息 ID
  role: "user" | "assistant";  // 角色：用户或助手
  agent?: string;        // 处理此消息的 Agent 名称
  content: string;       // 消息内容
  created_at: string;    // 创建时间
}

/**
 * 聊天历史响应数据
 */
export interface ChatHistoryResponse {
  session_id: string;    // 会话 ID
  messages: ChatMessage[];  // 消息列表
  total: number;         // 总消息数
  has_more: boolean;     // 是否有更多消息
}

// ============================================================
// 项目相关类型
// ============================================================

/**
 * 项目初始化请求体
 * POST /api/project/init
 */
export interface ProjectInitRequest {
  project_name: string;  // 项目名称
  path: string;          // 项目路径
  language?: string;     // 编程语言
  framework?: string;    // 框架
}

/**
 * 项目初始化响应数据
 */
export interface ProjectInitResponse {
  project: string;       // 项目名称
  mimo_dir: string;      // .mimo 目录路径
  structure: Record<string, string>;  // 创建的目录结构
}

/**
 * 项目状态响应数据
 * GET /api/project/status
 */
export interface ProjectStatusResponse {
  name: string;          // 项目名称
  version: string;       // 版本号
  agents: string[];      // 可用 Agent 列表
  memory_layers: string[];  // Memory 层级列表
  tools: string[];       // 可用工具列表
}

// ============================================================
// 设置相关类型
// ============================================================

/**
 * 设置响应数据
 * GET /api/settings
 */
export interface SettingsResponse {
  模型设置: Record<string, string>;     // 模型配置
  "Agent 设置": Record<string, any>;    // Agent 配置
  "Memory 设置": Record<string, any>;   // Memory 配置
  "Workflow 设置": Record<string, any>; // Workflow 配置
  "RAG 设置": Record<string, any>;      // RAG 配置
  "Tool 设置": Record<string, any>;     // Tool 配置
}

/**
 * 更新设置请求体
 * POST /api/settings
 */
export interface UpdateSettingsRequest {
  section: string;       // 设置分类（如"模型设置"）
  key: string;           // 设置键名
  value: any;            // 新的设置值
}

/**
 * 更新设置响应数据
 */
export interface UpdateSettingsResponse {
  section: string;       // 设置分类
  key: string;           // 设置键名
  old_value: any;        // 旧值
  new_value: any;        // 新值
}

// ============================================================
// Memory 相关类型
// ============================================================

/**
 * Memory 查询请求参数
 * GET /api/memory
 */
export interface MemoryRequest {
  project: string;       // 项目名称
  layer: string;         // Memory 层级
}

/**
 * Memory 查询响应数据
 */
export interface MemoryResponse {
  layer: string;         // Memory 层级
  content: string;       // Memory 内容
  updated_at: string;    // 更新时间
}

// ============================================================
// 工具相关类型
// ============================================================

/**
 * 工具调用请求体
 * POST /api/tools/call
 */
export interface ToolCallRequest {
  tool: string;          // 工具名称
  args: Record<string, any>;  // 工具参数
}

/**
 * 工具调用响应数据
 */
export interface ToolCallResponse {
  tool: string;          // 工具名称
  success: boolean;      // 是否成功
  result: string;        // 执行结果
}

/**
 * 工具定义
 * GET /api/tools/list
 */
export interface ToolDefinition {
  name: string;          // 工具名称
  description: string;   // 工具描述
  parameters: Record<string, { type: string; description: string }>;  // 参数定义
}

// ============================================================
// SSE 事件类型
// ============================================================

/**
 * SSE 事件类型枚举
 * 定义所有可能的 Server-Sent Events 事件类型
 */
export type SSEEventType =
  | "agent_start"        // Agent 开始执行
  | "constraint_result"  // 约束检索结果
  | "plan"               // Planner 输出计划
  | "approval_required"  // 需要用户审批
  | "approval_response"  // 用户审批响应
  | "tool_call"          // 工具调用
  | "code"               // 代码生成
  | "test_result"        // 测试结果
  | "review_result"      // 审查结果
  | "memory_update"      // Memory 更新
  | "done"               // 任务完成
  | "error";             // 错误

// ============================================================
// SSE 事件数据接口
// ============================================================

/**
 * Agent 启动事件数据
 */
export interface AgentStartEvent {
  agent: string;         // Agent 名称
  status: string;        // 状态描述
}

/**
 * 约束检索结果事件数据
 */
export interface ConstraintResultEvent {
  constraints: string[]; // 检索到的约束列表
  summary: string;       // 约束摘要
}

/**
 * 计划事件数据
 */
export interface PlanEvent {
  tasks: string[];       // 任务列表
  delegated_agent: string;  // 委派的 Agent
}

/**
 * 审批请求事件数据
 */
export interface ApprovalRequiredEvent {
  plan: string;          // 执行计划
  agent: string;         // 即将执行的 Agent
  reason: string;        // 需要审批的原因
}

/**
 * 工具调用事件数据
 */
export interface ToolCallEvent {
  tool: string;          // 工具名称
  args: Record<string, any>;  // 工具参数
}

/**
 * 代码生成事件数据
 */
export interface CodeEvent {
  file: string;          // 文件路径
  content: string;       // 代码内容
}

/**
 * 测试结果事件数据
 */
export interface TestResultEvent {
  status: "passed" | "failed";  // 测试状态
  tests_total: number;          // 总测试数
  tests_passed: number;         // 通过数
  errors?: Array<{              // 错误列表（可选）
    file: string;               // 错误文件
    line: number;               // 错误行号
    error: string;              // 错误信息
    suggestion: string;         // 修复建议
  }>;
}

/**
 * 审查结果事件数据
 */
export interface ReviewResultEvent {
  status: "passed" | "failed";  // 审查状态
  violations: Array<{           // 违规列表
    constraint: string;         // 违反的约束
    severity: string;           // 严重程度
    detail: string;             // 详细说明
  }>;
}

/**
 * Memory 更新事件数据
 */
export interface MemoryUpdateEvent {
  layers: string[];      // 更新的 Memory 层级
  message: string;       // 更新消息
}

/**
 * 完成事件数据
 */
export interface DoneEvent {
  session_id: string;    // 会话 ID
  summary: string;       // 任务摘要
}

/**
 * 错误事件数据
 */
export interface ErrorEvent {
  message: string;       // 错误消息
}

// ============================================================
// SSE 事件联合类型
// ============================================================

/**
 * SSE 事件数据联合类型
 * 所有可能的事件数据类型
 */
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

/**
 * SSE 事件对象接口
 * 包含事件类型和事件数据
 */
export interface SSEEvent {
  type: SSEEventType;    // 事件类型
  data: SSEEventData;    // 事件数据
}

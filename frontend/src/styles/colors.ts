/**
 * colors.ts - 终端色彩定义
 * 定义所有颜色常量和图标
 */

/**
 * 颜色常量
 */
export const COLORS = {
  // 状态颜色
  success: "green",
  error: "red",
  warning: "yellow",
  info: "cyan",

  // Agent颜色
  planner: "blue",
  simpleCoder: "green",
  complexCoder: "magenta",
  tester: "yellow",
  constraint: "gray",
  review: "red",

  // UI颜色
  primary: "cyan",
  secondary: "gray",
  border: "white",
  text: "white",
  muted: "gray",

  // 消息颜色
  userMessage: "cyan",
  assistantMessage: "green",
  errorMessage: "red",
  systemMessage: "yellow",
};

/**
 * 图标常量
 */
export const ICONS = {
  success: "✅",
  error: "❌",
  warning: "⚠️",
  loading: "🔄",
  pending: "⏳",
  arrow: "▶",
  bullet: "•",
  separator: "─",
  settings: "⚙️",
  memory: "🧠",
  agent: "🤖",
  tool: "🔧",
  file: "📄",
  folder: "📁",
  search: "🔍",
  save: "💾",
  edit: "✏️",
  delete: "🗑️",
  add: "➕",
  remove: "➖",
  refresh: "🔄",
  check: "✓",
  cross: "✗",
};

/**
 * Agent颜色映射
 */
export const AGENT_COLORS: Record<string, string> = {
  constraint: COLORS.constraint,
  planner: COLORS.planner,
  "simple-coder": COLORS.simpleCoder,
  "complex-coder": COLORS.complexCoder,
  tester: COLORS.tester,
  review: COLORS.review,
};

/**
 * 状态颜色映射
 */
export const STATUS_COLORS: Record<string, string> = {
  success: COLORS.success,
  error: COLORS.error,
  warning: COLORS.warning,
  loading: COLORS.info,
  pending: COLORS.muted,
  running: COLORS.info,
  completed: COLORS.success,
  failed: COLORS.error,
};
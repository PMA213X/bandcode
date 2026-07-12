/**
 * API 错误类
 * 用于封装后端 API 返回的错误信息
 */
export class ApiError extends Error {
  /**
   * @param message - 错误消息
   * @param code - HTTP 状态码或业务错误码
   * @param endpoint - 请求的 API 端点路径
   */
  constructor(
    message: string,
    public code: number,
    public endpoint: string
  ) {
    super(message);
    this.name = "ApiError";  // 设置错误名称，便于 instanceof 判断
  }
}

/**
 * SSE 连接错误类
 * 用于封装 Server-Sent Events 连接相关的错误
 */
export class SSEConnectionError extends Error {
  /**
   * @param message - 错误消息
   * @param sessionId - 发生错误的会话 ID
   */
  constructor(
    message: string,
    public sessionId: string
  ) {
    super(message);
    this.name = "SSEConnectionError";  // 设置错误名称
  }
}

/**
 * 提取错误消息的工具函数
 * 统一处理不同类型的错误，返回可读的错误消息
 * @param error - 未知类型的错误对象
 * @returns 错误消息字符串
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;  // 标准 Error 对象
  if (typeof error === "string") return error;        // 字符串类型的错误
  return "未知错误";  // 兜底返回
}

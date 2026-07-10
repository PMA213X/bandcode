export class ApiError extends Error {
  constructor(
    message: string,
    public code: number,
    public endpoint: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class SSEConnectionError extends Error {
  constructor(
    message: string,
    public sessionId: string
  ) {
    super(message);
    this.name = "SSEConnectionError";
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message;
  if (typeof error === "string") return error;
  return "未知错误";
}

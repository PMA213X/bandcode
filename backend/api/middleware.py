"""
中间件模块

本模块实现了 FastAPI 中间件，包括：
1. 请求日志中间件 - 记录请求处理时间和状态
2. 安全头中间件 - 添加安全相关的 HTTP 响应头

中间件的作用：
- 在请求到达路由处理函数之前进行预处理
- 在响应返回客户端之前进行后处理
- 可以用于日志记录、认证、安全防护等
"""

# 导入时间处理模块
import time
# 导入 FastAPI 请求对象
from fastapi import Request
# 导入 Starlette 中间件基类
from starlette.middleware.base import BaseHTTPMiddleware
# 导入日志模块
from config.logging import get_logger

# 获取中间件专用的日志器
logger = get_logger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    
    记录每个 HTTP 请求的处理时间和状态码。
    用于性能监控和问题排查。
    
    功能：
    - 记录请求开始时间
    - 记录请求结束时间
    - 计算处理耗时
    - 将处理时间添加到响应头
    """
    
    async def dispatch(self, request: Request, call_next):
        # SSE 流式端点跳过中间件，避免 BaseHTTPMiddleware 缓冲响应
        if "/stream" in request.url.path:
            return await call_next(request)

        start_time = time.time()
        logger.info(f"请求开始: {request.method} {request.url.path}")
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"请求完成: {request.method} {request.url.path} "
            f"状态码={response.status_code} 耗时={process_time:.3f}s"
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全头中间件
    
    添加安全相关的 HTTP 响应头，提高应用的安全性。
    
    添加的安全头：
    - X-Content-Type-Options: 防止 MIME 类型嗅探
    - X-Frame-Options: 防止点击劫持
    - X-XSS-Protection: 启用 XSS 过滤
    """
    
    async def dispatch(self, request: Request, call_next):
        # SSE 流式端点跳过中间件，避免 BaseHTTPMiddleware 缓冲响应
        if "/stream" in request.url.path:
            return await call_next(request)

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

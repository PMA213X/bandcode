"""
全局错误处理
定义错误码和异常处理器
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Any


# ========== 错误码定义 ==========

class ErrorCode:
    """错误码定义"""

    SUCCESS = 0
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

    # 业务错误码
    USER_EXISTS = 1001
    TOOL_NOT_FOUND = 1002
    SETTINGS_ERROR = 1003
    MEMORY_ERROR = 1004
    AGENT_ERROR = 1005


class AppException(Exception):
    """应用异常"""

    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data


def create_error_response(code: int, message: str, data: Any = None) -> dict:
    """创建错误响应"""
    return {"code": code, "data": data, "message": message}


def create_success_response(data: Any = None, message: str = "ok") -> dict:
    """创建成功响应"""
    return {"code": 0, "data": data, "message": message}


def register_error_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=200,
            content=create_error_response(exc.code, exc.message, exc.data),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=200,
            content=create_error_response(
                ErrorCode.INTERNAL_ERROR, f"服务器内部错误: {str(exc)}"
            ),
        )

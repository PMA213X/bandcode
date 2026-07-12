"""
全局错误处理模块

本模块实现了全局异常处理功能，包括：
1. 错误码定义 - 统一的错误码体系
2. 自定义异常类 - AppException
3. 响应创建函数 - create_error_response, create_success_response
4. 全局异常处理器注册 - register_error_handlers

错误码体系：
- 0: 成功
- 400-509: HTTP 标准错误码
- 1001-1099: 业务错误码
"""

# 导入 FastAPI 框架
from fastapi import FastAPI, Request
# 导入 JSON 响应类
from fastapi.responses import JSONResponse
# 导入类型注解
from typing import Any


# ==================== 错误码定义 ====================

class ErrorCode:
    """
    错误码定义类
    
    定义了所有可能的错误码，包括：
    - HTTP 标准错误码（400-509）
    - 业务错误码（1001-1099）
    """
    
    # 成功
    SUCCESS = 0  # 操作成功
    
    # HTTP 标准错误码
    BAD_REQUEST = 400  # 请求参数错误
    UNAUTHORIZED = 401  # 未授权
    FORBIDDEN = 403  # 禁止访问
    NOT_FOUND = 404  # 资源不存在
    INTERNAL_ERROR = 500  # 服务器内部错误
    
    # 业务错误码
    USER_EXISTS = 1001  # 用户已存在
    TOOL_NOT_FOUND = 1002  # 工具不存在
    SETTINGS_ERROR = 1003  # 设置错误
    MEMORY_ERROR = 1004  # 记忆系统错误
    AGENT_ERROR = 1005  # Agent 错误


class AppException(Exception):
    """
    应用自定义异常类
    
    用于在业务逻辑中抛出异常，会被全局异常处理器捕获。
    
    Attributes:
        code: 错误码
        message: 错误信息
        data: 附加数据（可选）
    """
    
    def __init__(self, code: int, message: str, data: Any = None):
        """
        初始化异常
        
        Args:
            code: 错误码
            message: 错误信息
            data: 附加数据
        """
        self.code = code  # 错误码
        self.message = message  # 错误信息
        self.data = data  # 附加数据


def create_error_response(code: int, message: str, data: Any = None) -> dict:
    """
    创建错误响应
    
    Args:
        code: 错误码
        message: 错误信息
        data: 附加数据
    
    Returns:
        统一格式的错误响应字典
    """
    return {"code": code, "data": data, "message": message}


def create_success_response(data: Any = None, message: str = "ok") -> dict:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 提示信息
    
    Returns:
        统一格式的成功响应字典
    """
    return {"code": 0, "data": data, "message": message}


def register_error_handlers(app: FastAPI) -> None:
    """
    注册全局异常处理器
    
    将自定义异常和通用异常的处理器注册到 FastAPI 应用中。
    
    Args:
        app: FastAPI 应用实例
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """
        处理自定义应用异常
        
        当业务逻辑中抛出 AppException 时，会被这个处理器捕获。
        返回统一格式的错误响应。
        """
        return JSONResponse(
            status_code=200,  # 使用 200 状态码，通过 code 字段表示业务错误
            content=create_error_response(exc.code, exc.message, exc.data),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        处理通用异常
        
        当发生未捕获的异常时，会被这个处理器捕获。
        返回统一格式的错误响应，隐藏具体的错误细节。
        """
        return JSONResponse(
            status_code=200,  # 使用 200 状态码，通过 code 字段表示业务错误
            content=create_error_response(
                ErrorCode.INTERNAL_ERROR, f"服务器内部错误: {str(exc)}"
            ),
        )

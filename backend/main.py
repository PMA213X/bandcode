"""
BandCode 后端入口
FastAPI 应用框架搭建

本文件是后端服务的主入口，负责：
1. 创建 FastAPI 应用实例
2. 配置 CORS 跨域资源共享
3. 注册全局中间件（日志、安全头）
4. 注册全局异常处理器
5. 注册所有 API 路由
6. 启动 uvicorn 服务器
"""

# 导入 FastAPI 框架核心模块
from fastapi import FastAPI
# 导入 CORS 中间件，用于处理跨域请求
from fastapi.middleware.cors import CORSMiddleware
# 导入自定义错误处理器
from api.errors import register_error_handlers
# 导入自定义中间件：请求日志和安全头
from api.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
# 导入日志配置模块
from config.logging import setup_logging, get_logger

# 初始化日志系统
setup_logging()
# 获取名为 "bandcode" 的日志器实例
logger = get_logger("bandcode")

# 创建 FastAPI 应用实例
# title: API 文档标题
# description: API 文档描述
# version: API 版本号
app = FastAPI(
    title="BandCode",
    description="基于分层记忆与六智能体协作的 AI 编程助手",
    version="1.0.0",
)

# 配置 CORS 中间件
# allow_origins=["*"]: 允许所有来源的跨域请求
# allow_credentials: 允许携带认证信息（如 Cookie）
# allow_methods: 允许所有 HTTP 方法
# allow_headers: 允许所有请求头
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
# 注意：中间件的添加顺序很重要，后添加的先执行
# SecurityHeadersMiddleware: 添加安全响应头
# RequestLoggingMiddleware: 记录请求日志和处理时间
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# 注册全局异常处理器
# 捕获所有未处理的异常，返回统一格式的错误响应
register_error_handlers(app)


@app.get("/")
async def root():
    """
    根路由 - 健康检查接口
    
    返回服务运行状态和版本信息
    用于前端或监控系统检测服务是否正常运行
    """
    # 记录健康检查请求日志
    logger.info("健康检查请求")
    # 返回统一格式的成功响应
    return {
        "code": 0,  # 状态码，0 表示成功
        "data": {"status": "running", "version": "1.0.0"},  # 业务数据
        "message": "BandCode 后端服务运行中",  # 提示信息
    }


@app.get("/health")
async def health():
    """
    健康检查接口（备用）
    
    返回简单的健康状态
    用于负载均衡器或容器编排系统的健康检查
    """
    return {"code": 0, "data": {"status": "healthy"}, "message": "ok"}


# ==================== 注册 API 路由 ====================
# 每个路由模块负责一组相关的 API 接口
# prefix="/api" 表示所有路由都以 /api 开头

# 聊天 API：流式聊天（SSE）、聊天历史
from api.chat import router as chat_router
# 设置 API：获取和更新系统配置
from api.settings import router as settings_router
# Memory API：获取和搜索记忆数据
from api.memory import router as memory_router
# 项目 API：初始化项目、获取项目状态
from api.project import router as project_router
# 工具 API：调用内置工具
from api.tools import router as tools_router
# 用户 API：创建用户
from api.users import router as users_router
# 测试 API：模型测试
from api.test import router as test_router
# 工作区 API：获取和管理工作区路径
from api.workspace import router as workspace_router

# 将所有路由注册到应用中
app.include_router(chat_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(tools_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(test_router, prefix="/api")
app.include_router(workspace_router, prefix="/api")


# ==================== 启动服务器 ====================
if __name__ == "__main__":
    import uvicorn

    # 记录服务启动日志
    logger.info("BandCode 后端服务启动中...")
    # 启动 uvicorn 服务器
    # host="0.0.0.0": 监听所有网络接口
    # port=8000: 监听端口 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

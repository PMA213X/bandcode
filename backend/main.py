"""
BandCode 后端入口
FastAPI 应用框架搭建
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.errors import register_error_handlers
from api.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from config.logging import setup_logging, get_logger

# 设置日志
setup_logging()
logger = get_logger("bandcode")

# 创建 FastAPI 应用实例
app = FastAPI(
    title="BandCode",
    description="基于分层记忆与六智能体协作的 AI 编程助手",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# 注册全局异常处理
register_error_handlers(app)


@app.get("/")
async def root():
    """健康检查接口"""
    logger.info("健康检查请求")
    return {
        "code": 0,
        "data": {"status": "running", "version": "1.0.0"},
        "message": "BandCode 后端服务运行中",
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"code": 0, "data": {"status": "healthy"}, "message": "ok"}


# 注册路由
from api.chat import router as chat_router
from api.settings import router as settings_router
from api.memory import router as memory_router
from api.project import router as project_router
from api.tools import router as tools_router
from api.users import router as users_router

app.include_router(chat_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(tools_router, prefix="/api")
app.include_router(users_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn

    logger.info("BandCode 后端服务启动中...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

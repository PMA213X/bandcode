"""
API 路由模块
"""
from api.chat import router as chat_router
from api.settings import router as settings_router
from api.memory import router as memory_router
from api.project import router as project_router
from api.tools import router as tools_router
from api.users import router as users_router

__all__ = [
    "chat_router",
    "settings_router",
    "memory_router",
    "project_router",
    "tools_router",
    "users_router",
]

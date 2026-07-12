"""
用户 API 模块

本模块实现了用户管理相关的 API 接口，包括：
1. 创建用户 - POST /api/users/create
2. 获取用户列表 - GET /api/users/list

用户数据结构：
- user_id: 用户 ID
- username: 用户名
- created_at: 创建时间
"""

# 导入 FastAPI 路由和异常处理
from fastapi import APIRouter, HTTPException
# 导入 Pydantic 数据验证模型
from pydantic import BaseModel
# 导入类型注解
from typing import Optional
# 导入时间处理模块
from datetime import datetime

# 创建路由器，prefix="/users" 表示所有路由以 /users 开头
# tags=["用户"] 用于 API 文档分组
router = APIRouter(prefix="/users", tags=["用户"])


class CreateUserRequest(BaseModel):
    """
    创建用户请求模型
    
    与前端 types/api.ts 中的 CreateUserRequest 保持一致
    """
    username: str  # 用户名（必填）
    preferences: Optional[dict] = None  # 用户偏好设置（可选）


class UserResponse(BaseModel):
    """
    用户响应模型
    
    定义了用户数据的返回格式
    """
    user_id: str  # 用户 ID
    username: str  # 用户名
    created_at: str  # 创建时间


# 临时存储用户数据（后续会对接数据库）
# key 为 username，value 为用户信息
users_db: dict = {}


@router.post("/create")
async def create_user(request: CreateUserRequest):
    """
    创建用户接口
    
    创建一个新用户，用户名必须唯一。
    
    Args:
        request: 创建用户请求，包含用户名和可选的偏好设置
    
    Returns:
        包含新创建用户信息的响应
    
    Raises:
        HTTPException: 如果用户名已存在，返回 400 错误
    """
    # 检查用户名是否已存在
    if request.username in users_db:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 生成用户 ID
    user_id = f"user_{len(users_db) + 1}"
    # 创建用户对象
    user = {
        "user_id": user_id,  # 用户 ID
        "username": request.username,  # 用户名
        "created_at": datetime.now().isoformat(),  # 创建时间
    }
    # 存储到用户数据库
    users_db[request.username] = user

    # 返回统一格式的响应
    return {"code": 0, "data": user, "message": "用户创建成功"}


@router.get("/list")
async def list_users():
    """
    获取用户列表接口
    
    返回所有已创建的用户列表。
    
    Returns:
        包含用户列表的响应
    """
    # 返回统一格式的响应
    return {"code": 0, "data": list(users_db.values()), "message": "ok"}

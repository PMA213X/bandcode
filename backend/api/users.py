"""
用户 API
POST /api/users/create - 创建用户
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["用户"])


class CreateUserRequest(BaseModel):
    """创建用户请求"""

    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None


class UserResponse(BaseModel):
    """用户响应"""

    id: str
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None


# 临时存储（后续会对接数据库）
users_db: dict = {}


@router.post("/create")
async def create_user(request: CreateUserRequest):
    """
    创建用户
    """
    if request.username in users_db:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user_id = f"user_{len(users_db) + 1}"
    user = {
        "id": user_id,
        "username": request.username,
        "email": request.email,
        "display_name": request.display_name or request.username,
    }
    users_db[request.username] = user

    return {"code": 0, "data": user, "message": "用户创建成功"}


@router.get("/list")
async def list_users():
    """获取用户列表"""
    return {"code": 0, "data": list(users_db.values()), "message": "ok"}

"""
用户 API
POST /api/users/create - 创建用户
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/users", tags=["用户"])


class CreateUserRequest(BaseModel):
    """创建用户请求（与前端 types/api.ts 一致）"""

    username: str
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    """用户响应"""

    user_id: str
    username: str
    created_at: str


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
        "user_id": user_id,
        "username": request.username,
        "created_at": datetime.now().isoformat(),
    }
    users_db[request.username] = user

    return {"code": 0, "data": user, "message": "用户创建成功"}


@router.get("/list")
async def list_users():
    """获取用户列表"""
    return {"code": 0, "data": list(users_db.values()), "message": "ok"}

"""
设置 API
GET /api/settings - 获取设置
POST /api/settings - 更新设置
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from config.loader import get_config

router = APIRouter(prefix="/settings", tags=["设置"])


class UpdateSettingsRequest(BaseModel):
    """更新设置请求（与前端 types/api.ts 一致）"""

    section: str
    key: str
    value: Any


@router.get("")
async def get_settings():
    """
    获取全部设置
    返回格式与前端 SettingsResponse 一致
    """
    config = get_config()
    return {"code": 0, "data": config.settings, "message": "ok"}


@router.get("/{section}")
async def get_settings_section(section: str):
    """
    获取指定配置节
    """
    config = get_config()
    section_data = config.get_section(section)
    if not section_data:
        raise HTTPException(status_code=404, detail=f"配置节 '{section}' 不存在")
    return {"code": 0, "data": section_data, "message": "ok"}


@router.post("")
async def update_settings(request: UpdateSettingsRequest):
    """
    更新单个配置项
    返回旧值和新值
    """
    config = get_config()
    old_value = config.get(request.section, request.key)
    config.update(request.section, request.key, request.value)

    return {
        "code": 0,
        "data": {
            "section": request.section,
            "key": request.key,
            "old_value": old_value,
            "new_value": request.value,
        },
        "message": "设置已更新",
    }


@router.post("/reload")
async def reload_settings():
    """
    重新加载设置
    """
    config = get_config()
    config.reload()
    return {"code": 0, "data": None, "message": "设置已重新加载"}

"""
设置 API 模块

本模块实现了系统配置相关的 API 接口，包括：
1. 获取全部设置 - GET /api/settings
2. 获取指定配置节 - GET /api/settings/{section}
3. 更新单个配置项 - POST /api/settings
4. 重新加载设置 - POST /api/settings/reload

配置结构：
- 模型设置：AI 模型相关配置
- Agent 设置：智能体相关配置
- Memory 设置：记忆系统配置
- Workflow 设置：工作流配置
- RAG 设置：RAG 检索配置
- Tool 设置：工具系统配置
"""

# 导入 FastAPI 路由和异常处理
from fastapi import APIRouter, HTTPException
# 导入 Pydantic 数据验证模型
from pydantic import BaseModel
# 导入类型注解
from typing import Any
# 导入配置加载器
from config.loader import get_config

# 创建路由器，prefix="/settings" 表示所有路由以 /settings 开头
# tags=["设置"] 用于 API 文档分组
router = APIRouter(prefix="/settings", tags=["设置"])


class UpdateSettingsRequest(BaseModel):
    """
    更新设置请求模型
    
    与前端 types/api.ts 中的 UpdateSettingsRequest 保持一致
    """
    section: str  # 配置节名称，如 "模型设置"
    key: str  # 配置项键名，如 "默认模型"
    value: Any  # 配置项值，可以是任意类型


@router.get("")
async def get_settings():
    """
    获取全部设置接口
    
    返回所有配置节的内容，格式与前端 SettingsResponse 一致。
    
    Returns:
        包含所有配置的响应：
        - 模型设置: AI 模型相关配置
        - Agent 设置: 智能体相关配置
        - Memory 设置: 记忆系统配置
        - Workflow 设置: 工作流配置
        - RAG 设置: RAG 检索配置
        - Tool 设置: 工具系统配置
    """
    # 获取全局配置实例
    config = get_config()
    # 返回统一格式的响应
    return {"code": 0, "data": config.settings, "message": "ok"}


@router.get("/{section}")
async def get_settings_section(section: str):
    """
    获取指定配置节接口
    
    根据配置节名称返回该节的配置内容。
    
    Args:
        section: 配置节名称，如 "模型设置"
    
    Returns:
        包含指定配置节的响应
    
    Raises:
        HTTPException: 如果配置节不存在，返回 404 错误
    """
    # 获取全局配置实例
    config = get_config()
    # 获取指定配置节
    section_data = config.get_section(section)
    # 如果配置节不存在，抛出 404 异常
    if not section_data:
        raise HTTPException(status_code=404, detail=f"配置节 '{section}' 不存在")
    # 返回统一格式的响应
    return {"code": 0, "data": section_data, "message": "ok"}


@router.post("")
async def update_settings(request: UpdateSettingsRequest):
    """
    更新单个配置项接口
    
    更新指定配置节中的某个配置项，并返回旧值和新值。
    
    Args:
        request: 更新设置请求，包含 section、key、value
    
    Returns:
        包含更新结果的响应：
        - section: 配置节名称
        - key: 配置项键名
        - old_value: 更新前的值
        - new_value: 更新后的值
    """
    # 获取全局配置实例
    config = get_config()
    # 获取更新前的值
    old_value = config.get(request.section, request.key)
    # 更新配置项
    config.update(request.section, request.key, request.value)

    # 返回统一格式的响应
    return {
        "code": 0,
        "data": {
            "section": request.section,  # 配置节名称
            "key": request.key,  # 配置项键名
            "old_value": old_value,  # 更新前的值
            "new_value": request.value,  # 更新后的值
        },
        "message": "设置已更新",
    }


@router.post("/reload")
async def reload_settings():
    """
    重新加载设置接口
    
    从配置文件重新加载所有配置。
    用于在配置文件被外部修改后刷新配置。
    
    Returns:
        包含操作结果的响应
    """
    # 获取全局配置实例
    config = get_config()
    # 重新加载配置
    config.reload()
    # 返回统一格式的响应
    return {"code": 0, "data": None, "message": "设置已重新加载"}

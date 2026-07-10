"""
请求模型
与前端 types/api.ts 对齐
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class CreateUserRequest(BaseModel):
    """创建用户请求"""

    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    preferences: Optional[Dict[str, str]] = Field(None, description="用户偏好设置")


class ChatStreamRequest(BaseModel):
    """聊天流式请求"""

    session_id: str = Field(..., description="会话ID")
    project: str = Field(..., description="项目名称")
    message: str = Field(..., min_length=1, description="用户消息")
    options: Optional[Dict[str, Any]] = Field(None, description="选项")


class UpdateSettingsRequest(BaseModel):
    """更新设置请求"""

    section: str = Field(..., description="配置节名称")
    key: str = Field(..., description="配置项键名")
    value: Any = Field(..., description="配置项值")


class ProjectInitRequest(BaseModel):
    """初始化项目请求"""

    project_name: str = Field(..., min_length=1, description="项目名称")
    path: str = Field(..., description="项目路径")
    language: Optional[str] = Field(None, description="编程语言")
    framework: Optional[str] = Field(None, description="框架")


class ToolCallRequest(BaseModel):
    """工具调用请求"""

    tool: str = Field(..., description="工具名称")
    args: Dict[str, Any] = Field(default_factory=dict, description="工具参数")

"""
响应模型
统一响应格式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ApiResponse(BaseModel):
    """通用 API 响应"""

    code: int = Field(0, description="状态码，0表示成功")
    data: Optional[Any] = Field(None, description="响应数据")
    message: str = Field("ok", description="响应消息")


class UserResponse(BaseModel):
    """用户响应"""

    user_id: str
    username: str
    created_at: str


class ChatMessage(BaseModel):
    """聊天消息"""

    id: int
    role: str
    agent: Optional[str] = None
    content: str
    created_at: str


class ChatHistoryResponse(BaseModel):
    """聊天历史响应"""

    session_id: str
    messages: List[ChatMessage]
    total: int
    has_more: bool


class SettingsResponse(BaseModel):
    """设置响应"""

    模型设置: Dict[str, Any]
    Agent设置: Dict[str, Any] = Field(alias="Agent 设置")
    Memory设置: Dict[str, Any] = Field(alias="Memory 设置")
    Workflow设置: Dict[str, Any] = Field(alias="Workflow 设置")
    RAG设置: Dict[str, Any] = Field(alias="RAG 设置")
    Tool设置: Dict[str, Any] = Field(alias="Tool 设置")

    class Config:
        populate_by_name = True


class MemoryResponse(BaseModel):
    """Memory 响应"""

    layer: str
    content: str
    updated_at: str


class ProjectStatusResponse(BaseModel):
    """项目状态响应"""

    name: str
    version: str
    agents: List[str]
    memory_layers: List[str]
    tools: List[str]


class ToolResponse(BaseModel):
    """工具调用响应"""

    tool: str
    success: bool
    result: str

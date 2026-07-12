"""
响应模型模块

本模块定义了所有 API 接口的响应数据模型。
统一了响应格式，确保前后端数据结构一致。

响应格式：
{
    "code": 0,  # 状态码，0表示成功
    "data": {...},  # 响应数据
    "message": "ok"  # 提示信息
}
"""

# 导入 Pydantic 模型和字段定义
from pydantic import BaseModel, Field
# 导入类型注解
from typing import Optional, List, Dict, Any


class ApiResponse(BaseModel):
    """
    通用 API 响应模型
    
    所有 API 接口的响应都遵循这个格式。
    
    Attributes:
        code: 状态码，0表示成功
        data: 响应数据，可以是任意类型
        message: 提示信息
    """
    # 状态码：0表示成功，其他值表示错误
    code: int = Field(0, description="状态码，0表示成功")
    # 响应数据：可以是任意类型
    data: Optional[Any] = Field(None, description="响应数据")
    # 提示信息
    message: str = Field("ok", description="响应消息")


class UserResponse(BaseModel):
    """
    用户响应模型
    
    定义了用户数据的返回格式。
    
    Attributes:
        user_id: 用户 ID
        username: 用户名
        created_at: 创建时间
    """
    user_id: str  # 用户 ID
    username: str  # 用户名
    created_at: str  # 创建时间


class ChatMessage(BaseModel):
    """
    聊天消息模型
    
    定义了单条聊天消息的数据结构。
    
    Attributes:
        id: 消息 ID
        role: 消息角色（user/assistant）
        agent: 处理消息的 Agent（可选）
        content: 消息内容
        created_at: 创建时间
    """
    id: int  # 消息 ID
    role: str  # 消息角色
    agent: Optional[str] = None  # Agent 名称
    content: str  # 消息内容
    created_at: str  # 创建时间


class ChatHistoryResponse(BaseModel):
    """
    聊天历史响应模型
    
    定义了聊天历史的返回格式。
    
    Attributes:
        session_id: 会话 ID
        messages: 消息列表
        total: 消息总数
        has_more: 是否还有更多消息
    """
    session_id: str  # 会话 ID
    messages: List[ChatMessage]  # 消息列表
    total: int  # 消息总数
    has_more: bool  # 是否还有更多消息


class SettingsResponse(BaseModel):
    """
    设置响应模型
    
    定义了系统配置的返回格式。
    与前端 SettingsResponse 保持一致。
    
    Attributes:
        模型设置: AI 模型相关配置
        Agent设置: 智能体相关配置
        Memory设置: 记忆系统配置
        Workflow设置: 工作流配置
        RAG设置: RAG 检索配置
        Tool设置: 工具系统配置
    """
    # AI 模型相关配置
    模型设置: Dict[str, Any]
    # 智能体相关配置（使用 alias 处理中文键名）
    Agent设置: Dict[str, Any] = Field(alias="Agent 设置")
    # 记忆系统配置
    Memory设置: Dict[str, Any] = Field(alias="Memory 设置")
    # 工作流配置
    Workflow设置: Dict[str, Any] = Field(alias="Workflow 设置")
    # RAG 检索配置
    RAG设置: Dict[str, Any] = Field(alias="RAG 设置")
    # 工具系统配置
    Tool设置: Dict[str, Any] = Field(alias="Tool 设置")
    
    class Config:
        # 允许使用字段名或别名
        populate_by_name = True


class MemoryResponse(BaseModel):
    """
    Memory 响应模型
    
    定义了 Memory 数据的返回格式。
    
    Attributes:
        layer: Memory 层名称
        content: Memory 内容
        updated_at: 最后更新时间
    """
    layer: str  # Memory 层名称
    content: str  # Memory 内容
    updated_at: str  # 最后更新时间


class ProjectStatusResponse(BaseModel):
    """
    项目状态响应模型
    
    定义了项目状态的返回格式。
    
    Attributes:
        name: 项目名称
        version: 版本号
        agents: Agent 列表
        memory_layers: Memory 层列表
        tools: 工具列表
    """
    name: str  # 项目名称
    version: str  # 版本号
    agents: List[str]  # Agent 列表
    memory_layers: List[str]  # Memory 层列表
    tools: List[str]  # 工具列表


class ToolResponse(BaseModel):
    """
    工具调用响应模型
    
    定义了工具调用结果的返回格式。
    
    Attributes:
        tool: 工具名称
        success: 是否执行成功
        result: 执行结果
    """
    tool: str  # 工具名称
    success: bool  # 是否执行成功
    result: str  # 执行结果

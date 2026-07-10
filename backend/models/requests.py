"""
请求模型模块

本模块定义了所有 API 接口的请求数据模型。
与前端 types/api.ts 中的类型定义保持一致。

使用 Pydantic 进行数据验证，确保：
- 数据类型正确
- 必填字段不为空
- 字符串长度符合要求
"""

# 导入 Pydantic 模型和字段定义
from pydantic import BaseModel, Field
# 导入类型注解
from typing import Optional, Dict, Any


class CreateUserRequest(BaseModel):
    """
    创建用户请求模型
    
    对应前端 types/api.ts 中的 CreateUserRequest
    
    Attributes:
        username: 用户名（1-50个字符）
        preferences: 用户偏好设置（可选）
    """
    # 用户名：必填，1-50个字符
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    # 用户偏好设置：可选，字典类型
    preferences: Optional[Dict[str, str]] = Field(None, description="用户偏好设置")


class ChatStreamRequest(BaseModel):
    """
    聊天流式请求模型
    
    对应前端 types/api.ts 中的 ChatStreamRequest
    
    Attributes:
        session_id: 会话 ID
        project: 项目名称
        message: 用户消息
        options: 可选参数
    """
    # 会话 ID：必填
    session_id: str = Field(..., description="会话ID")
    # 项目名称：必填
    project: str = Field(..., description="项目名称")
    # 用户消息：必填，至少1个字符
    message: str = Field(..., min_length=1, description="用户消息")
    # 可选参数：可选
    options: Optional[Dict[str, Any]] = Field(None, description="选项")


class UpdateSettingsRequest(BaseModel):
    """
    更新设置请求模型
    
    对应前端 types/api.ts 中的 UpdateSettingsRequest
    
    Attributes:
        section: 配置节名称
        key: 配置项键名
        value: 配置项值
    """
    # 配置节名称：必填
    section: str = Field(..., description="配置节名称")
    # 配置项键名：必填
    key: str = Field(..., description="配置项键名")
    # 配置项值：必填，可以是任意类型
    value: Any = Field(..., description="配置项值")


class ProjectInitRequest(BaseModel):
    """
    初始化项目请求模型
    
    对应前端 types/api.ts 中的 ProjectInitRequest
    
    Attributes:
        project_name: 项目名称
        path: 项目路径
        language: 编程语言（可选）
        framework: 框架（可选）
    """
    # 项目名称：必填，至少1个字符
    project_name: str = Field(..., min_length=1, description="项目名称")
    # 项目路径：必填
    path: str = Field(..., description="项目路径")
    # 编程语言：可选
    language: Optional[str] = Field(None, description="编程语言")
    # 框架：可选
    framework: Optional[str] = Field(None, description="框架")


class ToolCallRequest(BaseModel):
    """
    工具调用请求模型
    
    对应前端 types/api.ts 中的 ToolCallRequest
    
    Attributes:
        tool: 工具名称
        args: 工具参数
    """
    # 工具名称：必填
    tool: str = Field(..., description="工具名称")
    # 工具参数：可选，默认为空字典
    args: Dict[str, Any] = Field(default_factory=dict, description="工具参数")

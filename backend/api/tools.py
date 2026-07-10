"""
工具 API 模块

本模块实现了工具系统相关的 API 接口，包括：
1. 获取工具列表 - GET /api/tools/list
2. 调用工具 - POST /api/tools/call

内置 8 个工具：
- read_file: 读取文件内容
- write_file: 写入文件内容
- list_directory: 列出目录内容
- search_project: 搜索项目文件
- search_knowledge: 搜索知识库
- create_task: 创建任务
- update_memory: 更新记忆
- finish_task: 完成任务
"""

# 导入 FastAPI 路由和异常处理
from fastapi import APIRouter, HTTPException
# 导入 Pydantic 数据验证模型
from pydantic import BaseModel
# 导入类型注解
from typing import Any, Dict

# 创建路由器，prefix="/tools" 表示所有路由以 /tools 开头
# tags=["工具"] 用于 API 文档分组
router = APIRouter(prefix="/tools", tags=["工具"])


class ToolCallRequest(BaseModel):
    """
    工具调用请求模型
    
    与前端 types/api.ts 中的 ToolCallRequest 保持一致
    """
    tool: str  # 工具名称
    args: Dict[str, Any] = {}  # 工具参数，可以是任意字典


# 工具注册表（模拟数据，后续会对接 tools/registry.py）
# 每个工具包含名称、描述和参数定义
TOOLS_REGISTRY = {
    "read_file": {
        "name": "read_file",  # 工具名称
        "description": "读取文件内容",  # 工具描述
        "parameters": {  # 参数定义
            "path": {"type": "string", "description": "文件路径"}
        },
    },
    "write_file": {
        "name": "write_file",
        "description": "写入文件内容",
        "parameters": {
            "path": {"type": "string", "description": "文件路径"},
            "content": {"type": "string", "description": "文件内容"},
        },
    },
    "list_directory": {
        "name": "list_directory",
        "description": "列出目录内容",
        "parameters": {
            "path": {"type": "string", "description": "目录路径"}
        },
    },
    "search_project": {
        "name": "search_project",
        "description": "搜索项目文件",
        "parameters": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
    },
    "search_knowledge": {
        "name": "search_knowledge",
        "description": "搜索知识库",
        "parameters": {
            "query": {"type": "string", "description": "搜索关键词"}
        },
    },
    "create_task": {
        "name": "create_task",
        "description": "创建任务",
        "parameters": {
            "title": {"type": "string", "description": "任务标题"},
            "description": {"type": "string", "description": "任务描述"},
        },
    },
    "update_memory": {
        "name": "update_memory",
        "description": "更新记忆",
        "parameters": {
            "layer": {"type": "string", "description": "记忆层"},
            "content": {"type": "string", "description": "内容"},
        },
    },
    "finish_task": {
        "name": "finish_task",
        "description": "完成任务",
        "parameters": {
            "task_id": {"type": "string", "description": "任务ID"}
        },
    },
}


@router.get("/list")
async def list_tools():
    """
    获取工具列表接口
    
    返回所有可用工具的定义，包括名称、描述和参数。
    
    Returns:
        包含工具列表的响应
    """
    # 返回统一格式的响应
    return {"code": 0, "data": list(TOOLS_REGISTRY.values()), "message": "ok"}


@router.post("/call")
async def call_tool(request: ToolCallRequest):
    """
    调用工具接口
    
    根据工具名称和参数执行工具。
    后续会对接 tools/registry.py 实现真实的工具执行。
    
    Args:
        request: 工具调用请求，包含工具名称和参数
    
    Returns:
        包含工具执行结果的响应
    
    Raises:
        HTTPException: 如果工具不存在，返回 404 错误
    """
    # 检查工具是否存在
    if request.tool not in TOOLS_REGISTRY:
        raise HTTPException(status_code=404, detail=f"工具 '{request.tool}' 不存在")

    # 获取工具定义
    tool = TOOLS_REGISTRY[request.tool]
    # 模拟工具执行结果
    result = {
        "tool": request.tool,  # 工具名称
        "success": True,  # 执行是否成功
        "result": f"模拟执行 {tool['description']}",  # 执行结果
    }

    # 返回统一格式的响应
    return {"code": 0, "data": result, "message": "工具执行成功"}

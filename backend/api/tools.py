"""
工具 API
POST /api/tools/call - 调用工具
GET /api/tools/list - 获取工具列表
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

router = APIRouter(prefix="/tools", tags=["工具"])


class ToolCallRequest(BaseModel):
    """工具调用请求（与前端 types/api.ts 一致）"""

    tool: str
    args: Dict[str, Any] = {}


# 模拟工具定义（后续会对接 tools/registry.py）
TOOLS_REGISTRY = {
    "read_file": {
        "name": "read_file",
        "description": "读取文件内容",
        "parameters": {"path": {"type": "string", "description": "文件路径"}},
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
        "parameters": {"path": {"type": "string", "description": "目录路径"}},
    },
    "search_project": {
        "name": "search_project",
        "description": "搜索项目文件",
        "parameters": {"query": {"type": "string", "description": "搜索关键词"}},
    },
    "search_knowledge": {
        "name": "search_knowledge",
        "description": "搜索知识库",
        "parameters": {"query": {"type": "string", "description": "搜索关键词"}},
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
        "parameters": {"task_id": {"type": "string", "description": "任务ID"}},
    },
}


@router.get("/list")
async def list_tools():
    """获取工具列表"""
    return {"code": 0, "data": list(TOOLS_REGISTRY.values()), "message": "ok"}


@router.post("/call")
async def call_tool(request: ToolCallRequest):
    """
    调用工具
    """
    if request.tool not in TOOLS_REGISTRY:
        raise HTTPException(status_code=404, detail=f"工具 '{request.tool}' 不存在")

    # 模拟工具执行（后续会对接 tools/registry.py）
    tool = TOOLS_REGISTRY[request.tool]
    result = {
        "tool": request.tool,
        "success": True,
        "result": f"模拟执行 {tool['description']}",
    }

    return {"code": 0, "data": result, "message": "工具执行成功"}

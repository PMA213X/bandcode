"""工作区API - 获取和管理工作区路径"""

import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/workspace", tags=["workspace"])

# 工作区路径：优先使用环境变量（用户运行命令的目录），否则使用当前目录
workspace_path = os.environ.get("BANDCODE_WORKSPACE", os.getcwd())


class WorkspaceInfo(BaseModel):
    path: str
    name: str
    exists: bool


class UpdateWorkspaceRequest(BaseModel):
    path: str


@router.get("/info", response_model=dict)
async def get_workspace_info():
    """获取工作区信息"""
    return {
        "code": 0,
        "data": {
            "path": workspace_path,
            "name": os.path.basename(workspace_path),
            "exists": os.path.exists(workspace_path),
        },
        "message": "获取成功",
    }


@router.post("/update", response_model=dict)
async def update_workspace(req: UpdateWorkspaceRequest):
    """修改工作区路径"""
    global workspace_path
    new_path = os.path.normpath(req.path)
    if not os.path.isdir(new_path):
        return {"code": -1, "message": f"路径不存在或不是目录: {new_path}", "data": None}
    workspace_path = new_path
    return {
        "code": 0,
        "data": {
            "path": workspace_path,
            "name": os.path.basename(workspace_path),
            "exists": True,
        },
        "message": "工作区已更新",
    }


@router.get("/files", response_model=dict)
async def list_workspace_files(path: str = ""):
    """列出工作区内的文件"""
    full_path = os.path.join(workspace_path, path) if path else workspace_path
    full_path = os.path.normpath(full_path)

    if not full_path.startswith(workspace_path):
        return {"code": -1, "message": "路径超出工作区范围", "data": None}

    if not os.path.exists(full_path):
        return {"code": -1, "message": "路径不存在", "data": None}

    try:
        items = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            items.append(
                {
                    "name": item,
                    "path": os.path.relpath(item_path, workspace_path),
                    "is_dir": os.path.isdir(item_path),
                    "size": (
                        os.path.getsize(item_path)
                        if os.path.isfile(item_path)
                        else None
                    ),
                }
            )
        return {
            "code": 0,
            "data": {"items": items, "path": path},
            "message": "获取成功",
        }
    except Exception as e:
        return {"code": -1, "message": str(e), "data": None}


@router.get("/validate", response_model=dict)
async def validate_path(path: str):
    """验证路径是否在工作区内"""
    full_path = os.path.join(workspace_path, path)
    full_path = os.path.normpath(full_path)

    is_valid = full_path.startswith(workspace_path)

    return {
        "code": 0,
        "data": {"valid": is_valid, "path": path, "full_path": full_path},
        "message": "验证成功",
    }

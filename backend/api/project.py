"""
项目 API
POST /api/project/init - 初始化项目
GET /api/project/status - 获取项目状态
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import json

router = APIRouter(prefix="/project", tags=["项目"])


class InitProjectRequest(BaseModel):
    """初始化项目请求"""

    project_path: str = "."
    project_name: Optional[str] = None


@router.post("/init")
async def init_project(request: InitProjectRequest):
    """
    初始化项目
    创建 .mimo/ 目录结构和配置文件
    """
    project_path = Path(request.project_path)

    # 创建 .mimo 目录结构
    mimo_dirs = [
        ".mimo/global",
        ".mimo/project",
        ".mimo/tasks",
        ".mimo/sessions",
        ".mimo/checkpoints",
        ".mimo/notes",
    ]

    created_dirs = []
    for dir_path in mimo_dirs:
        full_path = project_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(full_path))

    # 创建默认配置文件
    config_path = project_path / ".mimo/config.json"
    if not config_path.exists():
        default_config = {
            "project_name": request.project_name or project_path.name,
            "version": "1.0.0",
            "created_at": "2026-07-10",
        }
        config_path.write_text(
            json.dumps(default_config, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    return {
        "code": 0,
        "data": {
            "project_path": str(project_path),
            "created_dirs": created_dirs,
            "config_path": str(config_path),
        },
        "message": "项目初始化成功",
    }


@router.get("/status")
async def get_project_status():
    """
    获取项目状态
    """
    # 模拟项目状态（后续会读取实际状态）
    status = {
        "name": "BandCode",
        "version": "1.0.0",
        "agents": ["planner", "simple_coder", "complex_coder", "tester", "constraint", "review"],
        "memory_layers": ["global", "project", "task", "session", "checkpoint", "notes"],
        "tools": [
            "read_file",
            "write_file",
            "list_directory",
            "search_project",
            "search_knowledge",
            "create_task",
            "update_memory",
            "finish_task",
        ],
    }
    return {"code": 0, "data": status, "message": "ok"}

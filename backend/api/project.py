"""
项目 API 模块

本模块实现了项目管理相关的 API 接口，包括：
1. 初始化项目 - POST /api/project/init
2. 获取项目状态 - GET /api/project/status

项目初始化会创建 .mimo/ 目录结构，用于存储：
- global: 全局记忆
- project: 项目记忆
- tasks: 任务数据
- sessions: 会话数据
- checkpoints: 检查点数据
- notes: 笔记
"""

# 导入 FastAPI 路由
from fastapi import APIRouter
# 导入 Pydantic 数据验证模型
from pydantic import BaseModel
# 导入类型注解
from typing import Optional
# 导入路径处理模块
from pathlib import Path
# 导入 JSON 序列化模块
import json

# 创建路由器，prefix="/project" 表示所有路由以 /project 开头
# tags=["项目"] 用于 API 文档分组
router = APIRouter(prefix="/project", tags=["项目"])


class ProjectInitRequest(BaseModel):
    """
    初始化项目请求模型
    
    与前端 types/api.ts 中的 ProjectInitRequest 保持一致
    """
    project_name: str  # 项目名称
    path: str  # 项目路径
    language: Optional[str] = None  # 编程语言（可选）
    framework: Optional[str] = None  # 框架（可选）


@router.post("/init")
async def init_project(request: ProjectInitRequest):
    """
    初始化项目接口
    
    创建 .mimo/ 目录结构和配置文件。
    这是项目使用 BandCode 的第一步。
    
    Args:
        request: 初始化项目请求，包含项目名称、路径等信息
    
    Returns:
        包含项目初始化结果的响应：
        - project: 项目名称
        - mimo_dir: .mimo 目录路径
        - structure: 目录结构
    """
    # 将路径字符串转换为 Path 对象
    project_path = Path(request.path)

    # 定义 .mimo 目录结构
    mimo_dirs = [
        ".mimo/global",  # 全局记忆
        ".mimo/project",  # 项目记忆
        ".mimo/tasks",  # 任务数据
        ".mimo/sessions",  # 会话数据
        ".mimo/checkpoints",  # 检查点数据
        ".mimo/notes",  # 笔记
    ]

    # 创建目录
    created_dirs = []
    for dir_path in mimo_dirs:
        full_path = project_path / dir_path
        # mkdir(parents=True) 会创建所有必要的父目录
        # exist_ok=True 表示如果目录已存在不会报错
        full_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(full_path))

    # 创建默认配置文件
    config_path = project_path / ".mimo/config.json"
    if not config_path.exists():
        # 默认配置
        default_config = {
            "project_name": request.project_name,
            "version": "1.0.0",
            "language": request.language,
            "framework": request.framework,
        }
        # 写入配置文件，ensure_ascii=False 支持中文，indent=2 格式化输出
        config_path.write_text(
            json.dumps(default_config, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # 返回统一格式的响应
    return {
        "code": 0,
        "data": {
            "project": request.project_name,  # 项目名称
            "mimo_dir": str(project_path / ".mimo"),  # .mimo 目录路径
            "structure": {dir: str(project_path / dir) for dir in mimo_dirs},  # 目录结构
        },
        "message": "项目初始化成功",
    }


@router.get("/status")
async def get_project_status():
    """
    获取项目状态接口
    
    返回当前项目的配置信息，包括：
    - Agent 列表
    - Memory 层列表
    - 工具列表
    
    Returns:
        包含项目状态的响应
    """
    # 模拟项目状态（后续会读取实际状态）
    status = {
        "name": "BandCode",  # 项目名称
        "version": "1.0.0",  # 版本号
        # 6 个 Agent
        "agents": [
            "planner",  # 规划 Agent
            "simple_coder",  # 简单编码 Agent
            "complex_coder",  # 复杂编码 Agent
            "tester",  # 测试 Agent
            "constraint",  # 约束 Agent
            "review",  # 审查 Agent
        ],
        # 6 个 Memory 层
        "memory_layers": [
            "global",  # 全局记忆
            "project",  # 项目记忆
            "task",  # 任务记忆
            "session",  # 会话记忆
            "checkpoint",  # 检查点
            "notes",  # 笔记
        ],
        # 8 个内置工具
        "tools": [
            "read_file",  # 读取文件
            "write_file",  # 写入文件
            "list_directory",  # 列出目录
            "search_project",  # 搜索项目
            "search_knowledge",  # 搜索知识库
            "create_task",  # 创建任务
            "update_memory",  # 更新记忆
            "finish_task",  # 完成任务
        ],
    }
    # 返回统一格式的响应
    return {"code": 0, "data": status, "message": "ok"}

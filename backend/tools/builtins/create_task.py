"""
create_task工具 - 创建新任务

本模块实现了任务创建工具，支持创建新的任务。
"""

# 导入时间模块
import time
# 导入JSON模块
import json
# 导入路径处理
from pathlib import Path

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class CreateTaskTool(Tool):
    """
    创建任务工具

    创建新的任务并保存到任务文件。
    """

    # 工具名称
    name = "create_task"
    # 工具描述
    description = "创建新的任务"
    # 所需权限：write
    permission = "write"
    # 参数定义
    parameters = {
        "title": {
            "type": "string",
            "description": "任务标题",
            "required": True
        },
        "description": {
            "type": "string",
            "description": "任务描述",
            "required": False
        },
        "priority": {
            "type": "string",
            "description": "优先级（low/medium/high）",
            "required": False
        },
        "assigned_to": {
            "type": "string",
            "description": "分配给谁",
            "required": False
        }
    }

    async def execute(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        assigned_to: str = "",
        **kwargs
    ) -> ToolResult:
        """
        执行创建任务

        Args:
            title: 任务标题
            description: 任务描述
            priority: 优先级
            assigned_to: 分配给谁

        Returns:
            创建结果或错误信息
        """
        try:
            # 生成任务ID
            task_id = f"task_{int(time.time())}"

            # 创建任务对象
            task = {
                "id": task_id,
                "title": title,
                "description": description,
                "priority": priority,
                "assigned_to": assigned_to,
                "status": "open",
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            }

            # 保存到文件
            tasks_file = Path("tasks.json")
            tasks = []

            # 读取现有任务
            if tasks_file.exists():
                try:
                    tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
                except Exception:
                    tasks = []

            # 添加新任务
            tasks.append(task)

            # 保存到文件
            tasks_file.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")

            return ToolResult(success=True, data=task)

        except Exception as e:
            return ToolResult(success=False, error=str(e))
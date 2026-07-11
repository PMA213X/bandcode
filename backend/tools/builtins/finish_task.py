"""
finish_task工具 - 标记任务完成

本模块实现了任务完成工具，支持标记任务为已完成。
"""

# 导入时间模块
import time
# 导入JSON模块
import json
# 导入路径处理
from pathlib import Path

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class FinishTaskTool(Tool):
    """
    完成任务工具

    标记任务为已完成。
    """

    # 工具名称
    name = "finish_task"
    # 工具描述
    description = "标记任务完成"
    # 所需权限：write
    permission = "write"
    # 参数定义
    parameters = {
        "task_id": {
            "type": "string",
            "description": "任务ID",
            "required": True
        },
        "result": {
            "type": "string",
            "description": "任务结果",
            "required": False
        }
    }

    async def execute(
        self,
        task_id: str,
        result: str = "",
        **kwargs
    ) -> ToolResult:
        """
        执行完成任务

        Args:
            task_id: 任务ID
            result: 任务结果

        Returns:
            完成结果或错误信息
        """
        try:
            # 读取任务文件
            tasks_file = Path("tasks.json")
            if not tasks_file.exists():
                return ToolResult(success=False, error="Tasks file not found")

            # 读取任务列表
            tasks = json.loads(tasks_file.read_text(encoding="utf-8"))

            # 查找任务
            task_found = False
            for task in tasks:
                if task.get("id") == task_id:
                    # 更新任务状态
                    task["status"] = "completed"
                    task["result"] = result
                    task["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    task_found = True
                    break

            if not task_found:
                return ToolResult(success=False, error=f"Task not found: {task_id}")

            # 保存到文件
            tasks_file.write_text(json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8")

            return ToolResult(success=True, data={
                "task_id": task_id,
                "status": "completed"
            })

        except Exception as e:
            return ToolResult(success=False, error=str(e))
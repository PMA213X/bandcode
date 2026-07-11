"""
update_memory工具 - 写入或更新Memory

本模块实现了Memory更新工具，支持写入或更新Memory内容。
"""

# 导入时间模块
import time
# 导入JSON模块
import json
# 导入路径处理
from pathlib import Path

# 导入Tool基类和结果类
from tools.base import Tool, ToolResult


class UpdateMemoryTool(Tool):
    """
    更新Memory工具

    写入或更新Memory内容。
    """

    # 工具名称
    name = "update_memory"
    # 工具描述
    description = "写入或更新Memory"
    # 所需权限：write
    permission = "write"
    # 参数定义
    parameters = {
        "key": {
            "type": "string",
            "description": "Memory键",
            "required": True
        },
        "value": {
            "type": "string",
            "description": "Memory值",
            "required": True
        },
        "memory_type": {
            "type": "string",
            "description": "Memory类型（global/project/task/session）",
            "required": False
        }
    }

    async def execute(
        self,
        key: str,
        value: str,
        memory_type: str = "project",
        **kwargs
    ) -> ToolResult:
        """
        执行更新Memory

        Args:
            key: Memory键
            value: Memory值
            memory_type: Memory类型

        Returns:
            更新结果或错误信息
        """
        try:
            # 构造Memory文件路径
            memory_dir = Path("memory") / memory_type
            memory_dir.mkdir(parents=True, exist_ok=True)
            memory_file = memory_dir / f"{key}.md"

            # 写入Memory内容
            content = f"""# {key}

更新时间：{time.strftime("%Y-%m-%dT%H:%M:%SZ")}

{value}
"""
            memory_file.write_text(content, encoding="utf-8")

            return ToolResult(success=True, data={
                "key": key,
                "memory_type": memory_type,
                "file": str(memory_file)
            })

        except Exception as e:
            return ToolResult(success=False, error=str(e))
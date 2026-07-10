"""
六层分层 Memory 存储管理器

Memory 层级:
- global: 全局偏好、编码规范、技术栈偏好（更新频率低）
- project: 架构决策、模块说明、项目约定（更新频率中）
- task: 单任务目标、进展、决策（每任务更新）
- session: 对话历史摘要（每会话更新）
- checkpoint: 文件变更列表、快照摘要（按需更新）
- notes: TODO、临时记录、灵感（任意更新）
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional
import re


class MemoryStore:
    """分层 Memory 存储管理器"""

    def __init__(self, project_path: str):
        self.base_path = Path(project_path) / ".mimo"
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """确保所有 Memory 目录存在"""
        for layer in ["global", "project", "tasks", "sessions", "checkpoints", "notes"]:
            (self.base_path / layer).mkdir(parents=True, exist_ok=True)

    def _read_file(self, path: Path) -> str:
        """读取文件内容"""
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _write_file(self, path: Path, content: str) -> None:
        """写入文件内容"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _append_file(self, path: Path, content: str) -> None:
        """追加写入文件内容"""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)

    # ==================== 读取操作 ====================

    def get_memory(self, layer: str, session_id: str = None) -> str:
        """读取指定层级的 Memory"""
        if layer == "global":
            return self._read_file(self.base_path / "global" / "MEMORY.md")
        elif layer == "project":
            return self._read_file(self.base_path / "project" / "MEMORY.md")
        elif layer == "task":
            return self._get_task_memory(session_id)
        elif layer == "session":
            return self._get_session_memory(session_id)
        elif layer == "checkpoint":
            return self._get_checkpoint_memory(session_id)
        elif layer == "notes":
            return self._read_file(self.base_path / "notes" / "NOTES.md")
        return ""

    def _get_task_memory(self, session_id: str = None) -> str:
        """获取当前任务的 Memory"""
        if not session_id:
            return ""
        task_file = self.base_path / "tasks" / f"task-{session_id}.md"
        return self._read_file(task_file)

    def _get_session_memory(self, session_id: str = None) -> str:
        """获取会话 Memory"""
        if not session_id:
            return ""
        session_file = self.base_path / "sessions" / f"{session_id}.md"
        return self._read_file(session_file)

    def _get_checkpoint_memory(self, session_id: str = None) -> str:
        """获取最新快照的 Memory"""
        if not session_id:
            return ""
        checkpoint_dir = self.base_path / "checkpoints"
        files = sorted(checkpoint_dir.glob(f"{session_id}-*.md"), reverse=True)
        if files:
            return self._read_file(files[0])
        return ""

    # ==================== 写入操作 ====================

    def update_memory(self, layer: str, content: str, session_id: str = None) -> None:
        """更新指定层级的 Memory（追加写入，保留历史）"""
        if layer == "global":
            self._append_file(self.base_path / "global" / "MEMORY.md", f"\n\n{content}")
        elif layer == "project":
            self._append_file(self.base_path / "project" / "MEMORY.md", f"\n\n{content}")
        elif layer == "task" and session_id:
            self._append_file(self.base_path / "tasks" / f"task-{session_id}.md", f"\n\n{content}")
        elif layer == "session" and session_id:
            self._append_file(self.base_path / "sessions" / f"{session_id}.md", f"\n\n{content}")
        elif layer == "notes":
            self._append_file(self.base_path / "notes" / "NOTES.md", f"\n\n{content}")

    def overwrite_memory(self, layer: str, content: str, session_id: str = None) -> None:
        """覆盖写入指定层级的 Memory"""
        if layer == "global":
            self._write_file(self.base_path / "global" / "MEMORY.md", content)
        elif layer == "project":
            self._write_file(self.base_path / "project" / "MEMORY.md", content)
        elif layer == "task" and session_id:
            self._write_file(self.base_path / "tasks" / f"task-{session_id}.md", content)
        elif layer == "session" and session_id:
            self._write_file(self.base_path / "sessions" / f"{session_id}.md", content)
        elif layer == "notes":
            self._write_file(self.base_path / "notes" / "NOTES.md", content)

    # ==================== 搜索操作 ====================

    def search_memory(self, layer: str, query: str) -> list[str]:
        """在指定层级中搜索与 query 相关的内容"""
        content = self.get_memory(layer)
        if not content:
            return []

        results = []
        lines = content.split("\n")
        query_lower = query.lower()

        for i, line in enumerate(lines):
            if query_lower in line.lower():
                # 返回匹配行及其上下文
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = "\n".join(lines[start:end])
                results.append(context)

        return results

    def search_all_layers(self, query: str) -> dict[str, list[str]]:
        """在所有层级中搜索"""
        results = {}
        for layer in ["global", "project", "task", "notes"]:
            matches = self.search_memory(layer, query)
            if matches:
                results[layer] = matches
        return results

    # ==================== 辅助方法 ====================

    def get_all_layers(self) -> dict[str, str]:
        """获取所有层级的 Memory 内容"""
        return {
            "global": self.get_memory("global"),
            "project": self.get_memory("project"),
            "task": self.get_memory("task"),
            "session": self.get_memory("session"),
            "checkpoint": self.get_memory("checkpoint"),
            "notes": self.get_memory("notes"),
        }

    def list_task_files(self) -> list[str]:
        """列出所有任务 Memory 文件"""
        tasks_dir = self.base_path / "tasks"
        return [f.name for f in tasks_dir.glob("*.md")]

    def list_session_files(self) -> list[str]:
        """列出所有会话 Memory 文件"""
        sessions_dir = self.base_path / "sessions"
        return [f.name for f in sessions_dir.glob("*.md")]

"""
快照管理 — 文件快照创建、恢复

支持在代码修改前创建快照，如果 Review 失败可回滚到修改前状态。
"""
from __future__ import annotations
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4


class CheckpointManager:
    """文件快照管理器"""

    def __init__(self, project_path: str):
        """
        Args:
            project_path: 项目根目录路径
        """
        self.project_path = Path(project_path)
        self.snapshot_dir = self.project_path / ".mimo" / "checkpoints"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(
        self,
        session_id: str,
        files: list[str],
        description: str = None,
    ) -> dict:
        """
        创建文件快照

        Args:
            session_id: 会话 ID
            files: 需要快照的文件路径列表
            description: 快照描述

        Returns:
            快照信息 {"checkpoint_id": ..., "files": [...], "snapshot_path": ...}
        """
        checkpoint_id = f"cp-{uuid4().hex[:8]}"
        snapshot_path = self.snapshot_dir / f"{session_id}-{checkpoint_id}"

        # 创建快照目录
        snapshot_path.mkdir(parents=True, exist_ok=True)

        # 复制文件到快照目录
        copied_files = []
        for file_path in files:
            src = self.project_path / file_path
            if src.exists():
                dst = snapshot_path / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
                copied_files.append(file_path)

        # 创建元数据文件
        metadata = {
            "checkpoint_id": checkpoint_id,
            "session_id": session_id,
            "description": description or f"快照 {checkpoint_id}",
            "files": copied_files,
            "created_at": datetime.now().isoformat(),
        }
        meta_file = snapshot_path / "metadata.json"
        with open(str(meta_file), "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return {
            "checkpoint_id": checkpoint_id,
            "files": copied_files,
            "snapshot_path": str(snapshot_path),
        }

    def restore_snapshot(self, checkpoint_id: str, session_id: str) -> list[str]:
        """
        恢复文件快照

        Args:
            checkpoint_id: 快照 ID
            session_id: 会话 ID

        Returns:
            已恢复的文件列表
        """
        snapshot_path = self.snapshot_dir / f"{session_id}-{checkpoint_id}"
        if not snapshot_path.exists():
            raise FileNotFoundError(f"快照不存在: {checkpoint_id}")

        # 读取元数据
        meta_file = snapshot_path / "metadata.json"
        if not meta_file.exists():
            raise FileNotFoundError(f"快照元数据不存在: {checkpoint_id}")

        metadata = json.loads(meta_file.read_text(encoding="utf-8"))
        restored_files = []

        # 恢复文件
        for file_path in metadata.get("files", []):
            src = snapshot_path / file_path
            dst = self.project_path / file_path
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
                restored_files.append(file_path)

        return restored_files

    def list_snapshots(self, session_id: str = None) -> list[dict]:
        """
        列出所有快照

        Args:
            session_id: 会话 ID（可选，用于过滤）

        Returns:
            快照列表
        """
        snapshots = []
        for snapshot_dir in self.snapshot_dir.iterdir():
            if not snapshot_dir.is_dir():
                continue

            meta_file = snapshot_dir / "metadata.json"
            if meta_file.exists():
                with open(str(meta_file), "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                if session_id is None or metadata.get("session_id") == session_id:
                    snapshots.append(metadata)

        return sorted(snapshots, key=lambda x: x.get("created_at", ""), reverse=True)

    def delete_snapshot(self, checkpoint_id: str, session_id: str) -> bool:
        """
        删除快照

        Args:
            checkpoint_id: 快照 ID
            session_id: 会话 ID

        Returns:
            是否删除成功
        """
        snapshot_path = self.snapshot_dir / f"{session_id}-{checkpoint_id}"
        if snapshot_path.exists():
            shutil.rmtree(str(snapshot_path))
            return True
        return False

    def get_latest_snapshot(self, session_id: str) -> Optional[dict]:
        """获取指定会话的最新快照"""
        snapshots = self.list_snapshots(session_id)
        return snapshots[0] if snapshots else None

"""Memory Manager - 统一管理 Memory 系统"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from .auto_recorder import AutoRecorder
from .index import MemoryIndex
from .compressor import SessionCompressor


class MemoryManager:
    """Memory Manager"""
    
    def __init__(self, base_path: str = "memory"):
        self.base_path = base_path
        self.index = MemoryIndex(base_path)
        self.compressor = SessionCompressor(base_path)
        self._current_session_id = None
        self._recorder = None
    
    def start_session(self, project_id: str = "default") -> str:
        """开始新会话"""
        session_id = f"ses_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self._current_session_id = session_id
        self._recorder = AutoRecorder(session_id, project_id)
        return session_id
    
    def get_recorder(self) -> Optional[AutoRecorder]:
        """获取当前记录器"""
        return self._recorder
    
    def record_conversation(self, role: str, content: str, agent: Optional[str] = None):
        """记录对话"""
        if self._recorder:
            self._recorder.record_conversation(role, content, agent)
            self.index.add_entry(self._current_session_id, "conversation", content[:500])
    
    def record_tool_call(self, tool_name: str, args: Dict, result: Any, success: bool = True):
        """记录工具调用"""
        if self._recorder:
            self._recorder.record_tool_call(tool_name, args, result, success)
            self.index.add_entry(self._current_session_id, "tool", f"{tool_name}: {str(result)[:200]}")
    
    def record_decision(self, decision: str, reason: str, impact: str = ""):
        """记录决策"""
        if self._recorder:
            self._recorder.record_decision(decision, reason, impact)
            self.index.add_entry(self._current_session_id, "decision", decision)
    
    def record_error(self, error: str, context: str = "", solution: str = ""):
        """记录错误"""
        if self._recorder:
            self._recorder.record_error(error, context, solution)
            self.index.add_entry(self._current_session_id, "error", error)
    
    def record_task(self, task_id: str, title: str, status: str, description: str = ""):
        """记录任务"""
        if self._recorder:
            self._recorder.record_task(task_id, title, status, description)
            self.index.add_entry(self._current_session_id, "task", f"{title}: {status}")
    
    def search(self, query: str, limit: int = 10, entry_type: Optional[str] = None) -> List[Dict]:
        """搜索记忆"""
        return self.index.search(query, limit, entry_type)
    
    def get_recent(self, limit: int = 20, entry_type: Optional[str] = None) -> List[Dict]:
        """获取最近的记忆"""
        return self.index.get_recent(limit, entry_type)
    
    def get_session_summary(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """获取会话摘要"""
        sid = session_id or self._current_session_id
        if not sid:
            return {"error": "没有活跃的会话"}
        
        return self.index.get_session_entries(sid)
    
    def compress_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """压缩会话"""
        sid = session_id or self._current_session_id
        if not sid:
            return {"error": "没有活跃的会话"}
        
        from pathlib import Path
        session_path = Path(self.base_path) / "sessions" / sid
        if session_path.exists():
            return self.compressor.compress_session(session_path)
        return {"error": "会话不存在"}
    
    def clean_old_sessions(self, max_age_days: int = 7) -> List[str]:
        """清理过期会话"""
        return self.compressor.clean_old_sessions(max_age_days)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        index_stats = self.index.get_stats()
        compression_stats = self.compressor.get_compression_stats()
        
        return {
            "index": index_stats,
            "compression": compression_stats,
            "current_session": self._current_session_id
        }
    
    def end_session(self):
        """结束会话"""
        if self._current_session_id:
            # 自动压缩
            self.compress_session()
            self._current_session_id = None
            self._recorder = None

"""Memory 索引 - 支持快速搜索"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class MemoryIndex:
    """Memory 索引"""
    
    def __init__(self, base_path: str = "memory"):
        self.base_path = Path(base_path)
        self.index_path = self.base_path / "index.json"
        self._ensure_index()
    
    def _ensure_index(self):
        """确保索引文件存在"""
        if not self.index_path.exists():
            self.index_path.write_text(json.dumps({"entries": [], "last_updated": None}, ensure_ascii=False, indent=2))
    
    def _load_index(self) -> Dict[str, Any]:
        """加载索引"""
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except:
            return {"entries": [], "last_updated": None}
    
    def _save_index(self, index: Dict[str, Any]):
        """保存索引"""
        index["last_updated"] = datetime.now().isoformat()
        self.index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2))
    
    def add_entry(self, session_id: str, entry_type: str, content: str, metadata: Optional[Dict] = None):
        """添加索引条目"""
        index = self._load_index()
        
        entry = {
            "id": f"{session_id}_{len(index['entries'])}",
            "session_id": session_id,
            "type": entry_type,  # conversation, tool, decision, error, task
            "content": content[:1000],  # 截断过长内容
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        index["entries"].append(entry)
        self._save_index(index)
    
    def search(self, query: str, limit: int = 10, entry_type: Optional[str] = None) -> List[Dict]:
        """搜索记忆"""
        index = self._load_index()
        query_lower = query.lower()
        
        results = []
        for entry in reversed(index["entries"]):  # 从最新开始搜索
            if entry_type and entry["type"] != entry_type:
                continue
            
            if query_lower in entry["content"].lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_recent(self, limit: int = 20, entry_type: Optional[str] = None) -> List[Dict]:
        """获取最近的记忆"""
        index = self._load_index()
        
        entries = index["entries"]
        if entry_type:
            entries = [e for e in entries if e["type"] == entry_type]
        
        return entries[-limit:]
    
    def get_session_entries(self, session_id: str) -> List[Dict]:
        """获取会话的所有条目"""
        index = self._load_index()
        return [e for e in index["entries"] if e["session_id"] == session_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        index = self._load_index()
        entries = index["entries"]
        
        stats = {
            "total_entries": len(entries),
            "by_type": {},
            "by_session": {},
            "last_updated": index.get("last_updated")
        }
        
        for entry in entries:
            entry_type = entry["type"]
            session_id = entry["session_id"]
            
            stats["by_type"][entry_type] = stats["by_type"].get(entry_type, 0) + 1
            stats["by_session"][session_id] = stats["by_session"].get(session_id, 0) + 1
        
        return stats

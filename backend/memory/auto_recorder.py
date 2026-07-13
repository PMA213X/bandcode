"""自动记录器 - 记录对话、工具调用、决策等"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class AutoRecorder:
    """自动记录器"""
    
    def __init__(self, session_id: str, project_id: str = "default"):
        self.session_id = session_id
        self.project_id = project_id
        self.base_path = Path("memory")
        self.session_path = self.base_path / "sessions" / session_id
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        """确保目录存在"""
        self.session_path.mkdir(parents=True, exist_ok=True)
    
    def record_conversation(self, role: str, content: str, agent: Optional[str] = None):
        """记录对话"""
        timestamp = datetime.now().isoformat()
        entry = f"\n## [{timestamp}] {role}\n\n{content}\n"
        
        if agent:
            entry = f"\n## [{timestamp}] {role} ({agent})\n\n{content}\n"
        
        file_path = self.session_path / "conversation.md"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    
    def record_tool_call(self, tool_name: str, args: Dict[str, Any], result: Any, success: bool = True):
        """记录工具调用"""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "tool": tool_name,
            "args": args,
            "result": str(result)[:500],  # 截断过长的结果
            "success": success
        }
        
        file_path = self.session_path / "tools.json"
        existing = []
        if file_path.exists():
            try:
                existing = json.loads(file_path.read_text(encoding="utf-8"))
            except:
                existing = []
        
        existing.append(entry)
        file_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def record_code_change(self, files: List[str], action: str, summary: str = ""):
        """记录代码变更"""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "files": files,
            "action": action,  # create, modify, delete
            "summary": summary
        }
        
        file_path = self.session_path / "code_changes.json"
        existing = []
        if file_path.exists():
            try:
                existing = json.loads(file_path.read_text(encoding="utf-8"))
            except:
                existing = []
        
        existing.append(entry)
        file_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def record_decision(self, decision: str, reason: str, impact: str = ""):
        """记录决策"""
        timestamp = datetime.now().isoformat()
        entry = f"\n## [{timestamp}] 决策\n\n**决策**: {decision}\n\n**原因**: {reason}\n"
        
        if impact:
            entry += f"\n**影响**: {impact}\n"
        
        file_path = self.session_path / "decisions.md"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    
    def record_error(self, error: str, context: str = "", solution: str = ""):
        """记录错误"""
        timestamp = datetime.now().isoformat()
        entry = f"\n## [{timestamp}] 错误\n\n**错误**: {error}\n\n**上下文**: {context}\n"
        
        if solution:
            entry += f"\n**解决方案**: {solution}\n"
        
        file_path = self.session_path / "errors.md"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)
    
    def record_task(self, task_id: str, title: str, status: str, description: str = ""):
        """记录任务状态"""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "task_id": task_id,
            "title": title,
            "status": status,  # created, in_progress, completed, failed
            "description": description
        }
        
        file_path = self.session_path / "tasks.json"
        existing = []
        if file_path.exists():
            try:
                existing = json.loads(file_path.read_text(encoding="utf-8"))
            except:
                existing = []
        
        existing.append(entry)
        file_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    
    def add_note(self, content: str):
        """添加临时笔记"""
        timestamp = datetime.now().isoformat()
        entry = f"\n## [{timestamp}] 笔记\n\n{content}\n"
        
        file_path = self.session_path / "notes.md"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(entry)

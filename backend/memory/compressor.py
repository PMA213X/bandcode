"""会话压缩器 - 自动压缩过长的会话"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional


class SessionCompressor:
    """会话压缩器"""
    
    def __init__(self, base_path: str = "memory", max_session_age_days: int = 7, max_entries_per_session: int = 100):
        self.base_path = Path(base_path)
        self.sessions_path = self.base_path / "sessions"
        self.max_session_age_days = max_session_age_days
        self.max_entries_per_session = max_entries_per_session
    
    def should_compress(self, session_path: Path) -> bool:
        """判断是否需要压缩"""
        # 检查会话年龄
        try:
            session_time = datetime.fromisoformat(session_path.name.split("_")[1]) if "_" in session_path.name else None
            if session_time and datetime.now() - session_time > timedelta(days=self.max_session_age_days):
                return True
        except:
            pass
        
        # 检查会话大小
        tools_file = session_path / "tools.json"
        if tools_file.exists():
            try:
                tools = json.loads(tools_file.read_text(encoding="utf-8"))
                if len(tools) > self.max_entries_per_session:
                    return True
            except:
                pass
        
        return False
    
    def compress_session(self, session_path: Path) -> Dict[str, Any]:
        """压缩会话"""
        summary = {
            "session_id": session_path.name,
            "compressed_at": datetime.now().isoformat(),
            "original_files": [],
            "compressed_file": None
        }
        
        # 读取所有文件
        conversation = self._read_file(session_path / "conversation.md")
        tools = self._read_json(session_path / "tools.json")
        decisions = self._read_file(session_path / "decisions.md")
        errors = self._read_file(session_path / "errors.md")
        tasks = self._read_json(session_path / "tasks.json")
        
        # 生成摘要
        compressed_content = self._generate_summary(conversation, tools, decisions, errors, tasks)
        
        # 保存压缩后的文件
        compressed_file = session_path / "compressed.md"
        compressed_file.write_text(compressed_content, encoding="utf-8")
        
        summary["compressed_file"] = str(compressed_file)
        summary["original_files"] = [str(f) for f in session_path.iterdir() if f.name != "compressed.md"]
        
        # 删除原始文件（保留压缩文件）
        for file in session_path.iterdir():
            if file.name != "compressed.md" and file.name != "summary.json":
                file.unlink()
        
        # 保存摘要
        summary_file = session_path / "summary.json"
        summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
        
        return summary
    
    def _generate_summary(self, conversation: str, tools: List, decisions: str, errors: str, tasks: List) -> str:
        """生成会话摘要"""
        timestamp = datetime.now().isoformat()
        
        summary = f"# 会话摘要\n\n**压缩时间**: {timestamp}\n\n"
        
        # 统计信息
        summary += "## 统计\n\n"
        summary += f"- 对话长度: {len(conversation)} 字符\n"
        summary += f"- 工具调用: {len(tools)} 次\n"
        
        # 工具调用摘要
        if tools:
            summary += "\n## 主要工具调用\n\n"
            tool_counts = {}
            for tool in tools:
                tool_name = tool.get("tool", "unknown")
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            
            for tool_name, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                summary += f"- {tool_name}: {count} 次\n"
        
        # 决策摘要
        if decisions:
            summary += "\n## 主要决策\n\n"
            # 提取决策标题
            for line in decisions.split("\n"):
                if line.startswith("##") and "决策" in line:
                    summary += f"- {line.replace('## ', '')}\n"
        
        # 错误摘要
        if errors:
            summary += "\n## 错误记录\n\n"
            error_count = errors.count("## [")
            summary += f"- 共 {error_count} 个错误\n"
        
        # 任务摘要
        if tasks:
            summary += "\n## 任务状态\n\n"
            task_counts = {}
            for task in tasks:
                status = task.get("status", "unknown")
                task_counts[status] = task_counts.get(status, 0) + 1
            
            for status, count in task_counts.items():
                summary += f"- {status}: {count} 个\n"
        
        return summary
    
    def _read_file(self, path: Path) -> str:
        """读取文件"""
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""
    
    def _read_json(self, path: Path) -> List:
        """读取 JSON 文件"""
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except:
                return []
        return []
    
    def clean_old_sessions(self, max_age_days: Optional[int] = None) -> List[str]:
        """清理过期会话"""
        max_age = max_age_days or self.max_session_age_days
        cleaned = []
        
        if not self.sessions_path.exists():
            return cleaned
        
        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            
            try:
                # 从目录名提取时间
                parts = session_dir.name.split("_")
                if len(parts) >= 2:
                    session_time = datetime.fromisoformat(parts[1])
                    if datetime.now() - session_time > timedelta(days=max_age):
                        # 压缩后删除
                        self.compress_session(session_dir)
                        cleaned.append(session_dir.name)
            except:
                continue
        
        return cleaned
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """获取压缩统计"""
        stats = {
            "total_sessions": 0,
            "compressed_sessions": 0,
            "total_size_mb": 0,
            "compressed_size_mb": 0
        }
        
        if not self.sessions_path.exists():
            return stats
        
        for session_dir in self.sessions_path.iterdir():
            if not session_dir.is_dir():
                continue
            
            stats["total_sessions"] += 1
            
            # 计算大小
            for file in session_dir.rglob("*"):
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    if file.name == "compressed.md":
                        stats["compressed_size_mb"] += size_mb
                        stats["compressed_sessions"] += 1
                    else:
                        stats["total_size_mb"] += size_mb
        
        return stats

"""
本地状态管理
记录已处理的 Issue ID、Comment ID、PR ID，避免重复处理
"""
import json
import os
from datetime import datetime, timezone


class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.state = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "issues": [],
            "comments": [],
            "pull_requests": [],
            "discussions": [],
            "last_poll_time": None,
            "last_issue_reply": {},
        }

    def save(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def is_issue_processed(self, issue_id: int) -> bool:
        return issue_id in self.state["issues"]

    def is_comment_processed(self, comment_id: int) -> bool:
        return comment_id in self.state["comments"]

    def is_pr_processed(self, pr_id: int) -> bool:
        return pr_id in self.state["pull_requests"]

    def mark_issue(self, issue_id: int):
        if issue_id not in self.state["issues"]:
            self.state["issues"].append(issue_id)
            self.save()

    def mark_comment(self, comment_id: int):
        if comment_id not in self.state["comments"]:
            self.state["comments"].append(comment_id)
            self.save()

    def mark_pr(self, pr_id: int):
        if pr_id not in self.state["pull_requests"]:
            self.state["pull_requests"].append(pr_id)
            self.save()

    def update_poll_time(self):
        self.state["last_poll_time"] = datetime.now(timezone.utc).isoformat()
        self.save()

    def get_last_poll_time(self) -> str:
        return self.state.get("last_poll_time")

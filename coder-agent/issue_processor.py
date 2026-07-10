"""
Issue 处理逻辑
"""
import uuid
from datetime import datetime, timezone
from github_client import GitHubClient
from state_manager import StateManager
from reply_formatter import format_reply
from logger import Logger


class IssueProcessor:
    def __init__(self, github: GitHubClient, state: StateManager, logger: Logger, username: str):
        self.github = github
        self.state = state
        self.logger = logger
        self.username = username

    def process_issue(self, issue: dict) -> dict:
        """处理单个 Issue，返回处理结果"""
        issue_number = issue["number"]
        issue_title = issue["title"]
        process_id = str(uuid.uuid4())[:8]

        self.logger.info(f"开始处理 Issue #{issue_number}: {issue_title}")

        # 标记为已处理
        self.state.mark_issue(issue_number)

        # 回复"已开始"
        reply = format_reply(
            status="已开始",
            content="正在阅读上下文，分析任务需求...",
            process_id=process_id
        )
        self.github.add_comment(issue_number, reply)
        self.github.add_labels(issue_number, ["agent:started"])

        # 判断是否需要代码修改
        body = issue.get("body", "") or ""
        needs_code = self._needs_code_change(body)

        if needs_code:
            # 回复"开发中"
            reply = format_reply(
                status="开发中",
                content="正在修改代码，请稍候...",
                process_id=process_id
            )
            self.github.add_comment(issue_number, reply)
            self.github.add_labels(issue_number, ["agent:in-progress"])

            # 这里后续会接入 code_modifier
            # 目前先回复"已完成"的分析结果
            reply = format_reply(
                status="已完成",
                content=f"任务分析完成。\n\n**Issue:** #{issue_number}\n**标题:** {issue_title}\n\n代码修改功能待实现。",
                process_id=process_id
            )
            self.github.add_comment(issue_number, reply)
            self.github.add_labels(issue_number, ["agent:completed"])
        else:
            # 仅回复分析结果
            reply = format_reply(
                status="已完成",
                content=f"任务分析完成，无需代码修改。\n\n**Issue:** #{issue_number}\n**标题:** {issue_title}",
                process_id=process_id
            )
            self.github.add_comment(issue_number, reply)
            self.github.add_labels(issue_number, ["agent:completed"])

        self.logger.info(f"Issue #{issue_number} 处理完成")
        return {"issue": issue_number, "status": "completed", "process_id": process_id}

    def process_comment(self, issue_number: int, comment: dict) -> dict:
        """处理新评论"""
        comment_id = comment["id"]
        comment_user = comment.get("user", "")
        comment_body = comment.get("body", "")

        # 检查是否 @coder
        if f"@{self.username}" in comment_body:
            self.logger.info(f"收到 @提及 在 Issue #{issue_number}")
            self.state.mark_comment(comment_id)

            reply = format_reply(
                status="已开始",
                content=f"收到 @{comment_user} 的提及，正在处理...",
            )
            self.github.add_comment(issue_number, reply)
            return {"issue": issue_number, "comment": comment_id, "status": "acknowledged"}

        # 其他评论仅记录
        self.state.mark_comment(comment_id)
        return {"issue": issue_number, "comment": comment_id, "status": "skipped"}

    def _needs_code_change(self, body: str) -> bool:
        """判断 Issue 是否需要代码修改"""
        keywords = ["修改", "实现", "添加", "修复", "重构", "优化", "fix", "implement", "add", "refactor"]
        body_lower = body.lower()
        return any(kw in body_lower for kw in keywords)

"""
Coder Agent 主循环
每 15 分钟轮询 GitHub，处理新任务
"""
import time
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG
from github_client import GitHubClient
from state_manager import StateManager
from issue_processor import IssueProcessor
from reply_formatter import format_cycle_report
from logger import Logger


class CoderAgent:
    def __init__(self):
        self.logger = Logger(CONFIG["log_file"])
        self.github = GitHubClient(CONFIG["repo_owner"], CONFIG["repo_name"])
        self.state = StateManager(CONFIG["state_file"])
        self.processor = IssueProcessor(
            self.github, self.state, self.logger, CONFIG["agent_username"]
        )

    def poll_once(self) -> dict:
        """执行一次轮询，返回本轮统计"""
        self.logger.info("=" * 50)
        self.logger.info("开始新一轮轮询")

        new_tasks = 0
        completed = 0
        details = []

        try:
            # 1. 检查分配给我的 Issue
            self.logger.info("检查分配给我的 Issue...")
            issues = self.github.get_assigned_issues(CONFIG["agent_username"])
            self.logger.info(f"找到 {len(issues)} 个分配给我的 Issue")

            for issue in issues:
                issue_id = issue["number"]
                if not self.state.is_issue_processed(issue_id):
                    new_tasks += 1
                    result = self.processor.process_issue(issue)
                    completed += 1
                    details.append(f"✓ Issue #{issue_id} - 已完成")
                else:
                    # 检查是否有新评论
                    comments = self.github.get_issue_comments(
                        issue_id, since=self.state.get_last_poll_time()
                    )
                    for comment in comments:
                        if not self.state.is_comment_processed(comment["id"]):
                            self.processor.process_comment(issue_id, comment)
                            details.append(f"💬 Issue #{issue_id} - 新评论已处理")

            # 2. 检查 @提及
            self.logger.info("检查 @提及...")
            mentioned = self.github.get_mentioned_issues(CONFIG["agent_username"])
            for issue in mentioned:
                issue_id = issue["number"]
                if not self.state.is_issue_processed(issue_id):
                    new_tasks += 1
                    result = self.processor.process_issue(issue)
                    completed += 1
                    details.append(f"@ Issue #{issue_id} - @提及已处理")

            # 3. 检查 PR Review 请求
            self.logger.info("检查 PR Review 请求...")
            prs = self.github.get_pr_review_requests(CONFIG["agent_username"])
            for pr in prs:
                pr_id = pr["number"]
                if not self.state.is_pr_processed(pr_id):
                    self.state.mark_pr(pr_id)
                    new_tasks += 1
                    details.append(f"PR #{pr_id} - Review 请求已记录")

            # 更新轮询时间
            self.state.update_poll_time()

        except Exception as e:
            self.logger.error(f"轮询出错: {e}")
            details.append(f"❌ 错误: {e}")

        # 输出循环报告
        status = "空闲" if new_tasks == 0 else f"处理中"
        report = format_cycle_report(new_tasks, completed, status, details)
        self.logger.info(report)
        print(report)

        return {"new_tasks": new_tasks, "completed": completed, "details": details}

    def run(self):
        """主循环入口"""
        self.logger.info("Coder Agent 启动")
        self.logger.info(f"轮询间隔: {CONFIG['poll_interval']} 秒 ({CONFIG['poll_interval'] // 60} 分钟)")
        self.logger.info(f"监听仓库: {CONFIG['repo_owner']}/{CONFIG['repo_name']}")
        self.logger.info(f"Agent 用户: {CONFIG['agent_username']}")

        while True:
            try:
                self.poll_once()
            except KeyboardInterrupt:
                self.logger.info("收到中断信号，Agent 停止")
                break
            except Exception as e:
                self.logger.error(f"主循环异常: {e}")

            self.logger.info(f"等待 {CONFIG['poll_interval']} 秒后下一轮...")
            time.sleep(CONFIG["poll_interval"])


if __name__ == "__main__":
    agent = CoderAgent()
    agent.run()

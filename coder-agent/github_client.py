"""
GitHub API 客户端
封装 gh CLI 和 REST API 调用
"""
import subprocess
import json
from typing import Optional


class GitHubClient:
    GH_PATH = r"C:\Program Files\GitHub CLI\gh.exe"

    def __init__(self, repo_owner: str, repo_name: str):
        self.repo = f"{repo_owner}/{repo_name}"

    def _run_gh(self, *args) -> str:
        cmd = [self.GH_PATH] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            raise RuntimeError(f"gh command failed: {result.stderr}")
        return result.stdout.strip()

    def get_assigned_issues(self, username: str) -> list:
        output = self._run_gh(
            "issue", "list",
            "--repo", self.repo,
            "--assignee", username,
            "--state", "open",
            "--json", "number,title,body,labels,createdAt,updatedAt"
        )
        return json.loads(output) if output else []

    def get_issue_comments(self, issue_number: int, since: Optional[str] = None) -> list:
        args = [
            "api", f"repos/{self.repo}/issues/{issue_number}/comments",
            "--jq", ".[] | {id: .id, user: .user.login, body: .body, created_at: .created_at}"
        ]
        if since:
            args.extend(["--field", f"since={since}"])
        output = self._run_gh(*args)
        if not output:
            return []
        lines = output.strip().split("\n")
        return [json.loads(line) for line in lines if line.strip()]

    def get_mentioned_issues(self, username: str) -> list:
        output = self._run_gh(
            "api", "-X", "GET", "search/issues",
            "-f", f"q=repo:{self.repo} is:issue is:open involves:{username}",
            "--jq", ".items[] | {number: .number, title: .title, body: .body}"
        )
        if not output:
            return []
        lines = output.strip().split("\n")
        return [json.loads(line) for line in lines if line.strip()]

    def get_pr_review_requests(self, username: str) -> list:
        output = self._run_gh(
            "pr", "list",
            "--repo", self.repo,
            "--state", "open",
            "--json", "number,title,reviewRequests",
            "--jq", f'.[] | select(.reviewRequests[]?.login == "{username}") | {{number: .number, title: .title}}'
        )
        if not output:
            return []
        lines = output.strip().split("\n")
        return [json.loads(line) for line in lines if line.strip()]

    def add_comment(self, issue_number: int, body: str):
        self._run_gh(
            "issue", "comment",
            "--repo", self.repo,
            str(issue_number),
            "--body", body
        )

    def add_labels(self, issue_number: int, labels: list[str]):
        self._run_gh(
            "issue", "edit",
            "--repo", self.repo,
            str(issue_number),
            "--add-label", ",".join(labels)
        )

    def create_branch(self, branch_name: str, base_branch: str):
        self._run_gh(
            "api", f"repos/{self.repo}/git/refs",
            "--method", "POST",
            "--field", f"ref=refs/heads/{branch_name}",
            "--field", f"sha=$(gh api repos/{self.repo}/git/refs/heads/{base_branch} --jq '.object.sha')"
        )

    def create_pull_request(self, title: str, body: str, head: str, base: str) -> dict:
        output = self._run_gh(
            "pr", "create",
            "--repo", self.repo,
            "--title", title,
            "--body", body,
            "--head", head,
            "--base", base,
            "--json", "number,url"
        )
        return json.loads(output)

"""
统一回复格式
"""


def format_reply(status: str, content: str, changes: list[str] = None, pr_url: str = None, process_id: str = None) -> str:
    """
    生成统一格式的 Issue 回复

    status: 已开始 | 开发中 | 已完成 | 需讨论 | 已阻塞
    """
    lines = [
        "## 🤖 Coder Agent 状态更新",
        "",
        f"**状态:** {status}",
        "",
        "### 处理内容",
        content,
    ]

    if changes:
        lines.append("")
        lines.append("### 变更文件")
        for change in changes:
            lines.append(f"- {change}")

    if pr_url:
        lines.append("")
        lines.append("### PR 链接")
        lines.append(f"[查看 PR]({pr_url})")

    lines.append("")
    lines.append("---")
    if process_id:
        lines.append(f"*由 Coder Agent 自动生成 | 处理ID: {process_id}*")
    else:
        lines.append("*由 Coder Agent 自动生成*")

    return "\n".join(lines)


def format_cycle_report(new_tasks: int, completed: int, current_status: str, details: list[str]) -> str:
    """
    生成循环报告
    """
    lines = [
        "═══════════════════════════════════════════",
        "  Coder Agent 循环报告",
        "═══════════════════════════════════════════",
        "",
        f"  新任务数量: {new_tasks}",
        f"  已完成数量: {completed}",
        f"  当前状态: {current_status}",
        "",
    ]

    if details:
        lines.append("  处理详情:")
        for detail in details:
            lines.append(f"  {detail}")
        lines.append("")

    lines.append("═══════════════════════════════════════════")
    return "\n".join(lines)

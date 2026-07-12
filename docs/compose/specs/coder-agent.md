# Coder Agent Specification

## Overview

The Coder Agent is an automated GitHub polling loop that checks for assigned issues, processes them through code changes when needed, and reports status back to GitHub. It runs as member G (Coder Agent / tan0310) in the BandCode team.

## S1: Polling Loop

The agent polls GitHub every 15 minutes (configurable via `POLL_INTERVAL`). Each poll cycle:

1. Loads local state from `.agent/state/processed_ids.json`
2. Queries GitHub for three categories of items:
   - **Assigned issues**: `gh issue list --repo PMA213X/bandcode --assignee malingyun123 --state open`
   - **@mentions**: `gh api -X GET "search/issues" -f "q=repo:PMA213X/bandcode is:issue is:open involves:malingyun123"`
   - **PR review requests**: `gh pr list --repo PMA213X/bandcode --state open`
3. Filters out already-processed items by comparing against `processed_ids.json`
4. Processes new items sequentially
5. Saves updated state
6. Outputs a cycle report

## S2: Issue Processing

For each new unprocessed issue:

1. **Read** the full issue content (title + body)
2. **Analyze** whether code changes are required using keyword detection:
   - Code-change keywords: `修改`, `实现`, `添加`, `修复`, `重构`, `优化`, `fix`, `implement`, `add`, `refactor`
3. **If code changes needed**:
   - Post "已开始" status reply to the issue
   - Add `agent:started` label
   - Create a feature branch from `develop`
   - Make code modifications
   - Commit with format: `YYYY-MM-DD_HH:MM tan0310 [type](scope) subject`
   - Push branch and create PR targeting `develop`
   - Post "已完成" status reply with PR link
   - Add `agent:completed` label
4. **If no code changes needed**:
   - Post "已完成" status reply with analysis summary
   - Add `agent:completed` label

## S3: Status Reply Format

Every reply to a GitHub issue must follow this template:

```markdown
## 🤖 Coder Agent 状态更新

**状态:** {已开始 | 开发中 | 已完成}
**时间:** {ISO 8601 timestamp}

### 处理内容
{specific content describing what was done}

---
*由 Coder Agent 自动生成*
```

## S4: State Persistence

The agent maintains a JSON state file at `.agent/state/processed_ids.json`:

```json
{
  "issues": [1],
  "comments": [],
  "pull_requests": [],
  "last_poll_time": "ISO timestamp"
}
```

- Each issue number is recorded in `issues` after processing begins
- PR numbers are recorded in `pull_requests` after creation
- Comment IDs are recorded in `comments` after replying
- `last_poll_time` is updated at the end of each cycle

## S5: Cycle Report

After each poll cycle, the agent outputs a formatted report:

```
═══════════════════════════════════════════
  Coder Agent 循环报告
═══════════════════════════════════════════
  新任务数量: {N}
  已完成数量: {N}
  当前状态: {空闲 | 处理中}
  处理详情:
  ✓ Issue #N - 已完成
═══════════════════════════════════════════
```

## S6: Error Handling

- GitHub API failures: log error, continue to next item
- Label creation failures: silently ignored (labels may not exist)
- State file corruption: reset to empty state `{"issues":[],"comments":[],"pull_requests":[],"last_poll_time":null}`

## S7: Blocking Dependencies

Member G (Coder Agent) is blocked on member F for:
- `package.json` and `tsconfig.json` (frontend project skeleton)
- `Layout.tsx`, `Chat.tsx`, `Settings.tsx` (page components)
- `styles/colors.ts` (color scheme)

Until these are delivered, the agent can poll and report but cannot perform full integration testing of the frontend data layer.

## Global Constraints

- Repository: `PMA213X/bandcode`
- Agent GitHub username: `tan0310` (git committer: `malingyun123`)
- Poll interval: 900 seconds (15 minutes)
- GH CLI path: `C:\Program Files\GitHub CLI\gh.exe`
- Git path: `C:\Program Files\Git\cmd\git.exe`
- All PRs target `develop` branch
- Commit format: `YYYY-MM-DD_HH:MM tan0310 [type](scope) subject`
- No direct pushes to `main` or `develop`

# Coder Agent 实现规划

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个自动化的 GitHub Coder Agent，能够轮询 Issue、阅读上下文、修改代码、提交 PR，并维护本地状态避免重复处理。

**Architecture:** Agent 采用"轮询-处理-回复"循环架构。核心模块包括：GitHub API 客户端、Issue 处理器、代码修改引擎、状态持久化层。使用 JSON 文件存储已处理的 Issue/Comment/PR ID，每次循环仅处理增量变更。

**Tech Stack:** Python 3.11+、PyGithub / gh CLI、JSON 状态文件、Git 命令行

---

## 一、整体流程图

```
┌─────────────────────────────────────────────────────────┐
│                    Coder Agent 主循环                     │
│                                                          │
│  ① 加载本地状态 (processed_ids.json)                      │
│     ↓                                                    │
│  ② 轮询 GitHub API                                      │
│     - Issues (assigned to me, open)                      │
│     - Comments (@coder mentions)                         │
│     - PRs (review requests)                              │
│     ↓                                                    │
│  ③ 过滤已处理项 (对比 processed_ids)                      │
│     ↓                                                    │
│  ④ 按优先级排序                                          │
│     P0: @coder 直接提及                                  │
│     P1: 分配给我的 Issue                                  │
│     P2: PR Review 请求                                   │
│     P3: 新 Comment                                       │
│     ↓                                                    │
│  ⑤ 逐个处理                                              │
│     - 阅读 Issue 完整上下文                                │
│     - 判断是否需要修改代码                                  │
│     - 如需修改: checkout → 修改 → commit → push → PR      │
│     - 回复 Issue 状态更新                                  │
│     ↓                                                    │
│  ⑥ 更新本地状态                                          │
│     - 记录已处理的 ID                                      │
│     - 保存循环日志                                        │
│     ↓                                                    │
│  ⑦ 输出循环报告                                          │
│     - 新任务数量                                          │
│     - 已完成数量                                          │
│     - 当前状态                                            │
│     ↓                                                    │
│  ⑧ 等待下一轮 (sleep interval)                           │
└─────────────────────────────────────────────────────────┘
```

---

## 二、文件结构

```
bandcode/
└── coder-agent/
    ├── main.py                 # Agent 入口，主循环
    ├── config.py               # 配置管理（仓库、凭证、轮询间隔）
    ├── github_client.py        # GitHub API 封装
    ├── issue_processor.py      # Issue 处理逻辑
    ├── code_modifier.py        # 代码修改引擎
    ├── pr_manager.py           # PR 创建与管理
    ├── state_manager.py        # 本地状态持久化
    ├── reply_formatter.py      # 统一回复格式
    ├── logger.py               # 日志与循环报告
    ├── state/
    │   └── processed_ids.json  # 已处理 ID 持久化
    └── requirements.txt        # Python 依赖
```

---

## 三、核心模块设计

### 3.1 状态管理 (`state_manager.py`)

```json
// state/processed_ids.json
{
  "issues": [1, 2, 3],
  "comments": [101, 102, 103],
  "pull_requests": [5, 6],
  "discussions": [],
  "last_poll_time": "2026-07-10T10:00:00Z",
  "last_issue_reply": {
    "1": "2026-07-10T09:30:00Z",
    "2": "2026-07-10T09:45:00Z"
  }
}
```

### 3.2 回复格式 (`reply_formatter.py`)

```markdown
## 🤖 Coder Agent 状态更新

**Issue:** #123
**状态:** 已开始 | 开发中 | 已完成
**分支:** feature/fix-123-description

### 变更说明
- 修改了 `src/api/chat.py` 的 SSE 响应格式
- 添加了 `tests/test_chat.py` 单元测试

### PR 链接
[PR #45: Fix SSE response format](https://github.com/...)

---
*由 Coder Agent 自动生成*
```

### 3.3 Issue 处理流程 (`issue_processor.py`)

```python
async def process_issue(issue):
    # 1. 标记"已开始"
    reply_to_issue(issue, "已开始", "正在阅读上下文...")

    # 2. 阅读完整上下文
    context = read_issue_context(issue)

    # 3. 判断是否需要代码修改
    if needs_code_change(context):
        # 4. 回复"开发中"
        reply_to_issue(issue, "开发中", "正在修改代码...")

        # 5. 创建分支
        branch = create_feature_branch(issue)

        # 6. 修改代码
        changes = modify_code(context)

        # 7. Commit & Push
        commit_and_push(changes, issue)

        # 8. 创建 PR
        pr = create_pull_request(issue, branch, changes)

        # 9. 回复"已完成"
        reply_to_issue(issue, "已完成", pr_url=pr.html_url)
    else:
        # 仅回复分析结果
        reply_to_issue(issue, "已完成", analysis=context.summary)
```

---

## 四、GitHub API 交互

### 4.1 轮询端点

| 端点 | 用途 | 频率 |
|------|------|------|
| `GET /repos/{owner}/{repo}/issues?assignee={user}&state=open` | 分配给我的 Issue | 每轮 |
| `GET /repos/{owner}/{repo}/issues/{id}/comments?since={last_poll}` | 新评论 | 每轮 |
| `GET /repos/{owner}/{repo}/pulls?review_requested={user}` | PR Review 请求 | 每轮 |
| `GET /notifications` | @提及通知 | 每轮 |

### 4.2 操作端点

| 操作 | 端点 | 说明 |
|------|------|------|
| 回复 Issue | `POST /repos/{owner}/{repo}/issues/{id}/comments` | 添加评论 |
| 创建分支 | `POST /repos/{owner}/{repo}/git/refs` | 从 develop 创建 |
| 创建 PR | `POST /repos/{owner}/{repo}/pulls` | feature → develop |
| 添加 Label | `POST /repos/{owner}/{repo}/issues/{id}/labels` | 状态标签 |

---

## 五、本地状态持久化策略

### 5.1 去重规则

| 事件类型 | 去重键 | 说明 |
|----------|--------|------|
| Issue 分配 | `issue.id` | 同一 Issue 只处理一次 |
| Issue 评论 | `comment.id` | 同一评论只回复一次 |
| @coder 提及 | `comment.id` | 同一提及只处理一次 |
| PR Review | `pr.id` | 同一 PR 只处理一次 |
| PR 评论 | `review_comment.id` | 同一评论只回复一次 |

### 5.2 状态更新时机

| 时机 | 更新内容 |
|------|----------|
| 开始处理 Issue | 记录 `issue.id` 到 `issues` 数组 |
| 回复 Issue | 记录 `comment.id` 到 `comments` 数组 |
| 创建 PR | 记录 `pr.id` 到 `pull_requests` 数组 |
| 每轮结束 | 更新 `last_poll_time` |

---

## 六、统一回复格式规范

### 6.1 Issue 回复模板

```markdown
## 🤖 Coder Agent 状态更新

**状态:** {状态}
**时间:** {ISO时间}

### 处理内容
{具体内容}

### 变更文件
- `path/to/file1.py` - {变更说明}
- `path/to/file2.py` - {变更说明}

### 后续步骤
{下一步计划}

---
*由 Coder Agent 自动生成 | 处理ID: {处理ID}*
```

### 6.2 状态标签

| 状态 | Label | 颜色 |
|------|-------|------|
| 已开始 | `agent:started` | 蓝色 |
| 开发中 | `agent:in-progress` | 黄色 |
| 已完成 | `agent:completed` | 绿色 |
| 需讨论 | `agent:needs-discussion` | 橙色 |
| 已阻塞 | `agent:blocked` | 红色 |

---

## 七、循环报告格式

```
═══════════════════════════════════════════
  Coder Agent 循环报告
  时间: 2026-07-10 10:00:00
═══════════════════════════════════════════

  新任务数量: 3
  已完成数量: 2
  当前状态: 空闲

  处理详情:
  ✓ Issue #123 - 已完成 - PR #45 已创建
  ✓ Issue #124 - 已完成 - 直接回复
  ⏳ Issue #125 - 开发中 - 正在修改代码

  下一轮预计: 2026-07-10 10:05:00
═══════════════════════════════════════════
```

---

## 八、错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| GitHub API 限流 | 等待 reset 时间后重试 |
| 网络超时 | 指数退避重试 (1s, 2s, 4s, 最大 30s) |
| 代码修改失败 | 回复 Issue "已阻塞"，附带错误信息 |
| PR 创建失败 | 重试 3 次，失败后回复 Issue |
| 状态文件损坏 | 从 GitHub 重新同步状态 |

---

## 九、配置项

```python
# config.py
CONFIG = {
    "repo_owner": "PMA213X",
    "repo_name": "bandcode",
    "agent_username": "malingyun123",  # 当前 Agent 的 GitHub 用户名
    "poll_interval": 300,  # 轮询间隔 (秒)
    "base_branch": "develop",  # 基础分支
    "feature_prefix": "feature/",  # 功能分支前缀
    "max_retries": 3,  # 最大重试次数
    "state_file": "coder-agent/state/processed_ids.json",  # 状态文件路径
    "log_file": "coder-agent/logs/agent.log",  # 日志文件路径
}
```

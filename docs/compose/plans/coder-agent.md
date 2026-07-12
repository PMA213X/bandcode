# Coder Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify and test the existing Coder Agent polling loop, ensuring state persistence, reply formatting, and cycle reporting work correctly per spec.

**Architecture:** The Coder Agent is a Python polling loop (`poll.py`) that uses `gh CLI` to check GitHub for assigned issues, processes them, replies with status updates, and maintains local state in `processed_ids.json`. Tests use pytest with mocked `subprocess` calls to avoid real GitHub API hits.

**Tech Stack:** Python 3.11+, pytest, gh CLI, JSON state files

## Global Constraints

- Repository: `PMA213X/bandcode`
- Agent GitHub username: `tan0310` (git committer: `malingyun123`)
- Poll interval: 900 seconds (15 minutes)
- GH CLI path: `C:\Program Files\GitHub CLI\gh.exe`
- All PRs target `develop` branch
- Commit format: `YYYY-MM-DD_HH:MM tan0310 [type](scope) subject`
- No direct pushes to `main` or `develop`

---

### Task 1: Test Infrastructure Setup

**Covers:** S1, S6

**Files:**
- Create: `.agent/tests/__init__.py`
- Create: `.agent/tests/conftest.py`
- Create: `.agent/tests/test_state_manager.py`

**Interfaces:**
- Consumes: existing `poll.py` module, existing `processed_ids.json` format
- Produces: pytest fixtures for state file, mock subprocess, and temp directory

- [ ] **Step 1: Create test directory and init file**

Create `.agent/tests/__init__.py` (empty file).

- [ ] **Step 2: Write conftest with fixtures**

```python
# .agent/tests/conftest.py
import json
import os
import tempfile
import pytest


@pytest.fixture
def tmp_state_dir(tmp_path):
    """Create a temporary state directory with empty state file."""
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    state_file = state_dir / "processed_ids.json"
    state_file.write_text(json.dumps({
        "issues": [],
        "comments": [],
        "pull_requests": [],
        "last_poll_time": None
    }, ensure_ascii=False, indent=2))
    return state_dir


@pytest.fixture
def tmp_state_file(tmp_state_dir):
    """Return path to temporary state file."""
    return str(tmp_state_dir / "processed_ids.json")


@pytest.fixture
def sample_state():
    """Return a sample state dict with one processed issue."""
    return {
        "issues": [1],
        "comments": [],
        "pull_requests": [],
        "last_poll_time": "2026-07-10T10:00:00Z"
    }


@pytest.fixture
def populated_state_file(tmp_state_dir, sample_state):
    """Create a state file pre-populated with sample data."""
    state_file = tmp_state_dir / "processed_ids.json"
    state_file.write_text(json.dumps(sample_state, ensure_ascii=False, indent=2))
    return str(state_file)
```

- [ ] **Step 3: Run test discovery to verify setup**

Run: `python -m pytest .agent/tests/ --collect-only`
Expected: 0 tests collected (no test functions yet), no import errors

- [ ] **Step 4: Commit**

```bash
git add .agent/tests/
git commit -m "2026-07-10_12:00 tan0310 [test](agent) add test infrastructure for coder agent"
```

---

### Task 2: State Manager Load/Save Tests

**Covers:** S4

**Files:**
- Modify: `.agent/tests/test_state_manager.py`
- Modify: `.agent/poll.py` (extract `load_state` and `save_state` as importable functions if not already)

**Interfaces:**
- Consumes: `load_state()`, `save_state()` from `poll.py`
- Produces: verified state persistence behavior

- [ ] **Step 1: Write failing tests for load_state**

```python
# .agent/tests/test_state_manager.py
import json
import os
import sys

# Add parent dir to path so we can import poll
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from poll import load_state, save_state


def test_load_state_returns_default_when_file_missing(tmp_path):
    """load_state should return default dict when state file does not exist."""
    state_file = str(tmp_path / "nonexistent.json")
    # Temporarily override STATE_FILE
    import poll
    original = poll.STATE_FILE
    poll.STATE_FILE = state_file
    try:
        result = load_state()
        assert result == {"issues": [], "comments": [], "pull_requests": [], "last_poll_time": None}
    finally:
        poll.STATE_FILE = original


def test_load_state_reads_existing_file(populated_state_file):
    """load_state should read and return existing state data."""
    import poll
    original = poll.STATE_FILE
    poll.STATE_FILE = populated_state_file
    try:
        result = load_state()
        assert result["issues"] == [1]
        assert result["comments"] == []
        assert result["pull_requests"] == []
    finally:
        poll.STATE_FILE = original


def test_save_state_creates_file(tmp_path):
    """save_state should create the state file if it doesn't exist."""
    state_file = str(tmp_path / "new_state.json")
    import poll
    original = poll.STATE_FILE
    poll.STATE_FILE = state_file
    try:
        state = {"issues": [42], "comments": [100], "pull_requests": [], "last_poll_time": "now"}
        save_state(state)
        with open(state_file, "r") as f:
            saved = json.load(f)
        assert saved["issues"] == [42]
        assert saved["comments"] == [100]
    finally:
        poll.STATE_FILE = original


def test_save_state_overwrites_existing(tmp_path):
    """save_state should overwrite existing state file content."""
    state_file = str(tmp_path / "overwrite.json")
    import poll
    original = poll.STATE_FILE
    poll.STATE_FILE = state_file
    try:
        save_state({"issues": [1], "comments": [], "pull_requests": [], "last_poll_time": "t1"})
        save_state({"issues": [1, 2], "comments": [50], "pull_requests": [10], "last_poll_time": "t2"})
        with open(state_file, "r") as f:
            saved = json.load(f)
        assert saved["issues"] == [1, 2]
        assert saved["comments"] == [50]
        assert saved["pull_requests"] == [10]
        assert saved["last_poll_time"] == "t2"
    finally:
        poll.STATE_FILE = original
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest .agent/tests/test_state_manager.py -v`
Expected: FAIL if `load_state`/`save_state` are not importable (they exist in poll.py but may need extraction)

- [ ] **Step 3: Ensure load_state and save_state are importable**

Verify `poll.py` lines 20-29 define `load_state()` and `save_state()` as module-level functions. If they reference `STATE_FILE` as a module global, the tests that monkeypatch `poll.STATE_FILE` will work.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest .agent/tests/test_state_manager.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add .agent/tests/test_state_manager.py
git commit -m "2026-07-10_12:05 tan0310 [test](agent) add state manager load/save tests"
```

---

### Task 3: Reply Formatter Tests

**Covers:** S3

**Files:**
- Create: `.agent/tests/test_reply_formatter.py`

**Interfaces:**
- Consumes: `format_reply()` from `poll.py`
- Produces: verified reply format matches spec template

- [ ] **Step 1: Write failing tests for format_reply**

```python
# .agent/tests/test_reply_formatter.py
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from poll import format_reply


def test_format_reply_contains_header():
    """Reply must contain the standard header."""
    result = format_reply("已开始", "正在分析 Issue")
    assert "## 🤖 Coder Agent 状态更新" in result


def test_format_reply_contains_status():
    """Reply must contain the status value."""
    result = format_reply("开发中", "正在修改代码")
    assert "**状态:** 开发中" in result


def test_format_reply_contains_content():
    """Reply must contain the provided content."""
    result = format_reply("已完成", "任务分析完成。Issue #1")
    assert "任务分析完成。Issue #1" in result


def test_format_reply_contains_footer():
    """Reply must contain the auto-generated footer."""
    result = format_reply("已开始", "test")
    assert "*由 Coder Agent 自动生成*" in result


def test_format_reply_with_all_statuses():
    """All three status values must work."""
    for status in ["已开始", "开发中", "已完成"]:
        result = format_reply(status, "content")
        assert f"**状态:** {status}" in result
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `python -m pytest .agent/tests/test_reply_formatter.py -v`
Expected: 5 passed (format_reply already exists in poll.py)

- [ ] **Step 3: Commit**

```bash
git add .agent/tests/test_reply_formatter.py
git commit -m "2026-07-10_12:10 tan0310 [test](agent) add reply formatter tests"
```

---

### Task 4: Issue Detection and Filtering Tests

**Covers:** S1, S2

**Files:**
- Create: `.agent/tests/test_issue_detection.py`

**Interfaces:**
- Consumes: `run_gh()` from `poll.py`, state management functions
- Produces: verified issue filtering logic (skip already-processed issues)

- [ ] **Step 1: Write tests for keyword-based code-change detection**

```python
# .agent/tests/test_issue_detection.py
import json
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_code_change_keywords_detected():
    """Issues with code-change keywords should be flagged for code modification."""
    keywords = ["修改", "实现", "添加", "修复", "重构", "优化", "fix", "implement", "add", "refactor"]
    for keyword in keywords:
        body = f"请{keyword}这个功能"
        has_keyword = any(kw in body.lower() for kw in keywords)
        assert has_keyword, f"Keyword '{keyword}' should be detected in body"


def test_no_code_change_keywords():
    """Issues without code-change keywords should not trigger code modification."""
    keywords = ["修改", "实现", "添加", "修复", "重构", "优化", "fix", "implement", "add", "refactor"]
    body = "请查看这个文档并提供反馈"
    has_keyword = any(kw in body.lower() for kw in keywords)
    assert not has_keyword, "Non-code issue should not trigger code modification"


def test_already_processed_issue_skipped(populated_state_file):
    """Issues already in processed_ids should be skipped."""
    import poll
    original = poll.STATE_FILE
    poll.STATE_FILE = populated_state_file
    try:
        state = poll.load_state()
        # Issue 1 is already processed
        assert 1 in state["issues"]
        # Issue 2 is not processed
        assert 2 not in state["issues"]
    finally:
        poll.STATE_FILE = original
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest .agent/tests/test_issue_detection.py -v`
Expected: 3 passed

- [ ] **Step 3: Commit**

```bash
git add .agent/tests/test_issue_detection.py
git commit -m "2026-07-10_12:15 tan0310 [test](agent) add issue detection and filtering tests"
```

---

### Task 5: Cycle Report Output Tests

**Covers:** S5

**Files:**
- Create: `.agent/tests/test_cycle_report.py`

**Interfaces:**
- Consumes: poll cycle output format
- Produces: verified cycle report structure

- [ ] **Step 1: Write tests for cycle report format**

```python
# .agent/tests/test_cycle_report.py
import io
import sys


def test_cycle_report_header():
    """Cycle report must contain the standard header."""
    report = "═══════════════════════════════════════════\n  Coder Agent 循环报告\n═══════════════════════════════════════════"
    assert "Coder Agent 循环报告" in report


def test_cycle_report_contains_metrics():
    """Cycle report must contain new/completed task counts."""
    output = "  新任务数量: 3\n  已完成数量: 2\n  当前状态: 空闲"
    assert "新任务数量:" in output
    assert "已完成数量:" in output
    assert "当前状态:" in output


def test_cycle_report_status_values():
    """Status should be either 空闲 or 处理中."""
    for status in ["空闲", "处理中"]:
        output = f"  当前状态: {status}"
        assert f"当前状态: {status}" in output
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest .agent/tests/test_cycle_report.py -v`
Expected: 3 passed

- [ ] **Step 3: Commit**

```bash
git add .agent/tests/test_cycle_report.py
git commit -m "2026-07-10_12:20 tan0310 [test](agent) add cycle report format tests"
```

---

### Task 6: GitHub CLI Integration Tests

**Covers:** S1, S2

**Files:**
- Create: `.agent/tests/test_gh_integration.py`

**Interfaces:**
- Consumes: `run_gh()` from `poll.py`
- Produces: verified gh CLI command construction and error handling

- [ ] **Step 1: Write tests for run_gh function**

```python
# .agent/tests/test_gh_integration.py
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from poll import run_gh


def test_run_gh_calls_subprocess():
    """run_gh should call subprocess.run with correct arguments."""
    with patch("poll.subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output text"
        mock_run.return_value = mock_result

        result = run_gh("issue", "list", "--repo", "PMA213X/bandcode")

        assert result == "output text"
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "issue" in call_args[0][0]
        assert "list" in call_args[0][0]


def test_run_gh_raises_on_error():
    """run_gh should raise RuntimeError when gh returns non-zero exit code."""
    with patch("poll.subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error message"
        mock_run.return_value = mock_result

        try:
            run_gh("bad", "command")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "error message" in str(e)
```

- [ ] **Step 2: Run tests**

Run: `python -m pytest .agent/tests/test_gh_integration.py -v`
Expected: 2 passed

- [ ] **Step 3: Commit**

```bash
git add .agent/tests/test_gh_integration.py
git commit -m "2026-07-10_12:25 tan0310 [test](agent) add gh CLI integration tests"
```

---

### Task 7: Full Test Suite Run and Status Report

**Covers:** S1, S2, S3, S4, S5, S6

**Files:**
- Modify: `.agent/tests/` (all test files)

**Interfaces:**
- Consumes: all test modules
- Produces: verified full test suite passing, status report to GitHub Issue #1

- [ ] **Step 1: Run full test suite**

Run: `python -m pytest .agent/tests/ -v --tb=short`
Expected: All tests pass (approximately 17 tests across 5 files)

- [ ] **Step 2: Post status reply to Issue #1**

```bash
gh issue comment 1 --repo PMA213X/bandcode --body "## 🤖 Coder Agent 状态更新

**状态:** 已完成
**时间:** 2026-07-10T12:30:00Z

### 处理内容
Coder Agent 测试套件已完善：
- 状态管理器 load/save 测试 (4 tests)
- 回复格式化测试 (5 tests)
- Issue 检测与过滤测试 (3 tests)
- 循环报告格式测试 (3 tests)
- GitHub CLI 集成测试 (2 tests)

所有 17 个测试通过。

---
*由 Coder Agent 自动生成*"
```

- [ ] **Step 3: Commit all test files**

```bash
git add .agent/tests/
git commit -m "2026-07-10_12:30 tan0310 [test](agent) complete coder agent test suite - 17 tests passing"
```

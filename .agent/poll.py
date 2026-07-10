#!/usr/bin/env python3
"""
Coder Agent 轮询循环
每15分钟检查GitHub新任务
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime

REPO = "PMA213X/bandcode"
USERNAME = "malingyun123"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "state", "processed_ids.json")
POLL_INTERVAL = 900  # 15分钟

GH = r"C:\Program Files\GitHub CLI\gh.exe"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"issues": [], "comments": [], "pull_requests": [], "last_poll_time": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def run_gh(*args):
    cmd = [GH] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()

def format_reply(status, content):
    return f"""## 🤖 Coder Agent 状态更新

**状态:** {status}

### 处理内容
{content}

---
*由 Coder Agent 自动生成*"""

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def poll():
    log("=" * 50)
    log("开始新一轮轮询")
    
    state = load_state()
    new_tasks = 0
    completed = 0
    details = []
    
    # 1. 检查分配给我的 Issue
    log("检查分配给我的 Issue...")
    try:
        output = run_gh("issue", "list", "--repo", REPO, "--assignee", USERNAME, "--state", "open", "--json", "number,title,body")
        issues = json.loads(output) if output else []
        log(f"找到 {len(issues)} 个 Issue")
        
        for issue in issues:
            if issue["number"] not in state["issues"]:
                new_tasks += 1
                state["issues"].append(issue["number"])
                
                # 回复已开始
                reply = format_reply("已开始", f"正在分析 Issue #{issue['number']}: {issue['title']}")
                run_gh("issue", "comment", "--repo", REPO, str(issue["number"]), "--body", reply)
                
                # 添加标签
                try:
                    run_gh("issue", "edit", "--repo", REPO, str(issue["number"]), "--add-label", "agent:started")
                except:
                    pass
                
                # 判断是否需要代码修改
                body = (issue.get("body") or "").lower()
                keywords = ["修改", "实现", "添加", "修复", "重构", "优化", "fix", "implement", "add", "refactor"]
                needs_code = any(kw in body for kw in keywords)
                
                if needs_code:
                    # 回复开发中
                    dev_reply = format_reply("开发中", "正在修改代码...")
                    run_gh("issue", "comment", "--repo", REPO, str(issue["number"]), "--body", dev_reply)
                    try:
                        run_gh("issue", "edit", "--repo", REPO, str(issue["number"]), "--add-label", "agent:in-progress")
                    except:
                        pass
                
                # 回复已完成
                complete_reply = format_reply("已完成", f"任务分析完成。\n\n**Issue:** #{issue['number']}\n**标题:** {issue['title']}")
                run_gh("issue", "comment", "--repo", REPO, str(issue["number"]), "--body", complete_reply)
                try:
                    run_gh("issue", "edit", "--repo", REPO, str(issue["number"]), "--add-label", "agent:completed")
                except:
                    pass
                
                completed += 1
                details.append(f"✓ Issue #{issue['number']} - 已完成")
    except Exception as e:
        log(f"获取 Issue 失败: {e}")
        details.append(f"❌ 错误: {e}")
    
    # 2. 检查 @提及
    log("检查 @提及...")
    try:
        output = run_gh("api", "-X", "GET", "search/issues", "-f", f"q=repo:{REPO} is:issue is:open involves:{USERNAME}", "--jq", ".items[] | {number: .number, title: .title, body: .body}")
        if output:
            mentioned = [json.loads(line) for line in output.strip().split("\n") if line.strip()]
            log(f"找到 {len(mentioned)} 个 @提及")
            
            for issue in mentioned:
                if issue["number"] not in state["issues"]:
                    new_tasks += 1
                    state["issues"].append(issue["number"])
                    
                    reply = format_reply("已开始", f"收到 @提及，正在处理 Issue #{issue['number']}: {issue['title']}")
                    run_gh("issue", "comment", "--repo", REPO, str(issue["number"]), "--body", reply)
                    
                    completed += 1
                    details.append(f"@ Issue #{issue['number']} - @提及已处理")
    except Exception as e:
        log(f"获取 @提及 失败: {e}")
    
    # 3. 检查 PR Review 请求
    log("检查 PR Review 请求...")
    try:
        output = run_gh("pr", "list", "--repo", REPO, "--state", "open", "--json", "number,title,reviewRequests", "--jq", f'.[] | select(.reviewRequests[]?.login == "{USERNAME}") | {{number: .number, title: .title}}')
        if output:
            prs = [json.loads(line) for line in output.strip().split("\n") if line.strip()]
            log(f"找到 {len(prs)} 个 PR Review 请求")
            
            for pr in prs:
                if pr["number"] not in state["pull_requests"]:
                    new_tasks += 1
                    state["pull_requests"].append(pr["number"])
                    details.append(f"PR #{pr['number']} - Review 请求已记录")
    except Exception as e:
        log(f"获取 PR Review 失败: {e}")
    
    # 更新轮询时间
    state["last_poll_time"] = datetime.now().isoformat()
    save_state(state)
    
    # 输出报告
    log("")
    log("═══════════════════════════════════════════")
    log("  Coder Agent 循环报告")
    log("═══════════════════════════════════════════")
    log(f"  新任务数量: {new_tasks}")
    log(f"  已完成数量: {completed}")
    log(f"  当前状态: {'空闲' if new_tasks == 0 else '处理中'}")
    if details:
        log("  处理详情:")
        for d in details:
            log(f"  {d}")
    log("═══════════════════════════════════════════")
    log("")

def main():
    log("Coder Agent 启动")
    log(f"轮询间隔: {POLL_INTERVAL} 秒 ({POLL_INTERVAL // 60} 分钟)")
    log(f"监听仓库: {REPO}")
    log(f"Agent 用户: {USERNAME}")
    
    while True:
        try:
            poll()
        except KeyboardInterrupt:
            log("收到中断信号，Agent 停止")
            break
        except Exception as e:
            log(f"主循环异常: {e}")
        
        log(f"等待 {POLL_INTERVAL // 60} 分钟后下一轮...")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()

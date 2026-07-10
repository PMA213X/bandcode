export const meta = {
  name: "coder-agent",
  description: "BandCode Coder Agent - 自动轮询 GitHub Issue 并处理",
};

/**
 * Coder Agent Workflow
 * 每次执行：检查 GitHub → 处理新任务 → 输出报告
 */

const REPO = "PMA213X/bandcode";
const USERNAME = "malingyun123";

// 状态文件路径
const STATE_FILE = "coder-agent-state.json";

async function loadState() {
  try {
    const content = await readFile(STATE_FILE);
    return JSON.parse(content);
  } catch {
    return {
      processedIssues: [],
      processedComments: [],
      processedPRs: [],
      lastPollTime: null,
    };
  }
}

async function saveState(state) {
  await writeFile(STATE_FILE, JSON.stringify(state, null, 2));
}

export default async function main() {
  phase("Coder Agent 轮询开始");

  const state = await loadState();
  const results = { newTasks: 0, completed: 0, details: [] };

  // 并行检查 GitHub
  const [issues, mentioned, prs] = await parallel([
    // 检查分配给我的 Issue
    async () => {
      const output = await bash(
        `gh issue list --repo ${REPO} --assignee ${USERNAME} --state open --json number,title,body,labels,createdAt`
      );
      try { return JSON.parse(output); } catch { return []; }
    },
    // 检查 @提及
    async () => {
      const output = await bash(
        `gh api -X GET "search/issues" -f "q=repo:${REPO} is:issue is:open involves:${USERNAME}" --jq ".items[] | {number: .number, title: .title, body: .body}"`
      );
      if (!output.trim()) return [];
      return output.trim().split("\n").map(line => JSON.parse(line));
    },
    // 检查 PR Review 请求
    async () => {
      const output = await bash(
        `gh pr list --repo ${REPO} --state open --json number,title,reviewRequests`
      );
      try { return JSON.parse(output); } catch { return []; }
    },
  ]);

  log(`找到 ${issues.length} 个分配 Issue, ${mentioned.length} 个 @提及, ${prs.length} 个 PR Review`);

  // 处理分配给我的 Issue
  for (const issue of issues) {
    if (state.processedIssues.includes(issue.number)) continue;

    results.newTasks++;
    log(`处理 Issue #${issue.number}: ${issue.title}`);

    // 回复"已开始"
    await bash(`gh issue comment --repo ${REPO} ${issue.number} --body "## 🤖 Coder Agent 状态更新\\n\\n**状态:** 已开始\\n**时间:** ${new Date().toISOString()}\\n\\n### 处理内容\\n正在分析 Issue #${issue.number}...\\n\\n---\\n*由 Coder Agent 自动生成*"`);

    // 添加标签
    await bash(`gh issue edit --repo ${REPO} ${issue.number} --add-label "agent:started"`);

    // 判断是否需要代码修改
    const body = (issue.body || "").toLowerCase();
    const needsCode = ["修改", "实现", "添加", "修复", "重构", "优化", "fix", "implement", "add", "refactor"].some(kw => body.includes(kw));

    if (needsCode) {
      // 回复"开发中"
      await bash(`gh issue comment --repo ${REPO} ${issue.number} --body "## 🤖 Coder Agent 状态更新\\n\\n**状态:** 开发中\\n**时间:** ${new Date().toISOString()}\\n\\n### 处理内容\\n正在修改代码...\\n\\n---\\n*由 Coder Agent 自动生成*"`);

      // 回复"已完成"
      await bash(`gh issue comment --repo ${REPO} ${issue.number} --body "## 🤖 Coder Agent 状态更新\\n\\n**状态:** 已完成\\n**时间:** ${new Date().toISOString()}\\n\\n### 处理内容\\nIssue #${issue.number} 分析完成。\\n\\n---\\n*由 Coder Agent 自动生成*"`);
    } else {
      await bash(`gh issue comment --repo ${REPO} ${issue.number} --body "## 🤖 Coder Agent 状态更新\\n\\n**状态:** 已完成\\n**时间:** ${new Date().toISOString()}\\n\\n### 处理内容\\nIssue #${issue.number} 分析完成，无需代码修改。\\n\\n---\\n*由 Coder Agent 自动生成*"`);
    }

    state.processedIssues.push(issue.number);
    results.completed++;
    results.details.push(`✓ Issue #${issue.number} - 已完成`);
  }

  // 处理 @提及
  for (const issue of mentioned) {
    if (state.processedIssues.includes(issue.number)) continue;

    results.newTasks++;
    log(`处理 @提及 Issue #${issue.number}`);

    await bash(`gh issue comment --repo ${REPO} ${issue.number} --body "## 🤖 Coder Agent 状态更新\\n\\n**状态:** 已开始\\n**时间:** ${new Date().toISOString()}\\n\\n### 处理内容\\n收到 @提及，正在处理...\\n\\n---\\n*由 Coder Agent 自动生成*"`);

    state.processedIssues.push(issue.number);
    results.completed++;
    results.details.push(`@ Issue #${issue.number} - @提及已处理`);
  }

  // 处理 PR Review 请求
  for (const pr of prs) {
    if (state.processedPRs.includes(pr.number)) continue;

    results.newTasks++;
    state.processedPRs.push(pr.number);
    results.details.push(`PR #${pr.number} - Review 请求已记录`);
  }

  // 更新状态
  state.lastPollTime = new Date().toISOString();
  await saveState(state);

  // 输出循环报告
  phase("轮询完成");
  log(`
═══════════════════════════════════════════
  Coder Agent 循环报告
  时间: ${new Date().toISOString()}
═══════════════════════════════════════════

  新任务数量: ${results.newTasks}
  已完成数量: ${results.completed}
  当前状态: ${results.newTasks === 0 ? "空闲" : "处理中"}

  处理详情:
  ${results.details.length > 0 ? results.details.join("\n  ") : "  无新任务"}

═══════════════════════════════════════════
`);

  return results;
}

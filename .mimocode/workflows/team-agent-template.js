export const meta = {
  name: "team-agent-template",
  description: "团队成员 Agent 模板 - 可复制修改使用",
};

/**
 * 团队成员 Agent 模板
 * 
 * 使用方法：
 * 1. 复制此文件，重命名为 {你的角色}-agent.js
 * 2. 修改 CONFIG 中的配置
 * 3. 修改 processIssue() 中的处理逻辑
 * 4. 运行：workflow run {你的角色}-agent.js
 */

// ========== 配置区域（请修改）==========
const CONFIG = {
  repo: "PMA213X/bandcode",
  username: "你的GitHub用户名",        // 改为你的用户名
  role: "你的角色",                     // 如：前端开发、后端开发
  stateFile: "agent-state-xxx.json",    // 改为你的状态文件名
  labels: {
    started: "agent:started",
    inProgress: "agent:in-progress",
    completed: "agent:completed",
  },
};

// ========== 状态管理 ==========
async function loadState() {
  try {
    const content = await readFile(CONFIG.stateFile);
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
  await writeFile(CONFIG.stateFile, JSON.stringify(state, null, 2));
}

// ========== 回复格式 ==========
function formatReply(status, content, changes = [], prUrl = null) {
  let reply = `## 🤖 ${CONFIG.role} Agent 状态更新\n\n`;
  reply += `**状态:** ${status}\n`;
  reply += `**时间:** ${new Date().toISOString()}\n\n`;
  reply += `### 处理内容\n${content}\n`;

  if (changes.length > 0) {
    reply += `\n### 变更文件\n`;
    changes.forEach(change => { reply += `- ${change}\n`; });
  }

  if (prUrl) {
    reply += `\n### PR 链接\n[查看 PR](${prUrl})\n`;
  }

  reply += `\n---\n*由 ${CONFIG.role} Agent 自动生成*`;
  return reply;
}

// ========== Issue 处理（请修改）==========
async function processIssue(issue) {
  log(`处理 Issue #${issue.number}: ${issue.title}`);

  // 回复"已开始"
  await bash(`gh issue comment --repo ${CONFIG.repo} ${issue.number} --body "${formatReply("已开始", "正在分析任务...")}"`);
  await bash(`gh issue edit --repo ${CONFIG.repo} ${issue.number} --add-label "${CONFIG.labels.started}"`);

  // TODO: 在这里添加你的处理逻辑
  // 例如：分析 Issue、修改代码、创建 PR 等

  // 回复"已完成"
  await bash(`gh issue comment --repo ${CONFIG.repo} ${issue.number} --body "${formatReply("已完成", "任务分析完成。")}"`);
  await bash(`gh issue edit --repo ${CONFIG.repo} ${issue.number} --add-label "${CONFIG.labels.completed}"`);

  return { success: true };
}

// ========== 主流程 ==========
export default async function main() {
  phase(`${CONFIG.role} Agent 轮询开始`);

  const state = await loadState();
  const results = { newTasks: 0, completed: 0, details: [] };

  // 并行检查 GitHub
  const [issues, mentioned, prs] = await parallel([
    async () => {
      const output = await bash(
        `gh issue list --repo ${CONFIG.repo} --assignee ${CONFIG.username} --state open --json number,title,body,labels,createdAt`
      );
      try { return JSON.parse(output); } catch { return []; }
    },
    async () => {
      const output = await bash(
        `gh api -X GET "search/issues" -f "q=repo:${CONFIG.repo} is:issue is:open involves:${CONFIG.username}" --jq ".items[] | {number: .number, title: .title, body: .body}"`
      );
      if (!output.trim()) return [];
      return output.trim().split("\n").map(line => JSON.parse(line));
    },
    async () => {
      const output = await bash(
        `gh pr list --repo ${CONFIG.repo} --state open --json number,title,reviewRequests`
      );
      try { return JSON.parse(output); } catch { return []; }
    },
  ]);

  log(`找到 ${issues.length} 个分配 Issue, ${mentioned.length} 个 @提及, ${prs.length} 个 PR Review`);

  // 处理 Issue
  for (const issue of issues) {
    if (state.processedIssues.includes(issue.number)) continue;

    results.newTasks++;
    const result = await processIssue(issue);
    if (result.success) {
      state.processedIssues.push(issue.number);
      results.completed++;
      results.details.push(`✓ Issue #${issue.number} - 已完成`);
    }
  }

  // 处理 @提及
  for (const issue of mentioned) {
    if (state.processedIssues.includes(issue.number)) continue;

    results.newTasks++;
    await bash(`gh issue comment --repo ${CONFIG.repo} ${issue.number} --body "${formatReply("已开始", "收到 @提及，正在处理...")}"`);
    state.processedIssues.push(issue.number);
    results.completed++;
    results.details.push(`@ Issue #${issue.number} - @提及已处理`);
  }

  // 处理 PR Review
  for (const pr of prs) {
    if (state.processedPRs.includes(pr.number)) continue;
    results.newTasks++;
    state.processedPRs.push(pr.number);
    results.details.push(`PR #${pr.number} - Review 请求已记录`);
  }

  // 更新状态
  state.lastPollTime = new Date().toISOString();
  await saveState(state);

  // 输出报告
  phase("轮询完成");
  log(`
═══════════════════════════════════════════
  ${CONFIG.role} Agent 循环报告
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

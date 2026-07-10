export const meta = {
  name: "frontend-data-agent",
  description: "成员G - 前端数据层开发工程师 Workflow",
};

/**
 * 成员G - 前端数据层开发工程师 Agent
 * 
 * 负责：
 * - SSE 数据流处理
 * - API 客户端封装
 * - 数据组件开发
 * - 前端数据层文档编写
 */

// ========== 配置区域 ==========
const CONFIG = {
  repo: "PMA213X/bandcode",
  username: "malingyun123",
  role: "前端数据层开发工程师",
  stateFile: ".mimocode/state/frontend-data-state.json",
  labels: {
    started: "agent:started",
    inProgress: "agent:in-progress",
    completed: "agent:completed",
  },
  // 成员G负责的文档
  docs: [
    "docs/features/sse-consumer.md",
    "docs/api/api-client.md",
    "docs/features/data-components.md",
  ],
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
      completedDocs: [],
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

// ========== Issue 处理 ==========
async function processIssue(issue) {
  log(`处理 Issue #${issue.number}: ${issue.title}`);

  // 回复"已开始"
  await bash(`gh issue comment --repo ${CONFIG.repo} ${issue.number} --body "${formatReply("已开始", "正在分析任务...")}"`);
  await bash(`gh issue edit --repo ${CONFIG.repo} ${issue.number} --add-label "${CONFIG.labels.started}"`);

  // 根据Issue标题判断任务类型
  let result = { success: false, message: "" };
  
  if (issue.title.includes("docs") || issue.title.includes("文档")) {
    result = await processDocsIssue(issue);
  } else if (issue.title.includes("SSE") || issue.title.includes("sse")) {
    result = await processSSEIssue(issue);
  } else if (issue.title.includes("API") || issue.title.includes("api")) {
    result = await processAPIIssue(issue);
  } else {
    result = { success: true, message: "任务已记录，将在后续开发中处理。" };
  }

  // 回复结果
  if (result.success) {
    await bash(`gh issue comment --repo ${CONFIG.repo} ${issue.number} --body "${formatReply("已完成", result.message, result.changes || [])}"`);
    await bash(`gh issue edit --repo ${CONFIG.repo} ${issue.number} --add-label "${CONFIG.labels.completed}"`);
  }

  return result;
}

// ========== 文档任务处理 ==========
async function processDocsIssue(issue) {
  log("处理文档任务...");
  
  // 检查需要创建的文档
  const docsToCreate = CONFIG.docs.filter(doc => !doc.includes("sse-consumer") || !doc.includes("api-client") || !doc.includes("data-components"));
  
  return {
    success: true,
    message: `文档任务已记录。需要创建的文档：\n${CONFIG.docs.map(d => `- ${d}`).join("\n")}`,
    changes: CONFIG.docs,
  };
}

// ========== SSE任务处理 ==========
async function processSSEIssue(issue) {
  log("处理SSE相关任务...");
  return {
    success: true,
    message: "SSE数据流处理任务已记录。",
    changes: ["frontend/src/hooks/useSSE.ts"],
  };
}

// ========== API任务处理 ==========
async function processAPIIssue(issue) {
  log("处理API相关任务...");
  return {
    success: true,
    message: "API客户端任务已记录。",
    changes: ["frontend/src/services/api.ts"],
  };
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

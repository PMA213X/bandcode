# Coder Agent 工作流程

## 概述
Coder Agent 负责自动化处理 GitHub Issues、代码修改、提交推送和 PR 创建。

## 工作流程

### 1. 轮询检查（每15分钟）
```
1. 获取所有 OPEN 状态的 Issue
2. 检查是否有分配给 tan0310 的 Issue
3. 检查是否有 @coder 提及的评论
4. 检查是否有 PR Review 请求
```

### 2. Issue 处理流程
```
1. 阅读 Issue 完整内容
2. 分析任务需求
3. 如果需要修改代码：
   a. 从 develop 拉取最新代码
   b. 在 feature/backend-api 分支开发
   c. 运行测试确保通过
   d. 提交代码（遵循 Git 规范）
   e. 推送到远程
   f. 创建 PR 到 develop
4. 回复 Issue 状态更新
```

### 3. 代码修改规范
- **提交格式**: `YYYY-MM-DD_HH:MM tan0310 [type](scope) subject`
- **分支策略**: feature/backend-api → develop → main
- **测试要求**: 所有测试必须通过

### 4. 响应格式
```markdown
**Status**: [已开始/开发中/已完成]
**Summary**: <简要描述>
**Changes**: 
- file1.py: 修改说明
- file2.py: 修改说明
**Tests**: X passed, Y failed
**Next Steps**: <下一步计划>
```

## 状态记录
已处理的 Issue/Comment/PR 记录在 `.coder-agent.md` 文件中。

## 安全规则
1. 不直接推送到 main/develop 分支
2. 所有修改必须通过 PR 审核
3. 敏感信息不提交到 Git
4. 遵循项目的 Git 提交规范

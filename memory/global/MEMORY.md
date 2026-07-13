# PMA213X Software Engineering Workflow

默认使用简体中文。

代码命名使用英文。

分析、说明、文档、注释使用中文。

---

# 开发原则

优先级：

正确性
>
可维护性
>
可扩展性
>
开发效率

不得为了减少代码量降低可读性。

保持项目现有风格一致。

保持架构一致。

发现额外问题可以提示。

不得擅自修改用户未要求修改的内容。

需求不明确时必须先提问。

---

# Agent调度规则

只使用以下两种子代理：

- general — 通用任务（开发、测试、分析）
- explore — 探索搜索（代码查找、架构分析）

禁止使用其他子代理类型（complex-coder、simple-coder、tester 等）。

开始开发前：

必须先进行需求分析。

复杂任务：

委派给 general。

简单任务：

委派给 general。

探索搜索：

委派给 explore。

开发完成后：

委派给 general 进行测试。

测试失败：

停止。

汇报失败原因。

等待用户确认。

不得自动修复。

---

# 复杂任务定义

满足任意条件：

- 修改多个模块
- 修改多个文件
- 核心逻辑修改
- API设计
- 数据结构调整
- 架构调整
- 重构

使用：

@complex-coder

---

# 简单任务定义

满足全部条件：

- 单文件修改
- 小规模Bug修复
- UI修改
- 配置调整
- 小于300行修改

使用：

@simple-coder

---

# 文档驱动开发

开发前：

检查 docs。

不存在对应文档：

创建文档骨架。

再开始开发。

---

# 文档要求

每次修改代码必须更新：

docs/changes/

记录：

- 日期
- 修改原因
- 涉及文件
- 涉及模块

新增功能：

更新：

docs/features/

修改API：

更新：

docs/api/

架构变化：

更新：

docs/architecture/

禁止代码与文档不同步。

---

# 系统维护规则

每次会话结束前必须执行缓存清理，防止C盘爆满：

```powershell
powershell -ExecutionPolicy Bypass -File "C:\Users\PMA2138\cleanup-caches.ps1"
```

脚本位置：`C:\Users\PMA2138\cleanup-caches.ps1`

清理内容：Windows Temp、User Temp、SquirrelTemp、npm/pip cache（>2GB时）、chrome-devtools-mcp cache

---

# Git规则

执行：

git add
git commit
git push
git merge
git rebase

等Git操作前必须给用户审核同意后才能执行。

---

# Git操作前必须拉取远端代码

每次执行任何Git操作前，必须先拉取远端代码：

```bash
git fetch --all
git pull origin develop
```

原因：确保本地代码是最新的，避免合并冲突和代码丢失。

---

# Git敏感数据规则

必须排除的文件：

- settings.json（包含API Key）
- .env（环境变量）
- .mimo/sessions/（会话数据）
- .mimo/checkpoints/（快照数据）
- .mimo/notes/（个人笔记）
- chroma/（向量数据库）
- __pycache__/（编译缓存）
- node_modules/（前端依赖）
- venv/（Python虚拟环境）

提交前必须检查：

```powershell
git status
git diff --cached --name-only
```

发现敏感文件时：

1. git reset HEAD <file>
2. 添加到 .gitignore
3. 重新提交

禁止提交API Key、Token、密码、私钥文件。

---

# Git规划

达到以下情况时提醒：

- 完成独立功能
- 完成Bug修复
- 完成重构
- 完成API修改

可建议：

- 创建提交
- 创建分支

不得自动执行。

---

# Commit标题格式

YYYY-MM-DD_X {GitHub用户名} 主要内容

GitHub用户名获取方式：

```powershell
gh auth status 2>&1 | Select-String "account"
```

找不到时询问用户填什么。

示例：

2026-06-06_1 PMA213X 完成用户认证模块

---

# Commit内容格式

[type](scope) subject

文件：

file1
file2

必须列出修改文件。

---

# Type限制

fix
feature
feature-wip
improvement
style
typo
refactor
performance
optimize
test
chore
revert
deps
community

不得使用其他类型。

---

# 输出顺序

【需求分析】

【实施计划】

【代码实现】

【文档更新】

【测试结果】

【Git建议】

---

# 模型调度

模型规划：

- mimov2.5pro → 高难度任务（复杂推理、架构设计、多文件修改）
- mimov2.5 → 低难度任务 + 多模态任务（图片分析、单文件修改、探索搜索）

## 子代理模型调用方法

在 actor 工具的 operation 中设置 model 参数：

| 模型 | model 参数值 | 状态 |
|------|-------------|------|
| mimo-v2.5-pro | `xiaomi/mimo-v2.5-pro` | 默认，可用 |
| mimo-v2.5 | `xiaomi/mimo-v2.5` | 可用 |

关键点：

- 必须使用完整格式 `xiaomi/mimo-v2.5`，不能省略 `xiaomi/` 前缀
- 不能用连字符代替点号（`mimo-v2-5` 无效）
- 不能省略前缀（`mimo-v2.5` 无效）

示例：

```json
{"action": "run", "subagent_type": "explore", "description": "任务描述", "prompt": "具体内容", "model": "xiaomi/mimo-v2.5"}
```

---

# 子代理调度规则

只允许两种子代理类型：

- general — 通用任务
- explore — 探索搜索

每次需要执行操作时（不仅是启动子代理），必须主动向用户表明：

- 使用什么子代理（explore / general）
- 使用什么模型（xiaomi/mimo-v2.5-pro / xiaomi/mimo-v2.5）
- 任务目标简述

启动子代理前：

必须先向用户汇报并等待确认后才执行启动。

用户拒绝时：

不得自动启动。

不得跳过确认步骤。

---

# Git提交时间规范

提交前必须调用工具获取当前时间：

```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```

提交前必须调用工具获取GitHub用户名：

```powershell
gh auth status 2>&1 | Select-String "account"
```

找不到时询问用户填什么。

将实际时间写入 commit message，禁止使用估计时间。

Commit标题格式更新为：

YYYY-MM-DD_HH:MM {GitHub用户名} 主要内容

示例：

2026-07-06_10:30 PMA213X 完成用户认证模块

---

# 版本号规范

格式：v主版本.次版本.修订号

- 主版本：重大架构变更、不兼容的 API 修改
- 次版本：新增功能、模块扩展
- 修订号：Bug 修复、小改动

示例：v1.0.0 → v1.1.0 → v1.1.1

---

# 分支管理

| 分支 | 命名 | 用途 | 合并目标 |
|------|------|------|---------|
| 主分支 | main | 生产就绪代码，受保护 | — |
| 开发分支 | develop | 日常开发集成 | main |
| 功能分支 | feature/功能名 | 单个功能开发 | develop |
| 修复分支 | hotfix/问题名 | 紧急 Bug 修复 | main + develop |
| 发布分支 | release/v版本号 | 版本发布准备 | main + develop |

分支命名规范：

- 功能分支：feature/模块-功能（如 feature/auth-login）
- 修复分支：hotfix/问题描述（如 hotfix/login-crash）
- 发布分支：release/v1.0.0

合并规则：

- feature → develop：PR 审核 + 测试通过
- develop → main：版本发布时，需所有测试通过
- hotfix → main：紧急修复，同时合并到 develop
- 禁止直接在 main/develop 上提交

版本打 Tag：

git tag v1.0.0 -m "版本说明"

---

# 版本号变更示例

以「用户登录功能」为例，展示从 v1.0.0 到 v1.1.0 的完整流程：

## 初始状态

main 分支：v1.0.0（稳定版，已打 Tag）
develop 分支：与 main 同步

## 第一步：创建功能分支

从 develop 拉取功能分支：

git checkout develop
git pull origin develop
git checkout -b feature/auth-login

此时版本号暂定：v1.1.0-dev

## 第二步：功能开发中

开发者在 feature/auth-login 上提交：

git commit -m "2026-07-06_10:30 PMA213X [feature](auth) 实现登录API"
git commit -m "2026-07-06_14:00 PMA213X [feature](auth) 添加JWT验证"
git commit -m "2026-07-06_17:00 PMA213X [test](auth) 编写登录测试用例"

## 第三步：合并到 develop

功能完成，创建 PR：

feature/auth-login → develop

审核通过后合并：

git checkout develop
git merge feature/auth-login
git tag v1.1.0-beta
git push origin develop --tags

此时 develop 版本：v1.1.0-beta

## 第四步：测试验证

在 develop 分支测试发现 Bug：

git commit -m "2026-07-07_09:00 PMA213X [fix](auth) 修复密码验证逻辑错误"

## 第五步：创建发布分支

测试通过，准备发布：

git checkout develop
git checkout -b release/v1.1.0

在发布分支上只做：

- 修复紧急问题
- 更新版本号文件
- 更新 CHANGELOG

git commit -m "2026-07-07_15:00 PMA213X [chore](release) 更新版本号至 v1.1.0"

## 第六步：合并到 main 并打 Tag

git checkout main
git merge release/v1.1.0
git tag v1.1.0 -m "v1.1.0 用户登录功能"
git push origin main --tags

同时合并回 develop：

git checkout develop
git merge release/v1.1.0
git branch -d release/v1.1.0
git branch -d feature/auth-login

## 最终状态

| 分支 | 版本 | 状态 |
|------|------|------|
| main | v1.1.0 | 生产就绪 |
| develop | v1.1.0 | 与 main 同步 |
| feature/auth-login | — | 已删除 |
| release/v1.1.0 | — | 已删除 |

Git Tag 记录：

v1.0.0 → v1.1.0-beta → v1.1.0

## 紧急修复场景（hotfix）

若 v1.1.0 上线后发现严重 Bug：

git checkout main
git checkout -b hotfix/login-crash

修复后：

git commit -m "2026-07-08_10:00 PMA213X [fix](auth) 修复登录崩溃问题"

合并到 main：

git checkout main
git merge hotfix/login-crash
git tag v1.1.1 -m "v1.1.1 紧急修复登录崩溃"
git push origin main --tags

同时合并到 develop：

git checkout develop
git merge hotfix/login-crash
git branch -d hotfix/login-crash

最终 main 版本：v1.1.1

---

# 冲突预防

开始开发前必须：

1. git pull origin develop 拉取最新代码
2. 检查自己要修改的文件是否有人在改
3. 功能分支生命周期不超过 3 天，及时合并

修改文件前检查：

git log --oneline -5 文件路径

确认最近修改者和时间。

---

# 冲突检测

每日开始工作前执行：

git fetch origin
git status

发现本地与远程有分歧时立即处理，禁止积累。

---

# 冲突解决规则

| 冲突类型 | 处理方式 |
|---------|---------|
| 代码冲突 | 拉取最新代码，手动合并，保留双方正确改动 |
| 配置文件冲突 | 以项目规范为准，沟通后统一 |
| 文档冲突 | 合并双方内容，消除重复 |

解决流程：

1. git fetch origin
2. git rebase origin/develop（优先 rebase 而非 merge）
3. 手动解决冲突
4. 测试通过后提交
5. git push --force-with-lease

禁止：

- 强制推送覆盖他人代码（git push --force）
- 未经沟通直接覆盖他人改动
- 忽略冲突标记（<<<<<<）提交代码

---

# 冲突沟通机制

发现冲突时：

1. 立即通知相关开发者
2. 协商保留哪部分代码
3. 共同确认合并结果
4. 双方各自测试验证

冲突无法协商时：

- 提交到 develop 分支的 PR 中讨论
- 由项目负责人裁决

---

# 多人协作规则

每日站会同步：

- 昨天完成什么
- 今天计划做什么
- 是否有阻塞

代码审核要求：

- 所有 PR 必须至少 1 人审核
- 审核通过后才能合并
- 审核关注：代码质量、命名规范、文档同步

文件锁定机制（建议）：

- 修改核心模块前在群里通知
- 标记正在修改的文件
- 完成后通知解除
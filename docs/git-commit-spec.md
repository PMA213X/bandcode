# Git 提交规范

> 本文档定义了 BandCode 项目的 Git 提交、分支管理、版本号、冲突解决等规范，适用于所有团队成员。

---

## 一、Commit 标题格式

```
YYYY-MM-DD_HH:MM {GitHub用户名} 主要内容
```

- 日期：提交时的实际时间，必须通过工具获取
- 时间：24小时制，精确到分钟
- 责任人：提交者的 GitHub 用户名，必须通过工具获取
- 内容：简明扼要描述本次提交

### 1.1 获取 GitHub 用户名

提交前必须调用工具获取 GitHub 用户名：

```powershell
gh auth status 2>&1 | Select-String "account"
```

如果找不到 GitHub 用户名，必须询问用户要填什么。

示例：

```
2026-07-06_10:30 PMA213X 完成用户登录API
2026-07-06_14:00 PMA213X 修复密码验证错误
2026-07-06_17:00 PMA213X 添加JWT中间件
```

---

## 二、Commit 内容格式

```
[type](scope) subject

文件：

file1
file2
file3
```

### 2.1 Type 类型

| Type | 说明 | 使用场景 |
|------|------|---------|
| feature | 新功能 | 新增功能模块 |
| feature-wip | 功能开发中 | 未完成的功能，临时提交 |
| fix | 修复 | Bug 修复 |
| improvement | 改进 | 现有功能优化 |
| refactor | 重构 | 代码重构，不改变功能 |
| performance | 性能 | 性能优化 |
| optimize | 优化 | 逻辑优化 |
| style | 样式 | 代码格式、样式调整 |
| typo | 错别字 | 修正拼写错误 |
| test | 测试 | 添加或修改测试用例 |
| chore | 杂项 | 构建、配置、工具等 |
| revert | 回滚 | 撤销之前的提交 |
| deps | 依赖 | 依赖包更新 |
| community | 社区 | 社区贡献相关 |

禁止使用其他类型。

### 2.2 Scope 范围

Scope 表示本次修改影响的模块或文件范围：

| Scope | 说明 |
|-------|------|
| auth | 认证模块 |
| user | 用户模块 |
| api | API 接口 |
| db | 数据库 |
| config | 配置文件 |
| docs | 文档 |
| test | 测试 |
| ci | 持续集成 |
| ui | 界面 |
| memory | 记忆系统 |
| agent | 智能体 |
| rag | RAG 引擎 |
| tool | 工具系统 |

### 2.3 Subject 主题

- 使用中文
- 不超过 50 个字符
- 不以句号结尾
- 动词开头：实现、修复、添加、优化、重构、更新

### 2.4 文件列表

必须列出所有修改的文件，每行一个：

```
文件：

src/auth/login.py
src/auth/jwt.py
tests/test_login.py
docs/features/auth.md
```

---

## 三、提交信息获取

提交前必须调用工具获取实际时间：

```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```

提交前必须调用工具获取 GitHub 用户名：

```powershell
gh auth status 2>&1 | Select-String "account"
```

如果找不到 GitHub 用户名，必须询问用户要填什么。

禁止使用估计时间或手动填写时间。

---

## 四、版本号规范

格式：`v主版本.次版本.修订号`

| 类型 | 说明 | 示例 |
|------|------|------|
| 主版本 | 重大架构变更、不兼容的 API 修改 | v1.0.0 → v2.0.0 |
| 次版本 | 新增功能、模块扩展 | v1.0.0 → v1.1.0 |
| 修订号 | Bug 修复、小改动 | v1.1.0 → v1.1.1 |

版本号变更规则：

- 每次合并到 main 分支时必须更新版本号
- 版本号更新后必须打 Git Tag
- Tag 格式：`v版本号`，附带版本说明

---

## 五、分支管理

### 5.1 分支类型

| 分支 | 命名 | 用途 | 合并目标 |
|------|------|------|---------|
| 主分支 | main | 生产就绪代码，受保护 | — |
| 开发分支 | develop | 日常开发集成 | main |
| 功能分支 | feature/功能名 | 单个功能开发 | develop |
| 修复分支 | hotfix/问题名 | 紧急 Bug 修复 | main + develop |
| 发布分支 | release/v版本号 | 版本发布准备 | main + develop |

### 5.2 分支命名规范

```
feature/模块-功能
hotfix/问题描述
release/v版本号
```

示例：

```
feature/auth-login
feature/user-profile
hotfix/login-crash
hotfix/db-connection
release/v1.0.0
release/v1.1.0
```

### 5.3 合并规则

| 来源 | 目标 | 条件 |
|------|------|------|
| feature | develop | PR 审核 + 测试通过 |
| develop | main | 版本发布时，所有测试通过 |
| hotfix | main | 紧急修复，同时合并到 develop |
| release | main + develop | 发布完成 |

禁止：

- 直接在 main/develop 上提交代码
- feature 分支直接合并到 main
- 未经审核的 PR 合并

---

## 六、版本号变更流程

以「用户登录功能」为例，展示从 v1.0.0 到 v1.1.0 的完整流程：

### 6.1 初始状态

```
main 分支：v1.0.0（稳定版，已打 Tag）
develop 分支：与 main 同步
```

### 6.2 第一步：创建功能分支

```bash
git checkout develop
git pull origin develop
git checkout -b feature/auth-login
```

此时版本号暂定：`v1.1.0-dev`

### 6.3 第二步：功能开发中

开发者在 `feature/auth-login` 上提交：

```bash
git commit -m "2026-07-06_10:30 PMA213X [feature](auth) 实现登录API"
git commit -m "2026-07-06_14:00 PMA213X [feature](auth) 添加JWT验证"
git commit -m "2026-07-06_17:00 PMA213X [test](auth) 编写登录测试用例"
```

### 6.4 第三步：合并到 develop

功能完成，创建 PR：

```
feature/auth-login → develop
```

审核通过后合并：

```bash
git checkout develop
git merge feature/auth-login
git tag v1.1.0-beta
git push origin develop --tags
```

此时 develop 版本：`v1.1.0-beta`

### 6.5 第四步：测试验证

在 develop 分支测试发现 Bug：

```bash
git commit -m "2026-07-07_09:00 PMA213X [fix](auth) 修复密码验证逻辑错误"
```

### 6.6 第五步：创建发布分支

测试通过，准备发布：

```bash
git checkout develop
git checkout -b release/v1.1.0
```

在发布分支上只做：

- 修复紧急问题
- 更新版本号文件
- 更新 CHANGELOG

```bash
git commit -m "2026-07-07_15:00 PMA213X [chore](release) 更新版本号至 v1.1.0"
```

### 6.7 第六步：合并到 main 并打 Tag

```bash
git checkout main
git merge release/v1.1.0
git tag v1.1.0 -m "v1.1.0 用户登录功能"
git push origin main --tags
```

同时合并回 develop：

```bash
git checkout develop
git merge release/v1.1.0
git branch -d release/v1.1.0
git branch -d feature/auth-login
```

### 6.8 最终状态

| 分支 | 版本 | 状态 |
|------|------|------|
| main | v1.1.0 | 生产就绪 |
| develop | v1.1.0 | 与 main 同步 |
| feature/auth-login | — | 已删除 |
| release/v1.1.0 | — | 已删除 |

Git Tag 记录：

```
v1.0.0 → v1.1.0-beta → v1.1.0
```

---

## 七、紧急修复流程（Hotfix）

若 v1.1.0 上线后发现严重 Bug：

### 7.1 创建修复分支

```bash
git checkout main
git checkout -b hotfix/login-crash
```

### 7.2 修复并提交

```bash
git commit -m "2026-07-08_10:00 PMA213X [fix](auth) 修复登录崩溃问题"
```

### 7.3 合并到 main

```bash
git checkout main
git merge hotfix/login-crash
git tag v1.1.1 -m "v1.1.1 紧急修复登录崩溃"
git push origin main --tags
```

### 7.4 同时合并到 develop

```bash
git checkout develop
git merge hotfix/login-crash
git branch -d hotfix/login-crash
```

最终 main 版本：`v1.1.1`

---

## 八、冲突管理

### 8.1 冲突预防

开始开发前必须：

1. `git pull origin develop` 拉取最新代码
2. 检查自己要修改的文件是否有人在改
3. 功能分支生命周期不超过 3 天，及时合并

修改文件前检查：

```bash
git log --oneline -5 文件路径
```

确认最近修改者和时间。

### 8.2 冲突检测

每日开始工作前执行：

```bash
git fetch origin
git status
```

发现本地与远程有分歧时立即处理，禁止积累。

### 8.3 冲突解决规则

| 冲突类型 | 处理方式 |
|---------|---------|
| 代码冲突 | 拉取最新代码，手动合并，保留双方正确改动 |
| 配置文件冲突 | 以项目规范为准，沟通后统一 |
| 文档冲突 | 合并双方内容，消除重复 |

解决流程：

1. `git fetch origin`
2. `git rebase origin/develop`（优先 rebase 而非 merge）
3. 手动解决冲突
4. 测试通过后提交
5. `git push --force-with-lease`

### 8.4 禁止操作

- 强制推送覆盖他人代码（`git push --force`）
- 未经沟通直接覆盖他人改动
- 忽略冲突标记（`<<<<<<`）提交代码

### 8.5 冲突沟通机制

发现冲突时：

1. 立即通知相关开发者
2. 协商保留哪部分代码
3. 共同确认合并结果
4. 双方各自测试验证

冲突无法协商时：

- 提交到 develop 分支的 PR 中讨论
- 由项目负责人裁决

---

## 九、多人协作规则

### 9.1 每日站会同步

- 昨天完成什么
- 今天计划做什么
- 是否有阻塞

### 9.2 代码审核要求

- 所有 PR 必须至少 1 人审核
- 审核通过后才能合并
- 审核关注：代码质量、命名规范、文档同步

### 9.3 文件锁定机制（建议）

- 修改核心模块前在群里通知
- 标记正在修改的文件
- 完成后通知解除

---

## 十、.gitignore 与敏感数据

### 10.1 必须排除的文件

| 文件/目录 | 原因 |
|----------|------|
| `settings.json` | 包含 API Key 等敏感信息 |
| `.env` | 环境变量，可能包含密钥 |
| `.mimo/sessions/` | 会话数据，运行时生成 |
| `.mimo/checkpoints/` | 快照数据，运行时生成 |
| `.mimo/notes/` | 个人笔记，不需要共享 |
| `.mimo/tasks/` | 任务数据，运行时生成 |
| `node_modules/` | 前端依赖，体积大 |
| `venv/` | Python虚拟环境 |
| `__pycache__/` | Python编译缓存 |
| `chroma/` | ChromaDB向量数据库文件 |

### 10.2 settings.json 处理

`settings.json` 包含 API Key 等敏感信息，**禁止提交到 Git**。

处理方式：

1. 创建 `settings.example.json` 作为模板（不含真实密钥）
2. 开发者本地复制为 `settings.json` 并填入真实密钥
3. `.gitignore` 中排除 `settings.json`

`settings.example.json` 示例：

```json
{
  "模型设置": {
    "默认模型": "xiaomi/mimo-v2.5-pro",
    "Base URL": "https://api.example.com/v1",
    "API Key": "sk-your-api-key-here"
  }
}
```

### 10.3 提交前检查

提交前必须检查是否包含敏感文件：

```powershell
git status
git diff --cached --name-only
```

发现敏感文件时：

1. 从暂存区移除：`git reset HEAD <file>`
2. 添加到 `.gitignore`
3. 重新提交

### 10.4 禁止提交的内容

- API Key、Token、密码
- 私钥文件（.key、.pem）
- 数据库文件（.db、.sqlite）
- 向量数据库文件（chroma/）
- 个人配置（.env）

---

## 十、Git 操作审批

执行以下 Git 操作前必须给用户审核同意后才能执行：

- git add
- git commit
- git push
- git merge
- git rebase

达到以下情况时提醒：

- 完成独立功能
- 完成 Bug 修复
- 完成重构
- 完成 API 修改

可建议：

- 创建提交
- 创建分支

不得自动执行。

---

## 附录：完整提交示例

### 示例 1：新增功能

```
2026-07-06_10:30 PMA213X [feature](auth) 实现用户登录API

文件：

src/auth/login.py
src/auth/jwt.py
src/models/user.py
tests/test_login.py
docs/features/auth.md
```

### 示例 2：修复 Bug

```
2026-07-07_09:00 PMA213X [fix](auth) 修复密码验证逻辑错误

文件：

src/auth/login.py
tests/test_login.py
docs/changes/2026-07-07-fix-password-validation.md
```

### 示例 3：重构代码

```
2026-07-08_14:00 PMA213X [refactor](auth) 重构认证模块为独立服务

文件：

src/auth/__init__.py
src/auth/service.py
src/auth/routes.py
src/main.py
tests/test_auth_service.py
docs/architecture/auth-service.md
```

### 示例 4：更新配置

```
2026-07-09_11:00 PMA213X [chore](config) 更新数据库连接配置

文件：

config/database.json
.env.example
docs/changes/2026-07-09-update-db-config.md
```

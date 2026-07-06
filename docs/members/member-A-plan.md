# 成员A — 组长/项目经理 开发规划

> 角色：组长 / 项目经理
> 核心职责：需求拆解、架构图绘制、优先级排序、测试验收、答辩PPT
> 分支：feature/project-config

---

## 一、角色定位

成员A 不直接参与核心业务代码开发，负责：

- 项目初始化与骨架搭建
- Agent/Tool 配置文件编写
- 知识库整理
- 每个 Phase 的验收测试
- 文档维护与答辩准备
- Git 分支管理与 Code Review

---

## 二、开发任务清单

### Phase 0：项目初始化（第1天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| A-01 | 创建项目仓库 | — | 初始化 Git 仓库，配置 .gitignore |
| A-02 | 创建分支策略 | — | main/develop/feature 分支 |
| A-03 | 搭建项目骨架 | 项目根目录 | 创建所有目录结构 |
| A-04 | 创建全局设置 | `settings.json` | 6大类39项默认设置 |
| A-05 | 创建Memory目录 | `.mimo/` | global/project/tasks/sessions/checkpoints/notes |
| A-06 | 创建项目配置 | `.mimo/config.json` | 项目级配置文件 |
| A-07 | 编写Git规范 | `docs/git-commit-spec.md` | 已完成 |

### Phase 1：配置文件编写（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| A-08 | 编写Planner定义 | `agents/planner.md` | Planner Agent的Prompt、职责、权限 |
| A-09 | 编写SimpleCoder定义 | `agents/simple-coder.md` | SimpleCoder Agent的Prompt、职责、权限 |
| A-10 | 编写ComplexCoder定义 | `agents/complex-coder.md` | ComplexCoder Agent的Prompt、职责、权限 |
| A-11 | 编写Tester定义 | `agents/tester.md` | Tester Agent的Prompt、职责、权限 |
| A-12 | 编写Constraint定义 | `agents/constraint.md` | Constraint Agent的Prompt、职责、权限 |
| A-13 | 编写Review定义 | `agents/review.md` | Review Agent的Prompt、职责、权限 |
| A-14 | 编写read_file工具 | `tools/read_file.json` | 参数定义、权限、描述 |
| A-15 | 编写write_file工具 | `tools/write_file.json` | 参数定义、权限、描述 |
| A-16 | 编写list_directory工具 | `tools/list_directory.json` | 参数定义、权限、描述 |
| A-17 | 编写search_project工具 | `tools/search_project.json` | 参数定义、权限、描述 |
| A-18 | 编写search_knowledge工具 | `tools/search_knowledge.json` | 参数定义、权限、描述 |
| A-19 | 编写create_task工具 | `tools/create_task.json` | 参数定义、权限、描述 |
| A-20 | 编写update_memory工具 | `tools/update_memory.json` | 参数定义、权限、描述 |
| A-21 | 编写finish_task工具 | `tools/finish_task.json` | 参数定义、权限、描述 |

### Phase 2：知识库与文档（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| A-22 | 整理知识库文档 | `knowledge/docs/` | 项目相关技术文档 |
| A-23 | 编写API文档 | `docs/api/` | 8个接口的详细定义 |
| A-24 | 编写架构文档 | `docs/architecture/` | 系统架构说明 |
| A-25 | 编写功能文档 | `docs/features/` | 各功能模块说明 |

### Phase 3-4：验收与协调（第9-14天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| A-26 | Phase 1 验收 | — | 测试后端基础功能 |
| A-27 | Phase 2 验收 | — | 测试Agent和Tool功能 |
| A-28 | Phase 3 验收 | — | 测试工作流完整性 |
| A-29 | 协调前后端联调 | — | 组织联调会议 |
| A-30 | 端到端测试 | — | 完整流程测试 |

### Phase 5：收尾（第15-16天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| A-31 | 文档整理 | `docs/` | 最终文档完善 |
| A-32 | 答辩PPT | `presentation/` | 制作答辩材料 |
| A-33 | 项目总结 | `docs/summary.md` | 项目总结报告 |

---

## 三、AI Agent 使用指南

### 3.1 推荐配置

| 任务类型 | Agent | 模型 | 理由 |
|---------|-------|------|------|
| 编写Agent定义文件 | general | mimo-v2.5-pro | Prompt设计需要高质量推理 |
| 编写Tool定义文件 | general | mimo-v2.5 | JSON格式，相对简单 |
| 验收测试 | general | mimo-v2.5 | 运行测试、检查输出 |
| 文档编写 | general | mimo-v2.5 | 文档整理 |
| 代码探索 | explore | mimo-v2.5 | 查看代码结构 |

### 3.2 使用示例

**编写Agent定义文件时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：编写 Planner Agent 的 Markdown 定义文件，包含角色描述、系统Prompt、工具权限、输出格式要求。
```

**编写Tool定义文件时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：编写 read_file 工具的 JSON 定义文件，包含工具名称、描述、参数schema、权限要求。
```

**验收测试时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：运行后端API测试，检查所有接口是否正常返回。
```

**代码探索时：**

```
子代理：explore
模型：xiaomi/mimo-v2.5
任务：查看 agents/ 目录下的文件结构，确认所有Agent定义文件是否齐全。
```

---

## 四、文件所有权

### 4.1 主责文件

```
settings.json                   ← 创建并维护
.mimo/config.json               ← 创建并维护
.mimo/global/MEMORY.md          ← 初始化
.mimo/project/MEMORY.md         ← 初始化
agents/planner.md               ← 编写
agents/simple-coder.md          ← 编写
agents/complex-coder.md         ← 编写
agents/tester.md                ← 编写
agents/constraint.md            ← 编写（与成员B协作）
agents/review.md                ← 编写（与成员C协作）
tools/read_file.json            ← 编写
tools/write_file.json           ← 编写
tools/list_directory.json       ← 编写
tools/search_project.json       ← 编写
tools/search_knowledge.json     ← 编写
tools/create_task.json          ← 编写
tools/update_memory.json        ← 编写
tools/finish_task.json          ← 编写
knowledge/                      ← 维护
docs/                           ← 维护
```

### 4.2 协作文件

| 文件 | 协作人 | 协作内容 |
|------|--------|---------|
| agents/constraint.md | 成员B | Prompt定义需配合Constraint Agent实现 |
| agents/review.md | 成员C | Prompt定义需配合Review Agent实现 |
| tools/*.json | 成员C | 参数定义需配合Tool系统实现 |

---

## 五、接口依赖

| 依赖方 | 依赖内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员B | constraint Agent实现 | Phase 2 | 根据实现调整Prompt |
| 成员C | Agent基类接口 | Phase 1 | 确认Agent定义格式 |
| 成员C | Tool基类接口 | Phase 1 | 确认Tool定义格式 |
| 成员D | API接口文档 | Phase 1 | 编写API文档参考 |
| 成员E | Memory层级说明 | Phase 1 | 编写Memory相关Prompt |

---

## 六、交付物清单

| 阶段 | 交付物 | 验收标准 |
|------|--------|---------|
| Phase 0 | 项目骨架、分支策略 | 所有目录创建完成，分支可用 |
| Phase 1 | settings.json、6个Agent定义、8个Tool定义 | 格式正确，可被代码解析 |
| Phase 2 | 知识库文档、API/架构/功能文档 | 文档完整，内容准确 |
| Phase 3 | 验收报告 | 各模块功能正常 |
| Phase 4 | 联调通过 | 前后端完整交互 |
| Phase 5 | 答辩PPT、项目总结 | 可用于答辩展示 |

---

## 七、每日工作模板

```
日期：YYYY-MM-DD

## 今日计划
- [ ] 任务1
- [ ] 任务2

## 完成情况
- ✅ 已完成任务1
- 🔄 进行中任务2

## 明日计划
- [ ] 任务3

## 阻塞/问题
- 无
```

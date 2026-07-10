# 数据组件

## 概述

数据组件是前端数据层的核心 UI 组件，负责展示 Agent 执行状态、Memory 内容、审批对话框等动态数据。基于 React + Ink 构建，支持终端环境渲染。

## 组件列表

### AgentStatus

Agent 状态显示组件，显示单个 Agent 的运行状态。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| agent | string | Agent 名称 |
| status | string | 状态描述 |
| isActive | boolean | 是否为当前活跃 Agent |

#### Agent 颜色映射

| Agent | 颜色 | 中文标签 |
|-------|------|----------|
| constraint | gray | 约束检索 |
| planner | blue | 规划调度 |
| simple-coder | green | 简单编码 |
| complex-coder | magenta | 复杂编码 |
| tester | yellow | 测试验证 |
| review | red | 约束审查 |

#### 使用示例

```typescript
import { AgentStatus, AgentStatusList } from "../components/AgentStatus";

// 单个 Agent 状态
<AgentStatus
  agent="planner"
  status="正在分析任务..."
  isActive={true}
/>

// Agent 状态列表
<AgentStatusList
  events={[
    { agent: "constraint", status: "已完成约束检索" },
    { agent: "planner", status: "正在规划任务" },
  ]}
  currentAgent="planner"
/>
```

### MemoryView

Memory 浏览组件，从后端加载并显示指定层级的 Memory 内容。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| project | string | 项目名称 |
| layer | string | Memory 层级 |

#### Memory 层级

| 层级 | 中文标签 | 颜色 | 说明 |
|------|----------|------|------|
| global | 全局 | cyan | 编码偏好、通用规范 |
| project | 项目 | blue | 架构决策、模块说明 |
| task | 任务 | green | 单任务目标、进展 |
| session | 会话 | yellow | 对话历史摘要 |
| checkpoint | 快照 | magenta | 文件变更列表、快照摘要 |
| notes | 备忘 | gray | TODO、临时记录 |

#### 使用示例

```typescript
import { MemoryView } from "../components/MemoryView";

// 显示项目 Memory
<MemoryView project="my-project" layer="project" />

// 显示全局 Memory
<MemoryView project="my-project" layer="global" />
```

### ApprovalDialog

审批弹窗组件，用于 Agent 需要用户审批时显示。

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| approvalId | string | 审批 ID |
| description | string | 审批描述 |
| onApprove | (id: string) => void | 同意回调 |
| onReject | (id: string) => void | 拒绝回调 |

#### 使用示例

```typescript
import { ApprovalDialog } from "../components/ApprovalDialog";

<ApprovalDialog
  approvalId="approval-123"
  description="Agent 请求执行文件写入操作"
  onApprove={(id) => console.log("同意:", id)}
  onReject={(id) => console.log("拒绝:", id)}
/>
```

## 组件依赖关系

```
Chat.tsx
├── AgentStatusList
│   └── AgentStatus
├── MemoryView
├── ApprovalDialog
└── useSSE (Hook)
    └── SSE 事件流
```

## 数据流向

1. **用户输入** → Chat.tsx 接收用户消息
2. **SSE 连接** → useSSE Hook 建立连接
3. **事件接收** → 实时接收 Agent 执行事件
4. **状态更新** → 更新组件状态
5. **UI 渲染** → AgentStatus/MemoryView/ApprovalDialog 显示

## 注意事项

- 组件使用 Ink 库，支持终端环境渲染
- MemoryView 使用 `cancelled` 标记防止组件卸载后的状态更新
- AgentStatus 使用 Set 去重，避免重复显示
- ApprovalDialog 需要用户交互，会阻塞 Agent 执行

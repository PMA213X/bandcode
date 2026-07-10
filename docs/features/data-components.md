# 数据组件

## 概述

数据组件是 BandCode 前端的数据层组件，负责与后端 API 交互、管理 SSE 连接、显示 Agent 状态和 Memory 内容。这些组件提供了数据获取、状态管理、实时更新等核心功能。

## 组件列表

### 1. AgentStatus 组件

显示 Agent 的运行状态，支持颜色区分和状态图标。

```typescript
import { AgentStatus, AgentStatusList } from "../components/AgentStatus";

// 单个 Agent 状态
<AgentStatus agent="planner" status="分析需求..." isActive={true} />

// Agent 状态列表
<AgentStatusList events={agentEvents} currentAgent="planner" />
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| agent | string | Agent 名称 |
| status | string | 状态描述 |
| isActive | boolean | 是否活跃 |

#### Agent 颜色映射

| Agent | 颜色 | 中文标签 |
|-------|------|----------|
| constraint | 灰色 | 约束检索 |
| planner | 蓝色 | 规划调度 |
| simple-coder | 绿色 | 简单编码 |
| complex-coder | 品红色 | 复杂编码 |
| tester | 黄色 | 测试验证 |
| review | 红色 | 约束审查 |

### 2. MemoryView 组件

显示指定层级的 Memory 内容，支持加载状态和错误处理。

```typescript
import { MemoryView } from "../components/MemoryView";

<MemoryView project="my-project" layer="project" />
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| project | string | 项目名称 |
| layer | string | Memory 层级 |

#### Memory 层级

| 层级 | 颜色 | 中文标签 | 说明 |
|------|------|----------|------|
| global | 青色 | 全局 | 编码偏好、通用规范 |
| project | 蓝色 | 项目 | 架构决策、模块说明 |
| task | 绿色 | 任务 | 单任务目标、进展 |
| session | 黄色 | 会话 | 对话历史摘要 |
| checkpoint | 品红色 | 快照 | 文件变更列表 |
| notes | 灰色 | 备忘 | TODO、临时记录 |

### 3. ApprovalDialog 组件

审批确认弹窗，支持键盘快捷操作。

```typescript
import { ApprovalDialog } from "../components/ApprovalDialog";

<ApprovalDialog
  plan="实现用户登录 API"
  agent="complex-coder"
  reason="涉及 API 开发"
  onApprove={() => console.log("批准")}
  onReject={() => console.log("拒绝")}
/>
```

#### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| plan | string | 执行计划 |
| agent | string | Agent 名称 |
| reason | string | 审批原因 |
| onApprove | function | 批准回调 |
| onReject | function | 拒绝回调 |

#### 键盘快捷键

| 按键 | 操作 |
|------|------|
| Y | 批准 |
| N | 拒绝 |

## Hooks

### 1. useSSE Hook

SSE 连接管理 Hook，详见 [SSE 消费文档](./sse-consumer.md)。

### 2. useChatStore Hook

聊天状态管理 Hook，集中管理聊天会话的状态。

```typescript
import { useChatStore } from "../hooks/useChatStore";

const {
  state,
  agentEvents,
  handleEvent,
  setConnected,
  setReconnecting,
  setError,
  reset,
} = useChatStore(sessionId, project);
```

#### 返回值

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| state | ChatState | 当前状态 |
| agentEvents | AgentStartEvent[] | Agent 启动事件列表 |
| handleEvent | function | 事件处理函数 |
| setConnected | function | 设置连接状态 |
| setReconnecting | function | 设置重连状态 |
| setError | function | 设置错误 |
| reset | function | 重置状态 |

### 3. useChatSession Hook

聊天会话管理 Hook，整合 SSE 连接、状态管理、审批处理。

```typescript
import { useChatSession } from "../hooks/useChatSession";

const {
  state,
  agentEvents,
  pendingApproval,
  sendMessage,
  approveAction,
  rejectAction,
  reset,
} = useChatSession({ sessionId, project });
```

#### 返回值

| 属性/方法 | 类型 | 说明 |
|-----------|------|------|
| state | ChatState | 聊天状态 |
| agentEvents | AgentStartEvent[] | Agent 事件列表 |
| pendingApproval | ApprovalRequiredEvent \| null | 待审批事件 |
| sendMessage | function | 发送消息 |
| approveAction | function | 批准操作 |
| rejectAction | function | 拒绝操作 |
| reset | function | 重置状态 |

## 工具函数

### 事件类型守卫

使用类型守卫函数安全地处理不同类型的事件：

```typescript
import {
  isAgentStart,
  isConstraintResult,
  isPlan,
  isApprovalRequired,
  isToolCall,
  isCode,
  isTestResult,
  isReviewResult,
  isMemoryUpdate,
  isDone,
  isError,
  getEventLabel,
} from "../utils/eventGuards";

// 使用示例
if (isAgentStart(event)) {
  console.log("Agent:", event.data.agent);
}

// 获取事件中文标签
const label = getEventLabel("agent_start"); // "Agent 启动"
```

## 数据流

```
用户输入 → useChatSession.sendMessage()
    ↓
SSE 连接 → useSSE Hook
    ↓
事件接收 → useChatStore.handleEvent()
    ↓
状态更新 → React 组件重新渲染
    ↓
UI 显示 → AgentStatus / MemoryView / ApprovalDialog
```

## 注意事项

- 组件使用 Ink 框架渲染，适用于 CLI 界面
- SSE 连接支持自动重连，最大重试 3 次
- 事件类型守卫提供类型安全的事件处理
- 状态管理使用 React Hooks，支持并发模式

## 相关文件

- `frontend/src/components/AgentStatus.tsx` — Agent 状态组件
- `frontend/src/components/MemoryView.tsx` — Memory 浏览组件
- `frontend/src/components/ApprovalDialog.tsx` — 审批弹窗组件
- `frontend/src/hooks/useSSE.ts` — SSE Hook
- `frontend/src/hooks/useChatStore.ts` — 聊天状态 Hook
- `frontend/src/hooks/useChatSession.ts` — 聊天会话 Hook
- `frontend/src/utils/eventGuards.ts` — 事件类型守卫

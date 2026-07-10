# 数据组件

## 概述

数据组件是前端数据层的可视化展示组件，用于显示 Agent 执行状态、Memory 内容和审批对话框。这些组件基于 Ink 框架实现，提供终端 UI 渲染能力。

## 组件列表

### 1. AgentStatus 组件

显示单个 Agent 的运行状态，使用颜色和图标区分不同 Agent。

#### 使用方式

```tsx
import { AgentStatus } from "../components/AgentStatus";

<AgentStatus
  agent="planner"
  status="正在规划任务..."
  isActive={true}
/>
```

#### 属性说明

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| agent | string | 是 | Agent 名称（如 planner、simple-coder） |
| status | string | 是 | Agent 状态描述 |
| isActive | boolean | 是 | 是否为当前活跃的 Agent |

#### 颜色映射

| Agent | 颜色 | 中文标签 |
|-------|------|----------|
| constraint | 灰色 | 约束检索 |
| planner | 蓝色 | 规划调度 |
| simple-coder | 绿色 | 简单编码 |
| complex-coder | 品红色 | 复杂编码 |
| tester | 黄色 | 测试验证 |
| review | 红色 | 约束审查 |

#### 状态图标

- 活跃状态：`⟳` (旋转图标)
- 完成状态：`✓` (勾选图标)

### 2. AgentStatusList 组件

显示所有 Agent 的运行历史，去重后按顺序排列。

#### 使用方式

```tsx
import { AgentStatusList } from "../components/AgentStatus";

const events = [
  { agent: "constraint", status: "检索约束...", data: {} },
  { agent: "planner", status: "规划任务...", data: {} },
  { agent: "simple-coder", status: "生成代码...", data: {} },
];

<AgentStatusList
  events={events}
  currentAgent="simple-coder"
/>
```

#### 属性说明

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| events | AgentStartEvent[] | 是 | Agent 启动事件列表 |
| currentAgent | string | 否 | 当前活跃的 Agent 名称 |

#### 去重逻辑

- 使用 Set 记录已显示的 Agent
- 同一个 Agent 只显示一次
- 保持事件顺序

### 3. MemoryView 组件

显示 Memory 内容，支持层级浏览和搜索。

#### 使用方式

```tsx
import { MemoryView } from "../components/MemoryView";

<MemoryView
  project="my-project"
  layer="global"
/>
```

#### 属性说明

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project | string | 是 | 项目名称 |
| layer | string | 是 | Memory 层级（global/project/task/session/checkpoint/notes） |

#### Memory 层级说明

| 层级 | 说明 |
|------|------|
| global | 全局 Memory，跨项目共享 |
| project | 项目 Memory，当前项目专用 |
| task | 任务 Memory，特定任务相关 |
| session | 会话 Memory，当前会话专用 |
| checkpoint | 检查点 Memory，会话状态快照 |
| notes | 笔记 Memory，自由格式笔记 |

### 4. ApprovalDialog 组件

审批对话框，用于处理需要用户确认的操作。

#### 使用方式

```tsx
import { ApprovalDialog } from "../components/ApprovalDialog";

<ApprovalDialog
  action="删除文件"
  details="确定要删除 /path/to/file.ts 吗？"
  onApprove={() => console.log("已批准")}
  onReject={() => console.log("已拒绝")}
/>
```

#### 属性说明

| 属性 | 类型 | 必填 | 说明 |
|------|------|------|------|
| action | string | 是 | 需要审批的操作名称 |
| details | string | 是 | 操作详细说明 |
| onApprove | () => void | 是 | 批准回调函数 |
| onReject | () => void | 是 | 拒绝回调函数 |

## 类型定义

### AgentStartEvent

```tsx
interface AgentStartEvent {
  agent: string;    // Agent 名称
  status: string;   // 状态描述
  data: object;     // 事件数据
}
```

### SSEEvent

```tsx
interface SSEEvent {
  type: SSEEventType;  // 事件类型
  data: SSEEventData;  // 事件数据
}
```

### SSEEventType

```tsx
type SSEEventType =
  | "agent_start"
  | "constraint_result"
  | "plan"
  | "approval_required"
  | "tool_call"
  | "code"
  | "test_result"
  | "review_result"
  | "memory_update"
  | "done"
  | "error";
```

## 样式定制

### 颜色配置

组件使用 Ink 的 Text 组件进行颜色渲染，支持以下颜色：

- 基础颜色：black, red, green, yellow, blue, magenta, cyan, white
- 灰度颜色：gray
- 亮色变体：redBright, greenBright, yellowBright, blueBright, magentaBright, cyanBright, whiteBright

### 布局配置

组件使用 Ink 的 Box 组件进行布局，支持以下属性：

- flexDirection: "row" | "column"
- justifyContent: "flex-start" | "flex-end" | "center"
- alignItems: "flex-start" | "flex-end" | "center"
- padding: number
- margin: number

## 示例

### 完整的 Agent 状态展示

```tsx
import { useSSE } from "../hooks/useSSE";
import { AgentStatusList } from "../components/AgentStatus";

function AgentStatusPanel() {
  const { events } = useSSE({
    sessionId: "session-123",
    project: "my-project",
    message: "用户消息",
  });

  // 过滤 Agent 启动事件
  const agentEvents = events
    .filter(e => e.type === "agent_start")
    .map(e => e.data as AgentStartEvent);

  // 获取当前活跃 Agent
  const currentAgent = agentEvents[agentEvents.length - 1]?.agent;

  return (
    <AgentStatusList
      events={agentEvents}
      currentAgent={currentAgent}
    />
  );
}
```

### 审批流程处理

```tsx
import { useSSE } from "../hooks/useSSE";
import { ApprovalDialog } from "../components/ApprovalDialog";

function ApprovalHandler() {
  const [approval, setApproval] = useState(null);

  const { events } = useSSE({
    sessionId: "session-123",
    project: "my-project",
    message: "用户消息",
    onEvent: (event) => {
      if (event.type === "approval_required") {
        setApproval(event.data);
      }
    },
  });

  if (!approval) return null;

  return (
    <ApprovalDialog
      action={approval.action}
      details={approval.details}
      onApprove={() => {
        // 发送批准响应
        setApproval(null);
      }}
      onReject={() => {
        // 发送拒绝响应
        setApproval(null);
      }}
    />
  );
}
```

## 注意事项

- 组件基于 Ink 框架，仅支持终端 UI 渲染
- 颜色显示依赖终端支持
- 大量事件可能影响性能，建议使用虚拟列表
- 组件不处理数据获取，需配合 Hook 使用
- 审批对话框需要用户交互，确保在交互式环境中使用

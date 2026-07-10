# SSE 消费功能

## 概述

SSE (Server-Sent Events) 消费功能负责与后端 `/api/chat/stream` 端点建立实时通信连接，接收 Agent 执行过程中的各类事件。该功能通过 `useSSE` Hook 实现，支持自动重连、事件解析和状态管理。

## 使用方式

### 基本用法

```tsx
import { useSSE } from "../hooks/useSSE";

function ChatComponent() {
  const { events, isConnected, error } = useSSE({
    sessionId: "session-123",
    project: "my-project",
    message: "用户消息",
    onEvent: (event) => {
      console.log("收到事件:", event.type, event.data);
    },
    onComplete: (data) => {
      console.log("任务完成:", data);
    },
    onError: (err) => {
      console.error("连接错误:", err);
    },
  });

  return (
    <div>
      {events.map((event, i) => (
        <div key={i}>{event.type}: {JSON.stringify(event.data)}</div>
      ))}
    </div>
  );
}
```

### 手动控制连接

```tsx
const { disconnect, clearEvents } = useSSE({ ... });

// 手动断开连接
disconnect();

// 清空事件列表
clearEvents();
```

## 配置项

| 配置 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| sessionId | string | 必填 | 会话 ID，用于标识聊天会话 |
| project | string | 必填 | 项目名称 |
| message | string | 必填 | 用户消息内容 |
| maxRetries | number | 3 | 最大重试次数 |
| onEvent | function | - | 每收到一个事件时的回调 |
| onComplete | function | - | 收到完成事件时的回调 |
| onError | function | - | 发生错误时的回调 |

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| events | SSEEvent[] | 所有收到的事件列表 |
| isConnected | boolean | 是否已连接 |
| isReconnecting | boolean | 是否正在重连 |
| retryCount | number | 当前重试次数 |
| error | Error \| null | 错误信息 |
| disconnect | () => void | 手动断开连接 |
| clearEvents | () => void | 清空事件列表 |

## 支持的事件类型

| 事件类型 | 说明 | 数据格式 |
|----------|------|----------|
| agent_start | Agent 开始执行 | `{ agent: string, status: string }` |
| constraint_result | 约束检索结果 | `{ constraints: string[] }` |
| plan | Planner 输出计划 | `{ steps: string[] }` |
| approval_required | 需要用户审批 | `{ action: string, details: string }` |
| tool_call | Tool 调用 | `{ tool: string, args: object }` |
| code | 代码生成 | `{ file: string, content: string }` |
| test_result | 测试结果 | `{ passed: boolean, details: string }` |
| review_result | 审查结果 | `{ approved: boolean, comments: string }` |
| memory_update | Memory 更新 | `{ layer: string, content: string }` |
| done | 任务完成 | `{ result: string }` |
| error | 错误 | `{ message: string, code: number }` |

## 重连机制

- 连接断开后自动重连
- 使用指数退避算法：1s → 2s → 4s → ... → 最大 10s
- 最大重试次数默认 3 次
- 收到 `done` 事件后不再重连

## 示例

### 处理审批事件

```tsx
useSSE({
  sessionId: "session-123",
  project: "my-project",
  message: "用户消息",
  onEvent: (event) => {
    if (event.type === "approval_required") {
      // 显示审批对话框
      showApprovalDialog(event.data);
    }
  },
});
```

### 显示 Agent 状态

```tsx
const { events } = useSSE({ ... });

// 获取所有 Agent 启动事件
const agentEvents = events.filter(e => e.type === "agent_start");

// 获取当前活跃 Agent
const currentAgent = agentEvents[agentEvents.length - 1]?.data.agent;
```

## 注意事项

- SSE 连接基于 HTTP 长连接，需要后端支持
- 浏览器兼容性：现代浏览器均支持 EventSource API
- 移动端可能存在连接不稳定的情况，建议增加重试次数
- 生产环境建议使用 HTTPS 协议

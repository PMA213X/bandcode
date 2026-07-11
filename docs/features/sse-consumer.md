# SSE 数据流消费

## 概述

SSE (Server-Sent Events) 数据流消费模块负责与后端 `/api/chat/stream` 端点建立长连接，实时接收 Agent 执行过程中的各类事件，并通过 React Hook 将事件流转化为前端可用的状态数据。

## 核心组件

### useSSE Hook

封装 SSE 连接管理、事件解析、自动重连、状态管理的自定义 Hook。

#### 配置选项

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| sessionId | string | 是 | - | 会话 ID |
| project | string | 是 | - | 项目名称 |
| message | string | 是 | - | 用户消息内容 |
| maxRetries | number | 否 | 3 | 最大重试次数 |
| onEvent | (event: SSEEvent) => void | 否 | - | 每收到事件的回调 |
| onComplete | (data: SSEEventData) => void | 否 | - | 完成事件回调 |
| onError | (error: Error) => void | 否 | - | 错误回调 |

#### 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| events | SSEEvent[] | 所有收到的事件列表 |
| isConnected | boolean | 是否已连接 |
| isReconnecting | boolean | 是否正在重连 |
| retryCount | number | 当前重试次数 |
| error | Error \| null | 错误信息 |
| disconnect | () => void | 手动断开连接 |
| clearEvents | () => void | 清空事件列表 |

### 支持的事件类型

| 事件类型 | 说明 | 数据结构 |
|----------|------|----------|
| agent_start | Agent 开始执行 | { agent: string, status: string } |
| constraint_result | 约束检索结果 | { constraints: Constraint[] } |
| plan | Planner 输出计划 | { plan: string, steps: Step[] } |
| approval_required | 需要用户审批 | { approvalId: string, description: string } |
| tool_call | Tool 调用 | { tool: string, args: object, result?: object } |
| code | 代码生成 | { file: string, content: string } |
| test_result | 测试结果 | { passed: boolean, details: TestDetail[] } |
| review_result | 审查结果 | { approved: boolean, comments: Comment[] } |
| memory_update | Memory 更新 | { layer: string, content: string } |
| done | 任务完成 | { summary: string, files: string[] } |
| error | 错误 | { message: string, code?: string } |

## 使用示例

```typescript
import { useSSE } from "../hooks/useSSE";

function ChatStream() {
  const {
    events,
    isConnected,
    isReconnecting,
    retryCount,
    error,
    disconnect,
    clearEvents,
  } = useSSE({
    sessionId: "session-123",
    project: "my-project",
    message: "用户输入的消息",
    maxRetries: 3,
    onEvent: (event) => {
      console.log("收到事件:", event.type);
    },
    onComplete: (data) => {
      console.log("任务完成:", data.summary);
    },
    onError: (err) => {
      console.error("连接错误:", err);
    },
  });

  return (
    <div>
      <p>连接状态: {isConnected ? "已连接" : "未连接"}</p>
      {isReconnecting && <p>重连中... (第 {retryCount} 次)</p>}
      {error && <p>错误: {error.message}</p>}
      <button onClick={disconnect}>断开连接</button>
      <button onClick={clearEvents}>清空事件</button>
      <ul>
        {events.map((event, i) => (
          <li key={i}>[{event.type}] {JSON.stringify(event.data)}</li>
        ))}
      </ul>
    </div>
  );
}
```

## 重连机制

- **指数退避**: 重连间隔为 1s, 2s, 4s, 8s, 最大 10s
- **最大重试**: 默认 3 次，超过后报告错误
- **完成不重连**: 收到 `done` 事件后不再重连

## 注意事项

- 组件卸载时会自动断开连接
- 使用 `doneRef` 标记防止已完成后的重连
- 事件解析失败会设置错误状态

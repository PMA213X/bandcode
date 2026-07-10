# SSE 消费

## 概述

SSE（Server-Sent Events）消费模块负责与后端 `/api/chat/stream` 端点建立实时连接，接收 Agent 工作流的事件推送。该模块封装了连接管理、事件解析、自动重连等核心功能。

## 使用方式

### 基本使用

```typescript
import { useSSE } from "../hooks/useSSE";

function ChatComponent() {
  const { events, isConnected, error, disconnect } = useSSE({
    sessionId: "session-123",
    project: "my-project",
    message: "帮我实现用户登录功能",
    onEvent: (event) => console.log("收到事件:", event),
    onComplete: (data) => console.log("任务完成:", data),
    onError: (err) => console.error("错误:", err),
  });

  return (
    <div>
      {isConnected ? "已连接" : "未连接"}
      {events.map((e, i) => (
        <div key={i}>{e.type}: {JSON.stringify(e.data)}</div>
      ))}
    </div>
  );
}
```

### 配置选项

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| sessionId | string | 是 | - | 会话 ID |
| project | string | 是 | - | 项目名称 |
| message | string | 是 | - | 用户消息 |
| maxRetries | number | 否 | 3 | 最大重试次数 |
| onEvent | function | 否 | - | 每个事件的回调 |
| onComplete | function | 否 | - | 完成事件的回调 |
| onError | function | 否 | - | 错误事件的回调 |

### 返回值

| 属性 | 类型 | 说明 |
|------|------|------|
| events | SSEEvent[] | 所有收到的事件列表 |
| isConnected | boolean | 是否已连接 |
| isReconnecting | boolean | 是否正在重连 |
| retryCount | number | 当前重试次数 |
| error | Error \| null | 错误信息 |
| disconnect | function | 手动断开连接 |
| clearEvents | function | 清空事件列表 |

## 支持的事件类型

| 事件类型 | 说明 | 数据结构 |
|----------|------|----------|
| agent_start | Agent 开始执行 | { agent, status } |
| constraint_result | 约束检索结果 | { constraints, summary } |
| plan | Planner 输出计划 | { tasks, delegated_agent } |
| approval_required | 需要用户审批 | { plan, agent, reason } |
| tool_call | 工具调用 | { tool, args } |
| code | 代码生成 | { file, content } |
| test_result | 测试结果 | { status, tests_total, tests_passed, errors } |
| review_result | 审查结果 | { status, violations } |
| memory_update | Memory 更新 | { layers, message } |
| done | 任务完成 | { session_id, summary } |
| error | 错误 | { message } |

## 自动重连机制

SSE 连接支持自动重连，采用指数退避策略：

- 最大重试次数：默认 3 次
- 重试间隔：1s, 2s, 4s（最大 10s）
- 完成后不再重连

```typescript
// 重连逻辑示例
const delay = Math.min(1000 * 2 ** (retryCount - 1), 10000);
setTimeout(() => connect(), delay);
```

## 事件类型守卫

使用类型守卫函数安全地处理不同类型的事件：

```typescript
import { isAgentStart, isCode, isDone } from "../utils/eventGuards";

function handleEvent(event: SSEEvent) {
  if (isAgentStart(event)) {
    console.log("Agent 启动:", event.data.agent);
  } else if (isCode(event)) {
    console.log("代码生成:", event.data.file);
  } else if (isDone(event)) {
    console.log("任务完成:", event.data.summary);
  }
}
```

## 注意事项

- SSE 连接使用 GET 请求，参数通过 URL 查询字符串传递
- 连接断开后会自动重连，超过最大重试次数后报错
- 完成事件（done）会自动关闭连接
- 事件数据使用 JSON 格式传输

## 相关文件

- `frontend/src/hooks/useSSE.ts` — SSE Hook 实现
- `frontend/src/utils/eventGuards.ts` — 事件类型守卫
- `frontend/src/types/api.ts` — 事件类型定义

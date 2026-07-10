# 流式聊天接口文档

> 模块：backend/api/chat.py  
> 负责人：成员D（后端-A）  
> 最后更新：2026-07-10

---

## 一、接口概述

流式聊天接口是 BandCode 的核心接口，通过 Server-Sent Events (SSE) 实现实时流式响应。

| 项目 | 说明 |
|------|------|
| 接口路径 | `GET /api/chat/stream` |
| 协议 | SSE (Server-Sent Events) |
| 认证方式 | 暂无（后续添加） |

---

## 二、请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话 ID |
| project | string | 是 | 项目名称 |
| message | string | 是 | 用户消息 |

**请求示例：**
```
GET /api/chat/stream?session_id=123&project=bandcode&message=你好
```

---

## 三、响应格式

### SSE 事件格式

```
event: <事件类型>
data: <JSON 数据>

```

### 事件类型

| 事件类型 | 说明 | 数据结构 |
|----------|------|----------|
| agent_start | Agent 开始执行 | `{agent: string, status: string}` |
| constraint_result | 约束检索结果 | `{constraints: string[], summary: string}` |
| plan | Planner 输出计划 | `{tasks: string[], delegated_agent: string}` |
| approval_required | 需要审批 | `{plan: string, agent: string, reason: string}` |
| tool_call | Tool 调用 | `{tool: string, args: object}` |
| code | 代码生成 | `{file: string, content: string}` |
| test_result | 测试结果 | `{status: string, tests_total: number, tests_passed: number}` |
| review_result | 审查结果 | `{status: string, violations: array}` |
| memory_update | Memory 更新 | `{layers: string[], message: string}` |
| done | 完成 | `{session_id: string, summary: string}` |
| error | 错误 | `{message: string}` |

---

## 四、处理流程

```
用户发送消息
    ↓
Constraint Agent 检索约束
    ↓
Planner Agent 生成计划
    ↓
ComplexCoder Agent 生成代码
    ↓
Tester Agent 运行测试
    ↓
Review Agent 审查代码
    ↓
更新 Memory
    ↓
返回完成事件
```

---

## 五、代码示例

### 前端 JavaScript

```javascript
const eventSource = new EventSource('/api/chat/stream?session_id=123&project=bandcode&message=你好');

eventSource.addEventListener('agent_start', (e) => {
  const data = JSON.parse(e.data);
  console.log(`Agent ${data.agent} 开始执行`);
});

eventSource.addEventListener('code', (e) => {
  const data = JSON.parse(e.data);
  console.log(`生成代码到 ${data.file}`);
});

eventSource.addEventListener('done', (e) => {
  const data = JSON.parse(e.data);
  console.log(`任务完成: ${data.summary}`);
  eventSource.close();
});
```

---

## 六、相关文件

- `backend/api/chat.py` - 接口实现
- `backend/api/sse.py` - SSE 事件封装
- `frontend/src/hooks/useSSE.ts` - 前端 SSE Hook

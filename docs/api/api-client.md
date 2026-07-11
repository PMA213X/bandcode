# API 客户端

## 概述

API 客户端封装了所有与后端的 HTTP 通信，基于 Axios 实现，提供统一的接口调用方法。支持请求/响应拦截、错误处理、超时控制。

## 基本信息

- **基础 URL**: `http://localhost:8000`
- **超时时间**: 30 秒
- **请求格式**: JSON

## 接口列表

### 用户管理

#### 创建用户

- **路径**: `POST /api/users/create`
- **说明**: 创建新用户并返回用户信息

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| preferences | object | 否 | 用户偏好设置 |

**响应**:

```json
{
  "code": 200,
  "data": {
    "id": "user-123",
    "username": "testuser",
    "createdAt": "2026-07-10T00:00:00Z"
  },
  "message": "成功"
}
```

### 聊天管理

#### 获取聊天历史

- **路径**: `GET /api/chat/history`
- **说明**: 获取指定会话的聊天历史记录

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话 ID |
| limit | number | 否 | 返回数量限制 |
| offset | number | 否 | 偏移量 |

**响应**:

```json
{
  "code": 200,
  "data": {
    "messages": [
      {
        "id": "msg-1",
        "role": "user",
        "content": "你好",
        "timestamp": "2026-07-10T00:00:00Z"
      }
    ],
    "total": 10
  },
  "message": "成功"
}
```

### 设置管理

#### 获取设置

- **路径**: `GET /api/settings`
- **说明**: 获取全部设置项

**响应**:

```json
{
  "code": 200,
  "data": {
    "模型设置": { "model": "gpt-4", "temperature": 0.7 },
    "Agent 设置": { "maxAgents": 6 },
    "Memory 设置": { "layers": ["global", "project", "task"] },
    "Workflow 设置": { "timeout": 300 },
    "RAG 设置": { "enabled": true },
    "Tool 设置": { "allowedTools": ["read_file", "write_file"] }
  },
  "message": "成功"
}
```

#### 更新设置

- **路径**: `POST /api/settings`
- **说明**: 更新单个设置项

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| section | string | 是 | 设置分类 |
| key | string | 是 | 设置键名 |
| value | any | 是 | 新的设置值 |

**响应**:

```json
{
  "code": 200,
  "data": {
    "previous": "gpt-4",
    "current": "gpt-4-turbo"
  },
  "message": "成功"
}
```

#### 重新加载设置

- **路径**: `POST /api/settings/reload`
- **说明**: 重新加载设置文件

### Memory 管理

#### 获取 Memory

- **路径**: `GET /api/memory`
- **说明**: 获取指定层级的 Memory 内容

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project | string | 是 | 项目名称 |
| layer | string | 是 | Memory 层级 |

**支持的层级**: global, project, task, session, checkpoint, notes

**响应**:

```json
{
  "code": 200,
  "data": {
    "content": "Memory 内容...",
    "updatedAt": "2026-07-10T00:00:00Z"
  },
  "message": "成功"
}
```

#### 搜索 Memory

- **路径**: `GET /api/memory/search`
- **说明**: 搜索 Memory 内容

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 搜索关键词 |
| limit | number | 否 | 返回数量限制 |

**响应**:

```json
{
  "code": 200,
  "data": [
    {
      "layer": "project",
      "content": "匹配的内容片段",
      "score": 0.95
    }
  ],
  "message": "成功"
}
```

### 工具管理

#### 获取工具列表

- **路径**: `GET /api/tools/list`
- **说明**: 获取所有可用工具

**响应**:

```json
{
  "code": 200,
  "data": [
    {
      "name": "read_file",
      "description": "读取文件内容",
      "parameters": {
        "path": { "type": "string", "required": true }
      }
    }
  ],
  "message": "成功"
}
```

#### 调用工具

- **路径**: `POST /api/tools/call`
- **说明**: 调用后端工具

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| tool | string | 是 | 工具名称 |
| args | object | 是 | 工具参数 |

**响应**:

```json
{
  "code": 200,
  "data": {
    "result": "文件内容..."
  },
  "message": "成功"
}
```

### 项目管理

#### 初始化项目

- **路径**: `POST /api/project/init`
- **说明**: 初始化新项目

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_name | string | 是 | 项目名称 |
| path | string | 是 | 项目路径 |
| language | string | 否 | 编程语言 |
| framework | string | 否 | 框架 |

**响应**:

```json
{
  "code": 200,
  "data": {
    "projectDir": ".mimo",
    "structure": {
      "agents": [],
      "tools": [],
      "memory": {}
    }
  },
  "message": "成功"
}
```

#### 获取项目状态

- **路径**: `GET /api/project/status`
- **说明**: 获取项目当前状态

**响应**:

```json
{
  "code": 200,
  "data": {
    "name": "my-project",
    "version": "1.0.0",
    "agents": ["constraint", "planner", "coder"],
    "memoryLayers": ["global", "project"],
    "tools": ["read_file", "write_file"]
  },
  "message": "成功"
}
```

## 错误处理

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

错误响应格式:

```json
{
  "code": 400,
  "data": null,
  "message": "参数错误: username 不能为空"
}
```

## 使用示例

```typescript
import { api } from "../services/api";

// 创建用户
const user = await api.createUser("testuser");

// 获取聊天历史
const history = await api.getChatHistory("session-123", 50);

// 更新设置
await api.updateSettings("模型设置", "model", "gpt-4-turbo");

// 获取 Memory
const memory = await api.getMemory("my-project", "project");

// 调用工具
const result = await api.callTool("read_file", { path: "README.md" });
```

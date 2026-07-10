# API 客户端

## 概述

API 客户端模块封装了与后端的所有 HTTP 通信，提供统一的接口调用方法。基于 Axios 实现，支持请求拦截、响应拦截、错误处理等特性。

## 使用方式

### 基本使用

```typescript
import { api } from "../services/api";

// 创建用户
const user = await api.createUser("developer_01", { language: "zh-CN" });

// 获取聊天历史
const history = await api.getChatHistory("session-123", 50, 0);

// 获取设置
const settings = await api.getSettings();

// 更新设置
await api.updateSettings("模型设置", "默认模型", "xiaomi/mimo-v2.5-pro");

// 获取 Memory
const memory = await api.getMemory("my-project", "project");

// 调用工具
const result = await api.callTool("read_file", { path: "src/main.py" });

// 初始化项目
await api.initProject("my-project", "/path/to/project", "python", "fastapi");

// 获取项目状态
const status = await api.getProjectStatus();

// 获取工具列表
const tools = await api.listTools();

// 搜索 Memory
const searchResults = await api.searchMemory("用户认证", 10);

// 重新加载设置
await api.reloadSettings();
```

## 接口列表

### 用户相关

| 方法 | 路径 | 说明 |
|------|------|------|
| createUser | POST /api/users/create | 创建用户 |

### 聊天相关

| 方法 | 路径 | 说明 |
|------|------|------|
| getChatHistory | GET /api/chat/history | 获取聊天历史 |

### 设置相关

| 方法 | 路径 | 说明 |
|------|------|------|
| getSettings | GET /api/settings | 获取全部设置 |
| updateSettings | POST /api/settings | 更新设置 |
| reloadSettings | POST /api/settings/reload | 重新加载设置 |

### Memory 相关

| 方法 | 路径 | 说明 |
|------|------|------|
| getMemory | GET /api/memory | 获取 Memory 内容 |
| searchMemory | GET /api/memory/search | 搜索 Memory |

### 项目相关

| 方法 | 路径 | 说明 |
|------|------|------|
| initProject | POST /api/project/init | 初始化项目 |
| getProjectStatus | GET /api/project/status | 获取项目状态 |

### 工具相关

| 方法 | 路径 | 说明 |
|------|------|------|
| callTool | POST /api/tools/call | 调用工具 |
| listTools | GET /api/tools/list | 获取工具列表 |

## 统一响应格式

所有接口返回统一的响应格式：

```typescript
interface ApiResponse<T> {
  code: number;    // 状态码：0 表示成功
  data: T;         // 响应数据
  message: string; // 响应消息
}
```

## 错误处理

API 客户端使用自定义的 `ApiError` 类处理错误：

```typescript
import { ApiError } from "../services/errors";

try {
  await api.createUser("existing_user");
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API 错误: ${error.message}`);
    console.error(`状态码: ${error.code}`);
    console.error(`端点: ${error.endpoint}`);
  }
}
```

### 错误类型

| 错误类 | 说明 |
|--------|------|
| ApiError | API 调用错误，包含状态码和端点信息 |
| SSEConnectionError | SSE 连接错误，包含会话 ID |

## 配置项

| 配置 | 默认值 | 说明 |
|------|--------|------|
| baseURL | http://localhost:8000 | 后端 API 基础 URL |
| timeout | 30000 | 请求超时时间（毫秒） |
| headers | Content-Type: application/json | 默认请求头 |

## 拦截器

### 请求拦截器

在每个请求发送前执行，可用于添加认证 token：

```typescript
this.client.interceptors.request.use((config) => {
  // 添加 token
  config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

### 响应拦截器

处理响应错误，统一包装为 `ApiError`：

```typescript
this.client.interceptors.response.use(
  (response) => response,
  (error) => {
    const endpoint = error.config?.url || "unknown";
    const code = error.response?.status || 0;
    const message = error.response?.data?.message || error.message;
    return Promise.reject(new ApiError(message, code, endpoint));
  }
);
```

## 注意事项

- 所有接口返回 Promise，支持 async/await
- 错误会自动包装为 ApiError，便于统一处理
- 超时时间默认 30 秒，可根据需要调整
- 请求头默认使用 JSON 格式

## 相关文件

- `frontend/src/services/api.ts` — API 客户端实现
- `frontend/src/services/errors.ts` — 错误类定义
- `frontend/src/types/api.ts` — 类型定义

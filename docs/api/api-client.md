# API 客户端

## 概述

API 客户端封装了与后端的所有 HTTP 通信，提供统一的接口调用方法。基于 Axios 库实现，支持请求拦截、响应拦截、错误处理等功能。

## 使用方式

### 基本用法

```tsx
import { api } from "../services/api";

// 创建用户
const response = await api.createUser("user1", { theme: "dark" });
console.log(response.data);

// 获取聊天历史
const history = await api.getChatHistory("session-123", 10, 0);
console.log(history.data);
```

### 错误处理

```tsx
import { api } from "../services/api";
import { ApiError } from "../services/errors";

try {
  await api.createUser("user1");
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`API 错误: ${error.message}, 状态码: ${error.code}`);
  }
}
```

## API 方法列表

### 用户管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| createUser | 创建新用户 | username: string, preferences?: object | ApiResponse\<CreateUserResponse\> |

### 聊天功能

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| getChatHistory | 获取聊天历史 | sessionId: string, limit?: number, offset?: number | ApiResponse\<ChatHistoryResponse\> |

### 设置管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| getSettings | 获取全部设置 | - | ApiResponse\<SettingsResponse\> |
| updateSettings | 更新单个设置 | section: string, key: string, value: any | ApiResponse\<UpdateSettingsResponse\> |
| reloadSettings | 重新加载设置文件 | - | ApiResponse\<null\> |

### Memory 管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| getMemory | 获取指定层级的 Memory | project: string, layer: string | ApiResponse\<MemoryResponse\> |
| searchMemory | 搜索 Memory 内容 | query: string, limit?: number | ApiResponse\<Array\<Record\<string, any\>\>\> |

### 工具管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| callTool | 调用后端工具 | tool: string, args: Record\<string, any\> | ApiResponse\<ToolCallResponse\> |
| listTools | 获取所有可用工具 | - | ApiResponse\<Array\<Record\<string, any\>\>\> |

### 项目管理

| 方法 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| initProject | 初始化项目 | projectName: string, path: string, language?: string, framework?: string | ApiResponse\<ProjectInitResponse\> |
| getProjectStatus | 获取项目状态 | - | ApiResponse\<Record\<string, any\>\> |

## 配置项

### Axios 实例配置

| 配置 | 默认值 | 说明 |
|------|--------|------|
| baseURL | http://localhost:8000 | 后端 API 基础 URL |
| timeout | 30000 | 请求超时时间（毫秒） |
| Content-Type | application/json | 请求头内容类型 |

### 自定义配置

```tsx
import { ApiClient } from "../services/api";

// 创建自定义配置的客户端
const customApi = new ApiClient("https://api.example.com");
```

## 错误处理

### ApiError 类

```tsx
class ApiError extends Error {
  code: number;      // HTTP 状态码
  endpoint: string;  // 请求的端点路径
}
```

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权 | 检查认证信息 |
| 403 | 禁止访问 | 检查权限配置 |
| 404 | 资源不存在 | 检查请求路径 |
| 500 | 服务器错误 | 联系后端开发人员 |

## 拦截器

### 请求拦截器

```tsx
// 在请求发送前执行，可用于添加 token
this.client.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 响应拦截器

```tsx
// 处理响应错误
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

## 示例

### 获取设置并更新

```tsx
// 获取当前设置
const settings = await api.getSettings();
console.log(settings.data);

// 更新模型设置
await api.updateSettings("模型设置", "temperature", 0.7);
```

### 搜索 Memory

```tsx
// 搜索包含 "认证" 的 Memory
const results = await api.searchMemory("认证", 5);
results.data.forEach(result => {
  console.log(result.content, result.score);
});
```

### 调用工具

```tsx
// 调用 read_file 工具
const result = await api.callTool("read_file", {
  path: "/path/to/file.ts"
});
console.log(result.data);
```

## 注意事项

- 所有 API 调用都是异步的，需要使用 async/await 或 .then() 处理
- 错误会自动包装为 ApiError，包含状态码和端点信息
- 请求超时默认 30 秒，可根据需要调整
- 生产环境建议使用环境变量配置 baseURL

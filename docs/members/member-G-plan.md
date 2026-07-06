# 成员G — 前端开发工程师B（数据对接方向）开发规划

> 角色：前端开发工程师
> 核心职责：API 对接、SSE 消费、数据驱动组件
> 分支：feature/frontend-data

---

## 一、角色定位

成员G 负责前端的「数据层」：

- Axios HTTP 客户端封装
- SSE (Server-Sent Events) 连接管理和事件解析
- Agent 状态实时显示组件
- Memory 浏览组件
- 审批交互弹窗组件
- TypeScript 类型定义

---

## 二、开发任务清单

### Phase 0：环境准备（第1天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| G-01 | 克隆仓库 | — | git clone + 切换到 feature/frontend-data 分支 |
| G-02 | 安装依赖 | — | axios、eventsource |
| G-03 | 阅读API文档 | — | 熟悉8个接口定义 |

### Phase 1：基础数据层（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| G-04 | Axios封装 | `frontend/src/services/api.ts` | HTTP请求封装、拦截器、错误处理 |
| G-05 | API类型定义 | `frontend/src/types/api.ts` | 请求/响应类型定义 |
| G-06 | 类型定义入口 | `frontend/src/types/index.ts` | 类型导出 |
| G-07 | API测试 | — | 测试API调用 |

### Phase 2：SSE与数据组件（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| G-08 | SSE Hook | `frontend/src/hooks/useSSE.ts` | SSE连接管理、事件解析、状态更新 |
| G-09 | Agent状态组件 | `frontend/src/components/AgentStatus.tsx` | 实时显示当前运行的Agent |
| G-10 | Memory浏览组件 | `frontend/src/components/MemoryView.tsx` | 各层Memory内容展示 |
| G-11 | 审批弹窗组件 | `frontend/src/components/ApprovalDialog.tsx` | 审批确认弹窗 |
| G-12 | SSE测试 | — | 测试SSE连接和事件解析 |

### Phase 3：集成与完善（第9-11天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| G-13 | 数据层集成测试 | — | 测试完整数据流 |
| G-14 | 错误处理完善 | — | 网络错误、超时、断线重连 |
| G-15 | 状态管理优化 | — | 减少不必要的状态更新 |

### Phase 4-5：联调与优化（第12-16天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| G-16 | 前后端联调 | — | 配合成员D调试所有接口 |
| G-17 | SSE稳定性测试 | — | 长时间连接测试 |
| G-18 | 性能优化 | — | 减少内存泄漏、优化更新频率 |

---

## 三、技术要点

### 3.1 Axios封装

```typescript
// frontend/src/services/api.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';

interface ApiResponse<T> {
    code: number;
    data: T;
    message: string;
}

class ApiClient {
    private client: AxiosInstance;

    constructor(baseURL: string = 'http://localhost:8000') {
        this.client = axios.create({
            baseURL,
            timeout: 30000,
            headers: { 'Content-Type': 'application/json' }
        });

        // 请求拦截器
        this.client.interceptors.request.use(config => {
            // 可添加token等
            return config;
        });

        // 响应拦截器
        this.client.interceptors.response.use(
            response => response,
            error => {
                console.error('API Error:', error.message);
                return Promise.reject(error);
            }
        );
    }

    // 用户相关
    async createUser(username: string, preferences?: object) {
        return this.post('/api/users/create', { username, preferences });
    }

    // 聊天相关
    async getChatHistory(sessionId: string, limit?: number, offset?: number) {
        return this.get('/api/chat/history', { session_id: sessionId, limit, offset });
    }

    // 设置相关
    async getSettings() {
        return this.get('/api/settings');
    }

    async updateSettings(section: string, key: string, value: any) {
        return this.post('/api/settings', { section, key, value });
    }

    // Memory相关
    async getMemory(project: string, layer: string) {
        return this.get('/api/memory', { project, layer });
    }

    // 工具相关
    async callTool(tool: string, args: object) {
        return this.post('/api/tools/call', { tool, args });
    }

    // 项目相关
    async initProject(projectName: string, path: string, language?: string, framework?: string) {
        return this.post('/api/project/init', { project_name: projectName, path, language, framework });
    }

    private async get<T>(url: string, params?: object): Promise<ApiResponse<T>> {
        const response = await this.client.get(url, { params });
        return response.data;
    }

    private async post<T>(url: string, data?: object): Promise<ApiResponse<T>> {
        const response = await this.client.post(url, data);
        return response.data;
    }
}

export const api = new ApiClient();
```

### 3.2 SSE Hook

```typescript
// frontend/src/hooks/useSSE.ts
import { useState, useEffect, useCallback, useRef } from 'react';

interface SSEEvent {
    type: string;
    data: any;
}

interface UseSSEOptions {
    sessionId: string;
    project: string;
    message: string;
    onEvent?: (event: SSEEvent) => void;
    onComplete?: () => void;
    onError?: (error: Error) => void;
}

export function useSSE(options: UseSSEOptions) {
    const [events, setEvents] = useState<SSEEvent[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    const connect = useCallback(() => {
        // 创建SSE连接
        const eventSource = new EventSource(
            `/api/chat/stream?session_id=${options.session_id}&project=${options.project}&message=${encodeURIComponent(options.message)}`
        );

        eventSource.onopen = () => {
            setIsConnected(true);
            setError(null);
        };

        // 监听所有事件类型
        const eventTypes = [
            'agent_start', 'constraint_result', 'plan',
            'approval_required', 'tool_call', 'code',
            'test_result', 'review_result', 'memory_update',
            'done', 'error'
        ];

        eventTypes.forEach(type => {
            eventSource.addEventListener(type, (e) => {
                const event: SSEEvent = {
                    type,
                    data: JSON.parse(e.data)
                };
                setEvents(prev => [...prev, event]);
                options.onEvent?.(event);
            });
        });

        eventSource.onerror = (e) => {
            setError(new Error('SSE connection error'));
            setIsConnected(false);
            options.onError?.(new Error('SSE connection error'));
        };

        eventSourceRef.current = eventSource;

        return () => {
            eventSource.close();
            setIsConnected(false);
        };
    }, [options.session_id, options.project, options.message]);

    useEffect(() => {
        const cleanup = connect();
        return cleanup;
    }, [connect]);

    const disconnect = useCallback(() => {
        eventSourceRef.current?.close();
        setIsConnected(false);
    }, []);

    return { events, isConnected, error, disconnect };
}
```

### 3.3 SSE事件类型定义

```typescript
// frontend/src/types/api.ts

// SSE事件类型
export type SSEEventType =
    | 'agent_start'
    | 'constraint_result'
    | 'plan'
    | 'approval_required'
    | 'approval_response'
    | 'tool_call'
    | 'code'
    | 'test_result'
    | 'review_result'
    | 'memory_update'
    | 'done'
    | 'error';

// SSE事件数据
export interface AgentStartEvent {
    agent: string;
    status: string;
}

export interface ConstraintResultEvent {
    constraints: string[];
    summary: string;
}

export interface PlanEvent {
    tasks: string[];
    delegated_agent: string;
}

export interface ApprovalRequiredEvent {
    plan: string;
    agent: string;
    reason: string;
}

export interface ToolCallEvent {
    tool: string;
    args: Record<string, any>;
}

export interface CodeEvent {
    file: string;
    content: string;
}

export interface TestResultEvent {
    status: 'passed' | 'failed';
    tests_total: number;
    tests_passed: number;
    errors?: Array<{
        file: string;
        line: number;
        error: string;
        suggestion: string;
    }>;
}

export interface ReviewResultEvent {
    status: 'passed' | 'failed';
    violations: Array<{
        constraint: string;
        severity: string;
        detail: string;
    }>;
}

export interface MemoryUpdateEvent {
    layers: string[];
    message: string;
}

export interface DoneEvent {
    session_id: string;
    summary: string;
}

export interface ErrorEvent {
    message: string;
}
```

### 3.4 Agent状态组件

```typescript
// frontend/src/components/AgentStatus.tsx
import React from 'react';
import { Box, Text } from 'ink';

interface AgentStatusProps {
    agent: string;
    status: string;
    isActive: boolean;
}

const AGENT_COLORS: Record<string, string> = {
    'constraint': 'gray',
    'planner': 'blue',
    'simple-coder': 'green',
    'complex-coder': 'magenta',
    'tester': 'yellow',
    'review': 'red'
};

const AgentStatus: React.FC<AgentStatusProps> = ({ agent, status, isActive }) => {
    const color = AGENT_COLORS[agent] || 'white';
    const icon = isActive ? '🔄' : '✅';

    return (
        <Box>
            <Text color={color}>
                {icon} [{agent}] {status}
            </Text>
        </Box>
    );
};

export default AgentStatus;
```

### 3.5 Memory浏览组件

```typescript
// frontend/src/components/MemoryView.tsx
import React, { useState, useEffect } from 'react';
import { Box, Text } from 'ink';
import { api } from '../services/api';

interface MemoryViewProps {
    project: string;
    layer: string;
}

const MemoryView: React.FC<MemoryViewProps> = ({ project, layer }) => {
    const [content, setContent] = useState<string>('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadMemory = async () => {
            try {
                const response = await api.getMemory(project, layer);
                setContent(response.data.content);
            } catch (error) {
                setContent('加载失败');
            } finally {
                setLoading(false);
            }
        };
        loadMemory();
    }, [project, layer]);

    if (loading) {
        return <Text color="gray">加载中...</Text>;
    }

    return (
        <Box flexDirection="column" borderStyle="single" padding={1}>
            <Text color="cyan" bold>[{layer} Memory]</Text>
            <Text>{content}</Text>
        </Box>
    );
};

export default MemoryView;
```

### 3.6 审批弹窗组件

```typescript
// frontend/src/components/ApprovalDialog.tsx
import React from 'react';
import { Box, Text, useInput } from 'ink';

interface ApprovalDialogProps {
    plan: string;
    agent: string;
    reason: string;
    onApprove: () => void;
    onReject: () => void;
}

const ApprovalDialog: React.FC<ApprovalDialogProps> = ({
    plan, agent, reason, onApprove, onReject
}) => {
    useInput((input, key) => {
        if (input === 'y' || input === 'Y') {
            onApprove();
        } else if (input === 'n' || input === 'N') {
            onReject();
        }
    });

    return (
        <Box flexDirection="column" borderStyle="double" padding={1}>
            <Text color="yellow" bold>[审批] 需要确认</Text>
            <Text>即将委派 {agent} 执行任务</Text>
            <Text color="gray">原因: {reason}</Text>
            <Text color="gray">计划: {plan}</Text>
            <Box marginTop={1}>
                <Text color="green">[Y] 确认 </Text>
                <Text color="red">[N] 取消</Text>
            </Box>
        </Box>
    );
};

export default ApprovalDialog;
```

---

## 四、AI Agent 使用指南

### 4.1 推荐配置

| 任务类型 | Agent | 模型 | 理由 |
|---------|-------|------|------|
| Axios封装 | general | mimo-v2.5 | HTTP封装 |
| SSE Hook实现 | general | mimo-v2.5 | SSE处理逻辑 |
| AgentStatus组件 | general | mimo-v2.5 | 状态展示组件 |
| MemoryView组件 | general | mimo-v2.5 | 数据展示组件 |
| ApprovalDialog组件 | general | mimo-v2.5 | 弹窗组件 |
| 类型定义 | general | mimo-v2.5 | TypeScript类型 |
| 代码探索 | explore | mimo-v2.5 | 查找SSE示例 |

### 4.2 使用示例

**实现Axios封装时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：实现 frontend/src/services/api.ts，封装Axios HTTP客户端。
要求：
1. 封装8个API接口
2. 添加请求/响应拦截器
3. 统一错误处理
4. 返回统一格式 {code, data, message}
参考文件：doc1.md 第4节API接口规范
```

**实现SSE Hook时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：实现 frontend/src/hooks/useSSE.ts，SSE连接管理Hook。
要求：
1. 管理SSE连接生命周期
2. 解析所有SSE事件类型
3. 维护事件状态列表
4. 处理连接错误和断开
参考文件：doc1.md 第4.2节接口2的SSE响应格式
```

**实现AgentStatus组件时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：实现 frontend/src/components/AgentStatus.tsx，Agent状态显示组件。
要求：
1. 显示当前运行的Agent名称
2. 显示Agent状态信息
3. 不同Agent使用不同颜色
4. 活动状态显示加载图标
参考文件：doc1.md 第2.2节界面布局
```

---

## 五、文件所有权

### 5.1 主责文件

```
frontend/src/services/api.ts            ← 主责
frontend/src/hooks/useSSE.ts            ← 主责
frontend/src/types/api.ts               ← 主责
frontend/src/types/index.ts             ← 主责
frontend/src/components/AgentStatus.tsx  ← 主责
frontend/src/components/MemoryView.tsx   ← 主责
frontend/src/components/ApprovalDialog.tsx ← 主责
```

### 5.2 协作文件

| 文件 | 协作人 | 协作内容 |
|------|--------|---------|
| components/Chat.tsx | 成员F | 使用SSE数据 |
| components/Layout.tsx | 成员F | 布局基础 |
| styles/colors.ts | 成员F | 色彩方案 |

---

## 六、接口依赖

### 6.1 我依赖的接口

| 依赖方 | 依赖内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员D | API接口定义 | Phase 1 | 8个接口的请求/响应格式 |
| 成员D | SSE事件格式 | Phase 1 | SSE事件类型和数据结构 |
| 成员F | 组件基础 | Phase 1 | Layout、样式系统 |

### 6.2 我提供的接口

| 接收方 | 提供内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员F | services/api.ts | Phase 1 | API调用封装 |
| 成员F | hooks/useSSE.ts | Phase 2 | SSE数据流 |
| 成员F | 类型定义 | Phase 1 | TypeScript类型 |

---

## 七、交付物清单

| 阶段 | 交付物 | 验收标准 |
|------|--------|---------|
| Phase 0 | 环境就绪 | 依赖安装完成 |
| Phase 1 | Axios封装、类型定义 | API可正常调用 |
| Phase 2 | SSE Hook、AgentStatus、MemoryView、ApprovalDialog | 组件可正常渲染 |
| Phase 3 | 集成测试通过 | 数据流正常 |
| Phase 4 | 联调通过 | 前后端完整交互 |
| Phase 5 | 性能优化完成 | SSE连接稳定 |

---

## 八、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| SSE兼容性差 | 流式输出异常 | 准备长轮询备选方案 |
| 网络不稳定 | 数据丢失 | 增加断线重连机制 |
| 事件解析错误 | 状态异常 | 增加格式校验 |
| 内存泄漏 | 性能下降 | 及时清理事件监听器 |

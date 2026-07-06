# 成员F — 前端开发工程师A（界面设计方向）开发规划

> 角色：前端开发工程师
> 核心职责：React Ink CLI 框架搭建、UI 组件实现、样式设计
> 分支：feature/frontend-ui

---

## 一、角色定位

成员F 负责前端的「界面与交互」：

- React Ink + TypeScript 项目框架搭建
- 聊天界面（Chat.tsx）：消息列表、输入框、打字机效果
- 设置面板（Settings.tsx）：全中文6大类39项设置
- 布局组件、样式系统、状态图标
- 终端色彩方案和排版设计

---

## 二、开发任务清单

### Phase 0：环境准备（第1天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| F-01 | 克隆仓库 | — | git clone + 切换到 feature/frontend-ui 分支 |
| F-02 | 初始化前端项目 | `frontend/` | npx create-ink-app |
| F-03 | 安装依赖 | `frontend/package.json` | ink、react、typescript |
| F-04 | 验证Ink环境 | — | 测试Ink基本渲染 |

### Phase 1：框架搭建（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| F-05 | 项目配置 | `frontend/tsconfig.json` | TypeScript配置 |
| F-06 | 入口文件 | `frontend/src/main.tsx` | 应用入口 |
| F-07 | App组件 | `frontend/src/App.tsx` | 根组件、路由管理 |
| F-08 | 布局组件 | `frontend/src/components/Layout.tsx` | 整体布局框架 |
| F-09 | 全局状态 | `frontend/src/store/index.ts` | Context/状态管理 |
| F-10 | 基础渲染测试 | — | 验证组件渲染正常 |

### Phase 2：核心UI组件（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| F-11 | 聊天界面 | `frontend/src/components/Chat.tsx` | 消息列表、输入框、打字机效果 |
| F-12 | 消息组件 | `frontend/src/components/Message.tsx` | 单条消息渲染 |
| F-13 | 输入框组件 | `frontend/src/components/Input.tsx` | 用户输入组件 |
| F-14 | 设置面板 | `frontend/src/components/Settings.tsx` | 全中文6大类39项设置 |
| F-15 | 设置项组件 | `frontend/src/components/SettingItem.tsx` | 单个设置项渲染 |

### Phase 2：样式系统（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| F-16 | 色彩方案 | `frontend/src/styles/colors.ts` | 终端色彩定义 |
| F-17 | 图标系统 | `frontend/src/styles/icons.ts` | 状态图标（✅❌🔄等） |
| F-18 | 布局样式 | `frontend/src/styles/layout.ts` | 间距、对齐、边框 |

### Phase 3：完善与优化（第9-11天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| F-19 | UI细节优化 | — | 边框、颜色、间距调整 |
| F-20 | 错误状态展示 | — | 错误信息美化 |
| F-21 | 加载状态展示 | — | Loading动画 |

### Phase 4-5：联调与优化（第12-16天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| F-22 | 前后端联调 | — | 配合成员G对接数据 |
| F-23 | UI响应优化 | — | 减少不必要的重渲染 |
| F-24 | 终端兼容性 | — | 测试不同终端的显示效果 |

---

## 三、技术要点

### 3.1 React Ink 基础

```tsx
// Ink 是 React 的终端渲染器
// 使用 JSX 语法，但渲染到终端而非浏览器
import React, { useState } from 'react';
import { render, Box, Text } from 'ink';

const App = () => {
    const [count, setCount] = useState(0);

    return (
        <Box flexDirection="column" padding={1}>
            <Text color="green">Count: {count}</Text>
            <Text color="gray">Press Enter to increment</Text>
        </Box>
    );
};

render(<App />);
```

### 3.2 Chat组件核心结构

```tsx
// frontend/src/components/Chat.tsx
import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

interface Message {
    role: 'user' | 'assistant';
    agent?: string;
    content: string;
}

const Chat: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');

    useInput((inputChar, key) => {
        if (key.return) {
            // 发送消息
            handleSend(input);
            setInput('');
        } else {
            setInput(prev => prev + inputChar);
        }
    });

    return (
        <Box flexDirection="column">
            {/* 消息列表 */}
            <Box flexDirection="column" flexGrow={1}>
                {messages.map((msg, i) => (
                    <Message key={i} {...msg} />
                ))}
            </Box>

            {/* 输入框 */}
            <Box borderStyle="single" paddingX={1}>
                <Text color="cyan">{'> '}</Text>
                <Text>{input}</Text>
                <Text color="gray">{'█'}</Text>
            </Box>
        </Box>
    );
};
```

### 3.3 Settings组件核心结构

```tsx
// frontend/src/components/Settings.tsx
import React, { useState } from 'react';
import { Box, Text } from 'ink';

const SETTINGS_CATEGORIES = [
    {
        name: '模型设置',
        items: ['默认模型', 'Base URL', 'API Key', 'Planner 模型', ...]
    },
    {
        name: 'Agent 设置',
        items: ['默认Agent', '审批模式', ...]
    },
    {
        name: 'Memory 设置',
        items: ['自动更新Memory', 'Memory压缩', ...]
    },
    {
        name: 'Workflow 设置',
        items: ['开启约束智能检索', '开启自动约束检查', '自动修正', ...]
    },
    {
        name: 'RAG 设置',
        items: ['知识库路径', '检索数量', ...]
    },
    {
        name: 'Tool 设置',
        items: ['工具目录', '权限配置', ...]
    }
];

const Settings: React.FC = () => {
    const [selectedCategory, setSelectedCategory] = useState(0);

    return (
        <Box flexDirection="column">
            {SETTINGS_CATEGORIES.map((cat, i) => (
                <Box key={i}>
                    <Text color={i === selectedCategory ? 'green' : 'white'}>
                        {i === selectedCategory ? '▶ ' : '  '}
                        {cat.name}
                    </Text>
                </Box>
            ))}
        </Box>
    );
};
```

### 3.4 色彩方案

```tsx
// frontend/src/styles/colors.ts
export const COLORS = {
    // 状态颜色
    success: 'green',
    error: 'red',
    warning: 'yellow',
    info: 'cyan',

    // Agent颜色
    planner: 'blue',
    simpleCoder: 'green',
    complexCoder: 'magenta',
    tester: 'yellow',
    constraint: 'gray',
    review: 'red',

    // UI颜色
    primary: 'cyan',
    secondary: 'gray',
    border: 'white',
    text: 'white',
    muted: 'gray',
};
```

### 3.5 状态图标

```tsx
// frontend/src/styles/icons.ts
export const ICONS = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    loading: '🔄',
    pending: '⏳',
    arrow: '▶',
    bullet: '•',
    separator: '─',
};
```

---

## 四、AI Agent 使用指南

### 4.1 推荐配置

| 任务类型 | Agent | 模型 | 理由 |
|---------|-------|------|------|
| Ink项目搭建 | general | mimo-v2.5 | 项目初始化 |
| Chat组件实现 | general | mimo-v2.5 | UI组件开发 |
| Settings组件实现 | general | mimo-v2.5 | 表单组件 |
| 样式系统 | general | mimo-v2.5 | 样式代码 |
| 代码探索 | explore | mimo-v2.5 | 查找Ink示例 |

### 4.2 使用示例

**搭建Ink项目时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：初始化 React Ink + TypeScript 项目。
要求：
1. 使用 create-ink-app 或手动配置
2. 配置 TypeScript
3. 安装必要依赖：ink、react、ink-text-input
4. 创建基础目录结构
```

**实现Chat组件时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：实现 frontend/src/components/Chat.tsx，聊天界面组件。
要求：
1. 消息列表展示（支持滚动）
2. 用户输入框
3. 打字机效果展示AI回复
4. 不同Agent的消息用不同颜色
5. 支持SSE流式消息
参考文件：doc1.md 第2.2节界面布局
```

**实现Settings组件时：**

```
子代理：general
模型：xiaomi/mimo-v2.5
任务：实现 frontend/src/components/Settings.tsx，设置面板组件。
要求：
1. 6大类设置：模型/Agent/Memory/Workflow/RAG/Tool
2. 全中文显示
3. 支持键盘导航
4. 支持修改和保存
参考文件：doc1.md 第4.2节接口5的设置结构
```

---

## 五、文件所有权

### 5.1 主责文件

```
frontend/package.json               ← 主责
frontend/tsconfig.json               ← 主责
frontend/src/main.tsx                ← 主责
frontend/src/App.tsx                 ← 主责
frontend/src/components/Layout.tsx   ← 主责
frontend/src/components/Chat.tsx     ← 主责
frontend/src/components/Message.tsx  ← 主责
frontend/src/components/Input.tsx    ← 主责
frontend/src/components/Settings.tsx ← 主责
frontend/src/components/SettingItem.tsx ← 主责
frontend/src/store/index.ts          ← 主责
frontend/src/styles/colors.ts        ← 主责
frontend/src/styles/icons.ts         ← 主责
frontend/src/styles/layout.ts        ← 主责
```

### 5.2 协作文件

| 文件 | 协作人 | 协作内容 |
|------|--------|---------|
| services/api.ts | 成员G | API调用封装 |
| hooks/useSSE.ts | 成员G | SSE数据流 |
| components/AgentStatus.tsx | 成员G | Agent状态组件 |
| components/MemoryView.tsx | 成员G | Memory浏览组件 |
| components/ApprovalDialog.tsx | 成员G | 审批弹窗组件 |

---

## 六、接口依赖

### 6.1 我依赖的接口

| 依赖方 | 依赖内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员G | services/api.ts | Phase 2 | API调用封装 |
| 成员G | hooks/useSSE.ts | Phase 2 | SSE数据流 |
| 成员D | API接口定义 | Phase 1 | 接口格式 |
| 成员D | SSE事件格式 | Phase 1 | SSE事件类型 |

### 6.2 我提供的接口

| 接收方 | 提供内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员G | 组件基础 | Phase 1 | Layout、样式系统 |
| 成员G | 类型定义 | Phase 1 | TypeScript类型 |

---

## 七、交付物清单

| 阶段 | 交付物 | 验收标准 |
|------|--------|---------|
| Phase 0 | 前端项目骨架 | Ink可正常渲染 |
| Phase 1 | 框架、布局、基础组件 | 组件可正常渲染 |
| Phase 2 | Chat、Settings、样式系统 | UI完整可用 |
| Phase 3 | UI优化完成 | 视觉效果良好 |
| Phase 4 | 联调通过 | 前后端完整交互 |
| Phase 5 | 性能优化完成 | 渲染流畅 |

---

## 八、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| Ink文档不足 | 开发困难 | 参考Ink官方示例和GitHub |
| 终端渲染限制 | UI效果差 | 简化设计，使用颜色区分 |
| 组件重渲染 | 性能问题 | 使用React.memo优化 |
| 不同终端兼容性 | 显示异常 | 测试主流终端 |

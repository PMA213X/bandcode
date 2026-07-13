# 成员F 答辩提示

## 你的角色
前端开发工程师 A

## 答辩要点

### 1. 界面设计（2分钟）
- 整体布局：左侧 Sidebar 导航 + 主内容区 + 命令面板
- 暗色主题设计，开发者友好的 CLI 工具界面风格
- 响应式布局，适配不同屏幕尺寸

### 2. 技术实现（2分钟）
- React 18 + TypeScript + Tailwind CSS + Vite 技术栈
- 组件化设计：App、Chat、Sidebar、CommandPalette、Settings 等核心组件
- SSE 客户端：使用 EventSource API 接收后端 12 种事件类型

### 3. 用户体验（2分钟）
- 流式输出实时显示 AI 回复
- 命令面板（Command Palette）快速导航
- Settings 页面管理模型配置、API Key 等系统参数

### 负责的源代码文件

- `frontend-web/src/App.tsx` — 应用根组件，路由配置、全局状态管理、布局结构
- `frontend-web/src/Chat.tsx` — 聊天组件，消息列表、输入框、SSE 流式消息渲染、Markdown 渲染
- `frontend-web/src/Sidebar.tsx` — 侧边栏组件，会话列表、导航菜单、项目切换
- `frontend-web/src/CommandPalette.tsx` — 命令面板组件，快捷键触发、命令搜索、快速操作
- `frontend-web/src/Settings.tsx` — 设置页面，模型配置、API Key 管理、系统参数修改

### 所需知识点

- React Hooks（useState、useEffect、useCallback、useRef、useMemo）
- TypeScript 类型系统（interface、type、泛型、类型守卫）
- Tailwind CSS 原子化样式（响应式前缀、暗色模式、自定义主题）
- 组件化设计原则（单一职责、props 向下传递、事件向上冒泡）
- SSE 客户端（EventSource API、addEventListener、事件类型分发）
- Vite 构建工具（HMR、环境变量、构建优化）

### 可能的问题

**Q1: 为什么选择 React 而不是 Vue？**

A: React 生态成熟，TypeScript 支持优秀，与项目技术需求匹配。React 的组件模型灵活（函数组件 + Hooks），适合构建复杂的交互式界面。React 社区有丰富的 SSE 和 Markdown 渲染相关库（如 react-markdown）。同时团队成员对 React 更熟悉，开发效率更高。Vite 作为构建工具与 React 配合良好，HMR 热更新体验流畅。

**Q2: 如何处理 SSE 流式输出的显示？**

A: 前端使用浏览器原生的 EventSource API 接收 SSE 事件。后端通过 sse-starlette 的 EventSourceResponse 返回 SSE 流，事件格式为 `event: <类型>\ndata: <JSON>\n\n`。前端通过 addEventListener 监听不同事件类型（text、agent_start、tool_call、done 等），实时更新 UI 状态。text 事件的 content 会追加到当前消息中，实现打字机效果。done 事件触发时关闭 EventSource 连接。

**Q3: 如何优化界面渲染性能？**

A: 通过以下方式优化：一是 React.memo 缓存不频繁变化的组件（如 Sidebar），避免父组件更新导致不必要的重渲染；二是 useCallback/useMemo 缓存回调函数和计算结果，减少子组件的 prop 变化；三是消息列表使用虚拟滚动或分页加载，避免大量消息一次性渲染；四是 Tailwind CSS 的 JIT 模式只生成实际使用的样式，减少 CSS 体积。

**Q4: CommandPalette 的设计思路是什么？**

A: CommandPalette 参考了 VS Code 的命令面板设计，通过快捷键（Ctrl+K）触发，提供模糊搜索功能。组件维护一个命令列表（切换会话、新建会话、打开设置、查看记忆等），用户输入关键词实时过滤。使用 useRef 管理输入焦点，useEffect 注册键盘事件。选中命令后执行对应的导航或操作函数，关闭面板。这种设计让用户无需鼠标即可快速访问所有功能。

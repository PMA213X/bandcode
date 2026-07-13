# 成员F 答辩提示

## 你的角色
前端开发工程师 A

## 答辩要点

### 1. 界面设计（2分钟）
- 聊天界面设计思路
- 用户交互流程
- UI/UX 设计原则

### 2. 技术实现（2分钟）
- React + TypeScript 框架
- 组件化开发
- Tailwind CSS 样式设计

### 3. 用户体验（2分钟）
- 响应式设计
- 加载状态处理
- 错误提示

### 负责的源代码文件

- `frontend-web/src/App.tsx` — 主应用组件，路由状态管理、布局结构
- `frontend-web/src/components/Chat.tsx` — 聊天界面，消息列表、输入框、SSE 流式接收、Markdown 渲染
- `frontend-web/src/components/Sidebar.tsx` — 侧边栏，导航菜单、快捷键支持
- `frontend-web/src/components/CommandPalette.tsx` — 命令面板，快捷命令搜索与执行
- `frontend-web/src/components/Settings.tsx` — 设置面板，配置项展示与编辑
- `frontend-web/src/index.css` — 全局样式
- `frontend-web/src/main.tsx` — 前端入口文件

### 所需知识点

- React 函数组件与 Hooks（useState、useEffect、useRef）
- TypeScript 类型系统（interface、type）
- Tailwind CSS 样式框架
- Lucide React 图标库
- 组件化设计模式（props 传递、状态提升）
- CSS 布局（Flexbox、Grid）

### 可能的问题

1. 为什么选择 React 而不是 Vue？
2. 如何处理流式输出显示？
3. 如何优化界面性能？
4. 如何进行用户测试？

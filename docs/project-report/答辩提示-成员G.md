# 成员G 答辩提示

## 你的角色
前端开发工程师 B

## 答辩要点

### 1. 数据展示组件（2分钟）
- 历史记录组件设计
- 记忆视图组件设计
- 文件浏览器组件设计

### 2. API 对接（2分钟）
- Axios HTTP 客户端使用
- SSE 流式接收实现
- 错误处理与 loading 状态

### 3. 用户体验优化（2分钟）
- 列表分页加载
- 搜索与过滤功能
- 响应式布局

### 负责的源代码文件

- `frontend-web/src/components/History.tsx` — 历史记录组件，会话列表、消息查看、删除会话
- `frontend-web/src/components/MemoryView.tsx` — 记忆视图组件，六层 Memory 展示、搜索功能
- `frontend-web/src/components/ModelTest.tsx` — 模型测试组件，模型连接测试、流式输出测试、模型信息展示
- `frontend-web/src/components/FileExplorer.tsx` — 文件浏览器组件，目录树展示、文件导航
- `frontend-web/src/components/WorkspaceInfo.tsx` — 工作区信息组件，工作区路径展示

### 所需知识点

- Axios HTTP 客户端（GET/POST/DELETE 请求）
- React 状态管理（useState、useEffect、条件渲染）
- Server-Sent Events（SSE）客户端接收
- 错误处理与 loading 状态管理
- 列表渲染与分页加载
- 文件树递归组件设计

### 可能的问题

1. 如何实现 SSE 流式接收？
2. 如何处理 API 请求失败？
3. 如何优化大量数据的渲染性能？
4. 如何实现文件浏览器的目录树？

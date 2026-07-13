# 成员G 答辩提示

## 你的角色
前端开发工程师 B

## 答辩要点

### 1. 数据展示组件（2分钟）
- History 组件：会话历史列表、消息详情查看、会话删除管理
- MemoryView 组件：六层 Memory 分层展示、搜索功能、层级切换
- FileExplorer 组件：递归目录树展示、文件/目录区分、展开折叠

### 2. API 对接（2分钟）
- Axios HTTP 客户端封装，统一请求/响应拦截
- SSE 流式接收：EventSource 监听 12 种事件类型
- 错误处理：网络异常、API 错误、loading 状态管理

### 3. 用户体验优化（2分钟）
- ModelTest 组件：模型连接测试、流式输出实时展示
- WorkspaceInfo 组件：工作区路径展示、文件统计
- 响应式布局与条件渲染优化

### 负责的源代码文件

- `frontend-web/src/components/History.tsx` — 历史记录组件，会话列表展示、消息查看、分页加载、删除会话
- `frontend-web/src/components/MemoryView.tsx` — 记忆视图组件，六层 Memory 展示（global/project/task/session/checkpoint/notes）、跨层搜索
- `frontend-web/src/components/ModelTest.tsx` — 模型测试组件，模型连接测试、流式输出实时展示、模型信息显示
- `frontend-web/src/components/FileExplorer.tsx` — 文件浏览器组件，递归目录树、文件/目录区分、点击导航
- `frontend-web/src/components/WorkspaceInfo.tsx` — 工作区信息组件，工作区路径、文件统计、项目状态

### 所需知识点

- Axios HTTP 客户端（GET/POST/DELETE、请求拦截器、响应拦截器、错误处理）
- React 状态管理（useState、useEffect、条件渲染、列表渲染）
- Server-Sent Events 客户端接收（EventSource、addEventListener、事件分发）
- 错误处理与 loading 状态管理（try-catch、finally、loading/error 状态机）
- 列表渲染与分页加载（limit/offset、has_more 字段、懒加载）
- 文件树递归组件设计（递归渲染、展开/折叠状态、图标区分）

### 可能的问题

**Q1: 如何实现 SSE 流式接收？**

A: 前端使用浏览器原生的 EventSource API 接收 SSE 事件。后端通过 sse-starlette 的 EventSourceResponse 返回 SSE 流，事件格式为 `event: <类型>\ndata: <JSON>\n\n`。前端通过 addEventListener 监听不同事件类型（如 text、agent_start、tool_call、done 等），实时更新组件状态。后端使用 asyncio.Queue 在处理函数和 SSE 生成器之间传递事件，push_done 函数放入 None 作为结束信号，sse_generator 检测到 None 后终止生成，前端收到 done 事件后关闭连接。

**Q2: 如何处理 API 请求失败？**

A: 项目在多个层面处理 API 失败：一是 LLMClient 的 _handle_error 方法将 API 错误分类处理（AuthenticationError 返回 API Key 无效提示、APIConnectionError 返回网络连接错误提示、429 返回频率超限提示），返回用户友好的错误消息；二是后端 register_error_handlers 统一捕获未处理异常，返回统一格式 {code, data, message}；三是前端通过 SSE 的 error 事件类型（chat_error）接收错误信息并展示；四是 Axios 拦截器统一处理 HTTP 层面的网络异常。

**Q3: 如何优化大量数据的渲染性能？**

A: 通过以下方式优化：一是 MemoryView 组件支持按层级分别展示，用户切换 Tab 时才加载对应层数据，避免一次性渲染所有内容；二是 History 组件支持分页加载（limit/offset 参数），后端返回 has_more 字段指示是否还有更多数据，实现按需加载；三是搜索功能在后端实现（MemoryStore.search_memory），只返回匹配的结果片段，减少前端数据传输量；四是 React 条件渲染，只在组件可见时执行数据请求。

**Q4: 如何实现文件浏览器的目录树？**

A: FileExplorer 组件通过递归渲染实现目录树。后端 /api/workspace/list 接口列出指定目录下的文件和子目录，返回每个条目的名称、类型（file/directory）、路径。前端定义递归组件，目录节点包含展开/折叠状态（useState），点击目录时切换状态并加载子项。使用 Lucide React 图标库区分文件和目录类型。WorkspaceInfo 组件显示当前工作区路径和文件统计信息。路径点击支持导航到对应目录。

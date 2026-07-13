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

**Q1: 如何实现 SSE 流式接收？**

A: 前端使用浏览器原生的 EventSource API 接收 SSE 事件。后端通过 sse-starlette 库的 EventSourceResponse 返回 SSE 流，事件格式为 `event: <类型>\ndata: <JSON>\n\n`。前端通过 addEventListener 监听不同事件类型（如 text、agent_start、done 等），实时更新 UI 状态。后端使用 asyncio.Queue 在处理函数和 SSE 生成器之间传递事件，push_done 函数会放入 None 作为结束信号，sse_generator 检测到 None 后终止生成。

**Q2: 如何处理 API 请求失败？**

A: 项目在多个层面处理 API 失败：一是 LLMClient 的 _handle_error 方法将 API 错误分类处理（AuthenticationError 返回 API Key 无效提示、APIConnectionError 返回网络连接错误提示、429 返回频率超限提示等），返回用户友好的错误消息；二是后端全局异常处理器 register_error_handlers 统一捕获未处理异常，返回统一格式的错误响应 {code, data, message}；三是前端通过 SSE 的 error 事件类型（chat_error）接收错误信息并展示给用户。

**Q3: 如何优化大量数据的渲染性能？**

A: 通过以下方式优化：一是 MemoryView 组件支持按层级（global/project/task/session/checkpoint/notes）分别展示，避免一次性渲染所有数据；二是 History 组件支持分页加载（limit/offset 参数），后端 /api/chat/history 接口返回 has_more 字段指示是否还有更多数据；三是搜索功能在后端实现（MemoryStore.search_memory），只返回匹配的结果片段，减少前端数据传输量；四是 React 条件渲染，只在用户切换到对应 Tab 时才加载数据。

**Q4: 如何实现文件浏览器的目录树？**

A: FileExplorer 组件通过递归渲染实现目录树。后端 /api/workspace 接口提供工作区信息，/api/workspace/list 接口列出指定目录下的文件和子目录。前端通过递归组件展示目录结构，每个目录节点可以展开/折叠。WorkspaceInfo 组件显示当前工作区路径。文件树使用 Lucide React 图标库区分文件和目录类型，支持点击文件导航到对应路径。

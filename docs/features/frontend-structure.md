# 前端项目整体目录架构
## 1.项目根目录 frontend/src
### 1.1 components（组件文件夹）
- Chat.tsx：聊天页面核心组件；
- Layout.tsx：全局外层布局组件，划分顶部导航栏、侧边菜单栏、页面主体；
- AgentStatus.tsx、MemoryView.tsx：辅助展示组件。
### 1.2 hooks（自定义钩子）
- useSSE.ts：封装SSE连接逻辑，管理和后端的长连接；
- useChatSession.ts：会话状态管理。
### 1.3 services（接口请求层）
- api.ts：统一封装后端接口请求；
- errors.ts：全局错误处理。
### 1.4 types（TS类型定义）
api.ts定义后端返回数据、请求参数的TypeScript类型，规避类型错误。
### 1.5 utils工具文件夹
eventGuards.ts：SSE事件类型守卫函数，校验后端推送的数据格式。

## 2.整体开发模式
1. 采用React+TypeScript开发；
2. 组件化开发：页面拆分为独立组件；
3. 遵循Git协作规范：每个人新建独立分支开发，完成之后提交PR审核合并至develop分支。

# Chat‑UI聊天组件文档
## 1.组件说明
聊天界面组件，实现消息发送、消息展示、滚动加载历史对话，适配全局scss样式。
- 组件文件：`src/Chat.tsx`
- 样式依赖：`.mimocode/workflows/global.scss`

## 2.Props参数
|参数|类型|必填|描述|
|---|---|---|---|
|messageList|Array|是|消息列表数组|
|onSendMsg|Function|是|发送消息回调函数|
|loading|boolean|false|加载状态|

##3.代码示例
```tsx
import Chat from "./Chat";
function ChatPage(){
  const list = [{content:"你好",role:"user"}];
  const send = (msg:string)=>{}
  return <Chat messageList={list} onSendMsg={send} loading={false}/>
}

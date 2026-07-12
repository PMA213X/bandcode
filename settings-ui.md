\# Settings‑UI组件文档

\## 1.组件说明

该组件负责页面设置模块，包含主题切换、布局配置、字体大小调整功能，配合全局样式文件 global.scss 完成样式渲染。

\- 对应文件：`src/Settings.tsx`

\- 全局样式：`.mimocode/workflows/global.scss`



\## 2.可配置参数

| 参数名 | 类型 | 默认值 | 说明 |

| ---- | ---- | ---- | ---- |

| themeMode | string | "light" | 主题模式，可选 light / dark |

| fontSize | number | 14 | 页面字体大小 |

| layoutType | string | "normal" | 布局方式 normal / compact |



\## 3.组件使用示例

```tsx

import Settings from "./Settings";



function App() {

&#x20; return (

&#x20;   <div>

&#x20;     <Settings

&#x20;       themeMode="light"

&#x20;       fontSize={14}

&#x20;       layoutType="normal"

&#x20;     />

&#x20;   </div>

&#x20; )

}

```

\## 4.开发完成说明

成员‑F完成全局样式配置，编写页面基础UI样式，对应Issue#20。




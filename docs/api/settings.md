# 设置接口文档

> 模块：backend/api/settings.py  
> 负责人：成员D（后端-A）  
> 最后更新：2026-07-10

---

## 一、接口概述

设置接口用于管理系统配置，支持获取和更新配置项。

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 获取全部设置 | GET | /api/settings | 返回所有配置 |
| 获取指定配置节 | GET | /api/settings/{section} | 返回指定配置节 |
| 更新配置项 | POST | /api/settings | 更新单个配置项 |
| 重新加载设置 | POST | /api/settings/reload | 从文件重新加载 |

---

## 二、配置结构

```json
{
  "模型设置": {
    "默认模型": "xiaomi/mimo-v2.5-pro",
    "Base URL": "https://api.example.com/v1",
    "API Key": "sk-your-api-key-here"
  },
  "Agent 设置": {
    "默认Agent": "planner",
    "审批模式": true
  },
  "Memory 设置": {
    "自动更新Memory": true,
    "Memory压缩": true,
    "压缩阈值": 1000
  },
  "Workflow 设置": {
    "开启约束智能检索": true,
    "自动修正": true,
    "最大修正次数": 3
  },
  "RAG 设置": {
    "知识库路径": "knowledge/",
    "检索数量": 5,
    "相似度阈值": 0.7
  },
  "Tool 设置": {
    "工具目录": "tools/",
    "自动发现": true
  }
}
```

---

## 三、接口详情

### 3.1 获取全部设置

**请求：**
```
GET /api/settings
```

**响应：**
```json
{
  "code": 0,
  "data": {
    "模型设置": {...},
    "Agent 设置": {...},
    "Memory 设置": {...},
    "Workflow 设置": {...},
    "RAG 设置": {...},
    "Tool 设置": {...}
  },
  "message": "ok"
}
```

### 3.2 更新配置项

**请求：**
```
POST /api/settings
Content-Type: application/json

{
  "section": "模型设置",
  "key": "默认模型",
  "value": "xiaomi/mimo-v2.5"
}
```

**响应：**
```json
{
  "code": 0,
  "data": {
    "section": "模型设置",
    "key": "默认模型",
    "old_value": "xiaomi/mimo-v2.5-pro",
    "new_value": "xiaomi/mimo-v2.5"
  },
  "message": "设置已更新"
}
```

---

## 四、相关文件

- `backend/api/settings.py` - 接口实现
- `backend/config/loader.py` - 配置加载器
- `settings.json` - 配置文件

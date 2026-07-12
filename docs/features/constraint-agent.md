# Constraint Agent（约束检索智能体）

## 概述

Constraint Agent 是 BandCode 的系统级智能体，负责从项目的分层 Memory 系统中检索与当前问题相关的约束信息。

## 角色定位

- **类型**：系统级，用户不可见
- **触发**：每次用户输入后自动触发
- **模型**：mimo-v2.5，温度 0.1

## 主要功能

### 1. 用户意图解析
- 解析用户输入，识别意图和关键词
- 分类任务类型（代码修改、查询、配置等）

### 2. 多层 Memory 检索
- Global Memory：通用编码规范
- Project Memory：项目架构决策
- Task Memory：当前任务约束

### 3. 约束筛选与排序
- 去重处理
- 按相关性排序
- 截取 top_k=10

### 4. 约束摘要生成
- 生成简洁的约束摘要
- 供后续 Agent 参考

## 工作流程

```
用户输入
    ↓
意图解析
    ↓
检索 Global Memory
    ↓
检索 Project Memory
    ↓
检索 Task Memory
    ↓
去重 + 排序
    ↓
生成约束摘要
    ↓
输出 constraints + constraint_summary
```

## 输出格式

```json
{
  "constraints": [
    "使用 JWT 认证",
    "密码使用 bcrypt 加密",
    "API 返回格式: {code, data, msg}"
  ],
  "constraint_summary": "当前任务需遵循认证规范和 API 格式约定"
}
```

## SSE 事件

```json
{"event": "agent_start", "data": {"agent": "constraint", "status": "检索相关约束..."}}
{"event": "constraint_result", "data": {"count": 3, "summary": "..."}}
```

## 工具权限

| 权限 | 值 |
|------|-----|
| read | allow |
| edit | deny |
| bash | deny |

## 文件结构

```
backend/agents/
├── constraint.py    # Constraint Agent 实现
└── ...
```

## 与其他 Agent 的关系

- **输入**：用户原始输入
- **输出**：constraints 和 constraint_summary
- **下游**：Planner Agent 使用约束信息进行任务规划

## 配置项

| 配置 | 默认值 | 说明 |
|------|--------|------|
| 开启约束智能检索 | true | 是否启用 Constraint Agent |
| top_k | 10 | 返回约束数量 |

# Constraint Agent（约束检索智能体）

## 基本信息

| 属性 | 值 |
|------|-----|
| Agent名称 | Constraint Agent |
| 中文名称 | 约束检索智能体 |
| 类型 | 系统级，用户不可见 |
| 模型 | mimo-v2.5 |
| 温度 | 0.1 |
| 触发方式 | 每次用户输入后自动触发 |

## 职责

从Memory中智能检索与当前用户意图相关的约束规则，为后续Agent提供约束上下文。

## 工具权限

| 工具 | 权限 |
|------|------|
| read | allow |
| edit | deny |
| bash | deny |

## 工作流程

1. **解析用户意图**：分析用户输入，提取关键语义信息
2. **检索各层Memory**：
   - Global Memory：全局约束规则
   - Project Memory：项目级约束
   - Task Memory：任务级约束
3. **去重+排序**：对检索结果进行去重，按相关性排序，取 top_k=10
4. **生成约束摘要**：将约束整理为结构化摘要

## 输出格式

```json
{
  "constraints": [
    {
      "id": "constraint_id",
      "source": "global|project|task",
      "content": "约束内容",
      "relevance": 0.95
    }
  ],
  "constraint_summary": "约束摘要文本"
}
```

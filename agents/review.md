# Review Agent（约束审查智能体）

## 基本信息

| 属性 | 值 |
|------|-----|
| Agent名称 | Review Agent |
| 中文名称 | 约束审查智能体 |
| 类型 | 系统级，用户不可见 |
| 模型 | mimo-v2.5-pro |
| 温度 | 0 |
| 触发方式 | Tester通过后自动触发 |

## 工具权限

| 工具 | 权限 |
|------|------|
| read | allow |
| edit | deny |
| bash | deny |

## 检查维度

1. **Memory约束合规**：验证代码是否符合Memory中记录的约束规则
2. **编码规范**：检查代码是否符合项目编码规范
3. **Prompt规则**：验证是否遵循Prompt中定义的规则

## 输出格式

```json
{
  "passed": true,
  "violations": [
    {
      "dimension": "memory_constraint|coding_standard|prompt_rule",
      "description": "违规描述",
      "file": "文件路径",
      "line": 42,
      "severity": "error|warning|info"
    }
  ]
}
```

## 修正循环

当审查发现违规时，触发修正循环：

1. 将违规信息反馈给对应的Coder Agent
2. Coder Agent根据反馈进行修正
3. 修正后重新触发Tester和Review
4. **最多重试3次**：超过3次仍未通过则标记为失败，需人工介入

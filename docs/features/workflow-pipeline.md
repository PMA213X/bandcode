# Workflow 管线文档

> 模块：`backend/workflow/`
> 负责人：成员E
> 更新时间：2026-07-10

---

## 一、概述

BandCode 的 Workflow 模块实现**六 Agent 协作流水线**，等价于 LangGraph 的 StateGraph 设计。

核心流程：

```
用户输入 → 约束检索 → RAG → Prompt构建 → Planner → 审批 → 子Agent → Tester → Review → 输出
```

## 二、核心组件

### 2.1 PipelineState

贯穿整个工作流的状态数据结构，通过状态传递实现节点间通信。

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| user_input | str | 用户原始输入 |
| session_id | str | 会话 ID |
| constraints | list | 约束列表 |
| constraint_summary | str | 约束摘要 |
| rag_context | str | RAG 检索结果 |
| memory_context | dict | Memory 各层级 |
| plan | dict | Planner 输出计划 |
| agent_output | dict | 子 Agent 输出 |
| test_result | dict | Tester 测试结果 |
| review_result | dict | Review 审查结果 |
| current_step | str | 当前步骤名 |
| retry_count | int | 修正循环计数 |
| error | str | 错误信息 |
| done | bool | 流程是否结束 |

### 2.2 Pipeline

主管线，8 个节点顺序执行。

**节点列表**：

| 节点 | 函数 | 说明 |
|------|------|------|
| ① 约束检索 | node_constraint | Constraint Agent 检索相关约束 |
| ② RAG 检索 | node_rag | 从知识库检索相关内容 |
| ③ Prompt 构建 | node_prompt_build | 组装完整 Prompt |
| ④ Planner 调度 | node_planner | 需求分析、任务拆解 |
| ⑤ 审批检查 | node_approval | 高风险操作请求确认 |
| ⑥ 子 Agent 执行 | node_subagent | SimpleCoder/ComplexCoder 执行 |
| ⑦ Tester 验证 | node_tester | 编译检查、测试执行 |
| ⑧ Review 审查 | node_review | 约束合规检查 |

**使用示例**：

```python
from workflow.pipeline import Pipeline
from workflow.state import PipelineState

pipeline = Pipeline()
state = PipelineState(
    user_input="帮我实现用户登录功能",
    session_id="session-123",
    project="my-project"
)

result = await pipeline.run(state)
```

### 2.3 ReviewLoop

自动修正循环管理器。

**工作流程**：

1. 执行 Review 检查
2. 如果失败且开启自动修正，将违规信息反馈给 Planner
3. Planner 重新生成代码
4. 重复直到通过或达到最大修正次数
5. 超过最大次数可回滚到修改前快照

**使用示例**：

```python
from workflow.review_loop import ReviewLoop

loop = ReviewLoop(max_retries=3, auto_fix=True)
result = await loop.run(state, review_fn, fix_fn, rollback_fn)
```

### 2.4 CheckpointManager

文件快照创建、恢复管理器。

**核心方法**：

```python
class CheckpointManager:
    def create_snapshot(session_id, files, description) -> dict
    def restore_snapshot(checkpoint_id, session_id) -> list[str]
    def list_snapshots(session_id=None) -> list[dict]
    def delete_snapshot(checkpoint_id, session_id) -> bool
```

**使用示例**：

```python
mgr = CheckpointManager("/path/to/project")

# 创建快照
cp = mgr.create_snapshot("session-1", ["src/auth.py"], "修改前")

# 恢复快照
restored = mgr.restore_snapshot(cp["checkpoint_id"], "session-1")
```

## 三、配置开关

| 开关名称 | 默认值 | 关闭后行为 |
|---------|-------|-----------|
| 开启约束智能检索 | True | 跳过 Constraint Agent |
| 开启自动约束检查 | True | 跳过 Review Agent |
| 自动修正 | True | Review 失败只报告 |
| 最大修正次数 | 3 | — |
| 修正失败自动回滚 | True | 失败后需手动处理 |
| 审批模式 | True | 不请求审批直接执行 |

## 四、文件结构

```
backend/workflow/
├── __init__.py          # 模块导出
├── state.py             # PipelineState 数据结构
├── pipeline.py          # Pipeline 主管线
├── review_loop.py       # ReviewLoop 修正循环
└── checkpoint.py        # CheckpointManager 快照管理
```

## 五、测试

```bash
cd backend
pytest tests/test_workflow.py -v
```

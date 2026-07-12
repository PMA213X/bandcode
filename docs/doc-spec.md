# 文档开发规范

> 版本：v1.0 | 日期：2026-07-06 | 适用范围：全员

---

## 一、文档驱动开发

开发前必须：

1. 检查 `docs/` 目录是否存在对应文档
2. 不存在对应文档时，先创建文档骨架
3. 再开始开发

---

## 二、文档目录结构

```
docs/
├── changes/                    # 代码变更记录
├── features/                   # 功能文档
├── api/                        # API 接口文档
├── architecture/               # 架构文档
├── members/                    # 成员开发规划
├── git-commit-spec.md          # Git 提交规范
├── development-plan.md         # 开发规划
└── doc-spec.md                 # 文档规范（本文件）
```

---

## 三、文档更新规则

### 3.1 必须更新的情况

| 场景 | 更新目录 | 记录内容 |
|------|---------|---------|
| 每次代码修改 | `docs/changes/` | 日期、修改原因、涉及文件、涉及模块 |
| 新增功能 | `docs/features/` | 功能说明、使用方式、示例 |
| 修改 API | `docs/api/` | 接口定义、请求/响应格式 |
| 架构变化 | `docs/architecture/` | 架构决策、模块关系、技术选型 |

### 3.2 禁止事项

- 禁止代码与文档不同步
- 禁止提交代码时遗漏文档更新
- 禁止文档中使用过时的代码示例

---

## 四、变更记录格式

文件命名：`YYYY-MM-DD-变更描述.md`

示例：`2026-07-06-add-user-auth.md`

### 4.1 模板

```markdown
# YYYY-MM-DD 变更标题

## 修改原因

简述为什么需要这次修改。

## 涉及文件

- file1.py（新增/修改/删除）
- file2.ts（新增/修改/删除）

## 涉及模块

- 模块名称

## 变更内容

详细描述变更内容。
```

### 4.2 示例

```markdown
# 2026-07-06 添加用户认证模块

## 修改原因

项目需要用户登录功能，实现 JWT 认证。

## 涉及文件

- backend/agents/auth.py（新增）
- backend/api/users.py（修改）
- backend/tests/test_auth.py（新增）

## 涉及模块

- Agent 系统
- API 路由

## 变更内容

1. 实现 JWT 认证 Agent
2. 添加登录/注册 API
3. 编写单元测试
```

---

## 五、功能文档格式

文件命名：`功能名称.md`

示例：`user-auth.md`

### 5.1 模板

```markdown
# 功能名称

## 概述

简述功能用途。

## 使用方式

如何使用该功能。

## 配置项

相关配置说明。

## 示例

代码示例或使用示例。

## 注意事项

使用时需要注意的问题。
```

### 5.2 示例

```markdown
# 用户认证

## 概述

实现基于 JWT 的用户认证系统。

## 使用方式

1. 调用 `/api/users/create` 创建用户
2. 调用 `/api/users/login` 登录获取 Token
3. 后续请求在 Header 中携带 Token

## 配置项

| 配置 | 默认值 | 说明 |
|------|--------|------|
| Token 有效期 | 24h | JWT Token 有效时间 |
| 加密算法 | HS256 | JWT 签名算法 |

## 示例

```python
# 登录获取 Token
response = requests.post("/api/users/login", json={
    "username": "user1",
    "password": "pass123"
})
token = response.json()["data"]["token"]
```

## 注意事项

- 密码必须 bcrypt 加密存储
- Token 过期后需要重新登录
```

---

## 六、API 文档格式

文件命名：`接口名称.md`

示例：`chat-stream.md`

### 6.1 模板

```markdown
# 接口名称

## 基本信息

- 路径：`POST /api/xxx`
- 说明：接口用途

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| field1 | string | 是 | 说明 |
| field2 | int | 否 | 说明 |

## 请求示例

```json
{
  "field1": "value1",
  "field2": 123
}
```

## 响应参数

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码 |
| data | object | 数据 |
| message | string | 消息 |

## 响应示例

```json
{
  "code": 200,
  "data": {},
  "message": "成功"
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 500 | 服务器错误 |
```

---

## 七、架构文档格式

文件命名：`架构主题.md`

示例：`agent-system.md`

### 7.1 模板

```markdown
# 架构主题

## 背景

为什么需要这个架构决策。

## 设计方案

详细设计方案。

## 模块关系

模块之间的依赖关系。

## 技术选型

选择的技术及理由。

## 注意事项

架构约束和注意事项。
```

### 7.2 示例

```markdown
# Agent 系统架构

## 背景

需要实现 6 个 Agent 协作的智能体系统。

## 设计方案

采用 Pipeline + 状态传递模式：

1. Constraint Agent → 约束检索
2. Planner Agent → 任务规划
3. SimpleCoder/ComplexCoder → 代码生成
4. Tester Agent → 测试验证
5. Review Agent → 约束审查

## 模块关系

```
用户输入 → Constraint → Planner → 子Agent → Tester → Review → 输出
```

## 技术选型

| 组件 | 技术 | 理由 |
|------|------|------|
| Agent 基类 | Python ABC | 统一接口 |
| 状态管理 | dataclass | 类型安全 |
| LLM 调用 | OpenAI SDK | 兼容性好 |

## 注意事项

- Tester 的 edit 权限为 deny
- Review 最多重试 3 次
```

---

## 八、代码注释规范

### 8.1 注释语言

- 所有注释使用简体中文
- 代码命名使用英文

### 8.2 文件头注释

```python
"""
模块名称 - 模块简述

详细说明模块的用途和主要功能。
"""
```

### 8.3 函数注释

```python
def function_name(param1: str, param2: int) -> bool:
    """
    函数简述

    Args:
        param1: 参数1说明
        param2: 参数2说明

    Returns:
        返回值说明

    Raises:
        ValueError: 异常说明
    """
```

### 8.4 类注释

```python
class ClassName:
    """
    类简述

    详细说明类的用途和主要功能。

    Attributes:
        attr1: 属性1说明
        attr2: 属性2说明
    """
```

---

## 九、文档审核清单

提交文档前检查：

- [ ] 文档与代码同步
- [ ] 示例代码可运行
- [ ] 格式符合规范
- [ ] 无错别字
- [ ] 链接有效
- [ ] 图片清晰

---

## 十、文档维护责任

| 角色 | 责任 |
|------|------|
| 成员A | 维护整体文档结构、审核文档质量 |
| 各成员 | 维护自己负责模块的文档 |
| 全员 | 提交代码时同步更新文档 |

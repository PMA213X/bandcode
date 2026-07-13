# BandCode

基于分层记忆与六智能体协作的 AI 编程助手 CLI 工具。

## 项目概述

BandCode 通过六层 Memory 系统和六个智能体的协作，实现项目级的长期记忆和智能代码生成。

### 核心特性

- **分层 Memory 系统**：Global → Project → Task → Session → Checkpoint → Notes
- **六 Agent 协作**：Planner / SimpleCoder / ComplexCoder / Tester / Constraint / Review
- **RAG 知识库**：支持知识库文档的自动索引和检索
- **SSE 流式输出**：全程 Server-Sent Events 推送
- **配置驱动**：Agent、Tool、Workflow 均通过配置定义
- **命令式交互**：输入 `/` 打开命令面板，`@` 选择文件
- **自动 Memory**：自动记录对话、工具调用、决策，支持搜索和压缩

## 技术栈

- **前端**：React 18 + Ink 4 + TypeScript
- **后端**：Python 3.11 + FastAPI
- **数据库**：SQLite + ChromaDB
- **AI 模型**：MiMo v2.5 Pro

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Git

### 安装

```bash
# 克隆仓库
git clone https://github.com/PMA213X/bandcode.git
cd bandcode

# 安装后端依赖
cd backend
pip install -r requirements.txt

# 安装前端依赖
cd ../frontend
npm install
```

### 配置

1. 复制配置模板：
```bash
cp settings.example.json settings.json
```

2. 编辑 settings.json，填入你的 API Key：
```json
{
  "模型设置": {
    "API Key": "your-api-key-here"
  }
}
```

### 运行

#### 方式一：一键启动（推荐）

**Windows：**
```powershell
.\start.ps1
```

**Linux/Mac：**
```bash
./start.sh
```

一键启动脚本会自动：
- 检查 Python 和 Node.js 环境
- 安装后端/前端依赖
- 创建配置文件（如果不存在）
- 启动后端服务（后台）
- 启动前端 CLI

#### 方式二：手动启动

```bash
# 启动后端
cd backend
python main.py

# 启动前端（新终端）
cd frontend
npm run dev
```

### 配置说明

首次运行时，一键启动脚本会自动创建 `settings.json` 配置文件。

你也可以通过前端界面配置：
- 输入 `/settings` 打开设置面板
- 选择模型提供商（MiMo/OpenAI/DeepSeek/Claude/Qwen）
- 输入 API Key
- 设置会自动保存到后端

## 项目结构

```
bandcode/
├── backend/                # 后端服务
│   ├── agents/            # Agent 实现
│   ├── api/               # API 路由
│   ├── config/            # 配置加载
│   ├── database/          # 数据库操作
│   ├── memory/            # Memory 系统
│   ├── models/            # 数据模型
│   ├── rag/               # RAG 引擎
│   ├── tests/             # 测试文件
│   ├── tools/             # Tool 系统
│   └── workflow/          # Workflow 管线
├── frontend/               # 前端 CLI
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   ├── hooks/         # React Hooks
│   │   ├── services/      # API 服务
│   │   ├── styles/        # 样式定义
│   │   ├── types/         # TypeScript 类型
│   │   └── utils/         # 工具函数
│   ├── package.json
│   └── tsconfig.json
├── agents/                 # Agent 定义文件
├── tools/                  # Tool 定义文件
├── memory/                 # Memory 数据（运行时）
│   └── global/            # 全局 Memory 模板
├── docs/                   # 项目文档
├── knowledge/              # RAG 知识库
├── start.ps1               # Windows 一键启动脚本
├── start.sh                # Linux/Mac 一键启动脚本
├── CHANGELOG.md            # 更新日志
├── README.md               # 项目说明
└── settings.example.json   # 配置模板
```

## 文档

- [开发规范](docs/doc-spec.md)
- [Git 提交规范](docs/git-commit-spec.md)
- [团队成员](docs/team-members.md)
- [开发规划](docs/development-plan.md)

## 团队成员

| 成员 | 角色 | GitHub |
|------|------|--------|
| 成员A | 组长/项目经理 | PMA2138 |
| 成员B | AI 开发工程师 A | 3599729594 |
| 成员C | AI 开发工程师 B | wang123456-123456 |
| 成员D | 后端开发工程师 A | tan0310 |
| 成员E | 后端开发工程师 B | lw-womm |
| 成员F | 前端开发工程师 A | hon22079 |
| 成员G | 前端开发工程师 B | malingyun123 |

## 版本历史

### v0.1.0 (2026-07-12) — 核心功能完成

#### 🎯 里程碑
- 实现完整的六 Agent 协作系统
- 实现分层 Memory 系统
- 实现 RAG 知识库检索
- 实现 SSE 流式输出
- 完成前后端联调

#### 👥 团队贡献

**成员A (PMA2138) — 组长/项目经理**
- 项目架构设计与规划
- Agent/Tool 定义文件编写
- 项目协调与代码审查
- 版本发布管理

**成员B (3599729594) — AI 开发工程师 A（RAG 方向）**
- RAG 引擎实现（文档切分、向量索引、相似度检索）
- LLM 统一封装
- Embedding 向量化封装
- Constraint Agent 实现
- Review Agent 约束检查

**成员C (wang123456-123456) — AI 开发工程师 B（Agent 编排方向）**
- Agent 基类与管理器
- Planner Agent 实现
- SimpleCoder Agent 实现
- ComplexCoder Agent 实现
- Tester Agent 实现
- Tool 系统实现（8 个内置工具）
- Agent/Tool 单元测试

**成员D (tan0310) — 后端开发工程师 A（框架与通信方向）**
- FastAPI 框架搭建
- 8 个 RESTful API 路由
- SSE 流式推送机制
- 错误处理和日志系统
- Pydantic 请求/响应模型
- 中间件实现

**成员E (lw-womm) — 后端开发工程师 B（数据与业务逻辑方向）**
- SQLite 数据库设计与实现
- Memory 分层存储系统
- Workflow 管线实现
- Review 修正循环
- 快照管理
- Prompt Builder

**成员F (hon22079) — 前端开发工程师 A（界面设计方向）**
- React Ink CLI 框架搭建
- Chat 聊天界面组件
- Layout 布局组件
- Settings 设置面板组件
- 全局样式系统
- 前端 UI 架构文档

**成员G (malingyun123) — 前端开发工程师 B（数据对接方向）**
- Axios HTTP 客户端封装
- SSE 连接管理 Hook
- Agent 状态显示组件
- Memory 浏览组件
- 审批弹窗组件
- TypeScript 类型定义
- 命令面板组件
- 文件选择组件

#### 📁 新增文件

**后端**
- `backend/agents/` — 6 个 Agent 实现
- `backend/tools/` — Tool 系统
- `backend/rag/` — RAG 引擎
- `backend/memory/` — Memory 系统
- `backend/workflow/` — Workflow 管线
- `backend/database/` — 数据库操作
- `backend/api/` — API 路由

**前端**
- `frontend/src/components/` — UI 组件
- `frontend/src/hooks/` — React Hooks
- `frontend/src/services/` — API 服务
- `frontend/src/styles/` — 样式定义

**配置**
- `agents/` — Agent 定义文件
- `tools/` — Tool 定义文件
- `settings.example.json` — 配置模板

#### 📚 文档

- `docs/doc-spec.md` — 文档开发规范
- `docs/git-commit-spec.md` — Git 提交规范
- `docs/team-members.md` — 团队成员对应表
- `docs/development-plan.md` — 开发规划
- `docs/features/` — 功能文档
- `docs/api/` — API 文档
- `docs/architecture/` — 架构文档

---

### v0.0.1 (2026-07-06) — 项目初始化

#### 🎯 里程碑
- 项目立项与架构设计
- 文档规范制定
- Git 提交规范制定
- 团队分工确定

#### 👥 团队贡献

**成员A (PMA2138) — 组长/项目经理**
- 项目架构设计
- 文档开发规范编写
- Git 提交规范编写
- 团队分工规划
- 初始化项目文档

#### 📁 新增文件

- `doc1.md` — 项目立项与架构说明书
- `docs/doc-spec.md` — 文档开发规范
- `docs/git-commit-spec.md` — Git 提交规范
- `settings.example.json` — 配置模板
- `.gitignore` — Git 忽略规则

---

### 版本规划

| 版本 | 计划日期 | 主要功能 |
|------|---------|----------|
| v0.2.0 | 2026-07-19 | 自动 Memory 系统、会话压缩 |
| v0.3.0 | 2026-07-26 | 性能优化、错误处理增强 |
| v1.0.0 | 2026-08-02 | 正式发布版本 |

## 许可证

MIT License

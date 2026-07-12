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

```bash
# 启动后端
cd backend
python main.py

# 启动前端（新终端）
cd frontend
npm run dev
```

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
├── docs/                   # 项目文档
├── knowledge/              # RAG 知识库
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

- v0.0.1 (2026-07-06)：项目初始化
- v0.1.0 (2026-07-12)：核心功能完成

## 许可证

MIT License

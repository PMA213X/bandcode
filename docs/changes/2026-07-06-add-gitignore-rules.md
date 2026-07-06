# 2026-07-06 添加 .gitignore 和敏感数据规则

## 修改原因

项目缺少 .gitignore 文件，settings.json 包含 API Key 但没有排除 git，需要添加敏感数据保护。

## 涉及文件

- .gitignore（新增）
- settings.example.json（新增）
- docs/git-commit-spec.md（更新）
- memory/global/MEMORY.md（更新）
- docs/changes/2026-07-06-add-gitignore-rules.md（新增）

## 涉及模块

- Git 配置
- 文档系统
- 全局记忆

## 变更内容

1. 创建 .gitignore 文件，排除：
   - settings.json（API Key）
   - .env（环境变量）
   - .mimo/sessions/、checkpoints/、notes/、tasks/（运行时数据）
   - node_modules/、venv/、__pycache__/（依赖和缓存）
   - chroma/（向量数据库）

2. 创建 settings.example.json 模板文件（不含真实密钥）

3. 更新 git-commit-spec.md，新增第十节：
   - 必须排除的文件列表
   - settings.json 处理方式
   - 提交前检查步骤
   - 禁止提交的内容

4. 更新全局记忆，新增 Git敏感数据规则

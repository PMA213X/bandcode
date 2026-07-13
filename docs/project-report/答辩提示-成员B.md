# 成员B 答辩提示

## 你的角色
AI 开发工程师 A（RAG 方向）

## 答辩要点

### 1. RAG 知识库设计（2分钟）
- 数据来源：产品信息、FAQ、物流政策、售后政策
- 文档加载：支持 Text/CSV/PDF/Markdown
- 文本切分策略：chunk_size=500, overlap=50

### 2. 向量化与检索（2分钟）
- Embedding 模型：text2vec-base-chinese
- 向量数据库：FAISS（轻量级、本地部署）
- 检索策略：Top-K 相似度检索

### 3. 检索优化（2分钟）
- 如何提高检索准确率
- 如何处理长文本
- 如何优化检索速度

### 可能的问题

1. 为什么选择 FAISS 而不是 Chroma？
2. chunk_size 如何确定？
3. 如何评估 RAG 效果？
4. 如何处理知识库更新？

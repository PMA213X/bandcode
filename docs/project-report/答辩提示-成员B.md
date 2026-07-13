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

### 负责的源代码文件

- `backend/rag/chunker.py` — 文本切分器，TextChunk 数据结构、按段落/句子切分、超长文本分割
- `backend/rag/indexer.py` — RAG 索引器，文档切分+向量化+存入 ChromaDB、批量索引、目录索引
- `backend/rag/retriever.py` — RAG 检索器，ChromaDB 相似度检索、带过滤条件检索、SearchResult 数据结构
- `backend/models/embedding.py` — Embedding 模型封装，SentenceTransformer 调用、单条/批量向量化

### 所需知识点

- ChromaDB 向量数据库（PersistentClient、Collection、cosine 距离）
- SentenceTransformers 文本向量化（all-MiniLM-L6-v2 模型）
- 文本切分策略（按段落切分、按句子切分、overlap 重叠）
- 余弦相似度检索与 Top-K 策略
- Python dataclass 与类型注解
- pathlib 文件路径处理

### 可能的问题

1. 为什么选择 ChromaDB 而不是 FAISS？
2. chunk_size 如何确定？
3. 如何评估 RAG 效果？
4. 如何处理知识库更新？

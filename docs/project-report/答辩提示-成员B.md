# 成员B 答辩提示

## 你的角色
AI 开发工程师 A（RAG 方向）

## 答辩要点

### 1. RAG 知识库设计（2分钟）
- 数据来源：项目代码文件、Markdown 文档、配置文件等
- 文本切分：DocumentChunker（按段落/句子切分，max_chunk_size=1000, overlap=100）
- 切分模式：chunk_by_paragraph（段落切分）、chunk_by_sentence（句子切分）

### 2. 向量化与检索（2分钟）
- Embedding 模型：SentenceTransformers all-MiniLM-L6-v2（384 维向量）
- 向量数据库：ChromaDB（PersistentClient, HNSW 索引, cosine 距离）
- 检索策略：Top-K 相似度检索 + 元数据过滤

### 3. 检索优化（2分钟）
- chunk_size 和 overlap 的调优策略
- 元数据过滤提升检索精度
- 批量索引与增量更新机制

### 负责的源代码文件

- `backend/rag/chunker.py` — 文本切分器，TextChunk 数据结构、按段落/句子切分、超长文本自动分割
- `backend/rag/indexer.py` — RAG 索引器，文档切分+向量化+存入 ChromaDB、批量索引、目录级索引
- `backend/rag/retriever.py` — RAG 检索器，ChromaDB 相似度检索、带过滤条件检索、SearchResult 数据结构
- `backend/models/embedding.py` — Embedding 模型封装，SentenceTransformer 调用、单条/批量向量化

### 所需知识点

- ChromaDB 向量数据库（PersistentClient、Collection、cosine 距离、HNSW 索引）
- SentenceTransformers 文本向量化（all-MiniLM-L6-v2 模型、384 维输出）
- 文本切分策略（按段落切分、按句子切分、overlap 重叠窗口）
- 余弦相似度检索与 Top-K 策略
- Python dataclass 与类型注解
- pathlib 文件路径处理

### 可能的问题

**Q1: 为什么选择 ChromaDB 而不是 FAISS？**

A: ChromaDB 是专为 AI 应用设计的向量数据库，相比 FAISS 有几个优势：一是内置持久化支持（PersistentClient），数据自动保存到磁盘，无需手动 save_local；二是支持元数据过滤（where 条件检索），可以按文档来源、类型等维度精确筛选；三是提供了 get_or_create_collection 等简洁 API，开发效率更高。项目中使用 cosine 距离（hnsw:space: cosine）进行相似度计算。

**Q2: chunk_size 如何确定？**

A: 项目中 DocumentChunker 的 max_chunk_size 默认为 1000 字符，overlap 为 100 字符。这个值是根据实际场景调优的结果：代码注释和文档通常每段 200-500 字，chunk_size=1000 可以完整保留一段逻辑说明；overlap=100 确保切分边界处的语义连贯。切分器支持按段落切分和按句子切分两种模式，超长文本会自动在句号处断开。

**Q3: 如何评估 RAG 检索效果？**

A: 通过以下方式评估：一是检索质量，使用 SearchResult 的 score 字段（余弦相似度，1 - distance）衡量检索结果与查询的相关性，score 越高表示越相关；二是端到端测试，构造典型编程问题，验证检索结果是否包含正确的代码上下文；三是通过 ModelTest 组件进行在线测试，观察 RAG 辅助下的回答质量是否优于纯 LLM 回答。

**Q4: 如何处理知识库更新？**

A: RAGIndexer 提供了三个层级的索引接口：index_file 索引单个文件、index_documents 索引多条文档、index_directory 批量索引目录下所有匹配文件（默认 *.md）。更新时只需重新调用索引接口，ChromaDB 会自动处理向量的添加和更新。索引器还会记录元数据（source、filename），方便追溯文档来源。通过 get_stats 方法可以查看当前索引的总 chunk 数量。

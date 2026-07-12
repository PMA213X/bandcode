# RAG 引擎

## 概述

RAG（Retrieval-Augmented Generation）引擎是 BandCode 项目的核心模块之一，负责知识库的索引、检索和上下文注入。

## 主要功能

### 1. 文档切分 (rag/chunker.py)
- 支持按段落切分
- 支持按句子切分
- 可配置切分大小和重叠

### 2. 文档索引 (rag/indexer.py)
- 文档切分后向量化
- 存入 ChromaDB 向量数据库
- 支持增量索引

### 3. 向量检索 (rag/retriever.py)
- ChromaDB 相似度检索
- 支持 top_k 参数
- 返回相关文档片段和元数据

## 技术架构

```
用户查询
    ↓
Embedding 向量化
    ↓
ChromaDB 相似度检索
    ↓
返回相关文档片段
```

## 使用方式

### 索引文档
```python
from backend.rag.indexer import RAGIndexer

indexer = RAGIndexer()
await indexer.index_directory("knowledge/")
```

### 检索文档
```python
from backend.rag.retriever import RAGRetriever

retriever = RAGRetriever()
results = await retriever.search("用户认证", top_k=5)
```

## 配置项

| 配置 | 默认值 | 说明 |
|------|--------|------|
| chunk_size | 500 | 切分块大小 |
| chunk_overlap | 50 | 切分块重叠 |
| top_k | 5 | 返回结果数量 |
| embedding_model | all-MiniLM-L6-v2 | Embedding模型 |

## 文件结构

```
backend/rag/
├── __init__.py
├── chunker.py      # 文档切分器
├── indexer.py      # 文档索引器
└── retriever.py    # 向量检索器
```

## 注意事项

- ChromaDB 数据存储在本地 chroma/ 目录
- 首次索引需要较长时间
- 支持增量更新，无需重复索引

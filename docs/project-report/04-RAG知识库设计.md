# 第四章 RAG 知识库设计

## 4.1 数据来源

BandCode 的 RAG 知识库用于存储项目相关的领域知识，为 AI 回答提供上下文支撑。知识库的数据来源包括：

| 数据类型 | 来源 | 内容 |
|----------|------|------|
| 项目文档 | 项目目录下的 Markdown 文件 | 架构说明、API 文档、开发规范 |
| Agent 提示词 | `agents/*.md` | 各 Agent 的角色定义、行为约束、输出格式 |
| 工具定义 | `tools/*.json` | 工具的 JSON Schema 定义、参数说明 |
| 项目配置 | `settings.json` | 模型配置、Agent 配置、工作流配置 |
| 用户知识 | 用户手动添加的文档 | 业务规范、技术文档、FAQ |

知识库支持增量更新：新增或修改文件时，通过 `RAGIndexer.index_file()` 重新索引单个文件，无需全量重建。

## 4.2 文档加载

文档加载流程为：原始文件 → DocumentChunker 切分 → EmbeddingClient 向量化 → ChromaDB 存储。

`RAGIndexer` 提供三个层级的索引接口：

| 方法 | 功能 | 使用场景 |
|------|------|----------|
| `index_documents(documents, metadatas)` | 索引多条文档 | 批量导入项目文档、Agent 提示词 |
| `index_file(file_path)` | 索引单个文件 | 更新单个知识库文件 |
| `index_directory(dir_path, pattern)` | 索引目录下所有匹配文件 | 全量重建知识库（默认 `*.md`） |

## 4.3 文本切分器（DocumentChunker）

`backend/rag/chunker.py` 实现了自定义的文档切分器，支持两种切分模式：

### TextChunk 数据结构

```python
@dataclass
class TextChunk:
    content: str       # 文本块内容
    index: int         # 块索引
    metadata: dict     # 元数据（paragraph、sub_index、sentence_start 等）
```

### 按段落切分（chunk_by_paragraph）

以 `\n\n`（双换行符）为分隔符切分文档。每个段落作为一个 TextChunk，保留段落索引作为元数据。当段落长度超过 `max_chunk_size`（默认 1000 字符）时，调用 `_split_long_text` 方法进一步切分：

```python
def chunk_by_paragraph(self, text: str) -> list[TextChunk]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for i, para in enumerate(paragraphs):
        if len(para) > self.max_chunk_size:
            sub_chunks = self._split_long_text(para)  # 超长文本二次切分
            for j, sub in enumerate(sub_chunks):
                chunks.append(TextChunk(content=sub, index=len(chunks),
                    metadata={"paragraph": i, "sub_index": j}))
        else:
            chunks.append(TextChunk(content=para, index=i,
                metadata={"paragraph": i}))
    return chunks
```

### 按句子切分（chunk_by_sentence）

使用正则表达式 `(?<=[。！？.!?])\s*` 按中英文句号、感叹号、问号切分。支持 overlap 机制，在切分边界处保留上下文：

```python
def chunk_by_sentence(self, text: str) -> list[TextChunk]:
    sentences = re.split(r'(?<=[。！？.!?])\s*', text)
    # 将多个句子合并到一个 chunk，直到达到 max_chunk_size
    # 超出时保留 overlap 词语确保语义连贯
```

### 超长文本切分（_split_long_text）

当单个段落超过 max_chunk_size 时，按固定长度切分，优先在句号处断开，保留 overlap 避免语义断裂：

```python
def _split_long_text(self, text: str) -> list[str]:
    # 尝试在句号处断开，保留 self.overlap 的重叠区域
    last_period = text.rfind("。", start, end)
    if last_period > start:
        end = last_period + 1
    start = end - self.overlap
```

## 4.4 Embedding 模型

`backend/models/embedding.py` 封装了 SentenceTransformers 的向量化功能：

```python
class EmbeddingClient:
    MODEL_DIMENSIONS = {
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "paraphrase-multilingual-MiniLM-L12-v2": 384,
    }

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dimension = self.MODEL_DIMENSIONS.get(model_name, 384)

    def embed(self, text: str) -> list[float]:
        """单条文本向量化"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """批量文本向量化"""
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
```

默认使用 `all-MiniLM-L6-v2` 模型，输出 384 维向量。支持多种模型切换，不同模型的向量维度会自动适配。

## 4.5 向量数据库（ChromaDB）

`backend/rag/indexer.py` 和 `backend/rag/retriever.py` 使用 ChromaDB 作为向量数据库：

### RAGIndexer 索引器

```python
class RAGIndexer:
    def __init__(self, chroma_path="./chroma", collection_name="knowledge"):
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦距离
        )
```

索引器提供三个层级的索引接口：

| 方法 | 功能 | 使用场景 |
|------|------|----------|
| index_documents(documents, metadatas) | 索引多条文档 | 批量导入项目文档、Agent 提示词 |
| index_file(file_path) | 索引单个文件 | 更新单个知识库文件 |
| index_directory(dir_path, pattern) | 索引目录下所有匹配文件 | 全量重建知识库 |

索引流程：文档 → DocumentChunker 切分 → EmbeddingClient 批量向量化 → ChromaDB collection.add()

### RAGRetriever 检索器

```python
class RAGRetriever:
    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """相似度检索"""
        query_embedding = self.embedding_client.embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )
        # 将距离转换为相似度分数: score = 1 - distance

    def search_with_filter(self, query, top_k=5, where=None) -> list[SearchResult]:
        """带过滤条件的检索（支持元数据过滤）"""
```

### SearchResult 数据结构

```python
@dataclass
class SearchResult:
    content: str      # 检索到的文本内容
    score: float      # 相似度分数（0-1，越大越相关）
    metadata: dict    # 元数据（source、filename 等）
```

## 4.6 检索流程

```mermaid
graph LR
    A[用户问题] --> B[EmbeddingClient.embed]
    B --> C[ChromaDB.query]
    C --> D[Top-K SearchResult]
    D --> E[拼接上下文到 Prompt]
    E --> F[LLM 生成回答]
    F --> G[返回用户]
```

完整检索流程：

1. 用户输入问题文本
2. EmbeddingClient.embed() 将问题向量化（384 维）
3. ChromaDB collection.query() 执行余弦相似度检索
4. 返回 Top-K 个 SearchResult（包含 content、score、metadata）
5. 将检索结果的 content 拼接到 LLM Prompt 中作为上下文
6. LLM 基于上下文生成回答，减少幻觉

### Pipeline 中的 RAG 节点

在 Pipeline 工作流中，RAG 检索是第 2 个节点（node_rag）。执行流程为：

1. 从 PipelineState.user_input 获取用户输入
2. 调用 RAGRetriever.search() 检索 Top-5 相关文档
3. 将检索结果存入 PipelineState.rag_context
4. 后续 Prompt 构建节点将 rag_context 整合到 LLM Prompt 中

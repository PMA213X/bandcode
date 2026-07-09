"""RAG索引器，负责文档切分、向量化、存入ChromaDB"""

from pathlib import Path
from typing import Optional
import chromadb

from .chunker import DocumentChunker, TextChunk
from models.embedding import EmbeddingClient


class RAGIndexer:
    """RAG文档索引器"""

    def __init__(
        self,
        chroma_path: str = "./chroma",
        collection_name: str = "knowledge",
        embedding_client: Optional[EmbeddingClient] = None,
        chunker: Optional[DocumentChunker] = None
    ):
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.embedding_client = embedding_client or EmbeddingClient()
        self.chunker = chunker or DocumentChunker()

        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def index_documents(self, documents: list[str], metadatas: Optional[list[dict]] = None) -> int:
        """索引多条文档，返回索引的chunk数量"""
        all_chunks = []
        all_metadatas = []

        for i, doc in enumerate(documents):
            meta = metadatas[i] if metadatas else {"source": f"doc_{i}"}
            chunks = self.chunker.chunk_by_paragraph(doc)
            for chunk in chunks:
                chunk.metadata.update(meta)
                all_chunks.append(chunk)
                all_metadatas.append(chunk.metadata)

        # 批量向量化
        texts = [c.content for c in all_chunks]
        embeddings = self.embedding_client.embed_batch(texts)

        # 存入ChromaDB
        ids = [f"chunk_{self.collection.count() + i}" for i in range(len(all_chunks))]
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=all_metadatas
        )

        return len(all_chunks)

    def index_file(self, file_path: str) -> int:
        """索引单个文件"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        content = path.read_text(encoding="utf-8")
        metadata = {"source": str(path), "filename": path.name}

        return self.index_documents([content], [metadata])

    def index_directory(self, dir_path: str, pattern: str = "*.md") -> int:
        """索引目录下所有匹配的文件"""
        path = Path(dir_path)
        if not path.is_dir():
            raise NotADirectoryError(f"目录不存在: {dir_path}")

        total_chunks = 0
        for file_path in path.glob(pattern):
            if file_path.is_file():
                total_chunks += self.index_file(str(file_path))

        return total_chunks

    def get_stats(self) -> dict:
        """获取索引统计信息"""
        return {
            "collection": self.collection_name,
            "total_chunks": self.collection.count(),
            "chroma_path": self.chroma_path
        }

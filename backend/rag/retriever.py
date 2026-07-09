"""RAG检索器，基于ChromaDB的相似度检索"""

from dataclasses import dataclass, field
from typing import Optional
import chromadb

from models.embedding import EmbeddingClient


@dataclass
class SearchResult:
    """检索结果"""
    content: str
    score: float
    metadata: dict = field(default_factory=dict)


class RAGRetriever:
    """RAG向量检索器"""

    def __init__(
        self,
        chroma_path: str = "./chroma",
        collection_name: str = "knowledge",
        embedding_client: Optional[EmbeddingClient] = None
    ):
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.embedding_client = embedding_client or EmbeddingClient()

        # 初始化ChromaDB
        self.client = chromadb.PersistentClient(path=chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """相似度检索，返回最相关的top_k个结果"""
        if self.collection.count() == 0:
            return []

        # 查询向量化
        query_embedding = self.embedding_client.embed(query)

        # ChromaDB检索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count())
        )

        # 组装结果
        search_results = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                score = 1 - results["distances"][0][i] if results["distances"] else 0
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                search_results.append(SearchResult(
                    content=doc,
                    score=score,
                    metadata=metadata
                ))

        return search_results

    def search_with_filter(
        self,
        query: str,
        top_k: int = 5,
        where: Optional[dict] = None
    ) -> list[SearchResult]:
        """带过滤条件的检索"""
        if self.collection.count() == 0:
            return []

        query_embedding = self.embedding_client.embed(query)

        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": min(top_k, self.collection.count())
        }
        if where:
            kwargs["where"] = where

        results = self.collection.query(**kwargs)

        search_results = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                score = 1 - results["distances"][0][i] if results["distances"] else 0
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                search_results.append(SearchResult(
                    content=doc,
                    score=score,
                    metadata=metadata
                ))

        return search_results

"""Embedding向量化封装模块"""

from typing import Optional
from sentence_transformers import SentenceTransformer


class EmbeddingClient:
    """sentence-transformers的Embedding封装"""

    # 默认模型维度
    MODEL_DIMENSIONS = {
        "all-MiniLM-L6-v2": 384,
        "all-mpnet-base-v2": 768,
        "paraphrase-multilingual-MiniLM-L12-v2": 384,
    }

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
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

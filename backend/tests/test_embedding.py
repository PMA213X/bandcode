"""Embedding模块单元测试"""

import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from models.embedding import EmbeddingClient


def test_embedding_client_init():
    """测试Embedding客户端初始化"""
    with patch('models.embedding.SentenceTransformer') as mock_st:
        mock_st.return_value = MagicMock()
        client = EmbeddingClient(model_name="all-MiniLM-L6-v2")
        assert client.model_name == "all-MiniLM-L6-v2"
        assert client.dimension == 384


def test_embedding_client_default_model():
    """测试默认模型"""
    with patch('models.embedding.SentenceTransformer') as mock_st:
        mock_st.return_value = MagicMock()
        client = EmbeddingClient()
        assert client.model_name == "all-MiniLM-L6-v2"
        assert client.dimension == 384


def test_embedding_client_embed():
    """测试单条文本向量化"""
    with patch('models.embedding.SentenceTransformer') as mock_st:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([0.1] * 384)
        mock_st.return_value = mock_model

        client = EmbeddingClient()
        embedding = client.embed("测试文本")

        assert isinstance(embedding, list)
        assert len(embedding) == 384
        mock_model.encode.assert_called_once()


def test_embedding_client_embed_batch():
    """测试批量文本向量化"""
    with patch('models.embedding.SentenceTransformer') as mock_st:
        mock_model = MagicMock()
        mock_model.encode.return_value = np.array([[0.1] * 384] * 3)
        mock_st.return_value = mock_model

        client = EmbeddingClient()
        texts = ["第一段文本", "第二段文本", "第三段文本"]
        embeddings = client.embed_batch(texts)

        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        mock_model.encode.assert_called_once_with(texts, convert_to_numpy=True)

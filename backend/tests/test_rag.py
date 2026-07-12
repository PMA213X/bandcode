"""RAG模块单元测试"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from rag.chunker import DocumentChunker, TextChunk
from rag.retriever import RAGRetriever, SearchResult


class TestDocumentChunker:
    """文档切分器测试"""

    def test_chunk_by_paragraph(self):
        """测试按段落切分"""
        chunker = DocumentChunker(max_chunk_size=1000)
        text = "第一段内容\n\n第二段内容\n\n第三段内容"
        chunks = chunker.chunk_by_paragraph(text)

        assert len(chunks) == 3
        assert chunks[0].content == "第一段内容"
        assert chunks[1].content == "第二段内容"
        assert chunks[2].content == "第三段内容"

    def test_chunk_by_paragraph_empty(self):
        """测试空文本切分"""
        chunker = DocumentChunker()
        chunks = chunker.chunk_by_paragraph("")
        assert len(chunks) == 0

    def test_chunk_by_sentence(self):
        """测试按句子切分"""
        chunker = DocumentChunker(max_chunk_size=100)
        text = "这是第一句话。这是第二句话。这是第三句话。"
        chunks = chunker.chunk_by_sentence(text)

        assert len(chunks) >= 1
        assert all(isinstance(c, TextChunk) for c in chunks)

    def test_chunk_metadata(self):
        """测试chunk元数据"""
        chunker = DocumentChunker()
        text = "段落一\n\n段落二"
        chunks = chunker.chunk_by_paragraph(text)

        assert chunks[0].metadata["paragraph"] == 0
        assert chunks[1].metadata["paragraph"] == 1


class TestSearchResult:
    """检索结果测试"""

    def test_search_result_init(self):
        """测试检索结果初始化"""
        result = SearchResult(
            content="测试内容",
            score=0.95,
            metadata={"source": "test"}
        )
        assert result.content == "测试内容"
        assert result.score == 0.95
        assert result.metadata == {"source": "test"}

    def test_search_result_default_metadata(self):
        """测试默认元数据"""
        result = SearchResult(content="测试", score=0.9)
        assert result.metadata == {}

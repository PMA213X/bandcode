"""文档切分器，支持按段落和按句子切分"""

import re
from dataclasses import dataclass


@dataclass
class TextChunk:
    """文本块数据结构"""
    content: str
    index: int
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentChunker:
    """文档切分器"""

    def __init__(self, max_chunk_size: int = 1000, overlap: int = 100):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_by_paragraph(self, text: str) -> list[TextChunk]:
        """按段落切分文档"""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        for i, para in enumerate(paragraphs):
            if len(para) > self.max_chunk_size:
                sub_chunks = self._split_long_text(para)
                for j, sub in enumerate(sub_chunks):
                    chunks.append(TextChunk(
                        content=sub,
                        index=len(chunks),
                        metadata={"paragraph": i, "sub_index": j}
                    ))
            else:
                chunks.append(TextChunk(
                    content=para,
                    index=i,
                    metadata={"paragraph": i}
                ))
        return chunks

    def chunk_by_sentence(self, text: str) -> list[TextChunk]:
        """按句子切分文档"""
        sentences = re.split(r'(?<=[。！？.!?])\s*', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for sent in sentences:
            if len(current_chunk) + len(sent) > self.max_chunk_size and current_chunk:
                chunks.append(TextChunk(
                    content=current_chunk.strip(),
                    index=chunk_index,
                    metadata={"sentence_start": max(0, chunk_index - 1)}
                ))
                chunk_index += 1
                # 保留overlap
                words = current_chunk.split()
                overlap_words = words[-self.overlap // 5:] if len(words) > self.overlap // 5 else []
                current_chunk = " ".join(overlap_words) + " " + sent
            else:
                current_chunk += " " + sent if current_chunk else sent

        if current_chunk.strip():
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                index=chunk_index,
                metadata={"sentence_start": max(0, chunk_index - 1)}
            ))

        return chunks

    def _split_long_text(self, text: str) -> list[str]:
        """将超长文本切分为多个块"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.max_chunk_size
            if end < len(text):
                # 尝试在句号处断开
                last_period = text.rfind("。", start, end)
                if last_period == -1:
                    last_period = text.rfind(".", start, end)
                if last_period > start:
                    end = last_period + 1
            chunks.append(text[start:end])
            start = end - self.overlap
        return chunks

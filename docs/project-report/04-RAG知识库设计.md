# 第四章 RAG 知识库设计

## 4.1 数据来源

| 数据类型 | 来源 | 内容 |
|----------|------|------|
| 产品信息 | 官方文档 | 产品名称、口味、规格、价格 |
| 常见问题 | 客服记录 | 用户高频问题及标准回答 |
| 物流政策 | 运营文档 | 配送方式、时效、费用 |
| 售后政策 | 公司制度 | 退换货规则、投诉处理 |

## 4.2 文档加载

使用 LangChain 的文档加载器：

```python
from langchain.document_loaders import (
    TextLoader,
    CSVLoader,
    PDFLoader,
    UnstructuredMarkdownLoader
)
```

## 4.3 文本切分

使用 RecursiveCharacterTextSplitter：

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "，", " "]
)
```

## 4.4 Embedding

使用 text2vec-base-chinese 模型：

```python
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="shibing624/text2vec-base-chinese"
)
```

## 4.5 向量数据库

使用 FAISS：

```python
from langchain.vectorstores import FAISS

vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)
vectorstore.save_local("faiss_index")
```

## 4.6 检索流程

```mermaid
graph LR
    A[用户问题] --> B[Embedding]
    B --> C[FAISS 检索]
    C --> D[Top-K 文档]
    D --> E[拼接上下文]
    E --> F[大模型生成]
    F --> G[返回回答]
```

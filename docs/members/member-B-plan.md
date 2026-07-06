# 成员B — AI开发工程师A（RAG与知识库方向）开发规划

> 角色：AI 开发工程师
> 核心职责：RAG 引擎、Embedding 集成、Constraint Agent、LLM 封装
> 分支：feature/ai-rag

---

## 一、角色定位

成员B 负责项目的「感知层」能力：

- LLM 统一调用封装（所有Agent的基础）
- Embedding 文本向量化
- RAG 知识库的索引、切分、检索
- Constraint Agent 实现（从Memory中智能检索约束）
- Review Agent 协助实现（约束审查部分）

---

## 二、开发任务清单

### Phase 0：环境准备（第1天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| B-01 | 克隆仓库 | — | git clone + 切换到 feature/ai-rag 分支 |
| B-02 | 安装依赖 | `requirements.txt` | openai、chromadb、sentence-transformers |
| B-03 | 验证LLM连接 | — | 测试 OpenAI Compatible API 连通性 |
| B-04 | 验证ChromaDB | — | 测试 ChromaDB 安装和基本操作 |

### Phase 1：基础模块开发（第2-4天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| B-05 | LLM封装 | `models/llm.py` | OpenAI SDK 统一调用，支持流式/非流式 |
| B-06 | LLM单元测试 | `tests/test_llm.py` | 测试流式/非流式调用 |
| B-07 | Embedding封装 | `models/embedding.py` | sentence-transformers 文本向量化 |
| B-08 | Embedding单元测试 | `tests/test_embedding.py` | 测试向量化效果 |
| B-09 | models模块初始化 | `models/__init__.py` | 模块导出 |

### Phase 2：RAG引擎开发（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| B-10 | 文档切分器 | `rag/chunker.py` | 按段落/句子切分文档 |
| B-11 | RAG索引器 | `rag/indexer.py` | 文档切分→向量化→存入ChromaDB |
| B-12 | RAG检索器 | `rag/retriever.py` | ChromaDB 相似度检索 |
| B-13 | RAG单元测试 | `tests/test_rag.py` | 索引和检索测试 |
| B-14 | rag模块初始化 | `rag/__init__.py` | 模块导出 |
| B-15 | 知识库索引测试 | — | 对 knowledge/ 目录文档建立索引 |
| B-16 | 检索效果验证 | — | 测试检索准确率 |

### Phase 2：Constraint Agent开发（第5-8天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| B-17 | Constraint Agent实现 | `agents/constraint.py` | Memory智能检索、意图解析、约束筛选 |
| B-18 | Constraint单元测试 | `tests/test_constraint.py` | 测试约束检索逻辑 |
| B-19 | Constraint集成测试 | — | 与Memory系统联调 |

### Phase 3：Review Agent协助（第9-11天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| B-20 | Review Agent约束检查 | `agents/review.py` | 实现约束合规检查逻辑（与成员C协作） |
| B-21 | Review单元测试 | `tests/test_review.py` | 测试约束审查 |

### Phase 4-5：联调与优化（第12-16天）

| 序号 | 任务 | 文件 | 说明 |
|------|------|------|------|
| B-22 | Pipeline集成测试 | — | 测试Constraint在完整工作流中的表现 |
| B-23 | RAG效果优化 | — | 调整切分策略、检索参数 |
| B-24 | Prompt优化 | — | 优化Constraint Agent的Prompt |
| B-25 | 性能测试 | — | 测试检索延迟、token消耗 |

---

## 三、技术要点

### 3.1 LLM封装核心逻辑

```python
# models/llm.py 核心接口
class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    async def chat(self, messages: list, temperature: float = 0.1, stream: bool = False):
        """统一对话接口"""
        ...

    async def chat_stream(self, messages: list, temperature: float = 0.1):
        """流式对话接口，返回异步生成器"""
        ...
```

### 3.2 RAG检索核心逻辑

```python
# rag/retriever.py 核心接口
class RAGRetriever:
    def __init__(self, chroma_path: str, embedding_model):
        self.collection = chromadb.PersistentClient(path=chroma_path)
        self.embedding = embedding_model

    async def index(self, documents: list[str], metadatas: list[dict]):
        """索引文档"""
        ...

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        """相似度检索"""
        ...
```

### 3.3 Constraint Agent核心逻辑

```python
# agents/constraint.py 核心接口
class ConstraintAgent:
    async def run(self, state: PipelineState) -> PipelineState:
        # 1. 解析用户意图
        intent = await self.llm.classify(state.user_input)

        # 2. 检索各层Memory
        global_results = self.memory.search_memory("global", intent)
        project_results = self.memory.search_memory("project", intent)
        task_results = self.memory.search_memory("task", intent)

        # 3. 去重 + 排序
        all_constraints = self.deduplicate_and_rank(
            global_results, project_results, task_results, top_k=10
        )

        # 4. 生成约束摘要
        summary = await self.llm.summarize(all_constraints)

        state.constraints = all_constraints
        state.constraint_summary = summary
        return state
```

---

## 四、AI Agent 使用指南

### 4.1 推荐配置

| 任务类型 | Agent | 模型 | 理由 |
|---------|-------|------|------|
| LLM封装开发 | general | mimo-v2.5-pro | 异步流式处理复杂 |
| RAG引擎开发 | general | mimo-v2.5-pro | 向量检索逻辑需要精确 |
| Constraint Agent | general | mimo-v2.5-pro | Agent逻辑复杂 |
| Embedding封装 | general | mimo-v2.5 | 相对简单的封装 |
| 单元测试 | general | mimo-v2.5 | 测试代码 |
| 代码探索 | explore | mimo-v2.5 | 查找相关模块 |

### 4.2 使用示例

**实现LLM封装时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 models/llm.py，封装 OpenAI SDK 的统一对话接口。
要求：
1. 支持流式和非流式两种调用方式
2. 使用 asyncio 异步实现
3. 支持通过配置切换模型和base_url
4. 包含错误处理和重试机制
参考文件：doc1.md 第2.4节的模型选型说明
```

**实现RAG引擎时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 rag/chunker.py、rag/indexer.py、rag/retriever.py 三个文件。
要求：
1. chunker.py：支持按段落和按句子两种切分方式
2. indexer.py：接收文档路径，切分后向量化存入ChromaDB
3. retriever.py：接收查询文本，返回top_k个相似文档片段
参考文件：doc1.md 第3.3节的RAG检索说明
```

**实现Constraint Agent时：**

```
子代理：general
模型：xiaomi/mimo-v2.5-pro
任务：实现 agents/constraint.py，从Memory中智能检索相关约束。
要求：
1. 继承 agents/base.py 的Agent基类
2. 实现意图解析、Memory检索、去重排序、摘要生成
3. 输出 constraints 和 constraint_summary
参考文件：doc1.md 第3.6节Constraint Agent设计
```

**代码探索时：**

```
子代理：explore
模型：xiaomi/mimo-v2.5
任务：查看 agents/base.py 的接口定义，确认Constraint Agent需要实现哪些方法。
```

---

## 五、文件所有权

### 5.1 主责文件

```
models/__init__.py              ← 创建
models/llm.py                   ← 主责
models/embedding.py             ← 主责
rag/__init__.py                 ← 创建
rag/chunker.py                  ← 主责
rag/indexer.py                  ← 主责
rag/retriever.py                ← 主责
agents/constraint.py            ← 主责
agents/review.py                ← 协助成员C（约束检查部分）
tests/test_llm.py               ← 主责
tests/test_embedding.py         ← 主责
tests/test_rag.py               ← 主责
tests/test_constraint.py        ← 主责
tests/test_review.py            ← 协助
```

### 5.2 协作文件

| 文件 | 协作人 | 协作内容 |
|------|--------|---------|
| agents/base.py | 成员C | 继承Agent基类 |
| agents/review.py | 成员C | 约束检查逻辑部分 |
| memory/store.py | 成员E | 调用Memory存储 |
| config/loader.py | 成员D | 获取模型配置 |
| agents/constraint.md | 成员A | Prompt定义 |

---

## 六、接口依赖

### 6.1 我依赖的接口

| 依赖方 | 依赖内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员A | agents/constraint.md | Phase 1 | Constraint Agent的Prompt定义 |
| 成员C | agents/base.py | Phase 1 | Agent基类，需继承 |
| 成员E | memory/store.py | Phase 1 | Memory读写接口 |
| 成员D | config/loader.py | Phase 1 | 获取模型配置 |

### 6.2 我提供的接口

| 接收方 | 提供内容 | 交付时间 | 说明 |
|--------|---------|---------|------|
| 成员C | models/llm.py | Phase 1 | LLM调用封装 |
| 成员E | rag/retriever.py | Phase 2 | RAG检索接口 |
| 成员D | agents/constraint.py | Phase 2 | Constraint Agent |
| 全员 | models/embedding.py | Phase 1 | Embedding封装 |

---

## 七、交付物清单

| 阶段 | 交付物 | 验收标准 |
|------|--------|---------|
| Phase 0 | 环境验证通过 | LLM连接正常、ChromaDB可用 |
| Phase 1 | LLM封装、Embedding封装 | 单元测试通过 |
| Phase 2 | RAG引擎、Constraint Agent | 索引和检索正常，约束检索准确 |
| Phase 3 | Review Agent约束检查 | 约束审查逻辑正确 |
| Phase 4 | 集成测试通过 | 在完整工作流中正常运行 |
| Phase 5 | 性能优化完成 | 检索延迟<500ms，token消耗降低50% |

---

## 八、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|---------|
| ChromaDB安装失败 | RAG功能无法实现 | 准备内存向量检索备选方案 |
| Embedding模型太大 | 内存溢出 | 使用轻量级模型 all-MiniLM-L6-v2 |
| LLM API不稳定 | 测试困难 | Mock LLM返回，先测试逻辑 |
| 检索准确率低 | Constraint效果差 | 调整切分策略、增加top_k |

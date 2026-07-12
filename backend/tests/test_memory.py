"""
记忆系统模块测试
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from memory.store import MemoryStore
from memory.builder import PromptBuilder, PromptMessage
from memory.compressor import MemoryCompressor


@pytest.fixture
def tmp_project(tmp_path):
    """创建临时项目目录"""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def memory_store(tmp_project):
    """创建 MemoryStore 实例"""
    return MemoryStore(str(tmp_project))


class TestMemoryStore:
    """Memory 存储测试"""

    def test_init_dirs(self, memory_store):
        """测试目录初始化"""
        assert memory_store.base_path.exists()
        assert (memory_store.base_path / "global").exists()
        assert (memory_store.base_path / "project").exists()
        assert (memory_store.base_path / "tasks").exists()

    def test_update_and_get_global(self, memory_store):
        """测试全局 Memory 读写"""
        memory_store.update_memory("global", "偏好 Python 3.11+")
        content = memory_store.get_memory("global")
        assert "Python 3.11+" in content

    def test_update_and_get_project(self, memory_store):
        """测试项目 Memory 读写"""
        memory_store.update_memory("project", "使用 FastAPI 框架")
        content = memory_store.get_memory("project")
        assert "FastAPI" in content

    def test_append_memory(self, memory_store):
        """测试追加写入"""
        memory_store.update_memory("global", "第一条记录")
        memory_store.update_memory("global", "第二条记录")
        content = memory_store.get_memory("global")
        assert "第一条记录" in content
        assert "第二条记录" in content

    def test_search_memory(self, memory_store):
        """测试 Memory 搜索"""
        memory_store.update_memory("global", "使用 Python 3.11")
        memory_store.update_memory("global", "使用 TypeScript")
        results = memory_store.search_memory("global", "Python")
        assert len(results) > 0
        assert any("Python" in r for r in results)

    def test_search_all_layers(self, memory_store):
        """测试跨层搜索"""
        memory_store.update_memory("global", "全局规则")
        memory_store.update_memory("project", "项目约定")
        results = memory_store.search_all_layers("规则")
        assert "global" in results

    def test_get_all_layers(self, memory_store):
        """测试获取所有层级"""
        memory_store.update_memory("global", "全局内容")
        layers = memory_store.get_all_layers()
        assert "global" in layers
        assert "project" in layers


class TestPromptBuilder:
    """Prompt Builder 测试"""

    def test_build_basic(self):
        """测试基本 Prompt 构建"""
        builder = PromptBuilder()
        messages = builder.build(user_input="帮我实现登录功能")
        assert len(messages) >= 2
        assert messages[-1].role == "user"
        assert messages[-1].content == "帮我实现登录功能"

    def test_build_with_constraints(self):
        """测试带约束的 Prompt 构建"""
        builder = PromptBuilder()
        messages = builder.build(
            user_input="实现登录",
            constraint_summary="使用 JWT 认证"
        )
        constraint_msgs = [m for m in messages if "项目约束" in m.content]
        assert len(constraint_msgs) > 0

    def test_build_with_memory(self):
        """测试带 Memory 的 Prompt 构建"""
        builder = PromptBuilder()
        messages = builder.build(
            user_input="实现登录",
            memory_context={"global": "偏好 Python", "project": "FastAPI 项目"}
        )
        assert len(messages) >= 4

    def test_messages_to_dicts(self):
        """测试转换为字典格式"""
        builder = PromptBuilder()
        messages = builder.build(user_input="测试")
        dicts = builder.messages_to_dicts(messages)
        assert isinstance(dicts, list)
        assert all(isinstance(d, dict) for d in dicts)
        assert all("role" in d and "content" in d for d in dicts)


class TestMemoryCompressor:
    """Memory 压缩器测试"""

    def test_should_compress(self):
        """测试是否需要压缩"""
        compressor = MemoryCompressor(threshold=10)
        assert compressor.should_compress(15) is True
        assert compressor.should_compress(5) is False

    def test_simple_summarize(self):
        """测试简单摘要"""
        compressor = MemoryCompressor()
        messages = [
            {"role": "user", "content": "帮我实现登录功能"},
            {"role": "assistant", "content": "好的，我来实现登录功能"},
            {"role": "user", "content": "添加 JWT 验证"},
        ]
        summary = compressor._simple_summarize(
            [f"用户请求: {m['content']}" for m in messages]
        )
        assert "会话历史摘要" in summary

    def test_estimate_tokens(self):
        """测试 token 估算"""
        compressor = MemoryCompressor()
        # 中文约 1.5 字符/token
        tokens = compressor.estimate_tokens("你好世界")
        assert tokens > 0

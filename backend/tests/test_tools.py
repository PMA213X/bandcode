"""
Tool模块单元测试

测试所有Tool的输入输出和基本功能。

作者：成员C（wang123456-123456）
"""

import pytest
import json
import tempfile
from pathlib import Path

from tools.base import Tool, ToolResult
from tools.registry import ToolRegistry
from tools.builtins.read_file import ReadFileTool
from tools.builtins.write_file import WriteFileTool
from tools.builtins.list_directory import ListDirectoryTool
from tools.builtins.search_project import SearchProjectTool
from tools.builtins.create_task import CreateTaskTool
from tools.builtins.finish_task import FinishTaskTool
from tools.builtins.search_knowledge import SearchKnowledgeTool
from tools.builtins.update_memory import UpdateMemoryTool


class TestToolResult:
    """ToolResult测试"""

    def test_success(self):
        """测试成功结果"""
        result = ToolResult(success=True, data="test_data")
        assert result.success == True
        assert result.data == "test_data"
        assert result.error is None

    def test_failure(self):
        """测试失败结果"""
        result = ToolResult(success=False, error="test_error")
        assert result.success == False
        assert result.data is None
        assert result.error == "test_error"


class TestToolBase:
    """Tool基类测试"""

    def test_cannot_instantiate(self):
        """测试不能直接实例化抽象类"""
        with pytest.raises(TypeError):
            Tool()


class TestReadFileTool:
    """ReadFileTool测试"""

    def setup_method(self):
        self.tool = ReadFileTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "read_file"
        assert self.tool.description == "读取指定文件的内容"
        assert self.tool.permission == "read"

    @pytest.mark.asyncio
    async def test_read_existing_file(self):
        """测试读取存在的文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            result = await self.tool.execute(file_path=temp_path)
            assert result.success == True
            assert result.data == "test content"
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_read_nonexistent_file(self):
        """测试读取不存在的文件"""
        result = await self.tool.execute(file_path="/nonexistent/file.txt")
        assert result.success == False
        assert "not found" in result.error.lower()

    def test_validate_params(self):
        """测试参数验证"""
        assert self.tool.validate_params(file_path="test.txt") == True
        assert self.tool.validate_params() == False


class TestWriteFileTool:
    """WriteFileTool测试"""

    def setup_method(self):
        self.tool = WriteFileTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "write_file"
        assert self.tool.description == "写入或创建文件"
        assert self.tool.permission == "write"

    @pytest.mark.asyncio
    async def test_write_file(self):
        """测试写入文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            result = await self.tool.execute(
                file_path=str(file_path),
                content="test content"
            )
            assert result.success == True
            assert file_path.read_text() == "test content"

    @pytest.mark.asyncio
    async def test_write_with_dirs(self):
        """测试写入文件并创建目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "test.txt"
            result = await self.tool.execute(
                file_path=str(file_path),
                content="test content",
                create_dirs=True
            )
            assert result.success == True
            assert file_path.read_text() == "test content"


class TestListDirectoryTool:
    """ListDirectoryTool测试"""

    def setup_method(self):
        self.tool = ListDirectoryTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "list_directory"
        assert self.tool.description == "列出目录中的文件和子目录"
        assert self.tool.permission == "read"

    @pytest.mark.asyncio
    async def test_list_directory(self):
        """测试列出目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            (Path(temp_dir) / "file1.txt").touch()
            (Path(temp_dir) / "file2.txt").touch()
            (Path(temp_dir) / "subdir").mkdir()

            result = await self.tool.execute(dir_path=temp_dir)
            assert result.success == True
            assert len(result.data) == 3

    @pytest.mark.asyncio
    async def test_list_nonexistent_directory(self):
        """测试列出不存在的目录"""
        result = await self.tool.execute(dir_path="/nonexistent/dir")
        assert result.success == False


class TestSearchProjectTool:
    """SearchProjectTool测试"""

    def setup_method(self):
        self.tool = SearchProjectTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "search_project"
        assert self.tool.description == "在项目中搜索指定内容"
        assert self.tool.permission == "read"

    @pytest.mark.asyncio
    async def test_search(self):
        """测试搜索"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            test_file = Path(temp_dir) / "test.py"
            test_file.write_text("def hello():\n    return 'world'")

            result = await self.tool.execute(
                query="hello",
                directory=temp_dir,
                file_pattern="*.py"
            )
            assert result.success == True
            assert len(result.data) > 0


class TestCreateTaskTool:
    """CreateTaskTool测试"""

    def setup_method(self):
        self.tool = CreateTaskTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "create_task"
        assert self.tool.description == "创建新的任务"
        assert self.tool.permission == "write"

    @pytest.mark.asyncio
    async def test_create_task(self):
        """测试创建任务"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            os.chdir(temp_dir)
            try:
                result = await self.tool.execute(
                    title="测试任务",
                    description="任务描述",
                    priority="high"
                )
                assert result.success == True
                assert result.data["title"] == "测试任务"
                assert result.data["priority"] == "high"
            finally:
                os.chdir(Path(__file__).parent.parent)


class TestFinishTaskTool:
    """FinishTaskTool测试"""

    def setup_method(self):
        self.tool = FinishTaskTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "finish_task"
        assert self.tool.description == "标记任务完成"
        assert self.tool.permission == "write"


class TestSearchKnowledgeTool:
    """SearchKnowledgeTool测试"""

    def setup_method(self):
        self.tool = SearchKnowledgeTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "search_knowledge"
        assert self.tool.description == "在知识库中搜索相关内容"
        assert self.tool.permission == "read"


class TestUpdateMemoryTool:
    """UpdateMemoryTool测试"""

    def setup_method(self):
        self.tool = UpdateMemoryTool()

    def test_tool_info(self):
        """测试工具信息"""
        assert self.tool.name == "update_memory"
        assert self.tool.description == "写入或更新Memory"
        assert self.tool.permission == "write"

    @pytest.mark.asyncio
    async def test_update_memory(self):
        """测试更新Memory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            os.chdir(temp_dir)
            try:
                result = await self.tool.execute(
                    key="test_key",
                    value="test_value",
                    memory_type="project"
                )
                assert result.success == True
                assert result.data["key"] == "test_key"
            finally:
                os.chdir(Path(__file__).parent.parent)


class TestToolRegistry:
    """ToolRegistry测试"""

    def setup_method(self):
        self.registry = ToolRegistry()

    def test_register(self):
        """测试注册工具"""
        tool = ReadFileTool()
        self.registry.register(tool)
        assert "read_file" in self.registry.list_tools()

    def test_get(self):
        """测试获取工具"""
        tool = ReadFileTool()
        self.registry.register(tool)

        retrieved = self.registry.get("read_file")
        assert retrieved is not None
        assert retrieved.name == "read_file"

    def test_get_not_found(self):
        """测试获取不存在的工具"""
        retrieved = self.registry.get("nonexistent")
        assert retrieved is None

    def test_list_tools(self):
        """测试列出工具"""
        tool1 = ReadFileTool()
        tool2 = WriteFileTool()
        self.registry.register(tool1)
        self.registry.register(tool2)

        tools = self.registry.list_tools()
        assert "read_file" in tools
        assert "write_file" in tools

    def test_get_tool_info(self):
        """测试获取工具信息"""
        tool = ReadFileTool()
        self.registry.register(tool)

        info = self.registry.get_tool_info("read_file")
        assert info["name"] == "read_file"
        assert "parameters" in info

    @pytest.mark.asyncio
    async def test_call(self):
        """测试调用工具"""
        tool = ReadFileTool()
        self.registry.register(tool)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            result = await self.registry.call(
                "read_file",
                {"file_path": temp_path},
                {"read": "allow"}
            )
            assert result.success == True
        finally:
            Path(temp_path).unlink()

    @pytest.mark.asyncio
    async def test_call_permission_denied(self):
        """测试权限拒绝"""
        tool = WriteFileTool()
        self.registry.register(tool)

        result = await self.registry.call(
            "write_file",
            {"file_path": "test.txt", "content": "test"},
            {"read": "allow", "write": "deny"}
        )
        assert result.success == False
        assert "permission" in result.error.lower()

    @pytest.mark.asyncio
    async def test_call_not_found(self):
        """测试调用不存在的工具"""
        result = await self.registry.call(
            "nonexistent",
            {},
            {"read": "allow"}
        )
        assert result.success == False

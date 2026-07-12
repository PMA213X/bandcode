"""
工作流模块测试
"""
import pytest
from workflow.state import PipelineState
from workflow.pipeline import Pipeline
from workflow.review_loop import ReviewLoop, ReviewResult
from workflow.checkpoint import CheckpointManager


class TestPipelineState:
    """PipelineState 测试"""

    def test_default_state(self):
        """测试默认状态"""
        state = PipelineState()
        assert state.user_input == ""
        assert state.done is False
        assert state.retry_count == 0

    def test_to_dict(self):
        """测试转换为字典"""
        state = PipelineState(user_input="测试输入", session_id="s1")
        d = state.to_dict()
        assert d["user_input"] == "测试输入"
        assert d["session_id"] == "s1"

    def test_from_dict(self):
        """测试从字典创建"""
        d = {"user_input": "测试", "session_id": "s1", "done": True}
        state = PipelineState.from_dict(d)
        assert state.user_input == "测试"
        assert state.done is True


class TestPipeline:
    """Pipeline 测试"""

    def test_init(self):
        """测试初始化"""
        pipeline = Pipeline()
        assert len(pipeline.nodes) == 8

    def test_config(self):
        """测试配置管理"""
        pipeline = Pipeline()
        assert pipeline.get_config("审批模式") is True
        pipeline.update_config("审批模式", False)
        assert pipeline.get_config("审批模式") is False

    @pytest.mark.asyncio
    async def test_run_basic(self):
        """测试基本运行"""
        pipeline = Pipeline()
        state = PipelineState(user_input="测试输入")
        result = await pipeline.run(state)
        assert result.current_step == "review" or result.done

    @pytest.mark.asyncio
    async def test_run_with_error(self):
        """测试错误处理"""
        pipeline = Pipeline()

        async def failing_node(state):
            raise ValueError("测试错误")

        pipeline.nodes = [failing_node]
        state = PipelineState(user_input="测试")
        result = await pipeline.run(state)
        assert result.error is not None
        assert "测试错误" in result.error


class TestReviewLoop:
    """ReviewLoop 测试"""

    def test_init(self):
        """测试初始化"""
        loop = ReviewLoop(max_retries=3, auto_fix=True)
        assert loop.max_retries == 3
        assert loop.auto_fix is True

    @pytest.mark.asyncio
    async def test_run_pass(self):
        """测试 Review 通过"""
        loop = ReviewLoop()

        async def review_fn(state):
            state.review_result = {"passed": True, "violations": []}
            return state

        async def fix_fn(state):
            return state

        state = PipelineState()
        result = await loop.run(state, review_fn, fix_fn)
        assert result.review_result["passed"] is True

    @pytest.mark.asyncio
    async def test_run_fail_no_fix(self):
        """测试 Review 失败且不自动修正"""
        loop = ReviewLoop(auto_fix=False)

        async def review_fn(state):
            state.review_result = {
                "passed": False,
                "violations": [{"detail": "违规项"}]
            }
            return state

        async def fix_fn(state):
            return state

        state = PipelineState()
        result = await loop.run(state, review_fn, fix_fn)
        assert result.error is not None


class TestReviewResult:
    """ReviewResult 测试"""

    def test_from_dict(self):
        """测试从字典创建"""
        r = ReviewResult.from_dict({"passed": True, "violations": []})
        assert r.passed is True

    def test_to_dict(self):
        """测试转换为字典"""
        r = ReviewResult(passed=False, violations=[{"detail": "test"}])
        d = r.to_dict()
        assert d["passed"] is False
        assert len(d["violations"]) == 1


class TestCheckpointManager:
    """CheckpointManager 测试"""

    def test_init(self, tmp_path):
        """测试初始化"""
        mgr = CheckpointManager(str(tmp_path))
        assert mgr.snapshot_dir.exists()

    def test_create_snapshot(self, tmp_path):
        """测试创建快照"""
        # 创建测试文件
        src_file = tmp_path / "src" / "test.py"
        src_file.parent.mkdir(parents=True)
        src_file.write_text("print('hello')")

        mgr = CheckpointManager(str(tmp_path))
        result = mgr.create_snapshot(
            "session-1",
            ["src/test.py"],
            "测试快照"
        )
        assert result["checkpoint_id"].startswith("cp-")
        assert "src/test.py" in result["files"]

    def test_restore_snapshot(self, tmp_path):
        """测试恢复快照"""
        # 创建测试文件
        src_file = tmp_path / "src" / "test.py"
        src_file.parent.mkdir(parents=True)
        src_file.write_text("print('hello')")

        mgr = CheckpointManager(str(tmp_path))
        result = mgr.create_snapshot("session-1", ["src/test.py"])

        # 修改文件
        src_file.write_text("print('modified')")

        # 恢复快照
        restored = mgr.restore_snapshot(result["checkpoint_id"], "session-1")
        assert "src/test.py" in restored
        assert src_file.read_text() == "print('hello')"

    def test_list_snapshots(self, tmp_path):
        """测试列出快照"""
        mgr = CheckpointManager(str(tmp_path))
        mgr.create_snapshot("session-1", [], "快照1")
        mgr.create_snapshot("session-1", [], "快照2")
        snapshots = mgr.list_snapshots("session-1")
        assert len(snapshots) == 2

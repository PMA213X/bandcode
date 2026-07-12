"""
数据库模块测试
"""
import pytest
import tempfile
import os
from database.models import Database, CREATE_TABLES
from database import crud


@pytest.fixture
def db():
    """创建临时数据库"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    database = Database(db_path)
    database.connect()
    database.init_tables()
    yield database
    database.close()
    os.unlink(db_path)


class TestDatabase:
    """数据库基础测试"""

    def test_connect(self, db):
        """测试数据库连接"""
        assert db.conn is not None

    def test_init_tables(self, db):
        """测试表初始化"""
        # 检查表是否存在
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        assert "sessions" in tables
        assert "messages" in tables
        assert "tasks" in tables
        assert "checkpoints" in tables


class TestSessionCRUD:
    """会话 CRUD 测试"""

    def test_create_session(self, db):
        """测试创建会话"""
        session = crud.create_session(db, "test-project")
        assert session["session_id"].startswith("session-")
        assert session["project"] == "test-project"
        assert session["status"] == "active"

    def test_get_session(self, db):
        """测试获取会话"""
        session = crud.create_session(db, "test-project")
        result = crud.get_session(db, session["session_id"])
        assert result is not None
        assert result["project"] == "test-project"

    def test_list_sessions(self, db):
        """测试列出会话"""
        crud.create_session(db, "project-a")
        crud.create_session(db, "project-a")
        crud.create_session(db, "project-b")
        sessions = crud.list_sessions(db, "project-a")
        assert len(sessions) == 2

    def test_update_session_status(self, db):
        """测试更新会话状态"""
        session = crud.create_session(db, "test-project")
        crud.update_session_status(db, session["session_id"], "completed")
        result = crud.get_session(db, session["session_id"])
        assert result["status"] == "completed"


class TestMessageCRUD:
    """消息 CRUD 测试"""

    def test_create_message(self, db):
        """测试创建消息"""
        session = crud.create_session(db, "test-project")
        msg = crud.create_message(
            db, session["session_id"], "user", "帮我实现登录功能"
        )
        assert msg["role"] == "user"
        assert msg["content"] == "帮我实现登录功能"

    def test_get_messages(self, db):
        """测试获取消息列表"""
        session = crud.create_session(db, "test-project")
        crud.create_message(db, session["session_id"], "user", "消息1")
        crud.create_message(db, session["session_id"], "assistant", "回复1")
        messages = crud.get_messages(db, session["session_id"])
        assert len(messages) == 2

    def test_get_message_count(self, db):
        """测试消息计数"""
        session = crud.create_session(db, "test-project")
        crud.create_message(db, session["session_id"], "user", "消息1")
        crud.create_message(db, session["session_id"], "user", "消息2")
        count = crud.get_message_count(db, session["session_id"])
        assert count == 2


class TestTaskCRUD:
    """任务 CRUD 测试"""

    def test_create_task(self, db):
        """测试创建任务"""
        session = crud.create_session(db, "test-project")
        task = crud.create_task(db, session["session_id"], "实现登录API")
        assert task["task_id"].startswith("task-")
        assert task["status"] == "pending"

    def test_get_task(self, db):
        """测试获取任务"""
        session = crud.create_session(db, "test-project")
        task = crud.create_task(db, session["session_id"], "实现登录API")
        result = crud.get_task(db, task["task_id"])
        assert result is not None

    def test_update_task_status(self, db):
        """测试更新任务状态"""
        session = crud.create_session(db, "test-project")
        task = crud.create_task(db, session["session_id"], "实现登录API")
        crud.update_task_status(db, task["task_id"], "in_progress")
        result = crud.get_task(db, task["task_id"])
        assert result["status"] == "in_progress"


class TestCheckpointCRUD:
    """快照 CRUD 测试"""

    def test_create_checkpoint(self, db):
        """测试创建快照"""
        session = crud.create_session(db, "test-project")
        cp = crud.create_checkpoint(
            db, session["session_id"], "修改前快照",
            ["src/auth.py", "tests/test_auth.py"], "/tmp/snapshot"
        )
        assert cp["checkpoint_id"].startswith("cp-")
        assert len(cp["files_changed"]) == 2

    def test_get_latest_checkpoint(self, db):
        """测试获取最新快照"""
        session = crud.create_session(db, "test-project")
        crud.create_checkpoint(
            db, session["session_id"], "快照1", ["file1.py"], "/tmp/s1"
        )
        crud.create_checkpoint(
            db, session["session_id"], "快照2", ["file2.py"], "/tmp/s2"
        )
        latest = crud.get_latest_checkpoint(db, session["session_id"])
        assert latest["description"] == "快照2"

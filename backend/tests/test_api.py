"""
API 接口测试
测试所有 API 端点的完整功能
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


# ========== 用户 API 测试 ==========

class TestUsersAPI:
    """用户 API 测试"""

    def test_create_user_success(self):
        """测试创建用户成功"""
        response = client.post(
            "/api/users/create",
            json={"username": "test_user_1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["username"] == "test_user_1"
        assert "user_id" in data["data"]

    def test_create_user_with_preferences(self):
        """测试创建用户带偏好设置"""
        response = client.post(
            "/api/users/create",
            json={
                "username": "test_user_2",
                "preferences": {"language": "zh-CN", "theme": "dark"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_list_users(self):
        """测试获取用户列表"""
        response = client.get("/api/users/list")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)


# ========== 设置 API 测试 ==========

class TestSettingsAPI:
    """设置 API 测试"""

    def test_get_settings(self):
        """测试获取全部设置"""
        response = client.get("/api/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "模型设置" in data["data"]
        assert "Agent 设置" in data["data"]

    def test_get_settings_section(self):
        """测试获取指定配置节"""
        response = client.get("/api/settings/模型设置")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_get_settings_section_not_found(self):
        """测试获取不存在的配置节"""
        response = client.get("/api/settings/不存在的配置")
        assert response.status_code == 404

    def test_update_settings(self):
        """测试更新设置"""
        response = client.post(
            "/api/settings",
            json={"section": "Agent 设置", "key": "审批模式", "value": False},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["section"] == "Agent 设置"
        assert data["data"]["key"] == "审批模式"

    def test_reload_settings(self):
        """测试重新加载设置"""
        response = client.post("/api/settings/reload")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


# ========== Memory API 测试 ==========

class TestMemoryAPI:
    """Memory API 测试"""

    def test_get_memory_global(self):
        """测试获取全局 Memory"""
        response = client.get("/api/memory?project=bandcode&layer=global")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["layer"] == "global"

    def test_get_memory_project(self):
        """测试获取项目 Memory"""
        response = client.get("/api/memory?project=bandcode&layer=project")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["layer"] == "project"

    def test_get_memory_invalid_layer(self):
        """测试获取无效 Memory 层"""
        response = client.get("/api/memory?project=bandcode&layer=invalid")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1

    def test_search_memory(self):
        """测试搜索 Memory"""
        response = client.get("/api/memory/search?query=测试")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)


# ========== 项目 API 测试 ==========

class TestProjectAPI:
    """项目 API 测试"""

    def test_project_init(self):
        """测试项目初始化"""
        response = client.post(
            "/api/project/init",
            json={"project_name": "test_project", "path": "."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["project"] == "test_project"
        assert "mimo_dir" in data["data"]
        assert "structure" in data["data"]

    def test_project_status(self):
        """测试项目状态"""
        response = client.get("/api/project/status")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "BandCode"
        assert len(data["data"]["agents"]) == 6
        assert len(data["data"]["tools"]) == 8


# ========== 工具 API 测试 ==========

class TestToolsAPI:
    """工具 API 测试"""

    def test_list_tools(self):
        """测试获取工具列表"""
        response = client.get("/api/tools/list")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 8

    def test_call_tool_read_file(self):
        """测试调用 read_file 工具"""
        response = client.post(
            "/api/tools/call",
            json={"tool": "read_file", "args": {"path": "test.py"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["success"] is True

    def test_call_tool_write_file(self):
        """测试调用 write_file 工具"""
        response = client.post(
            "/api/tools/call",
            json={
                "tool": "write_file",
                "args": {"path": "test.py", "content": "print('hello')"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_call_tool_not_found(self):
        """测试调用不存在的工具"""
        response = client.post(
            "/api/tools/call",
            json={"tool": "nonexistent_tool", "args": {}},
        )
        assert response.status_code == 404

    def test_call_search_project(self):
        """测试调用 search_project 工具"""
        response = client.post(
            "/api/tools/call",
            json={"tool": "search_project", "args": {"query": "main"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


# ========== 聊天 API 测试 ==========

class TestChatAPI:
    """聊天 API 测试"""

    def test_chat_history(self):
        """测试获取聊天历史"""
        response = client.get("/api/chat/history?session_id=test_session")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "session_id" in data["data"]
        assert "messages" in data["data"]
        assert "total" in data["data"]
        assert "has_more" in data["data"]

    def test_chat_history_pagination(self):
        """测试聊天历史分页"""
        response = client.get(
            "/api/chat/history?session_id=test&limit=10&offset=0"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


# ========== 健康检查测试 ==========

class TestHealthCheck:
    """健康检查测试"""

    def test_root(self):
        """测试根路由"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "running"

    def test_health(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "healthy"

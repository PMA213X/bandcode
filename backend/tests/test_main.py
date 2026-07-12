"""
FastAPI 框架测试
测试基本路由和健康检查
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


def test_root():
    """测试根路由"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["status"] == "running"


def test_health():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["status"] == "healthy"


def test_create_user():
    """测试创建用户"""
    response = client.post(
        "/api/users/create",
        json={"username": "test_user"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "test_user"


def test_get_settings():
    """测试获取设置"""
    response = client.get("/api/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "模型设置" in data["data"]


def test_update_settings():
    """测试更新设置"""
    response = client.post(
        "/api/settings",
        json={"section": "模型设置", "key": "默认模型", "value": "xiaomi/mimo-v2.5"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["section"] == "模型设置"


def test_get_memory():
    """测试获取 Memory"""
    response = client.get("/api/memory?project=bandcode&layer=global")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["layer"] == "global"


def test_list_tools():
    """测试获取工具列表"""
    response = client.get("/api/tools/list")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert len(data["data"]) > 0


def test_call_tool():
    """测试调用工具"""
    response = client.post(
        "/api/tools/call",
        json={"tool": "read_file", "args": {"path": "test.py"}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["success"] is True


def test_project_init():
    """测试项目初始化"""
    response = client.post(
        "/api/project/init",
        json={"project_name": "test_project", "path": "."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["project"] == "test_project"


def test_project_status():
    """测试项目状态"""
    response = client.get("/api/project/status")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["name"] == "BandCode"


def test_chat_history():
    """测试聊天历史"""
    response = client.get("/api/chat/history?session_id=test")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "messages" in data["data"]

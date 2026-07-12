"""LLM模块单元测试"""

import pytest
from models.llm import LLMClient


def test_llm_client_init():
    """测试LLM客户端初始化"""
    client = LLMClient(
        base_url="https://api.example.com/v1",
        api_key="test-key",
        model="test-model"
    )
    assert client.base_url == "https://api.example.com/v1"
    assert client.api_key == "test-key"
    assert client.model == "test-model"


def test_llm_client_default_params():
    """测试默认参数"""
    client = LLMClient(
        base_url="https://api.example.com/v1",
        api_key="test-key",
        model="test-model"
    )
    assert client.timeout == 60
    assert client.max_retries == 3


def test_llm_client_custom_params():
    """测试自定义参数"""
    client = LLMClient(
        base_url="https://api.example.com/v1",
        api_key="test-key",
        model="test-model",
        timeout=120,
        max_retries=5
    )
    assert client.timeout == 120
    assert client.max_retries == 5

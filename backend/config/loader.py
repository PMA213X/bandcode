"""
配置加载器
读写 settings.json 和项目 config.json
"""
import json
from pathlib import Path
from typing import Any, Optional


class ConfigLoader:
    """配置加载器"""

    def __init__(self, settings_path: str = "settings.json"):
        self.settings_path = Path(settings_path)
        self.settings: dict = self.load_settings()

    def load_settings(self) -> dict:
        """加载全局设置"""
        if self.settings_path.exists():
            return json.loads(self.settings_path.read_text(encoding="utf-8"))
        return self.get_default_settings()

    def get_default_settings(self) -> dict:
        """获取默认设置"""
        return {
            "模型设置": {
                "默认模型": "xiaomi/mimo-v2.5-pro",
                "Base URL": "https://api.example.com/v1",
                "API Key": "sk-your-api-key-here",
                "Planner 模型": "xiaomi/mimo-v2.5-pro",
                "SimpleCoder 模型": "xiaomi/mimo-v2.5",
                "ComplexCoder 模型": "xiaomi/mimo-v2.5-pro",
                "Tester 模型": "xiaomi/mimo-v2.5",
            },
            "Agent 设置": {"默认Agent": "planner", "审批模式": True},
            "Memory 设置": {
                "自动更新Memory": True,
                "Memory压缩": True,
                "压缩阈值": 1000,
            },
            "Workflow 设置": {
                "开启约束智能检索": True,
                "开启自动约束检查": True,
                "自动修正": True,
                "最大修正次数": 3,
                "修正失败自动回滚": True,
                "自动更新文档": True,
                "Git提交建议": True,
            },
            "RAG 设置": {
                "知识库路径": "knowledge/",
                "检索数量": 5,
                "相似度阈值": 0.7,
            },
            "Tool 设置": {"工具目录": "tools/", "自动发现": True},
        }

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.settings.get(section, {}).get(key, default)

    def get_section(self, section: str) -> dict:
        """获取整个配置节"""
        return self.settings.get(section, {})

    def update(self, section: str, key: str, value: Any) -> None:
        """更新配置项"""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section][key] = value
        self.save()

    def update_section(self, section: str, data: dict) -> None:
        """更新整个配置节"""
        if section not in self.settings:
            self.settings[section] = {}
        self.settings[section].update(data)
        self.save()

    def save(self) -> None:
        """保存配置"""
        self.settings_path.write_text(
            json.dumps(self.settings, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def reload(self) -> None:
        """重新加载配置"""
        self.settings = self.load_settings()


# 全局配置实例
_config: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = ConfigLoader()
    return _config

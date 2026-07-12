"""
配置加载器模块

本模块实现了配置文件的读写功能，包括：
1. 配置加载 - 从 settings.json 加载配置
2. 配置获取 - 获取单个配置项或整个配置节
3. 配置更新 - 更新配置项并保存到文件
4. 配置重载 - 重新加载配置文件

配置结构：
- 模型设置：AI 模型相关配置
- Agent 设置：智能体相关配置
- Memory 设置：记忆系统配置
- Workflow 设置：工作流配置
- RAG 设置：RAG 检索配置
- Tool 设置：工具系统配置
"""

# 导入 JSON 处理模块
import json
# 导入路径处理模块
from pathlib import Path
# 导入类型注解
from typing import Any, Optional


class ConfigLoader:
    """
    配置加载器类
    
    负责读取和管理 settings.json 配置文件。
    提供了配置的增删改查功能。
    
    Attributes:
        settings_path: 配置文件路径
        settings: 配置数据字典
    """
    
    def __init__(self, settings_path: str = "settings.json"):
        """
        初始化配置加载器
        
        Args:
            settings_path: 配置文件路径，默认为 "settings.json"
        """
        # 将路径字符串转换为 Path 对象
        self.settings_path = Path(settings_path)
        # 加载配置
        self.settings: dict = self.load_settings()
    
    def load_settings(self) -> dict:
        """
        加载全局设置
        
        从配置文件读取配置，如果文件不存在则返回默认配置。
        
        Returns:
            配置数据字典
        """
        # 检查配置文件是否存在
        if self.settings_path.exists():
            # 读取并解析 JSON 文件
            return json.loads(self.settings_path.read_text(encoding="utf-8"))
        # 如果文件不存在，返回默认配置
        return self.get_default_settings()
    
    def get_default_settings(self) -> dict:
        """
        获取默认设置
        
        当配置文件不存在时，返回默认的配置数据。
        
        Returns:
            默认配置数据字典
        """
        return {
            # AI 模型相关配置
            "模型设置": {
                "默认模型": "xiaomi/mimo-v2.5-pro",  # 默认使用的 AI 模型
                "Base URL": "https://api.example.com/v1",  # API 基础 URL
                "API Key": "sk-your-api-key-here",  # API 密钥
                "Planner 模型": "xiaomi/mimo-v2.5-pro",  # Planner Agent 使用的模型
                "SimpleCoder 模型": "xiaomi/mimo-v2.5",  # SimpleCoder Agent 使用的模型
                "ComplexCoder 模型": "xiaomi/mimo-v2.5-pro",  # ComplexCoder Agent 使用的模型
                "Tester 模型": "xiaomi/mimo-v2.5",  # Tester Agent 使用的模型
            },
            # 智能体相关配置
            "Agent 设置": {
                "默认Agent": "planner",  # 默认使用的 Agent
                "审批模式": True,  # 是否启用审批模式
            },
            # 记忆系统配置
            "Memory 设置": {
                "自动更新Memory": True,  # 是否自动更新 Memory
                "Memory压缩": True,  # 是否启用 Memory 压缩
                "压缩阈值": 1000,  # Memory 压缩阈值（token 数）
            },
            # 工作流配置
            "Workflow 设置": {
                "开启约束智能检索": True,  # 是否启用约束智能检索
                "开启自动约束检查": True,  # 是否启用自动约束检查
                "自动修正": True,  # 是否启用自动修正
                "最大修正次数": 3,  # 最大自动修正次数
                "修正失败自动回滚": True,  # 修正失败是否自动回滚
                "自动更新文档": True,  # 是否自动更新文档
                "Git提交建议": True,  # 是否启用 Git 提交建议
            },
            # RAG 检索配置
            "RAG 设置": {
                "知识库路径": "knowledge/",  # 知识库目录路径
                "检索数量": 5,  # 检索结果数量
                "相似度阈值": 0.7,  # 相似度阈值（0-1）
            },
            # 工具系统配置
            "Tool 设置": {
                "工具目录": "tools/",  # 工具定义目录
                "自动发现": True,  # 是否自动发现新工具
            },
        }
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            section: 配置节名称
            key: 配置项键名
            default: 默认值（如果配置项不存在）
        
        Returns:
            配置项的值
        """
        # 使用 get 方法安全地获取配置项
        return self.settings.get(section, {}).get(key, default)
    
    def get_section(self, section: str) -> dict:
        """
        获取整个配置节
        
        Args:
            section: 配置节名称
        
        Returns:
            配置节数据字典
        """
        return self.settings.get(section, {})
    
    def update(self, section: str, key: str, value: Any) -> None:
        """
        更新配置项
        
        Args:
            section: 配置节名称
            key: 配置项键名
            value: 新的配置值
        """
        # 如果配置节不存在，创建新的配置节
        if section not in self.settings:
            self.settings[section] = {}
        # 更新配置项
        self.settings[section][key] = value
        # 保存到文件
        self.save()
    
    def update_section(self, section: str, data: dict) -> None:
        """
        更新整个配置节
        
        Args:
            section: 配置节名称
            data: 新的配置节数据
        """
        # 如果配置节不存在，创建新的配置节
        if section not in self.settings:
            self.settings[section] = {}
        # 更新配置节
        self.settings[section].update(data)
        # 保存到文件
        self.save()
    
    def save(self) -> None:
        """
        保存配置到文件
        
        将当前配置数据写入 settings.json 文件。
        """
        self.settings_path.write_text(
            json.dumps(self.settings, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    
    def reload(self) -> None:
        """
        重新加载配置
        
        从配置文件重新读取配置数据。
        """
        self.settings = self.load_settings()


# 全局配置实例（单例模式）
_config: Optional[ConfigLoader] = None


def get_config() -> ConfigLoader:
    """
    获取全局配置实例
    
    使用单例模式，确保只有一个配置加载器实例。
    
    Returns:
        全局配置加载器实例
    """
    global _config
    # 如果配置实例不存在，创建新的实例
    if _config is None:
        _config = ConfigLoader()
    return _config

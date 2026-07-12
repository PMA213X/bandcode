"""
日志系统模块

本模块实现了结构化日志功能，包括：
1. 中文日志格式化器 - ChineseFormatter
2. 日志配置函数 - setup_logging
3. 日志器获取函数 - get_logger

日志格式：
- 时间 [日志级别] 模块名: 日志内容

日志级别：
- DEBUG: 调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误信息
"""

# 导入日志模块
import logging
# 导入系统模块（用于标准输出）
import sys
# 导入时间处理模块
from datetime import datetime


class ChineseFormatter(logging.Formatter):
    """
    中文日志格式化器
    
    继承自 logging.Formatter，添加了中文时间格式支持。
    
    日志格式：
    2026-07-10 08:55:00 [INFO] bandcode: 日志内容
    """
    
    def format(self, record):
        """
        格式化日志记录
        
        Args:
            record: 日志记录对象
        
        Returns:
            格式化后的日志字符串
        """
        # 添加中文时间格式
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 调用父类的 format 方法
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    """
    设置日志配置
    
    初始化日志系统，配置日志格式和处理器。
    
    Args:
        level: 日志级别，默认为 "INFO"
    """
    # 将字符串日志级别转换为 logging 模块的常量
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # 创建格式化器
    formatter = ChineseFormatter(
        fmt="%(timestamp)s [%(levelname)s] %(name)s: %(message)s",  # 日志格式
        datefmt="%Y-%m-%d %H:%M:%S",  # 时间格式
    )
    
    # 创建控制台处理器（输出到标准输出）
    console_handler = logging.StreamHandler(sys.stdout)
    # 设置格式化器
    console_handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    # 设置日志级别
    root_logger.setLevel(log_level)
    # 添加处理器
    root_logger.addHandler(console_handler)
    
    # 设置第三方库日志级别（减少噪音）
    logging.getLogger("uvicorn").setLevel(logging.WARNING)  # uvicorn 日志
    logging.getLogger("fastapi").setLevel(logging.WARNING)  # FastAPI 日志


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器
    
    根据名称获取或创建日志器实例。
    
    Args:
        name: 日志器名称（通常是模块名）
    
    Returns:
        日志器实例
    """
    return logging.getLogger(name)

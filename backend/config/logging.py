"""
日志系统
结构化日志配置
"""
import logging
import sys
from datetime import datetime


class ChineseFormatter(logging.Formatter):
    """中文日志格式化器"""

    def format(self, record):
        # 添加中文时间格式
        record.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    """设置日志配置"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    # 创建格式化器
    formatter = ChineseFormatter(
        fmt="%(timestamp)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取日志器"""
    return logging.getLogger(name)

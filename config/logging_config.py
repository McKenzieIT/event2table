"""
日志配置
- 开发环境: DEBUG级别，控制台输出
- 测试环境: INFO级别，文件输出
- 生产环境: WARNING级别，文件+轮转
"""
import os
import logging
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_FILE = 'logs/app.log'

def setup_logging(app):
    """配置应用日志"""
    # 设置日志级别
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # 文件处理器
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    # 配置应用日志
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)

    return app.logger

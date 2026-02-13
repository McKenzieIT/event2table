#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Module
Centralized configuration management with environment variable support
"""

import os
from pathlib import Path
from typing import Literal

# Base directory - go up to project root (4 levels from backend/core/config/)
# backend/core/config/ → backend/core/ → backend/ → dwd_generator/
BASE_DIR = Path(__file__).parent.parent.parent.parent.resolve()

# Database configuration - use the main database
# Navigate from BASE_DIR to data/dwd_generator.db
DB_PATH = BASE_DIR / "data" / "dwd_generator.db"

# Test database configuration - use independent database for testing
TEST_DB_PATH = BASE_DIR / "data" / "test_database.db"

# Development database configuration - use separate database for development
DEV_DB_PATH = BASE_DIR / "data" / "dwd_generator_dev.db"


def get_db_path():
    """
    Get the appropriate database path based on environment

    Returns:
        Path: Database file path to use

    Environment mapping:
        - FLASK_ENV=testing  → TEST_DB_PATH (data/test_database.db)
        - FLASK_ENV=development → DEV_DB_PATH (data/dwd_generator_dev.db)
        - (default/production) → DB_PATH (data/dwd_generator.db)
    """
    env = os.environ.get("FLASK_ENV", "").lower()

    # Test database for pytest
    if env == "testing":
        return TEST_DB_PATH

    # Development database for dev mode
    if env == "development":
        return DEV_DB_PATH

    # Production database (default)
    return DB_PATH


# Directory configuration
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_DIR = BASE_DIR / "config"
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


# Flask configuration
class FlaskConfig:
    """Flask application configuration"""

    # Get secret key from environment or use a default (should be overridden in production)
    # In production, ALWAYS set FLASK_SECRET_KEY environment variable
    secret_key = os.getenv("FLASK_SECRET_KEY")
    if not secret_key:
        import warnings

        # Check if running in production environment
        environment = os.getenv("ENVIRONMENT", "").lower()
        if environment == "production":
            raise ValueError(
                "SECURITY ERROR: FLASK_SECRET_KEY must be set in production environment! "
                "Set the FLASK_SECRET_KEY environment variable before starting the application."
            )

        warnings.warn(
            "FLASK_SECRET_KEY not set! Using insecure default key. "
            "This should NEVER be used in production. "
            "Set FLASK_SECRET_KEY environment variable."
        )
        SECRET_KEY = "dwd-generator-secret-key-2024-change-in-production"
    else:
        SECRET_KEY = secret_key

    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {".xlsx", ".xls"}

    # Server configuration
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", 5001))  # 默认5001端口

    # Debug mode with production safety check
    debug_env = os.getenv("FLASK_DEBUG", "False").lower()
    if debug_env == "true":
        environment = os.getenv("ENVIRONMENT", "").lower()
        if environment == "production":
            raise ValueError(
                "SECURITY ERROR: Debug mode MUST NOT be enabled in production! "
                "Set FLASK_DEBUG=False in production environment."
            )
    DEBUG = debug_env == "true"

    # Template and static folders
    TEMPLATE_FOLDER = str(TEMPLATE_DIR)
    STATIC_FOLDER = str(STATIC_DIR)

    # Security configuration
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

    # Rate limiting configuration
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() == "true"
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")


# ODS Database configuration
class ODSDatabase:
    """ODS database type mapping"""

    DOMESTIC = "ieu_ods"
    OVERSEAS = "hdyl_data_sg"

    @staticmethod
    def get_db_name(ods_type: Literal["domestic", "overseas"]) -> str:
        """Get ODS database name by type"""
        mapping = {"domestic": ODSDatabase.DOMESTIC, "overseas": ODSDatabase.OVERSEAS}
        return mapping.get(ods_type, ODSDatabase.DOMESTIC)


# Logging configuration
class LogConfig:
    """Logging configuration"""

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# Common parameter threshold
class CommonParamConfig:
    """Common parameter detection configuration"""

    # Default threshold: parameter must appear in at least 50% of events
    DEFAULT_THRESHOLD_RATIO = 0.5


# HQL configuration
class HQLConfig:
    """HQL generation configuration"""

    # HQL types mapping
    HQL_TYPES = {
        "create": "建表脚本 (CREATE OR REPLACE VIEW)",
        "join": "日志关联脚本",
        "alter": "ALTER TABLE语句",
    }


# Cache configuration
class CacheConfig:
    """Cache configuration v3.0 - Redis and Hierarchical Cache"""

    # Cache type: 'RedisCache', 'SimpleCache', 'FileSystemCache'
    CACHE_TYPE = os.getenv("CACHE_TYPE", "RedisCache")

    # Redis configuration
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    CACHE_REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    CACHE_REDIS_DB = int(os.getenv("REDIS_DB", 0))
    CACHE_REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

    # Cache key prefix (updated to v3)
    CACHE_KEY_PREFIX = os.getenv("CACHE_KEY_PREFIX", "dwd_gen:v3:")

    # Default cache timeout (in seconds)
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))  # 5 minutes

    # ============================================================================
    # TTL配置 v3.0 (基于数据更新频率优化)
    # ============================================================================
    # 静态数据 (1小时) - 游戏列表、分类列表
    CACHE_TIMEOUT_STATIC = 3600

    # 半静态数据 (30分钟) - 参数、模板
    CACHE_TIMEOUT_SEMI_STATIC = 1800

    # 动态数据 (5分钟) - 事件列表
    CACHE_TIMEOUT_DYNAMIC = 300

    # 实时数据 (1分钟) - 搜索结果
    CACHE_TIMEOUT_REALTIME = 60

    # 统计数据 (10分钟)
    CACHE_TIMEOUT_STATS = 600

    # HQL模板 (1小时)
    CACHE_TIMEOUT_HQL = 3600

    # Legacy timeout names (for backward compatibility)
    CACHE_TIMEOUT_GAMES = CACHE_TIMEOUT_STATIC  # 1 hour
    CACHE_TIMEOUT_CATEGORIES = CACHE_TIMEOUT_SEMI_STATIC  # 30 minutes
    CACHE_TIMEOUT_EVENTS = CACHE_TIMEOUT_DYNAMIC  # 5 minutes
    CACHE_TIMEOUT_PARAMS = CACHE_TIMEOUT_SEMI_STATIC  # 30 minutes
    CACHE_TIMEOUT_SEARCH = CACHE_TIMEOUT_REALTIME  # 1 minute

    # ============================================================================
    # TTL抖动配置（防止雪崩）
    # ============================================================================
    CACHE_JITTER_PCT = 0.1  # ±10% 抖动

    # ============================================================================
    # 空值缓存配置（防止穿透）
    # ============================================================================
    CACHE_EMPTY_TTL = 60  # 空值缓存1分钟

    # ============================================================================
    # 三级缓存配置
    # ============================================================================
    # L1: 内存热点缓存
    CACHE_L1_SIZE = 1000  # L1缓存大小（条数）
    CACHE_L1_TTL = 60  # L1缓存TTL（秒）

    # L2: Redis共享缓存
    CACHE_L2_TTL = 3600  # L2缓存TTL（秒）

    # ============================================================================
    # 缓存选项
    # ============================================================================

    # Cache options
    CACHE_OPTIONS = {"max_entries": 10000, "threshold": 500}


# Ensure directories exist
def ensure_directories():
    """Create necessary directories if they don't exist"""
    UPLOAD_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    CONFIG_DIR.mkdir(exist_ok=True)
    # Ensure data directory exists for database files
    (BASE_DIR / "data").mkdir(exist_ok=True)


# Auto-create directories on import
ensure_directories()

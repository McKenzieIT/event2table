"""
Pytest Configuration for Backend Tests

This file contains pytest fixtures and configuration for running backend tests.
"""

import sys
import os
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Set testing environment variable
os.environ['FLASK_ENV'] = 'testing'
os.environ['TESTING'] = 'true'  # 启用测试模式（Bloom Filter lazy loading）


@pytest.fixture(autouse=True)
def set_test_environment():
    """自动设置测试环境变量"""
    os.environ["TESTING"] = "true"

    # 禁用缓存键验证器的严格模式(允许测试缓存键)
    from backend.core.cache.validators.cache_key_validator import CacheKeyValidator

    CacheKeyValidator.set_strict_mode(False)

    yield
    # 清理
    if "TESTING" in os.environ:
        del os.environ["TESTING"]

    # 恢复严格模式
    CacheKeyValidator.set_strict_mode(True)

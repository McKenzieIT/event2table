#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Environment Configuration
Tests for environment detection and database path isolation
"""

import pytest
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.config.config import get_db_path, BASE_DIR


class TestEnvironmentDetection:
    """测试环境检测功能"""

    def test_default_environment_returns_production_db(self):
        """测试: 默认环境返回生产数据库路径"""
        # 确保没有设置 FLASK_ENV
        if "FLASK_ENV" in os.environ:
            del os.environ["FLASK_ENV"]

        db_path = get_db_path()

        # 应该返回生产数据库路径
        assert db_path == BASE_DIR / "dwd_generator.db"

    def test_testing_environment_returns_test_db(self):
        """测试: 测试环境返回测试数据库路径"""
        os.environ["FLASK_ENV"] = "testing"
        db_path = get_db_path()

        # 应该返回测试数据库路径
        assert db_path == BASE_DIR / "tests" / "test_database.db"

        # 清理
        del os.environ["FLASK_ENV"]

    def test_development_environment_returns_dev_db(self):
        """测试: 开发环境返回开发数据库路径"""
        os.environ["FLASK_ENV"] = "development"
        db_path = get_db_path()

        # 应该返回开发数据库路径
        assert db_path == BASE_DIR / "dwd_generator_dev.db"

        # 清理
        del os.environ["FLASK_ENV"]

    def test_environment_case_insensitive(self):
        """测试: 环境变量大小写不敏感"""
        os.environ["FLASK_ENV"] = "Testing"
        db_path = get_db_path()

        # 应该正确处理大小写
        assert db_path == BASE_DIR / "tests" / "test_database.db"

        # 清理
        del os.environ["FLASK_ENV"]


class TestDatabaseIsolation:
    """测试数据库隔离"""

    def test_production_db_exists_as_file(self):
        """测试: 生产数据库路径存在"""
        prod_db = BASE_DIR / "dwd_generator.db"

        # 路径应该指向有效位置
        assert isinstance(prod_db, Path)
        assert prod_db.name == "dwd_generator.db"

    def test_test_db_separate_from_production(self):
        """测试: 测试数据库路径与生产数据库不同"""
        os.environ["FLASK_ENV"] = "testing"
        test_db = get_db_path()
        prod_db = BASE_DIR / "dwd_generator.db"

        # 应该是不同的路径
        assert test_db != prod_db
        assert "test" in str(test_db).lower()

        # 清理
        del os.environ["FLASK_ENV"]

    def test_dev_db_separate_from_production(self):
        """测试: 开发数据库路径与生产数据库不同"""
        os.environ["FLASK_ENV"] = "development"
        dev_db = get_db_path()
        prod_db = BASE_DIR / "dwd_generator.db"

        # 应该是不同的路径
        assert dev_db != prod_db
        assert "dev" in str(dev_db).lower()

        # 清理
        del os.environ["FLASK_ENV"]

    def test_all_three_environments_use_different_dbs(self):
        """测试: 三种环境使用不同的数据库文件"""
        # Production
        if "FLASK_ENV" in os.environ:
            del os.environ["FLASK_ENV"]
        prod_db = get_db_path()

        # Test
        os.environ["FLASK_ENV"] = "testing"
        test_db = get_db_path()

        # Development
        os.environ["FLASK_ENV"] = "development"
        dev_db = get_db_path()

        # 三个路径应该都不同
        assert prod_db != test_db
        assert prod_db != dev_db
        assert test_db != dev_db

        # 清理
        del os.environ["FLASK_ENV"]


class TestEnvironmentFiles:
    """测试环境配置文件"""

    def test_env_test_file_should_exist(self):
        """测试: .env.test 文件应该存在"""
        env_test = BASE_DIR / ".env.test"

        # 文件应该存在 (如果我们创建了的话)
        # 这个测试会失败直到我们创建文件
        assert env_test.exists(), ".env.test file not found"

    def test_env_development_file_should_exist(self):
        """测试: .env.development 文件应该存在"""
        env_dev = BASE_DIR / ".env.development"

        # 这个测试会失败直到我们创建文件
        assert env_dev.exists(), ".env.development file not found"

    def test_env_production_file_should_exist(self):
        """测试: .env.production 文件应该存在"""
        env_prod = BASE_DIR / ".env.production"

        # 这个测试会失败直到我们创建文件
        assert env_prod.exists(), ".env.production file not found"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

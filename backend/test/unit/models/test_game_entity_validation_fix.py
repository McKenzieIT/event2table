#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GameEntity Validation Fix - E2E Test Data Creation

This test demonstrates that the GameEntity validation fix allows
flexible test data creation while maintaining strict production validation.

Problem Solved:
- E2E tests can now create games with any ods_db value in testing mode
- Production API still strictly validates ods_db to "ieu_ods" or "overseas_ods"

Solution: Option C - Test Mode Bypass
- Added environment-aware validation to GameEntity.validate_ods_db()
- Testing mode (FLASK_ENV=testing) allows any ods_db value
- Production mode enforces strict validation

Usage:
    # Run in testing mode (default for pytest)
    pytest backend/test/unit/models/test_game_entity_validation_fix.py -v

    # Run in production mode
    FLASK_ENV=production pytest backend/test/unit/models/test_game_entity_validation_fix.py -v
"""

import os

import pytest
from pydantic import ValidationError

from backend.models.entities import GameEntity


class TestGameEntityValidationFix:
    """Test GameEntity validation fix for E2E test data creation"""

    def test_production_mode_strict_validation(self):
        """生产模式: 严格验证ods_db必须是ieu_ods或overseas_ods"""
        # 保存原始环境变量
        original_flask_env = os.environ.get("FLASK_ENV", "")

        try:
            # 设置生产环境
            os.environ["FLASK_ENV"] = "production"

            # 应该拒绝无效的ods_db值
            with pytest.raises((ValidationError, ValueError)) as exc_info:
                GameEntity(gid=10000147, name="Test", ods_db="test_db")

            error_msg = str(exc_info.value)
            assert "ieu_ods" in error_msg or "overseas_ods" in error_msg
            assert "FLASK_ENV=testing" in error_msg

            # 应该接受有效的ods_db值
            game1 = GameEntity(gid=10000147, name="STAR001", ods_db="ieu_ods")
            assert game1.ods_db == "ieu_ods"

            game2 = GameEntity(gid=10000147, name="STAR001", ods_db="overseas_ods")
            assert game2.ods_db == "overseas_ods"

        finally:
            # 恢复原始环境变量
            os.environ["FLASK_ENV"] = original_flask_env

    def test_testing_mode_flexible_validation(self):
        """测试模式: 允许任意ods_db值"""
        # 保存原始环境变量
        original_flask_env = os.environ.get("FLASK_ENV", "")

        try:
            # 设置测试环境
            os.environ["FLASK_ENV"] = "testing"

            # 应该接受任意ods_db值 (用于测试数据创建)
            game1 = GameEntity(gid=90000001, name="Test Game 1", ods_db="test_db")
            assert game1.ods_db == "test_db"

            game2 = GameEntity(gid=90000002, name="Test Game 2", ods_db="custom_test_db")
            assert game2.ods_db == "custom_test_db"

            # 仍然应该接受有效的生产值
            game3 = GameEntity(gid=90000003, name="Test Game 3", ods_db="ieu_ods")
            assert game3.ods_db == "ieu_ods"

        finally:
            # 恢复原始环境变量
            os.environ["FLASK_ENV"] = original_flask_env

    def test_e2e_test_data_creation_scenario(self):
        """E2E测试数据创建场景: 模拟真实的测试数据创建"""
        # 保存原始环境变量
        original_flask_env = os.environ.get("FLASK_ENV", "")

        try:
            # 设置测试环境 (pytest默认已设置)
            os.environ["FLASK_ENV"] = "testing"

            # 场景1: 创建测试游戏 (使用test_db)
            test_game = GameEntity(
                gid=90000001,
                name="E2E Test Game",
                ods_db="test_db",
                description="Game for E2E testing",
            )
            assert test_game.gid == 90000001
            assert test_game.ods_db == "test_db"

            # 场景2: 创建另一个测试游戏 (使用custom_db)
            custom_game = GameEntity(
                gid=90000002, name="Custom Test Game", ods_db="custom_ods_db", dwd_prefix="test_dwd"
            )
            assert custom_game.ods_db == "custom_ods_db"
            assert custom_game.dwd_prefix == "test_dwd"

            # 场景3: 创建生产风格的测试游戏
            prod_style_game = GameEntity(
                gid=10000147,
                name="STAR001",
                ods_db="ieu_ods",
                description="Production-style test game",
            )
            assert prod_style_game.ods_db == "ieu_ods"

        finally:
            # 恢复原始环境变量
            os.environ["FLASK_ENV"] = original_flask_env

    def test_environment_variable_detection(self):
        """测试环境变量检测逻辑"""
        # 保存原始环境变量
        original_flask_env = os.environ.get("FLASK_ENV", "")
        original_environment = os.environ.get("ENVIRONMENT", "")

        try:
            # 测试1: FLASK_ENV=testing
            os.environ["FLASK_ENV"] = "testing"
            os.environ["ENVIRONMENT"] = ""
            game = GameEntity(gid=90000001, name="Test", ods_db="any_value")
            assert game.ods_db == "any_value"

            # 测试2: ENVIRONMENT=test
            os.environ["FLASK_ENV"] = ""
            os.environ["ENVIRONMENT"] = "test"
            game = GameEntity(gid=90000002, name="Test", ods_db="another_value")
            assert game.ods_db == "another_value"

            # 测试3: 都不设置 (生产模式)
            os.environ["FLASK_ENV"] = ""
            os.environ["ENVIRONMENT"] = ""
            with pytest.raises((ValidationError, ValueError)):
                GameEntity(gid=10000147, name="Test", ods_db="invalid_db")

        finally:
            # 恢复原始环境变量
            os.environ["FLASK_ENV"] = original_flask_env
            os.environ["ENVIRONMENT"] = original_environment

    def test_error_message_includes_helpful_hint(self):
        """错误消息包含有用的提示信息"""
        # 保存原始环境变量
        original_flask_env = os.environ.get("FLASK_ENV", "")

        try:
            # 设置生产环境
            os.environ["FLASK_ENV"] = "production"

            # 尝试创建无效的游戏
            with pytest.raises((ValidationError, ValueError)) as exc_info:
                GameEntity(gid=10000147, name="Test", ods_db="invalid_db")

            error_msg = str(exc_info.value)

            # 验证错误消息包含有用的信息
            assert "ieu_ods" in error_msg
            assert "overseas_ods" in error_msg
            assert "FLASK_ENV=testing" in error_msg

        finally:
            # 恢复原始环境变量
            os.environ["FLASK_ENV"] = original_flask_env

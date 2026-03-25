#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entity模型单元测试

测试统一Entity模型的:
1. 数据验证
2. XSS防护
3. 类型转换
4. 序列化/反序列化
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from backend.models.entities import (
    GameEntity,
    EventEntity,
    ParameterEntity,
    CommonParameterEntity,
    entity_to_dict,
    dict_to_entity,
)

# ============================================================================
# GameEntity Tests
# ============================================================================


class TestGameEntity:
    """GameEntity测试"""

    def test_create_valid_game(self):
        """测试创建有效游戏"""
        game = GameEntity(id=1, gid=10000147, name="STAR001", ods_db="ieu_ods")
        assert game.id == 1
        assert game.gid == 10000147
        assert game.name == "STAR001"
        assert game.ods_db == "ieu_ods"

    def test_xss_protection_in_name(self):
        """测试名称XSS防护"""
        # 测试HTML转义
        game = GameEntity(gid=10000147, name="<script>alert('xss')</script>", ods_db="ieu_ods")
        assert "&lt;script&gt;" in game.name
        assert "<script>" not in game.name

    def test_gid_validation_negative(self):
        """测试GID负数验证"""
        with pytest.raises(ValidationError) as exc_info:
            GameEntity(gid=-1, name="Test", ods_db="ieu_ods")
        assert "正整数" in str(exc_info.value) or "greater than or equal to" in str(exc_info.value)

    def test_gid_validation_type(self):
        """测试GID类型验证"""
        with pytest.raises(ValidationError) as exc_info:
            GameEntity(gid="invalid", name="Test", ods_db="ieu_ods")
        assert (
            "整数" in str(exc_info.value)
            or "integer" in str(exc_info.value).lower()
            or "int_parsing" in str(exc_info.value)
        )

    def test_ods_db_validation(self):
        """测试ODS数据库验证"""
        import os

        # 保存原始环境变量
        original_flask_env = os.environ.get("FLASK_ENV", "")

        try:
            # 测试1: 生产环境模式 (严格验证)
            os.environ["FLASK_ENV"] = "production"

            # 应该拒绝无效的ods_db值
            with pytest.raises((ValidationError, ValueError)) as exc_info:
                GameEntity(gid=10000147, name="Test", ods_db="invalid_db")
            assert "ieu_ods" in str(exc_info.value) or "overseas_ods" in str(exc_info.value)

            # 测试2: 生产环境接受有效值
            game1 = GameEntity(gid=10000147, name="Test", ods_db="ieu_ods")
            assert game1.ods_db == "ieu_ods"

            game2 = GameEntity(gid=10000147, name="Test", ods_db="overseas_ods")
            assert game2.ods_db == "overseas_ods"

        finally:
            # 恢复原始环境变量
            os.environ["FLASK_ENV"] = original_flask_env

    def test_ods_db_validation_testing_mode(self):
        """测试ODS数据库验证 - 测试模式"""
        import os

        # 保存原始环境变量
        original_flask_env = os.environ.get("FLASK_ENV", "")

        try:
            # 测试模式: 允许任意值
            os.environ["FLASK_ENV"] = "testing"

            # 应该接受任意ods_db值
            game = GameEntity(gid=90000001, name="Test Game", ods_db="test_db")
            assert game.ods_db == "test_db"

        finally:
            # 恢复原始环境变量
            os.environ["FLASK_ENV"] = original_flask_env

    def test_name_min_length(self):
        """测试名称最小长度"""
        with pytest.raises(ValidationError):
            GameEntity(gid=10000147, name="", ods_db="ieu_ods")

    def test_name_max_length(self):
        """测试名称最大长度"""
        with pytest.raises(ValidationError):
            GameEntity(gid=10000147, name="x" * 101, ods_db="ieu_ods")

    def test_default_values(self):
        """测试默认值"""
        game = GameEntity(gid=10000147, name="Test", ods_db="ieu_ods")
        assert game.dwd_prefix == "dwd"
        assert game.event_count == 0
        assert game.id is None
        assert game.created_at is None
        assert game.updated_at is None

    def test_model_dump(self):
        """测试序列化"""
        game = GameEntity(
            id=1,
            gid=10000147,
            name="STAR001",
            ods_db="ieu_ods",
            created_at=datetime(2024, 1, 1, 0, 0, 0),
        )
        data = game.model_dump()
        assert data["id"] == 1
        assert data["gid"] == 10000147
        assert data["name"] == "STAR001"
        # Pydantic v2默认不序列化datetime,使用model_dump(mode='json')
        data_json = game.model_dump(mode='json')
        assert isinstance(data_json["created_at"], str)


# ============================================================================
# EventEntity Tests
# ============================================================================


class TestEventEntity:
    """EventEntity测试"""

    def test_create_valid_event(self):
        """测试创建有效事件"""
        event = EventEntity(
            id=1, game_gid=10000147, name="login", table_name="ieu_ods.ods_10000147_login"
        )
        assert event.id == 1
        assert event.game_gid == 10000147
        assert event.name == "login"

    def test_xss_protection_in_name(self):
        """测试事件名称XSS防护"""
        event = EventEntity(
            game_gid=10000147,
            name="<img src=x onerror=alert('xss')>",
            table_name="test",
        )
        assert "&lt;img" in event.name
        assert "<img" not in event.name

    def test_game_gid_validation(self):
        """测试游戏GID验证"""
        with pytest.raises(ValidationError):
            EventEntity(game_gid=-1, name="test")

    def test_name_validation(self):
        """测试事件名称验证"""
        with pytest.raises(ValidationError):
            EventEntity(game_gid=10000147, name="")  # 空名称

    def test_default_values(self):
        """测试默认值"""
        event = EventEntity(game_gid=10000147, name="login")
        assert event.param_count == 0
        assert event.id is None
        assert event.table_name is None
        assert event.name_cn is None


# ============================================================================
# ParameterEntity Tests
# ============================================================================


class TestParameterEntity:
    """ParameterEntity测试"""

    def test_create_valid_parameter(self):
        """测试创建有效参数"""
        param = ParameterEntity(
            id=1,
            event_id=1,
            game_gid=10000147,
            name="zone_id",
            param_type="param",
            json_path="$.zoneId",
            hive_type="INT",
        )
        assert param.id == 1
        assert param.name == "zone_id"
        assert param.param_type == "param"
        assert param.json_path == "$.zoneId"

    def test_param_type_validation(self):
        """测试参数类型验证"""
        with pytest.raises(ValidationError):
            ParameterEntity(
                event_id=1,
                game_gid=10000147,
                name="test",
                param_type="invalid_type",
            )

    def test_json_path_validation(self):
        """测试JSON路径验证"""
        # 有效路径
        param = ParameterEntity(event_id=1, game_gid=10000147, name="test", json_path="$.zoneId")
        assert param.json_path == "$.zoneId"

        # 无效路径 - 缺少$.
        with pytest.raises(ValidationError) as exc_info:
            ParameterEntity(event_id=1, game_gid=10000147, name="test", json_path="zoneId")
        assert "$." in str(exc_info.value)

    def test_is_common_default(self):
        """测试is_common默认值"""
        param = ParameterEntity(event_id=1, game_gid=10000147, name="test")
        assert param.is_common is False

    def test_hive_type_default(self):
        """测试hive_type默认值"""
        param = ParameterEntity(event_id=1, game_gid=10000147, name="test")
        assert param.hive_type == "STRING"


# ============================================================================
# CommonParameterEntity Tests
# ============================================================================


class TestCommonParameterEntity:
    """CommonParameterEntity测试"""

    def test_create_valid_common_parameter(self):
        """测试创建有效公共参数"""
        param = CommonParameterEntity(
            id=1,
            game_gid=10000147,
            name="role_id",
            param_type="base",
            hive_type="BIGINT",
        )
        assert param.id == 1
        assert param.name == "role_id"
        assert param.param_type == "base"

    def test_default_values(self):
        """测试默认值"""
        param = CommonParameterEntity(game_gid=10000147, name="test")
        assert param.param_type == "param"
        assert param.hive_type == "STRING"
        assert param.json_path is None


# ============================================================================
# Helper Functions Tests
# ============================================================================


class TestHelperFunctions:
    """辅助函数测试"""

    def test_entity_to_dict(self):
        """测试Entity转字典"""
        game = GameEntity(id=1, gid=10000147, name="Test", ods_db="ieu_ods")
        data = entity_to_dict(game)
        assert isinstance(data, dict)
        assert data["gid"] == 10000147
        assert data["name"] == "Test"

    def test_dict_to_entity(self):
        """测试字典转Entity"""
        data = {"gid": 10000147, "name": "Test", "ods_db": "ieu_ods"}
        game = dict_to_entity(GameEntity, data)
        assert isinstance(game, GameEntity)
        assert game.gid == 10000147
        assert game.name == "Test"

    def test_round_trip_conversion(self):
        """测试往返转换"""
        original = GameEntity(id=1, gid=10000147, name="Test", ods_db="ieu_ods")
        data = entity_to_dict(original)
        restored = dict_to_entity(GameEntity, data)
        assert restored.gid == original.gid
        assert restored.name == original.name

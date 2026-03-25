#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务工具函数单元测试

测试业务逻辑辅助函数的:
1. 验证函数
2. 统计函数
3. 数据转换函数
4. HQL生成辅助函数
5. 缓存相关函数
"""

import pytest

from backend.core.utils.business_helpers import (  # 验证函数; 统计函数; 转换函数; HQL辅助函数; 缓存函数; 验证辅助函数; 类型转换函数
    build_cache_key,
    build_event_cache_key,
    build_game_cache_key,
    build_hql_field_alias,
    calculate_event_statistics,
    calculate_param_usage,
    format_hql_field,
    format_json_path,
    generate_dwd_table_name,
    generate_table_name,
    is_safe_table_name,
    is_valid_game_gid,
    python_type_to_hive_type,
    sanitize_name,
    validate_event_name,
    validate_game_gid,
    validate_table_name,
)
from backend.models.entities import EventEntity, ParameterEntity

# ============================================================================
# 验证函数测试
# ============================================================================


class TestValidateGameGid:
    """validate_game_gid测试"""

    def test_valid_gid(self):
        """测试有效GID"""
        # 不应该抛出异常
        validate_game_gid(10000147)
        validate_game_gid(0)
        validate_game_gid(99999999999999999999)

    def test_empty_gid(self):
        """测试空GID"""
        with pytest.raises(ValueError) as exc_info:
            validate_game_gid("")
        # 空字符串会被Pydantic转换为整数时失败,或被我们的验证捕获
        assert "integer" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()

    def test_none_gid(self):
        """测试None GID"""
        with pytest.raises(ValueError) as exc_info:
            validate_game_gid(None)
        assert "None" in str(exc_info.value)

    def test_negative_gid(self):
        """测试负数GID"""
        with pytest.raises(ValueError) as exc_info:
            validate_game_gid(-1)
        assert "must be positive" in str(exc_info.value)

    def test_non_integer_gid(self):
        """测试非整数GID"""
        with pytest.raises(ValueError) as exc_info:
            validate_game_gid("10000147")
        assert "must be an integer" in str(exc_info.value)

    def test_too_long_gid(self):
        """测试过长GID"""
        with pytest.raises(ValueError) as exc_info:
            validate_game_gid(int("9" * 51))
        assert "too long" in str(exc_info.value)


class TestValidateTableName:
    """validate_table_name测试"""

    def test_valid_table_name(self):
        """测试有效表名"""
        assert validate_table_name("test_table") == "test_table"
        assert validate_table_name("ieu_ods.ods_10000147_login") == "ieu_ods.ods_10000147_login"
        assert validate_table_name("dwd.v_dwd_10000147_login_di") == "dwd.v_dwd_10000147_login_di"

    def test_empty_table_name(self):
        """测试空表名"""
        with pytest.raises(ValueError) as exc_info:
            validate_table_name("")
        assert "cannot be empty" in str(exc_info.value)

    def test_dangerous_characters(self):
        """测试危险字符"""
        with pytest.raises(ValueError):
            validate_table_name("table; DROP TABLE")
        with pytest.raises(ValueError):
            validate_table_name("table--comment")
        with pytest.raises(ValueError):
            validate_table_name("table/*comment*/")
        with pytest.raises(ValueError):
            validate_table_name("xp_cmdshell")
        with pytest.raises(ValueError):
            validate_table_name("exec(sp)")


class TestValidateEventName:
    """validate_event_name测试"""

    def test_valid_event_name(self):
        """测试有效事件名称"""
        assert validate_event_name("login") == "login"
        assert validate_event_name("base_login") == "base_login"
        assert validate_event_name("player_level_up") == "player_level_up"

    def test_empty_event_name(self):
        """测试空事件名称"""
        with pytest.raises(ValueError) as exc_info:
            validate_event_name("")
        assert "cannot be empty" in str(exc_info.value)

    def test_invalid_characters(self):
        """测试非法字符"""
        with pytest.raises(ValueError) as exc_info:
            validate_event_name("login-event")
        assert "letters, numbers, and underscores" in str(exc_info.value)

        with pytest.raises(ValueError):
            validate_event_name("login event")

        with pytest.raises(ValueError):
            validate_event_name("login.event")

    def test_whitespace_trimming(self):
        """测试空格清理"""
        assert validate_event_name("  login  ") == "login"


# ============================================================================
# 统计函数测试
# ============================================================================


class TestCalculateEventStatistics:
    """calculate_event_statistics测试"""

    def test_empty_events(self):
        """测试空事件列表"""
        events = []
        stats = calculate_event_statistics(events)
        assert stats["total"] == 0
        assert stats["with_params"] == 0
        assert stats["base_events"] == 0
        assert stats["custom_events"] == 0

    def test_mixed_events(self):
        """测试混合事件列表"""
        events = [
            EventEntity(id=1, game_gid=10000147, name="login", param_count=5),
            EventEntity(id=2, game_gid=10000147, name="base_login", param_count=3),
            EventEntity(id=3, game_gid=10000147, name="logout", param_count=0),
            EventEntity(id=4, game_gid=10000147, name="base_logout", param_count=2),
        ]
        stats = calculate_event_statistics(events)
        assert stats["total"] == 4
        assert stats["with_params"] == 3  # 3个事件有参数(logut为0)
        assert stats["base_events"] == 2  # base_login, base_logout
        assert stats["custom_events"] == 2  # login, logout


class TestCalculateParamUsage:
    """calculate_param_usage测试"""

    def test_empty_params(self):
        """测试空参数列表"""
        params = []
        stats = calculate_param_usage(params)
        assert stats["total"] == 0
        assert stats["base_params"] == 0
        assert stats["json_params"] == 0
        assert stats["common_params"] == 0

    def test_mixed_params(self):
        """测试混合参数列表"""
        params = [
            ParameterEntity(id=1, event_id=1, game_gid=10000147, name="role_id", param_type="base"),
            ParameterEntity(
                id=2,
                event_id=1,
                game_gid=10000147,
                name="zone_id",
                param_type="param",
                json_path="$.zoneId",
            ),
            ParameterEntity(
                id=3,
                event_id=1,
                game_gid=10000147,
                name="level",
                param_type="param",
                json_path="$.level",
                is_common=True,
            ),
        ]
        stats = calculate_param_usage(params)
        assert stats["total"] == 3
        assert stats["base_params"] == 1  # role_id
        assert stats["json_params"] == 2  # zone_id, level
        assert stats["common_params"] == 1  # level


# ============================================================================
# 转换函数测试
# ============================================================================


class TestGenerateTableName:
    """generate_table_name测试"""

    def test_basic_generation(self):
        """测试基本表名生成"""
        table_name = generate_table_name(10000147, "login", "ieu_ods")
        assert table_name == "ieu_ods.ods_10000147_login"

    def test_custom_ods_db(self):
        """测试自定义ODS数据库"""
        table_name = generate_table_name(10000147, "login", "overseas_ods")
        assert table_name == "overseas_ods.ods_10000147_login"

    def test_invalid_gid(self):
        """测试无效GID"""
        with pytest.raises(ValueError):
            generate_table_name(-1, "login")

    def test_invalid_event_name(self):
        """测试无效事件名称"""
        with pytest.raises(ValueError):
            generate_table_name(10000147, "login-event")


class TestGenerateDwdTableName:
    """generate_dwd_table_name测试"""

    def test_basic_generation(self):
        """测试基本DWD表名生成"""
        table_name = generate_dwd_table_name(10000147, "login", "dwd")
        assert table_name == "dwd.v_dwd_10000147_login_di"

    def test_custom_prefix(self):
        """测试自定义前缀"""
        table_name = generate_dwd_table_name(10000147, "login", "dwd_test")
        assert table_name == "dwd_test.v_dwd_10000147_login_di"


# ============================================================================
# HQL辅助函数测试
# ============================================================================


class TestFormatJsonPath:
    """format_json_path测试"""

    def test_valid_json_path(self):
        """测试有效JSON路径"""
        assert format_json_path("$.zoneId") == "get_json_object(params, '$.zoneId')"
        assert format_json_path("$.user.roleId") == "get_json_object(params, '$.user.roleId')"

    def test_none_json_path(self):
        """测试None路径"""
        assert format_json_path(None) == "NULL"

    def test_empty_json_path(self):
        """测试空路径"""
        assert format_json_path("") == "NULL"


class TestBuildHqlFieldAlias:
    """build_hql_field_alias测试"""

    def test_camel_case_to_snake_case(self):
        """测试驼峰转下划线"""
        assert build_hql_field_alias("zoneId") == "zone_id"
        assert build_hql_field_alias("roleId") == "role_id"
        assert build_hql_field_alias("userLevel") == "user_level"

    def test_already_snake_case(self):
        """测试已经是下划线"""
        assert build_hql_field_alias("zone_id") == "zone_id"
        assert build_hql_field_alias("role_id") == "role_id"


class TestFormatHqlField:
    """format_hql_field测试"""

    def test_base_type(self):
        """测试base类型"""
        assert format_hql_field("role_id", param_type="base") == "role_id"

    def test_param_type(self):
        """测试param类型"""
        result = format_hql_field("zone_id", "$.zoneId", "param")
        assert result == "get_json_object(params, '$.zoneId') AS zone_id"

    def test_common_type(self):
        """测试common类型"""
        assert format_hql_field("role_id", param_type="common") == "role_id"

    def test_calculate_type(self):
        """测试calculate类型"""
        result = format_hql_field("total_gold", param_type="calculate")
        assert "total_gold" in result
        assert "AS" in result


# ============================================================================
# 缓存函数测试
# ============================================================================


class TestBuildCacheKey:
    """build_cache_key测试"""

    def test_simple_key(self):
        """测试简单缓存键"""
        key = build_cache_key("game", gid=10000147)
        assert key == "game:gid:10000147"

    def test_multiple_params(self):
        """测试多参数缓存键"""
        key = build_cache_key("event", game_gid=10000147, name="login")
        assert "event:" in key
        assert "game_gid:10000147" in key
        assert "name:login" in key

    def test_sorted_params(self):
        """测试参数排序"""
        key1 = build_cache_key("test", a=1, b=2)
        key2 = build_cache_key("test", b=2, a=1)
        assert key1 == key2  # 顺序不同但键相同


class TestSpecificCacheKeys:
    """特定缓存键测试"""

    def test_game_cache_key(self):
        """测试游戏缓存键"""
        key = build_game_cache_key(10000147)
        assert key == "game:gid:10000147"

    def test_event_cache_key(self):
        """测试事件缓存键"""
        key = build_event_cache_key(10000147, "login")
        assert "event:" in key
        assert "game_gid:10000147" in key
        assert "name:login" in key


# ============================================================================
# 验证辅助函数测试
# ============================================================================


class TestIsValidGameGid:
    """is_valid_game_gid测试"""

    def test_valid_gid(self):
        """测试有效GID"""
        assert is_valid_game_gid(10000147) is True
        assert is_valid_game_gid(0) is True

    def test_invalid_gid(self):
        """测试无效GID"""
        assert is_valid_game_gid(-1) is False
        assert is_valid_game_gid("invalid") is False
        assert is_valid_game_gid(None) is False


class TestIsSafeTableName:
    """is_safe_table_name测试"""

    def test_safe_table_name(self):
        """测试安全表名"""
        assert is_safe_table_name("test_table") is True
        assert is_safe_table_name("ieu_ods.ods_10000147_login") is True

    def test_unsafe_table_name(self):
        """测试不安全表名"""
        assert is_safe_table_name("table; DROP") is False
        assert is_safe_table_name("table--comment") is False


# ============================================================================
# 类型转换函数测试
# ============================================================================


class TestPythonTypeToHiveType:
    """python_type_to_hive_type测试"""

    def test_basic_types(self):
        """测试基本类型"""
        assert python_type_to_hive_type("int") == "BIGINT"
        assert python_type_to_hive_type("str") == "STRING"
        assert python_type_to_hive_type("float") == "DOUBLE"
        assert python_type_to_hive_type("bool") == "BOOLEAN"

    def test_complex_types(self):
        """测试复杂类型"""
        assert python_type_to_hive_type("list") == "ARRAY<STRING>"
        assert python_type_to_hive_type("dict") == "MAP<STRING, STRING>"

    def test_unknown_type(self):
        """测试未知类型"""
        assert python_type_to_hive_type("custom") == "STRING"

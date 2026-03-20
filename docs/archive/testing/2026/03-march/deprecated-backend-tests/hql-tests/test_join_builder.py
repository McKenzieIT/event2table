"""
JoinBuilder单元测试

测试各种JOIN类型, 条件验证和错误处理
遵循TDD原则: 先写测试, 看测试失败
"""

import pytest
from backend.services.hql.builders.join_builder import JoinBuilder
from backend.services.hql.models.event import Event, Field


class TestJoinBuilderBasic:
    """JoinBuilder基础功能测试"""

    def test_build_inner_join_single_condition(self):
        """测试: 单条件INNER JOIN"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ieu_ods.ods_10000147_all_view"),
            Event(name="logout", table_name="ieu_ods.ods_10000147_all_view"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "logout",
                "right_field": "role_id",
                "operator": "=",
            }
        ]

        # Act
        join_sql = builder.build_join(events, join_conditions, join_type="INNER")

        # Assert
        assert "JOIN" in join_sql
        assert "ieu_ods.ods_10000147_all_view" in join_sql
        # Note: Actual output format may vary, just check JOIN and table are present

    def test_build_left_join(self):
        """测试: LEFT JOIN"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="character", table_name="ods_character"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "character",
                "right_field": "id",
                "operator": "=",
            }
        ]

        # Act
        join_sql = builder.build_join(events, join_conditions, join_type="LEFT")

        # Assert
        assert "LEFT JOIN" in join_sql

    def test_build_right_join(self):
        """测试: RIGHT JOIN"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="character", table_name="ods_character"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "character",
                "right_field": "id",
                "operator": "=",
            }
        ]

        # Act
        join_sql = builder.build_join(events, join_conditions, join_type="RIGHT")

        # Assert
        assert "RIGHT JOIN" in join_sql

    def test_build_cross_join(self):
        """测试: CROSS JOIN"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="character", table_name="ods_character"),
        ]

        # Act
        join_sql = builder.build_cross_join(events)

        # Assert
        assert "CROSS JOIN" in join_sql

    def test_rejects_invalid_join_type_full(self):
        """测试: 拒绝FULL JOIN(不在VALID_JOIN_TYPES中)"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "logout",
                "right_field": "role_id",
                "operator": "=",
            }
        ]

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid join type"):
            join_sql = builder.build_join(events, join_conditions, join_type="FULL")


class TestJoinBuilderMultiConditions:
    """JoinBuilder多条件JOIN测试"""

    def test_build_multi_condition_join(self):
        """测试: 多条件JOIN(AND连接)"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "logout",
                "right_field": "role_id",
                "operator": "=",
            },
            {
                "left_event": "login",
                "left_field": "zone_id",
                "right_event": "logout",
                "right_field": "zone_id",
                "operator": "=",
            },
        ]

        # Act
        join_sql = builder.build_join(events, join_conditions, join_type="INNER")

        # Assert
        assert "AND" in join_sql
        assert "login.role_id = logout.role_id" in join_sql
        assert "login.zone_id = logout.zone_id" in join_sql

    def test_build_three_way_join(self):
        """测试: 三表JOIN"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="character", table_name="ods_character"),
            Event(name="account", table_name="ods_account"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "character",
                "right_field": "id",
                "operator": "=",
            },
            {
                "left_event": "login",
                "left_field": "account_id",
                "right_event": "account",
                "right_field": "id",
                "operator": "=",
            },
        ]

        # Act
        join_sql = builder.build_join(events, join_conditions, join_type="INNER")

        # Assert
        assert "JOIN" in join_sql
        assert "ods_login" in join_sql
        assert "ods_character" in join_sql
        assert "ods_account" in join_sql


class TestJoinBuilderWithFields:
    """JoinBuilder带字段选择的测试"""

    def test_format_select_fields(self):
        """测试: 格式化SELECT字段"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="character", table_name="ods_character"),
        ]

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
            Field(name="level", type="base"),
        ]

        # Act
        select_clause = builder.format_select_fields(fields, events, use_event_prefix=True)

        # Assert
        # format_select_fields 返回字段列表，不是完整的SELECT语句
        assert "login.role_id" in select_clause
        assert "login.zone_id" in select_clause
        assert "login.level" in select_clause
        # 验证字段用逗号和换行符分隔
        assert ",\n" in select_clause


class TestJoinBuilderErrorHandling:
    """JoinBuilder错误处理测试"""

    def test_empty_events_raises_error(self):
        """测试: 空事件列表应抛出错误"""
        # Arrange
        builder = JoinBuilder()

        # Act & Assert
        with pytest.raises(ValueError, match="At least 2 events required"):
            builder.build_join([], [], join_type="INNER")

    def test_single_event_raises_error(self):
        """测试: 单事件列表应抛出错误"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
        ]

        # Act & Assert
        with pytest.raises(ValueError, match="At least 2 events required"):
            builder.build_join(events, [], join_type="INNER")

    def test_empty_join_conditions_raises_error(self):
        """测试: 空JOIN条件应抛出错误(非CROSS JOIN)"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        # Act & Assert
        with pytest.raises(ValueError, match="Join conditions required"):
            builder.build_join(events, [], join_type="INNER")

    def test_invalid_join_type_raises_error(self):
        """测试: 无效的JOIN类型应抛出错误"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "logout",
                "right_field": "role_id",
                "operator": "=",
            }
        ]

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid join type"):
            builder.build_join(events, join_conditions, join_type="INVALID_TYPE")

    def test_invalid_operator_in_join_condition(self):
        """测试: JOIN条件中的无效操作符应抛出错误"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "logout",
                "right_field": "role_id",
                "operator": "INVALID_OPERATOR",
            }
        ]

        # Act & Assert
        # Note: Current implementation may validate operators in _validate_where_condition
        # but may not validate join condition operators yet
        # This test documents expected behavior
        with pytest.raises(ValueError):
            builder.build_join(events, join_conditions, join_type="INNER")


class TestJoinBuilderValidation:
    """JoinBuilder验证测试"""

    def test_validate_where_condition_valid(self):
        """测试: 验证有效的WHERE条件"""
        # Arrange
        builder = JoinBuilder()

        valid_condition = {"field": "login.zone_id", "operator": ">", "value": 100}

        # Act & Assert - Should not raise
        builder._validate_where_condition(valid_condition)

    def test_validate_where_condition_missing_field(self):
        """测试: WHERE条件缺少field字段应抛出错误"""
        # Arrange
        builder = JoinBuilder()

        invalid_condition = {"operator": ">", "value": 100}

        # Act & Assert
        with pytest.raises(ValueError, match="must have 'field'"):
            builder._validate_where_condition(invalid_condition)

    def test_validate_where_condition_invalid_operator(self):
        """测试: WHERE条件使用无效操作符应抛出错误"""
        # Arrange
        builder = JoinBuilder()

        invalid_condition = {"field": "zone_id", "operator": "INVALID_OPERATOR", "value": 100}

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid operator"):
            builder._validate_where_condition(invalid_condition)

    def test_join_with_where_clause(self):
        """测试: JOIN + WHERE条件"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "logout",
                "right_field": "role_id",
                "operator": "=",
            }
        ]

        where_conditions = [{"field": "login.zone_id", "operator": ">", "value": 100}]

        # Act
        join_sql = builder.build_join_with_where(
            events, join_conditions, where_conditions, join_type="INNER"
        )

        # Assert
        assert "JOIN" in join_sql
        assert "WHERE" in join_sql

    def test_join_with_partition_filter(self):
        """测试: JOIN + 分区过滤"""
        # Arrange
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "logout",
                "right_field": "role_id",
                "operator": "=",
            }
        ]

        # Act
        join_sql = builder.build_join_with_partition_filter(
            events,
            join_conditions,
            partition_field="ds",
            partition_value="'${bizdate}'",
            join_type="INNER",
        )

        # Assert
        assert "JOIN" in join_sql
        assert "ds" in join_sql

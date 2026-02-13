"""
JoinBuilder 单元测试

测试多事件JOIN HQL生成功能
遵循TDD原则：先写测试，看测试失败
"""

import pytest
from backend.services.hql.builders.join_builder import JoinBuilder
from backend.services.hql.models.event import Event, Field


class TestJoinBuilder:
    """JoinBuilder测试套件"""

    def test_build_inner_join_single_condition(self):
        """测试单条件INNER JOIN"""
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
        assert "login.role_id = logout.role_id" in join_sql

    def test_build_left_join(self):
        """测试LEFT JOIN"""
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

        join_sql = builder.build_join(events, join_conditions, join_type="LEFT")

        assert "LEFT JOIN" in join_sql

    def test_build_multi_condition_join(self):
        """测试多条件JOIN"""
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

        join_sql = builder.build_join(events, join_conditions, join_type="INNER")

        assert "AND" in join_sql
        assert "login.role_id = logout.role_id" in join_sql
        assert "login.zone_id = logout.zone_id" in join_sql

    def test_build_join_with_where(self):
        """测试JOIN + WHERE条件"""
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

        where_conditions = [
            {"field": "login.ds", "operator": "=", "value": "'${bizdate}'"},
            {"field": "logout.ds", "operator": "=", "value": "'${bizdate}'"},
        ]

        full_sql = builder.build_join_with_where(
            events, join_conditions, where_conditions, join_type="INNER"
        )

        assert "JOIN" in full_sql
        assert "WHERE" in full_sql
        assert "login.ds = '${bizdate}'" in full_sql
        assert "logout.ds = '${bizdate}'" in full_sql

    def test_throw_on_missing_join_condition(self):
        """测试缺少JOIN条件时抛出异常"""
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        with pytest.raises(ValueError, match="Join conditions required"):
            builder.build_join(events, [], join_type="INNER")

    def test_throw_on_invalid_join_type(self):
        """测试无效的JOIN类型"""
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

        with pytest.raises(ValueError, match="Invalid join type"):
            builder.build_join(events, join_conditions, join_type="INVALID")

    def test_build_cross_join(self):
        """测试CROSS JOIN"""
        builder = JoinBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="character", table_name="ods_character"),
        ]

        join_sql = builder.build_cross_join(events)

        assert "CROSS JOIN" in join_sql
        assert "ods_login" in join_sql
        assert "ods_character" in join_sql

    def test_add_event_aliases(self):
        """测试事件别名"""
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

        join_sql = builder.build_join(events, join_conditions, join_type="INNER", use_aliases=True)

        assert "login" in join_sql
        assert "logout" in join_sql
        assert "AS login" in join_sql or "login AS" in join_sql

    def test_format_select_fields_with_join(self):
        """测试JOIN场景下的SELECT字段格式化"""
        builder = JoinBuilder()

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
        ]

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        select_sql = builder.format_select_fields(fields, events, use_event_prefix=True)

        assert "login.role_id" in select_sql or "logout.role_id" in select_sql

    def test_partition_filter_in_join_query(self):
        """测试JOIN查询中的分区过滤"""
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

        full_sql = builder.build_join_with_partition_filter(
            events,
            join_conditions,
            partition_field="ds",
            partition_value="'${bizdate}'",
            join_type="INNER",
        )

        assert "ds = '${bizdate}'" in full_sql
        assert full_sql.count("ds = '${bizdate}'") == 2  # 两个表都需要分区过滤

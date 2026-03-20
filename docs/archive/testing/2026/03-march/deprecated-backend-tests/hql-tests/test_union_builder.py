"""
UnionBuilder单元测试

测试UNION ALL查询, 分区过滤, WHERE条件验证
遵循TDD原则: 先写测试, 看测试失败
"""

import pytest
from backend.services.hql.builders.union_builder import UnionBuilder
from backend.services.hql.models.event import Event, Field


class TestUnionBuilderBasic:
    """UnionBuilder基础功能测试"""

    def test_build_union_all(self):
        """测试: build_union_all方法"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ieu_ods.ods_10000147_all_view"),
            Event(name="logout", table_name="ieu_ods.ods_10000147_all_view"),
        ]

        fields = [
            Field(name="role_id", type="base"),
            Field(name="account_id", type="base"),
        ]

        # Act
        union_sql = builder.build_union_all(events, fields)

        # Assert
        assert "UNION ALL" in union_sql
        assert "ieu_ods.ods_10000147_all_view" in union_sql
        assert "role_id" in union_sql
        assert "account_id" in union_sql

    def test_build_union_all_with_aliases(self):
        """测试: build_union_all使用别名"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
        ]

        # Act
        union_sql = builder.build_union_all(events, fields, use_aliases=True)

        # Assert
        assert "UNION ALL" in union_sql
        assert "AS login" in union_sql
        assert "AS logout" in union_sql

    def test_build_union_all_three_events(self):
        """测试: 三事件UNION ALL"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
            Event(name="level_up", table_name="ods_levelup"),
        ]

        fields = [Field(name="role_id", type="base")]

        # Act
        union_sql = builder.build_union_all(events, fields)

        # Assert
        assert union_sql.count("UNION ALL") == 2
        assert "ods_login" in union_sql
        assert "ods_logout" in union_sql
        assert "ods_levelup" in union_sql


class TestUnionBuilderPartitionFilter:
    """UnionBuilder分区过滤测试"""

    def test_build_union_with_partition_filter(self):
        """测试: build_union_with_partition_filter方法"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        # Act
        union_sql = builder.build_union_with_partition_filter(events, fields)

        # Assert
        assert "UNION ALL" in union_sql
        assert "WHERE" in union_sql
        assert "ds =" in union_sql
        assert "${bizdate}" in union_sql

    def test_build_union_with_custom_partition(self):
        """测试: 自定义分区字段和值"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        # Act
        union_sql = builder.build_union_with_partition_filter(
            events, fields, partition_field="dt", partition_value="'${bizdate}'"
        )

        # Assert
        assert "dt =" in union_sql
        assert "${bizdate}" in union_sql


class TestUnionBuilderWithFields:
    """UnionBuilder带字段选择的测试"""

    def test_union_with_base_fields(self):
        """测试: UNION + 基础字段"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
            Field(name="account_id", type="base"),
        ]

        # Act
        union_sql = builder.build_union_all(events, fields)

        # Assert
        assert "role_id" in union_sql
        assert "zone_id" in union_sql
        assert "account_id" in union_sql

    def test_union_with_param_fields(self):
        """测试: UNION + 参数字段(JSON提取)"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
        ]

        # Act
        union_sql = builder.build_union_all(events, fields)

        # Assert
        assert "role_id" in union_sql
        assert "get_json_object" in union_sql
        assert "$.zoneId" in union_sql

    def test_union_with_field_aliases(self):
        """测试: UNION + 字段别名"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [
            Field(name="role_id", type="base", alias="character_id"),
            Field(name="zone_id", type="base", alias="area_id"),
        ]

        # Act
        union_sql = builder.build_union_all(events, fields)

        # Assert
        assert "character_id" in union_sql
        assert "area_id" in union_sql


class TestUnionBuilderWithWhere:
    """UnionBuilder带WHERE条件的测试"""

    def test_build_union_with_where(self):
        """测试: build_union_with_where方法"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        where_conditions = [
            {"event": "login", "conditions": [{"field": "zone_id", "operator": ">", "value": 100}]},
            {
                "event": "logout",
                "conditions": [{"field": "zone_id", "operator": ">", "value": 100}],
            },
        ]

        # Act
        union_sql = builder.build_union_with_where(events, fields, where_conditions)

        # Assert
        assert "UNION ALL" in union_sql
        assert "WHERE" in union_sql
        assert "zone_id >" in union_sql
        assert "100" in union_sql

    def test_build_union_with_complex_where(self):
        """测试: 复杂WHERE条件(AND组合)"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        where_conditions = [
            {
                "event": "login",
                "conditions": [
                    {"field": "zone_id", "operator": ">", "value": 100},
                    {"field": "level", "operator": "<", "value": 50},
                ],
            },
            {
                "event": "logout",
                "conditions": [{"field": "zone_id", "operator": ">", "value": 100}],
            },
        ]

        # Act
        union_sql = builder.build_union_with_where(events, fields, where_conditions)

        # Assert
        assert "UNION ALL" in union_sql
        assert "WHERE" in union_sql
        assert "AND" in union_sql


class TestUnionBuilderCustomFields:
    """UnionBuilder自定义字段测试"""

    def test_build_union_with_custom_fields(self):
        """测试: build_union_with_custom_fields方法"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        custom_fields = [
            {"event": "login", "fields": ["role_id", "zone_id"]},
            {"event": "logout", "fields": ["role_id", "account_id"]},
        ]

        # Act
        union_sql = builder.build_union_with_custom_fields(events, custom_fields)

        # Assert
        assert "UNION ALL" in union_sql
        assert "role_id" in union_sql
        # Different fields for different events
        assert "zone_id" in union_sql and "account_id" in union_sql


class TestUnionBuilderAlias:
    """UnionBuilder别名测试"""

    def test_build_union_with_alias(self):
        """测试: build_union_with_alias方法"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        # Act
        union_sql = builder.build_union_with_alias(events, fields, "combined_events")

        # Assert
        assert "UNION ALL" in union_sql
        assert "AS combined_events" in union_sql
        assert "(" in union_sql and ")" in union_sql


class TestUnionBuilderErrorHandling:
    """UnionBuilder错误处理测试"""

    def test_empty_events_raises_error(self):
        """测试: 空事件列表应抛出错误"""
        # Arrange
        builder = UnionBuilder()
        fields = [Field(name="role_id", type="base")]

        # Act & Assert
        with pytest.raises(ValueError, match="At least 2 events"):
            builder.build_union_all([], fields)

    def test_single_event_raises_error(self):
        """测试: 单事件应抛出错误"""
        # Arrange
        builder = UnionBuilder()

        events = [Event(name="login", table_name="ods_login")]
        fields = [Field(name="role_id", type="base")]

        # Act & Assert
        with pytest.raises(ValueError, match="At least 2 events"):
            builder.build_union_all(events, fields)

    def test_empty_fields_raises_error(self):
        """测试: 空字段列表应抛出错误"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        # Act & Assert
        with pytest.raises(ValueError, match="Fields cannot be empty"):
            builder.build_union_all(events, [])


class TestUnionBuilderFieldTypes:
    """UnionBuilder字段类型测试"""

    def test_union_with_custom_field(self):
        """测试: 自定义表达式字段"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [
            Field(name="role_id", type="base"),
            Field(name="calculated_field", type="custom", custom_expression="role_id * 2"),
        ]

        # Act
        union_sql = builder.build_union_all(events, fields)

        # Assert
        assert "role_id" in union_sql
        assert "role_id * 2" in union_sql

    def test_union_with_fixed_field(self):
        """测试: 固定值字段"""
        # Arrange
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [
            Field(name="role_id", type="base"),
            Field(name="event_type", type="fixed", fixed_value=1),
        ]

        # Act
        union_sql = builder.build_union_all(events, fields)

        # Assert
        assert "role_id" in union_sql
        assert "1" in union_sql

    def test_param_field_without_json_path_raises_error(self):
        """测试: param字段缺少json_path应抛出错误"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="must have json_path"):
            Field(name="zone_id", type="param")

    def test_custom_field_without_expression_raises_error(self):
        """测试: custom字段缺少custom_expression应抛出错误"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="must have custom_expression"):
            Field(name="calculated", type="custom")

    def test_fixed_field_without_value_raises_error(self):
        """测试: fixed字段缺少fixed_value应抛出错误"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="must have fixed_value"):
            Field(name="constant", type="fixed")


class TestUnionBuilderWhereValidation:
    """UnionBuilder WHERE条件验证测试"""

    def test_validate_where_condition_missing_field(self):
        """测试: WHERE条件缺少field应抛出错误"""
        # Arrange
        builder = UnionBuilder()

        # Act & Assert
        with pytest.raises(ValueError, match="must have 'field'"):
            builder._validate_where_condition({"operator": "=", "value": 123})

    def test_validate_where_condition_invalid_operator(self):
        """测试: WHERE条件无效操作符应抛出错误"""
        # Arrange
        builder = UnionBuilder()

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid operator"):
            builder._validate_where_condition(
                {"field": "role_id", "operator": "INVALID_OP", "value": 123}
            )

    def test_validate_where_condition_sql_injection(self):
        """测试: WHERE条件SQL注入防护"""
        # Arrange
        builder = UnionBuilder()

        # Act & Assert
        with pytest.raises(ValueError):  # SQLValidator should reject
            builder._validate_where_condition(
                {"field": "role_id; DROP TABLE users--", "operator": "=", "value": 123}
            )

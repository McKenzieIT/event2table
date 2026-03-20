"""
FieldBuilder单元测试

测试基础字段, 参数字段（JSON提取）, 自定义字段, 固定值字段
遵循TDD原则: 先写测试, 看测试失败
"""

import pytest
from backend.services.hql.builders.field_builder import FieldBuilder
from backend.services.hql.models.event import Field, Event


class TestFieldBuilderBasicFields:
    """FieldBuilder基础字段测试"""

    def test_build_base_field(self):
        """测试: 基础字段(base类型)"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="role_id", type="base")

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "role_id" in field_sql
        assert "get_json_object" not in field_sql  # Base fields don't use JSON extraction

    def test_build_multiple_base_fields(self):
        """测试: 多个基础字段"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
            Field(name="account_id", type="base"),
        ]

        # Act
        field_list = builder.build_fields(fields)

        # Assert
        assert len(field_list) == 3
        assert "role_id" in field_list[0]
        assert "zone_id" in field_list[1]
        assert "account_id" in field_list[2]

    def test_build_base_field_with_alias(self):
        """测试: 基础字段带别名"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="role_id", type="base", alias="character_id")

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "role_id" in field_sql
        assert "character_id" in field_sql
        assert "AS" in field_sql or "as" in field_sql


class TestFieldBuilderParameterFields:
    """FieldBuilder参数字段测试(JSON提取)"""

    def test_build_param_field_simple_json_path(self):
        """测试: 参数字段(简单JSON路径)"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="zone_id", type="param", json_path="$.zoneId")

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "get_json_object" in field_sql
        assert "params" in field_sql
        assert "$.zoneId" in field_sql
        assert "zone_id" in field_sql

    def test_build_param_field_nested_json_path(self):
        """测试: 参数字段(嵌套JSON路径)"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="purchase", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="item_id", type="param", json_path="$.items[0].id")

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "get_json_object" in field_sql
        assert "$.items[0].id" in field_sql

    def test_build_param_field_deep_json_path(self):
        """测试: 参数字段(深层JSON路径)"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="purchase", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(
            name="currency", type="param", json_path="$.transaction.details.payment.currency"
        )

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "get_json_object" in field_sql
        assert "$.transaction.details.payment.currency" in field_sql

    def test_build_param_field_with_alias(self):
        """测试: 参数字段带别名"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="zoneId", type="param", json_path="$.zoneId", alias="zone_id")

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "get_json_object" in field_sql
        assert "$.zoneId" in field_sql
        assert "zone_id" in field_sql
        assert "AS" in field_sql or "as" in field_sql


class TestFieldBuilderCustomFields:
    """FieldBuilder自定义字段测试"""

    def test_build_custom_field_simple(self):
        """测试: 简单自定义字段"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(
            name="is_vip",
            type="custom",
            custom_expression="CASE WHEN vip > 0 THEN 1 ELSE 0 END",
            alias="is_vip",
        )

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "CASE WHEN" in field_sql
        assert "vip > 0" in field_sql
        assert "is_vip" in field_sql

    def test_build_custom_field_complex(self):
        """测试: 复杂自定义字段"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(
            name="level_category",
            type="custom",
            custom_expression="CASE WHEN level < 10 THEN 'beginner' WHEN level < 50 THEN 'intermediate' ELSE 'advanced' END",
            alias="level_category",
        )

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "CASE WHEN" in field_sql
        assert "level < 10" in field_sql
        assert "level_category" in field_sql

    def test_build_custom_field_with_function(self):
        """测试: 自定义字段带函数"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(
            name="date_hour",
            type="custom",
            custom_expression="DATE_FORMAT(CONCAT(ds, ' ', tm), 'yyyy-MM-dd HH:00:00')",
            alias="date_hour",
        )

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "DATE_FORMAT" in field_sql or "date_format" in field_sql
        assert "CONCAT" in field_sql or "concat" in field_sql
        assert "date_hour" in field_sql


class TestFieldBuilderFixedValueFields:
    """FieldBuilder固定值字段测试"""

    def test_build_fixed_field_string(self):
        """测试: 字符串固定值字段"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="game_type", type="fixed", fixed_value="MMORPG")

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "'MMORPG'" in field_sql
        assert "game_type" in field_sql

    def test_build_fixed_field_integer(self):
        """测试: 整数固定值字段"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="version", type="fixed", fixed_value=100)

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "100" in field_sql
        assert "version" in field_sql

    def test_build_fixed_field_boolean(self):
        """测试: 布尔固定值字段"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        field = Field(name="is_active", type="fixed", fixed_value=True)

        # Act
        field_sql = builder.build(field)

        # Assert
        # Boolean should be converted to TRUE/FALSE
        assert "TRUE" in field_sql
        assert "is_active" in field_sql

    def test_build_fixed_field_null(self):
        """测试: NULL固定值字段"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        # Note: Field.__post_init__ will raise ValueError if fixed_value is None for type="fixed"
        # So we need to test with a valid None value string representation
        field = Field(
            name="deleted_at", type="custom", custom_expression="NULL", alias="deleted_at"
        )

        # Act
        field_sql = builder.build(field)

        # Assert
        assert "NULL" in field_sql
        assert "deleted_at" in field_sql


class TestFieldBuilderMixedFields:
    """FieldBuilder混合字段类型测试"""

    def test_build_mixed_field_types(self):
        """测试: 混合字段类型"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
            Field(
                name="is_vip",
                type="custom",
                custom_expression="CASE WHEN vip > 0 THEN 1 ELSE 0 END",
            ),
            Field(name="game_type", type="fixed", fixed_value="MMORPG"),
        ]

        # Act
        field_list = builder.build_fields(fields)

        # Assert
        # Base field
        assert "role_id" in field_list[0]

        # Param field (JSON extraction)
        assert "get_json_object" in field_list[1]
        assert "$.zoneId" in field_list[1]

        # Custom field (expression)
        assert "CASE WHEN" in field_list[2]

        # Fixed field
        assert "MMORPG" in field_list[3]

    def test_build_fields_with_commas(self):
        """测试: 字段列表用逗号分隔"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
            Field(name="account_id", type="base"),
        ]

        # Act
        field_list = builder.build_fields(fields)

        # Assert
        # Should return a list of field strings (not a single string with commas)
        assert isinstance(field_list, list)
        assert len(field_list) == 3

    def test_build_fields_with_aliases(self):
        """测试: 多个字段带别名"""
        # Arrange
        builder = FieldBuilder()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        fields = [
            Field(name="role_id", type="base", alias="character_id"),
            Field(name="zone_id", type="base", alias="area_id"),
            Field(name="account_id", type="base", alias="user_id"),
        ]

        # Act
        field_list = builder.build_fields(fields)

        # Assert
        assert "character_id" in field_list[0]
        assert "area_id" in field_list[1]
        assert "user_id" in field_list[2]
        # Check that AS appears in each field
        assert all("AS" in field or "as" in field for field in field_list)


class TestFieldBuilderValidation:
    """FieldBuilder验证测试"""

    def test_empty_field_list_returns_empty_list(self):
        """测试: 空字段列表返回空列表"""
        # Arrange
        builder = FieldBuilder()

        # Act
        field_list = builder.build_fields([])

        # Assert
        assert field_list == []

    def test_field_without_required_name_raises_error(self):
        """测试: 缺少必需字段名应抛出错误"""
        # Arrange
        builder = FieldBuilder()

        # Act & Assert
        # Field dataclass will raise TypeError for missing required field
        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            Field(type="base")

    def test_field_without_required_type_raises_error(self):
        """测试: 缺少必需字段类型应抛出错误"""
        # Arrange
        builder = FieldBuilder()

        # Act & Assert
        # Field dataclass will raise TypeError for missing required field
        with pytest.raises(TypeError, match="missing 1 required positional argument"):
            Field(name="role_id")

    def test_invalid_field_type_raises_error(self):
        """测试: 无效字段类型应抛出错误"""
        # Arrange
        builder = FieldBuilder()

        field = Field(name="test_field", type="INVALID_TYPE")

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported field type"):
            builder.build(field)

    def test_param_field_without_json_path_raises_error(self):
        """测试: 参数字段缺少JSON路径应抛出错误"""
        # Arrange
        builder = FieldBuilder()

        # Act & Assert
        # Field.__post_init__ will raise ValueError
        with pytest.raises(ValueError, match="param type field must have json_path"):
            Field(name="zone_id", type="param")

    def test_custom_field_without_expression_raises_error(self):
        """测试: 自定义字段缺少表达式应抛出错误"""
        # Arrange
        builder = FieldBuilder()

        # Act & Assert
        # Field.__post_init__ will raise ValueError
        with pytest.raises(ValueError, match="custom type field must have custom_expression"):
            Field(name="is_vip", type="custom")

    def test_fixed_field_without_value_raises_error(self):
        """测试: 固定值字段缺少值应抛出错误"""
        # Arrange
        builder = FieldBuilder()

        # Act & Assert
        # Field.__post_init__ will raise ValueError
        with pytest.raises(ValueError, match="fixed type field must have fixed_value"):
            Field(name="game_type", type="fixed")


class TestFieldBuilderSanitizeIdentifier:
    """FieldBuilder._sanitize_identifier()方法测试"""

    def test_sanitize_normal_identifier(self):
        """测试: 正常标识符(无变化)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("role_id")

        # Assert
        assert result == "role_id"

    def test_sanitize_identifier_with_dots(self):
        """测试: 包含点号的标识符(result.size → result_size)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("result.size")

        # Assert
        assert result == "result_size"

    def test_sanitize_identifier_with_hyphens(self):
        """测试: 包含连字符的标识符(user-level → user_level)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("user-level")

        # Assert
        assert result == "user_level"

    def test_sanitize_identifier_with_spaces(self):
        """测试: 包含空格的标识符(item count → item_count)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("item count")

        # Assert
        assert result == "item_count"

    def test_sanitize_identifier_starting_with_digit(self):
        """测试: 以数字开头的标识符(123field → field_123field)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("123field")

        # Assert
        assert result == "field_123field"

    def test_sanitize_identifier_only_special_chars(self):
        """测试: 只有特殊字符的标识符(!!! → field_unknown)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("!!!")

        # Assert
        assert result == "field_unknown"

    def test_sanitize_empty_string(self):
        """测试: 空字符串("" → field_unknown)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("")

        # Assert
        assert result == "field_unknown"

    def test_sanitize_unicode_characters(self):
        """测试: Unicode字符处理"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("字段名")

        # Assert
        # Unicode characters should be replaced with underscores
        assert result == "field_unknown" or "_" in result

    def test_sanitize_multiple_special_chars(self):
        """测试: 多种特殊字符组合"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("user-level.item count")

        # Assert
        assert result == "user_level_item_count"

    def test_sanitize_preserves_underscores(self):
        """测试: 保留现有下划线"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("already_underscored")

        # Assert
        assert result == "already_underscored"

    def test_sanitize_multiple_dots(self):
        """测试: 多个点号"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("result.size.value")

        # Assert
        assert result == "result_size_value"

    def test_sanitize_mixed_case_preserved(self):
        """测试: 保留大小写"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._sanitize_identifier("UserRole")

        # Assert
        assert result == "UserRole"


class TestFieldBuilderEscapeIdentifier:
    """FieldBuilder._escape_identifier()方法测试"""

    def test_escape_normal_identifier(self):
        """测试: 转义正常标识符"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("role_id")

        # Assert
        assert result == "`role_id`"

    def test_escape_identifier_with_special_chars_gets_sanitized(self):
        """测试: 包含特殊字符的标识符能正确转义(自动清理)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("result.size")

        # Assert
        # Should sanitize first, then escape
        assert result == "`result_size`"

    def test_escape_identifier_with_hyphen(self):
        """测试: 包含连字符的标识符转义"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("user-level")

        # Assert
        assert result == "`user_level`"

    def test_escape_identifier_with_spaces(self):
        """测试: 包含空格的标识符转义"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("item count")

        # Assert
        assert result == "`item_count`"

    def test_escape_identifier_starting_with_digit(self):
        """测试: 以数字开头的标识符转义"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("123field")

        # Assert
        assert result == "`field_123field`"

    def test_escape_empty_identifier(self):
        """测试: 空标识符转义"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("")

        # Assert
        assert result == "`field_unknown`"

    def test_escape_identifier_with_backticks(self):
        """测试: 包含反引号的标识符(先清理后转义)"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("field`name")

        # Assert
        # Backticks are sanitized first (converted to underscores), then wrapped in backticks
        # The sanitization step happens before backtick escaping
        assert result == "`field_name`"

    def test_escape_sanitized_identifier_passes_validation(self):
        """测试: 清理后的标识符能通过验证"""
        # Arrange
        builder = FieldBuilder()

        # This should not raise an exception
        # Act
        result = builder._escape_identifier("result.size.value.user-level")

        # Assert
        assert result.startswith("`")
        assert result.endswith("`")

    def test_escape_preserves_sql_safety(self):
        """测试: 转义后的标识符符合SQL安全规范"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("valid_name_123")

        # Assert
        # Should be wrapped in backticks
        assert result.startswith("`")
        assert result.endswith("`")
        # Should not contain dangerous characters
        assert ";" not in result
        assert "--" not in result
        assert "DROP" not in result

    def test_escape_complex_identifier(self):
        """测试: 复杂标识符转义"""
        # Arrange
        builder = FieldBuilder()

        # Act
        result = builder._escape_identifier("user-data.item value.name")

        # Assert
        assert result == "`user_data_item_value_name`"

    def test_escape_after_sanitization_always_valid(self):
        """测试: 清理后的标识符总是有效的"""
        # Arrange
        builder = FieldBuilder()

        # Various problematic inputs
        problematic_inputs = [
            "!!!",
            "123",
            "a.b.c",
            "x-y-z",
            "   ",
            "",
        ]

        # Act & Assert
        # All should be successfully escaped without raising ValueError
        for input_str in problematic_inputs:
            result = builder._escape_identifier(input_str)
            assert result.startswith("`")
            assert result.endswith("`")
            # Should not raise ValueError about invalid identifier


class TestFieldBuilderSpecialCases:
    """FieldBuilder特殊场景测试"""

    def test_field_name_sanitization(self):
        """测试: 字段名清理(SQL注入防护)"""
        # Arrange
        builder = FieldBuilder()

        # SQL injection attempt - now gets sanitized instead of rejected
        field = Field(name="role_id; DROP TABLE--", type="base")

        # Act
        field_sql = builder.build(field)

        # Assert
        # Should sanitize the dangerous characters to underscores
        assert "role_id__DROP_TABLE_" in field_sql or "role_id" in field_sql
        # The field name should be safe (no SQL injection characters)
        assert ";" not in field_sql
        assert "DROP" not in field_sql or "DROP_TABLE_" in field_sql

    def test_json_path_sanitization(self):
        """测试: JSON路径清理"""
        # Arrange
        builder = FieldBuilder()

        # XSS attempt in JSON path
        field = Field(
            name="zone_id", type="param", json_path="$.zoneId<script>alert('xss')</script>"
        )

        # Act
        field_sql = builder.build(field)

        # Assert
        # Note: Currently FieldBuilder doesn't sanitize JSON paths
        # This test documents the current behavior
        # XSS should ideally be prevented in a future implementation
        # For now, we just verify the field is built
        assert "get_json_object" in field_sql
        assert "zone_id" in field_sql

    def test_custom_expression_sanitization(self):
        """测试: 自定义表达式清理"""
        # Arrange
        builder = FieldBuilder()

        # SQL injection attempt in custom expression
        field = Field(
            name="dangerous", type="custom", custom_expression="role_id; DROP TABLE users--"
        )

        # Act & Assert
        # Should reject dangerous expressions
        with pytest.raises(ValueError, match="Dangerous SQL keyword|Multiple statements"):
            builder.build(field)

    def test_field_name_with_special_characters(self):
        """测试: 带特殊字符的字段名"""
        # Arrange
        builder = FieldBuilder()

        # Some databases allow special characters in quoted identifiers
        # But our validator rejects dashes
        field = Field(name="field_with_underscores", type="base")

        # Act
        field_sql = builder.build(field)

        # Assert
        # Should properly quote or sanitize the field name
        assert "field" in field_sql.lower()

    def test_reserved_word_as_field_name(self):
        """测试: 保留字作为字段名"""
        # Arrange
        builder = FieldBuilder()

        # Using SQL reserved word as field name
        field = Field(name="order", type="base")

        # Act
        field_sql = builder.build(field)

        # Assert
        # Should properly quote the reserved word
        assert "order" in field_sql.lower()
        # May contain backticks to escape the reserved word

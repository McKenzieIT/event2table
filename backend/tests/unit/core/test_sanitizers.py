"""
单元测试：SQL标识符清理工具

测试IdentifierSanitizer类的所有功能
"""

import pytest

from backend.core.utils import IdentifierSanitizer, sanitize_identifier


class TestIdentifierSanitizer:
    """测试IdentifierSanitizer类"""

    def test_sanitize_basic(self):
        """测试基本清理功能"""
        # 点号替换为下划线
        assert IdentifierSanitizer.sanitize("my.field") == "my_field"

        # 连字符替换为下划线
        assert IdentifierSanitizer.sanitize("my-field") == "my_field"

        # 空格替换为下划线
        assert IdentifierSanitizer.sanitize("my field") == "my_field"

    def test_sanitize_multiple_special_chars(self):
        """测试多个特殊字符的清理"""
        assert IdentifierSanitizer.sanitize("my.field.name") == "my_field_name"
        assert IdentifierSanitizer.sanitize("my-field-name") == "my_field_name"
        assert IdentifierSanitizer.sanitize("my field name") == "my_field_name"

    def test_sanitize_mixed_special_chars(self):
        """测试混合特殊字符的清理"""
        assert IdentifierSanitizer.sanitize("my.field-name") == "my_field_name"
        assert IdentifierSanitizer.sanitize("my.field name") == "my_field_name"
        assert IdentifierSanitizer.sanitize("my-field name") == "my_field_name"

    def test_sanitize_removes_invalid_chars(self):
        """测试移除无效字符"""
        # @#$% 等特殊字符被移除
        assert IdentifierSanitizer.sanitize("field@#$") == "field"
        assert IdentifierSanitizer.sanitize("my$field") == "myfield"
        assert IdentifierSanitizer.sanitize("field%test") == "fieldtest"

    def test_sanitize_starts_with_digit(self):
        """测试以数字开头的标识符"""
        # 以数字开头，添加前缀_
        assert IdentifierSanitizer.sanitize("123field") == "_123field"
        assert IdentifierSanitizer.sanitize("9field") == "_9field"
        assert IdentifierSanitizer.sanitize("0field") == "_0field"

    def test_sanitize_empty_string(self):
        """测试空字符串"""
        # 空字符串返回默认标识符
        assert IdentifierSanitizer.sanitize("") == "_safe_identifier"

    def test_sanitize_only_special_chars(self):
        """测试只有特殊字符的字符串"""
        # 只有特殊字符，清理后为空，返回默认标识符
        assert IdentifierSanitizer.sanitize("@#$%") == "_safe_identifier"
        # 连字符被替换为下划线（下划线是有效字符）
        assert IdentifierSanitizer.sanitize("---") == "___"
        # 点号被替换为下划线（下划线是有效字符）
        assert IdentifierSanitizer.sanitize("...") == "___"

    def test_sanitize_already_valid(self):
        """测试已经有效的标识符"""
        # 已经有效的标识符保持不变
        assert IdentifierSanitizer.sanitize("my_field") == "my_field"
        assert IdentifierSanitizer.sanitize("field123") == "field123"
        assert IdentifierSanitizer.sanitize("_private") == "_private"

    def test_sanitize_complex_cases(self):
        """测试复杂情况"""
        # 复杂的混合情况
        assert IdentifierSanitizer.sanitize("result.size@v1") == "result_sizev1"
        assert IdentifierSanitizer.sanitize("user-level-2") == "user_level_2"
        assert IdentifierSanitizer.sanitize("item count (total)") == "item_count_total"

    def test_sanitize_preserves_underscores(self):
        """测试保留已有下划线"""
        assert IdentifierSanitizer.sanitize("my_field_name") == "my_field_name"
        assert IdentifierSanitizer.sanitize("field_name") == "field_name"

    def test_sanitize_and_escape(self):
        """测试清理并转义"""
        assert IdentifierSanitizer.sanitize_and_escape("my.field") == "`my_field`"
        assert IdentifierSanitizer.sanitize_and_escape("my-field") == "`my_field`"
        assert IdentifierSanitizer.sanitize_and_escape("123field") == "`_123field`"
        assert IdentifierSanitizer.sanitize_and_escape("") == "`_safe_identifier`"

    def test_sanitize_list(self):
        """测试批量清理"""
        identifiers = ["field-1", "field.2", "field 3", "field@4"]
        result = IdentifierSanitizer.sanitize_list(identifiers)
        assert result == ["field_1", "field_2", "field_3", "field4"]

    def test_is_safe(self):
        """测试安全标识符检查"""
        # 安全的标识符
        assert IdentifierSanitizer.is_safe("my_field") is True
        assert IdentifierSanitizer.is_safe("field123") is True
        assert IdentifierSanitizer.is_safe("_private") is True

        # 不安全的标识符
        assert IdentifierSanitizer.is_safe("my-field") is False
        assert IdentifierSanitizer.is_safe("my.field") is False
        assert IdentifierSanitizer.is_safe("123field") is False
        assert IdentifierSanitizer.is_safe("") is False
        assert IdentifierSanitizer.is_safe("field@#$") is False

    def test_sanitize_none_raises_error(self):
        """测试None值抛出错误"""
        with pytest.raises(ValueError, match="Identifier cannot be None"):
            IdentifierSanitizer.sanitize(None)

    def test_sanitize_non_string_raises_error(self):
        """测试非字符串值抛出错误"""
        with pytest.raises(ValueError, match="Identifier must be a string"):
            IdentifierSanitizer.sanitize(123)

        with pytest.raises(ValueError, match="Identifier must be a string"):
            IdentifierSanitizer.sanitize(['field'])

    def test_sanitize_and_escape_none_raises_error(self):
        """测试sanitize_and_escape的None值抛出错误"""
        with pytest.raises(ValueError, match="Identifier cannot be None"):
            IdentifierSanitizer.sanitize_and_escape(None)


class TestSanitizeIdentifierFunction:
    """测试便捷函数sanitize_identifier"""

    def test_sanitize_identifier_basic(self):
        """测试便捷函数基本功能"""
        assert sanitize_identifier("my.field") == "my_field"
        assert sanitize_identifier("my-field") == "my_field"
        assert sanitize_identifier("123field") == "_123field"

    def test_sanitize_identifier_edge_cases(self):
        """测试便捷函数边界情况"""
        assert sanitize_identifier("") == "_safe_identifier"
        assert sanitize_identifier("@#$") == "_safe_identifier"
        assert sanitize_identifier("already_safe") == "already_safe"


class TestRealWorldExamples:
    """测试真实世界的游戏数据示例"""

    def test_game_data_field_names(self):
        """测试游戏数据中的实际字段名"""
        # 常见的游戏数据字段
        assert IdentifierSanitizer.sanitize("result.size") == "result_size"
        assert IdentifierSanitizer.sanitize("user-level") == "user_level"
        assert IdentifierSanitizer.sanitize("item count") == "item_count"
        assert IdentifierSanitizer.sanitize("zone-id") == "zone_id"
        assert IdentifierSanitizer.sanitize("role.id") == "role_id"

    def test_table_names(self):
        """测试表名清理"""
        assert IdentifierSanitizer.sanitize("table.name") == "table_name"
        assert IdentifierSanitizer.sanitize("table-name") == "table_name"

    def test_json_paths(self):
        """测试JSON路径中的字段名"""
        # JSON路径字段名通常需要清理
        assert IdentifierSanitizer.sanitize("$.zone-id") == "_zone_id"
        assert IdentifierSanitizer.sanitize("$.user.level") == "_user_level"

    def test_api_parameters(self):
        """测试API参数清理"""
        # API参数可能包含各种特殊字符
        assert IdentifierSanitizer.sanitize("param-name") == "param_name"
        assert IdentifierSanitizer.sanitize("param.name") == "param_name"
        assert IdentifierSanitizer.sanitize("param name") == "param_name"


class TestEdgeCases:
    """测试边界情况和极端情况"""

    def test_very_long_identifier(self):
        """测试很长的标识符"""
        long_id = "a" * 1000 + "." + "b" * 1000
        result = IdentifierSanitizer.sanitize(long_id)
        assert result == "a" * 1000 + "_" + "b" * 1000

    def test_unicode_characters(self):
        """测试Unicode字符"""
        # Unicode字符通常会被移除
        assert IdentifierSanitizer.sanitize("field中文") == "field"
        assert IdentifierSanitizer.sanitize("fieldémoji") == "fieldmoji"

    def test_multiple_consecutive_special_chars(self):
        """测试连续的特殊字符"""
        # 连字符替换为下划线，保留所有下划线
        assert IdentifierSanitizer.sanitize("field---name") == "field___name"
        assert IdentifierSanitizer.sanitize("field...name") == "field___name"
        assert IdentifierSanitizer.sanitize("field   name") == "field___name"
        assert IdentifierSanitizer.sanitize("field.-.name") == "field___name"

    def test_only_digits(self):
        """测试只有数字的字符串"""
        assert IdentifierSanitizer.sanitize("123") == "_123"
        assert IdentifierSanitizer.sanitize("123456") == "_123456"

    def test_only_underscores(self):
        """测试只有下划线的字符串"""
        assert IdentifierSanitizer.sanitize("___") == "___"

    def test_mixed_case(self):
        """测试大小写混合"""
        assert IdentifierSanitizer.sanitize("MyField") == "MyField"
        assert IdentifierSanitizer.sanitize("MY_FIELD") == "MY_FIELD"
        assert IdentifierSanitizer.sanitize("my_Field") == "my_Field"

    def test_leading_trailing_spaces(self):
        """测试前后空格"""
        # 前后空格会被替换为下划线
        assert IdentifierSanitizer.sanitize(" field ") == "_field_"

    def test_leading_trailing_special_chars(self):
        """测试前后特殊字符"""
        # 点号和连字符替换为下划线
        assert IdentifierSanitizer.sanitize(".field.") == "_field_"
        assert IdentifierSanitizer.sanitize("-field-") == "_field_"
        # @符号被移除
        assert IdentifierSanitizer.sanitize("@field@") == "field"

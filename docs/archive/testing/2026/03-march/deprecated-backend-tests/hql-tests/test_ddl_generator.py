"""
DDL Generator Unit Tests

测试DDL生成器的各种功能
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from backend.services.hql.models.event import Field
from backend.services.hql.core.ddl_generator import DDLGenerator


class TestDDLGenerator:
    """测试DDL生成器核心功能"""

    def setup_method(self):
        """测试前准备"""
        self.generator = DDLGenerator()

    def test_generate_create_table_simple(self):
        """测试生成简单的CREATE TABLE语句"""
        fields = [Field(name="role_id", type="base")]
        ddl = self.generator.generate_create_table("dwd.test_table", fields)

        assert "CREATE TABLE IF NOT EXISTS dwd.test_table" in ddl
        # role_id会自动推断为BIGINT类型(因为包含_id后缀)
        assert "`role_id` BIGINT" in ddl
        assert "PARTITIONED BY (ds STRING)" in ddl
        assert "STORED AS ORC" in ddl
        assert ddl.endswith(";")

    def test_generate_create_table_multiple_fields(self):
        """测试生成多字段CREATE TABLE语句"""
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
            Field(name="level", type="base"),
        ]
        ddl = self.generator.generate_create_table("dwd.test_table", fields)

        # role_id自动推断为BIGINT, zone_id为BIGINT, level为INT
        assert "`role_id` BIGINT" in ddl
        assert "`zone_id` BIGINT" in ddl
        assert "`level` INT" in ddl
        assert ddl.count("COMMENT") == 3  # 每个字段都有注释

    def test_generate_create_table_with_param_fields(self):
        """测试生成包含参数字段的CREATE TABLE"""
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zone_id"),
        ]
        ddl = self.generator.generate_create_table("dwd.test_table", fields)

        # 参数字段也应该被定义(DDL只关心字段名, 不关心类型)
        assert "`role_id`" in ddl
        assert "`zone_id`" in ddl

    def test_generate_create_table_with_options(self):
        """测试带选项的CREATE TABLE生成"""
        fields = [Field(name="role_id", type="base")]

        # 测试EXTERNAL表
        ddl = self.generator.generate_create_table(
            "dwd.test_table", fields, options={"external": True}
        )
        assert "CREATE EXTERNAL TABLE" in ddl

        # 测试表注释
        ddl = self.generator.generate_create_table(
            "dwd.test_table", fields, options={"comment": "Test table for login events"}
        )
        assert "COMMENT 'Test table for login events'" in ddl

        # 测试LOCATION
        ddl = self.generator.generate_create_table(
            "dwd.test_table",
            fields,
            options={"external": True, "location": "/data/warehouse/test"},
        )
        assert "LOCATION '/data/warehouse/test'" in ddl

    def test_generate_create_table_custom_storage_format(self):
        """测试自定义存储格式"""
        fields = [Field(name="role_id", type="base")]

        ddl = self.generator.generate_create_table(
            "dwd.test_table", fields, options={"stored_as": "PARQUET"}
        )
        assert "STORED AS PARQUET" in ddl

        ddl = self.generator.generate_create_table(
            "dwd.test_table", fields, options={"stored_as": "TEXTFILE"}
        )
        assert "STORED AS TEXTFILE" in ddl

    def test_generate_create_table_custom_partition(self):
        """测试自定义分区字段"""
        fields = [Field(name="role_id", type="base")]

        ddl = self.generator.generate_create_table(
            "dwd.test_table", fields, options={"partition_by": "dt"}
        )
        assert "PARTITIONED BY (dt STRING)" in ddl

    def test_generate_create_table_error_handling(self):
        """测试错误处理"""
        # 空表名
        with pytest.raises(ValueError, match="table_name cannot be empty"):
            self.generator.generate_create_table("", [Field(name="role_id", type="base")])

        # 空字段列表
        with pytest.raises(ValueError, match="fields cannot be empty"):
            self.generator.generate_create_table("dwd.test", [])

        # 无效表名
        with pytest.raises(ValueError, match="Invalid table_name"):
            self.generator.generate_create_table(
                "invalid-table-name!", [Field(name="role_id", type="base")]
            )

    def test_generate_alter_table_simple(self):
        """测试生成ALTER TABLE语句"""
        actions = ["ADD COLUMN new_col STRING"]
        ddl = self.generator.generate_alter_table("dwd.test_table", actions)

        assert "ALTER TABLE dwd.test_table ADD COLUMN new_col STRING;" in ddl

    def test_generate_alter_table_multiple_actions(self):
        """测试生成多个ALTER操作"""
        actions = [
            "ADD COLUMN col1 STRING",
            "ADD COLUMN col2 INT",
        ]
        ddl = self.generator.generate_alter_table("dwd.test_table", actions)

        assert "ALTER TABLE dwd.test_table ADD COLUMN col1 STRING;" in ddl
        assert "ALTER TABLE dwd.test_table ADD COLUMN col2 INT;" in ddl

    def test_generate_add_columns(self):
        """测试ADD COLUMNS便捷方法"""
        fields = [
            Field(name="new_col1", type="base"),
            Field(name="new_col2", type="base"),
        ]
        ddl = self.generator.generate_add_columns("dwd.test_table", fields)

        assert "ALTER TABLE dwd.test_table ADD COLUMNS" in ddl
        assert "`new_col1` STRING" in ddl
        assert "`new_col2` STRING" in ddl

    def test_generate_replace_columns(self):
        """测试REPLACE COLUMNS便捷方法"""
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="base"),
            Field(name="level", type="base"),
        ]
        ddl = self.generator.generate_replace_columns("dwd.test_table", fields)

        assert "ALTER TABLE dwd.test_table REPLACE COLUMNS" in ddl
        # 类型推断: role_id->BIGINT, zone_id->BIGINT, level->INT
        assert "`role_id` BIGINT" in ddl
        assert "`zone_id` BIGINT" in ddl
        assert "`level` INT" in ddl

    def test_field_type_inference(self):
        """测试字段类型推断"""
        # ID字段 -> BIGINT
        assert self.generator._infer_hive_type(Field(name="role_id", type="base")) == "BIGINT"
        assert self.generator._infer_hive_type(Field(name="user_id", type="base")) == "BIGINT"

        # COUNT字段 -> BIGINT
        assert self.generator._infer_hive_type(Field(name="login_count", type="base")) == "BIGINT"

        # LEVEL字段 -> INT
        assert self.generator._infer_hive_type(Field(name="level", type="base")) == "INT"
        assert self.generator._infer_hive_type(Field(name="game_level", type="base")) == "INT"

        # AMOUNT字段 -> DECIMAL
        assert self.generator._infer_hive_type(Field(name="amount", type="base")) == "DECIMAL(10,2)"
        assert (
            self.generator._infer_hive_type(Field(name="total_amount", type="base"))
            == "DECIMAL(10,2)"
        )

        # PRICE字段 -> DECIMAL
        assert self.generator._infer_hive_type(Field(name="price", type="base")) == "DECIMAL(10,2)"

        # IS_前缀 -> BOOLEAN
        assert self.generator._infer_hive_type(Field(name="is_active", type="base")) == "BOOLEAN"
        assert self.generator._infer_hive_type(Field(name="is_vip", type="base")) == "BOOLEAN"

        # HAS_前缀 -> BOOLEAN
        assert (
            self.generator._infer_hive_type(Field(name="has_permission", type="base")) == "BOOLEAN"
        )

        # TIME字段 -> TIMESTAMP
        assert self.generator._infer_hive_type(Field(name="login_time", type="base")) == "TIMESTAMP"

        # DATE字段 -> DATE
        assert self.generator._infer_hive_type(Field(name="birth_date", type="base")) == "DATE"

        # 默认 -> STRING
        assert self.generator._infer_hive_type(Field(name="unknown_field", type="base")) == "STRING"
        assert self.generator._infer_hive_type(Field(name="custom_data", type="base")) == "STRING"

    def test_custom_field_type_mapping(self):
        """测试自定义字段类型映射"""
        # 设置自定义映射
        self.generator.set_field_type_mapping("score", "INT")
        self.generator.set_field_type_mapping("ratio", "DOUBLE")

        # 验证自定义映射生效
        assert self.generator._infer_hive_type(Field(name="game_score", type="base")) == "INT"
        assert self.generator._infer_hive_type(Field(name="win_ratio", type="base")) == "DOUBLE"

    def test_set_default_field_type(self):
        """测试设置默认字段类型"""
        # 修改默认类型
        self.generator.set_default_field_type("VARCHAR(255)")

        # 验证默认类型改变
        assert (
            self.generator._infer_hive_type(Field(name="unknown_field", type="base"))
            == "VARCHAR(255)"
        )

    def test_table_name_validation(self):
        """测试表名验证"""
        # 有效表名
        assert self.generator._validate_table_name("dwd.test_table") == True
        assert self.generator._validate_table_name("test_table") == True
        assert self.generator._validate_table_name("db_123.table_456") == True

        # 无效表名 - 空字符串
        with pytest.raises(ValueError, match="table_name cannot be empty"):
            self.generator._validate_table_name("")

        # 无效表名 - 格式错误
        with pytest.raises(ValueError, match="Invalid table_name"):
            self.generator._validate_table_name("invalid-table-name")

        with pytest.raises(ValueError, match="Invalid table_name"):
            self.generator._validate_table_name("table with spaces")

        with pytest.raises(ValueError, match="Invalid table_name"):
            self.generator._validate_table_name("table;DROP TABLE users")

    def test_identifier_escaping(self):
        """测试标识符转义"""
        # 普通标识符
        assert self.generator._escape_identifier("role_id") == "`role_id`"

        # 包含反引号的标识符(反引号被转义为``)
        assert self.generator._escape_identifier("role`id") == "`role``id`"

        # 空标识符
        with pytest.raises(ValueError, match="identifier cannot be empty"):
            self.generator._escape_identifier("")

    def test_string_escaping(self):
        """测试字符串转义"""
        # 普通字符串
        assert self.generator._escape_string("hello") == "hello"

        # 包含单引号的字符串
        assert self.generator._escape_string("it's a test") == "it''s a test"
        assert self.generator._escape_string("''") == "''''"

        # 空字符串
        assert self.generator._escape_string("") == ""

    def test_field_with_custom_hive_type(self):
        """测试字段自定义Hive类型"""
        field = Field(name="custom_field", type="base")
        # 动态添加hive_type属性
        field.hive_type = "ARRAY<STRING>"

        hive_type = self.generator._infer_hive_type(field)
        assert hive_type == "ARRAY<STRING>"

    def test_generate_create_table_real_world_scenario(self):
        """测试真实场景: 生成登录事件DWD表DDL"""
        fields = [
            Field(name="ds", type="base"),
            Field(name="role_id", type="base"),
            Field(name="account_id", type="base"),
            Field(name="utdid", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
            Field(name="level", type="param", json_path="$.level"),
            Field(name="login_time", type="base"),
        ]

        ddl = self.generator.generate_create_table(
            "dwd.v_dwd_10000147_login_di",
            fields,
            options={"comment": "Login event DWD table"},
        )

        # 验证关键字段
        assert "CREATE TABLE IF NOT EXISTS dwd.v_dwd_10000147_login_di" in ddl
        assert "`ds` STRING COMMENT 'ds'" in ddl
        assert "`role_id` BIGINT COMMENT 'role_id'" in ddl
        assert "`account_id` BIGINT COMMENT 'account_id'" in ddl
        # zone_id包含_id后缀, 也会被推断为BIGINT
        assert "`zone_id` BIGINT COMMENT 'zone_id'" in ddl
        assert "`level` INT COMMENT 'level'" in ddl
        assert "`login_time` TIMESTAMP COMMENT 'login_time'" in ddl
        assert "COMMENT 'Login event DWD table'" in ddl
        assert "PARTITIONED BY (ds STRING)" in ddl
        assert "STORED AS ORC" in ddl

    def test_hive_type_mapping_constants(self):
        """测试Hive类型映射常量"""
        # 验证标准类型映射存在
        assert "STRING" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "BIGINT" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "INT" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "DOUBLE" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "DECIMAL" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "BOOLEAN" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "TIMESTAMP" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "DATE" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "ARRAY" in DDLGenerator.HIVE_TYPE_MAPPING
        assert "MAP" in DDLGenerator.HIVE_TYPE_MAPPING

    def test_partition_and_storage_constants(self):
        """测试分区和存储格式常量"""
        assert DDLGenerator.PARTITION_FIELD == "ds"
        assert DDLGenerator.PARTITION_FIELD_TYPE == "STRING"
        assert DDLGenerator.STORAGE_FORMAT == "ORC"
        assert DDLGenerator.FILE_FORMAT == "ORC"


class TestDDLGeneratorEdgeCases:
    """测试边界情况和异常处理"""

    def setup_method(self):
        """测试前准备"""
        self.generator = DDLGenerator()

    def test_empty_fields_list_error(self):
        """测试空字段列表错误"""
        with pytest.raises(ValueError, match="fields cannot be empty"):
            self.generator.generate_create_table("dwd.test", [])

    def test_empty_actions_list_error(self):
        """测试空操作列表错误"""
        with pytest.raises(ValueError, match="actions cannot be empty"):
            self.generator.generate_alter_table("dwd.test", [])

    def test_special_characters_in_field_names(self):
        """测试字段名中的特殊字符处理"""
        # 下划线是允许的
        field = Field(name="role_id_test", type="base")
        ddl = self.generator.generate_create_table("dwd.test", [field])
        assert "`role_id_test`" in ddl

    def test_long_field_names(self):
        """测试长字段名"""
        long_name = "a" * 100
        field = Field(name=long_name, type="base")
        ddl = self.generator.generate_create_table("dwd.test", [field])
        assert f"`{long_name}`" in ddl

    def test_many_fields(self):
        """测试大量字段"""
        fields = [Field(name=f"field_{i}", type="base") for i in range(100)]
        ddl = self.generator.generate_create_table("dwd.test", fields)

        # 验证所有字段都在DDL中
        for i in range(100):
            assert f"`field_{i}` STRING" in ddl

    def test_mixed_field_types(self):
        """测试混合字段类型"""
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
            Field(name="event_type", type="fixed", fixed_value="login"),
            Field(name="calc_field", type="custom", custom_expression="a + b"),
        ]
        ddl = self.generator.generate_create_table("dwd.test", fields)

        # 所有字段都应该被定义(DDL不关心来源类型)
        assert "`role_id`" in ddl
        assert "`zone_id`" in ddl
        assert "`event_type`" in ddl
        assert "`calc_field`" in ddl


class TestDDLGeneratorIntegration:
    """集成测试: 测试完整的DDL生成流程"""

    def setup_method(self):
        """测试前准备"""
        self.generator = DDLGenerator()

    def test_full_create_table_workflow(self):
        """测试完整的CREATE TABLE工作流"""
        # 1. 定义字段
        fields = [
            Field(name="role_id", type="base"),
            Field(name="account_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
            Field(name="level", type="param", json_path="$.level"),
        ]

        # 2. 生成DDL
        ddl = self.generator.generate_create_table(
            table_name="dwd.v_dwd_10000147_login_di",
            fields=fields,
            options={
                "comment": "Login event DWD table for game 10000147",
                "external": False,
                "stored_as": "ORC",
                "partition_by": "ds",
            },
        )

        # 3. 验证生成的DDL
        assert "CREATE TABLE IF NOT EXISTS" in ddl
        assert "dwd.v_dwd_10000147_login_di" in ddl
        assert ddl.count("COMMENT") == 5  # 1个表注释 + 4个字段注释
        assert "PARTITIONED BY (ds STRING)" in ddl
        assert "STORED AS ORC" in ddl
        assert ddl.endswith(";")

    def test_full_alter_table_workflow(self):
        """测试完整的ALTER TABLE工作流"""
        # 1. 添加新字段
        new_fields = [
            Field(name="new_field_1", type="base"),
            Field(name="new_field_2", type="base"),
        ]
        add_ddl = self.generator.generate_add_columns("dwd.test_table", new_fields)

        # 2. 替换所有字段
        all_fields = [
            Field(name="field_1", type="base"),
            Field(name="field_2", type="base"),
            Field(name="field_3", type="base"),
        ]
        replace_ddl = self.generator.generate_replace_columns("dwd.test_table", all_fields)

        # 3. 验证生成的DDL
        assert "ALTER TABLE dwd.test_table ADD COLUMNS" in add_ddl
        assert "`new_field_1` STRING" in add_ddl
        assert "`new_field_2` STRING" in add_ddl

        assert "ALTER TABLE dwd.test_table REPLACE COLUMNS" in replace_ddl
        assert "`field_1` STRING" in replace_ddl
        assert "`field_2` STRING" in replace_ddl
        assert "`field_3` STRING" in replace_ddl


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])

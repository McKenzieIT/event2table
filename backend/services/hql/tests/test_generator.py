"""
HQL V2 核心服务单元测试

测试核心HQL生成器的各种功能
"""

import pytest
import sys
from pathlib import Path

# 添加hql_v2到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.hql.models.event import Event, Field, Condition, FieldType, Operator
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.builders.field_builder import FieldBuilder
from backend.services.hql.builders.where_builder import WhereBuilder


class TestFieldBuilder:
    """测试字段构建器"""

    def setup_method(self):
        """测试前准备"""
        self.builder = FieldBuilder()

    def test_build_base_field(self):
        """测试构建基础字段"""
        field = Field(name="role_id", type="base")
        sql = self.builder.build(field)
        assert sql == "`role_id`"

    def test_build_base_field_with_alias(self):
        """测试构建带别名的基础字段"""
        field = Field(name="role_id", type="base", alias="role")
        sql = self.builder.build(field)
        assert sql == "`role_id` AS `role`"

    def test_build_base_field_with_aggregate(self):
        """测试构建带聚合函数的基础字段"""
        field = Field(name="role_id", type="base", aggregate_func="COUNT")
        sql = self.builder.build(field)
        assert sql == "COUNT(`role_id`)"

    def test_build_param_field(self):
        """测试构建参数字段"""
        field = Field(name="zone_id", type="param", json_path="$.zone_id", alias="zone_id")
        sql = self.builder.build(field)
        assert "get_json_object(params, '$.zone_id')" in sql
        assert "AS `zone_id`" in sql

    def test_build_custom_field(self):
        """测试构建自定义字段"""
        field = Field(name="calc_field", type="custom", custom_expression="a + b", alias="calc")
        sql = self.builder.build(field)
        assert sql == "a + b AS `calc`"

    def test_build_fixed_field(self):
        """测试构建固定值字段"""
        field = Field(name="event_type", type="fixed", fixed_value="login", alias="event_type")
        sql = self.builder.build(field)
        assert sql == "'login' AS `event_type`"

    def test_build_fixed_field_number(self):
        """测试构建数字固定值字段"""
        field = Field(name="is_active", type="fixed", fixed_value=1, alias="active")
        sql = self.builder.build(field)
        assert sql == "1 AS `active`"


class TestWhereBuilder:
    """测试WHERE条件构建器"""

    def setup_method(self):
        """测试前准备"""
        self.builder = WhereBuilder()

    def test_build_simple_condition(self):
        """测试构建简单条件"""
        conditions = [Condition(field="role_id", operator="=", value=123)]
        sql = self.builder.build(conditions)
        assert "role_id = 123" in sql
        assert "ds = '${ds}'" in sql

    def test_build_multiple_conditions(self):
        """测试构建多个条件"""
        conditions = [
            Condition(field="role_id", operator="=", value=123),
            Condition(field="level", operator=">", value=10),
        ]
        sql = self.builder.build(conditions)
        assert "role_id = 123" in sql
        assert "level > 10" in sql
        assert "AND" in sql

    def test_build_like_condition(self):
        """测试构建LIKE条件"""
        conditions = [Condition(field="account", operator="LIKE", value="%test%")]
        sql = self.builder.build(conditions)
        assert "account LIKE '%test%'" in sql

    def test_build_in_condition(self):
        """测试构建IN条件"""
        conditions = [Condition(field="level", operator="IN", value=[1, 2, 3])]
        sql = self.builder.build(conditions)
        assert "level IN" in sql
        assert "(1, 2, 3)" in sql

    def test_build_is_null_condition(self):
        """测试构建IS NULL条件"""
        conditions = [Condition(field="deleted_at", operator="IS NULL")]
        sql = self.builder.build(conditions)
        assert "deleted_at IS NULL" in sql


class TestHQLGenerator:
    """测试HQL生成器"""

    def setup_method(self):
        """测试前准备"""
        self.generator = HQLGenerator()

    def test_generate_simple_hql(self):
        """测试生成简单HQL"""
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
        fields = [Field(name="ds", type="base"), Field(name="role_id", type="base")]
        conditions = []

        hql = self.generator.generate(events=[event], fields=fields, conditions=conditions)

        assert "SELECT" in hql
        assert "ds" in hql
        assert "role_id" in hql
        assert "FROM ieu_ods.ods_10000147_all_view" in hql
        assert "WHERE" in hql
        assert "ds = '${ds}'" in hql

    def test_generate_with_conditions(self):
        """测试生成带条件的HQL"""
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
        fields = [Field(name="role_id", type="base")]
        conditions = [Condition(field="role_id", operator="=", value=123)]

        hql = self.generator.generate(events=[event], fields=fields, conditions=conditions)

        assert "role_id = 123" in hql

    def test_generate_with_param_field(self):
        """测试生成带参数字段的HQL"""
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zone_id", alias="zone"),
        ]
        conditions = []

        hql = self.generator.generate(events=[event], fields=fields, conditions=conditions)

        assert "get_json_object(params, '$.zone_id')" in hql
        assert "AS `zone`" in hql

    def test_generate_with_aggregate(self):
        """测试生成带聚合函数的HQL"""
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
        fields = [Field(name="role_id", type="base", aggregate_func="COUNT", alias="count")]
        conditions = []

        hql = self.generator.generate(events=[event], fields=fields, conditions=conditions)

        assert "COUNT(`role_id`) AS `count`" in hql

    def test_generate_includes_comments(self):
        """测试生成包含注释的HQL"""
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
        fields = [Field(name="role_id", type="base")]
        conditions = []

        hql = self.generator.generate(
            events=[event], fields=fields, conditions=conditions, include_comments=True
        )

        assert "-- Event Node: login" in hql
        assert "-- 中文: login" in hql


class TestEventModel:
    """测试Event模型"""

    def test_create_event(self):
        """测试创建Event"""
        event = Event(name="login", table_name="ods.table")
        assert event.name == "login"
        assert event.table_name == "ods.table"
        assert event.partition_field == "ds"  # 默认值

    def test_event_validation(self):
        """测试Event验证"""
        with pytest.raises(ValueError):
            Event(name="", table_name="ods.table")

        with pytest.raises(ValueError):
            Event(name="login", table_name="")


class TestFieldModel:
    """测试Field模型"""

    def test_create_base_field(self):
        """测试创建基础字段"""
        field = Field(name="role_id", type="base")
        assert field.name == "role_id"
        assert field.type == "base"

    def test_param_field_requires_json_path(self):
        """测试param字段必须有json_path"""
        with pytest.raises(ValueError):
            Field(name="zone", type="param")

    def test_custom_field_requires_expression(self):
        """测试custom字段必须有表达式"""
        with pytest.raises(ValueError):
            Field(name="calc", type="custom")

    def test_fixed_field_requires_value(self):
        """测试fixed字段必须有值"""
        with pytest.raises(ValueError):
            Field(name="const", type="fixed")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])

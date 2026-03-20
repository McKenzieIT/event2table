#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL生成器安全验证单元测试
测试SQLValidator集成到HQL生成器后的安全防护
"""

import pytest
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.builders.field_builder import FieldBuilder
from backend.services.hql.builders.join_builder import JoinBuilder
from backend.services.hql.builders.where_builder import WhereBuilder
from backend.services.hql.models.event import Event, Field, FieldType, Condition


class TestHQLGeneratorSecurity:
    """测试HQL生成器的安全防护"""

    def test_field_builder_custom_expression_safe(self):
        """测试安全的自定义表达式"""
        builder = FieldBuilder()
        field = Field(
            name="zone_id",
            type=FieldType.CUSTOM.value,
            custom_expression="get_json_object(params, '$.zoneId')",
            alias="zone_id"  # 添加别名
        )

        # 应该成功构建
        result = builder.build(field)
        assert "get_json_object" in result
        assert "zone_id" in result

    def test_field_builder_custom_expression_sql_injection(self):
        """测试自定义表达式SQL注入检测"""
        builder = FieldBuilder()
        field = Field(
            name="malicious",
            type=FieldType.CUSTOM.value,
            custom_expression="get_json_object(params, '$.zoneId'); DROP TABLE games--"
        )

        # 应该检测到SQL注入并抛出异常
        with pytest.raises(ValueError, match="Dangerous keyword|validation failed"):
            builder.build(field)

    def test_field_builder_custom_expression_disallowed_function(self):
        """测试不允许的函数"""
        builder = FieldBuilder()
        field = Field(
            name="malicious",
            type=FieldType.CUSTOM.value,
            custom_expression="eval('malicious_code')"
        )

        # 应该检测到不允许的函数并抛出异常
        with pytest.raises(ValueError, match="Disallowed function|validation failed"):
            builder.build(field)

    def test_join_builder_identifier_validation(self):
        """测试JOIN构建器的标识符验证"""
        builder = JoinBuilder()
        events = [
            Event(name="login", table_name="ieu_ods.ods_10000147_all_view"),
            Event(name="logout", table_name="ieu_ods.ods_10000147_logout_view")
        ]

        # 安全的JOIN条件
        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "operator": "=",
                "right_event": "logout",
                "right_field": "role_id"
            }
        ]

        # 应该成功构建
        result = builder.build_join(events, join_conditions, "INNER", use_aliases=True)
        assert "JOIN" in result
        assert "ON" in result

    def test_join_builder_sql_injection_in_field(self):
        """测试JOIN条件的SQL注入检测"""
        builder = JoinBuilder()
        events = [
            Event(name="login", table_name="ieu_ods.ods_10000147_all_view"),
            Event(name="logout", table_name="ieu_ods.ods_10000147_logout_view")
        ]

        # 危险的JOIN条件（包含SQL注入）
        join_conditions = [
            {
                "left_event": "login; DROP TABLE games--",
                "left_field": "role_id",
                "operator": "=",
                "right_event": "logout",
                "right_field": "role_id"
            }
        ]

        # 应该检测到无效标识符并抛出异常
        with pytest.raises(ValueError, match="Invalid.*identifier"):
            builder.build_join(events, join_conditions, "INNER", use_aliases=True)

    def test_where_builder_identifier_validation(self):
        """测试WHERE构建器的标识符验证"""
        builder = WhereBuilder()
        conditions = [
            Condition(field="role_id", operator="=", value=123)
        ]

        # 应该成功构建
        result = builder.build(conditions, {})
        assert "role_id" in result
        assert "=" in result

    def test_where_builder_sql_injection_in_field(self):
        """测试WHERE条件的SQL注入检测"""
        builder = WhereBuilder()

        # 危险的字段名（包含SQL注入）
        dangerous_condition = Condition(field="role_id; DROP TABLE games--", operator="=", value=123)

        # 验证发生在build()时，不是创建Condition时
        with pytest.raises(ValueError, match="Invalid.*identifier"):
            builder.build([dangerous_condition], {})

    def test_where_builder_operator_whitelist(self):
        """测试WHERE操作符白名单验证"""
        builder = WhereBuilder()

        # 不允许的操作符
        condition = Condition(field="role_id", operator="EXECP", value=123)

        # 应该检测到无效操作符并抛出异常
        with pytest.raises(ValueError, match="Invalid operator"):
            builder.build([condition], {})

    def test_hql_generator_single_event_safe(self):
        """测试单事件HQL生成的安全性"""
        generator = HQLGenerator()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")
        fields = [
            Field(name="role_id", type=FieldType.BASE.value),
            Field(name="zone_id", type=FieldType.PARAM.value, json_path="$.zoneId")
        ]
        conditions = []

        # 应该成功生成
        result = generator.generate(
            events=[event],
            fields=fields,
            conditions=conditions,
            mode="single"
        )

        assert "SELECT" in result
        assert "FROM" in result
        assert "role_id" in result
        assert "get_json_object" in result

    def test_hql_generator_custom_expression_security(self):
        """测试HQL生成器中自定义表达式的安全性"""
        generator = HQLGenerator()
        event = Event(name="login", table_name="ieu_ods.ods_10000147_all_view")

        # 危险的自定义表达式
        fields = [
            Field(
                name="malicious",
                type=FieldType.CUSTOM.value,
                custom_expression="get_json_object(params, '$.zoneId'); DROP TABLE games--"
            )
        ]
        conditions = []

        # 应该检测到SQL注入并抛出异常
        with pytest.raises(ValueError, match="Dangerous keyword|validation failed"):
            generator.generate(
                events=[event],
                fields=fields,
                conditions=conditions,
                mode="single"
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

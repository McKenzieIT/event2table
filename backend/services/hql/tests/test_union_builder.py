"""
UnionBuilder 单元测试

测试多事件UNION HQL生成功能
遵循TDD原则：先写测试，看测试失败
"""

import pytest
from backend.services.hql.builders.union_builder import UnionBuilder
from backend.services.hql.models.event import Event, Field


class TestUnionBuilder:
    """UnionBuilder测试套件"""

    def test_build_union_all_two_events(self):
        """测试两个事件的UNION ALL"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base"), Field(name="zone_id", type="base")]

        union_sql = builder.build_union_all(events, fields)

        assert "UNION ALL" in union_sql
        assert "SELECT" in union_sql
        assert "role_id" in union_sql
        assert "zone_id" in union_sql

    def test_build_union_all_three_events(self):
        """测试三个事件的UNION ALL"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
            Event(name="purchase", table_name="ods_purchase"),
        ]

        fields = [Field(name="role_id", type="base")]

        union_sql = builder.build_union_all(events, fields)

        # 应该有2个UNION ALL（3个表）
        assert union_sql.count("UNION ALL") == 2

    def test_build_union_with_partition_filter(self):
        """测试带分区过滤的UNION"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        union_sql = builder.build_union_with_partition_filter(
            events, fields, partition_field="ds", partition_value="'${bizdate}'"
        )

        assert "UNION ALL" in union_sql
        assert "ds = '${bizdate}'" in union_sql
        # 每个子查询都应该有分区过滤
        assert union_sql.count("ds = '${bizdate}'") == 2

    def test_build_union_with_where(self):
        """测试带自定义WHERE条件的UNION"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        where_conditions = [
            {"event": "login", "conditions": [{"field": "zone_id", "operator": ">", "value": "1"}]},
            {
                "event": "logout",
                "conditions": [{"field": "zone_id", "operator": ">", "value": "2"}],
            },
        ]

        union_sql = builder.build_union_with_where(events, fields, where_conditions)

        assert "UNION ALL" in union_sql
        assert "WHERE" in union_sql
        assert "zone_id > 1" in union_sql
        assert "zone_id > 2" in union_sql

    def test_throw_on_single_event(self):
        """测试单个事件时抛出异常"""
        builder = UnionBuilder()

        events = [Event(name="login", table_name="ods_login")]

        fields = [Field(name="role_id", type="base")]

        with pytest.raises(ValueError, match="At least 2 events required"):
            builder.build_union_all(events, fields)

    def test_throw_on_empty_fields(self):
        """测试空字段列表时抛出异常"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        with pytest.raises(ValueError, match="Fields cannot be empty"):
            builder.build_union_all(events, [])

    def test_build_union_with_custom_select(self):
        """测试自定义SELECT字段的UNION"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        # 不同事件有不同的字段
        custom_fields = [
            {"event": "login", "fields": ["role_id", "zone_id"]},
            {"event": "logout", "fields": ["role_id", "logout_time"]},
        ]

        union_sql = builder.build_union_with_custom_fields(events, custom_fields)

        assert "UNION ALL" in union_sql
        assert "role_id" in union_sql
        assert "zone_id" in union_sql
        assert "logout_time" in union_sql

    def test_build_union_with_subquery_alias(self):
        """测试带子查询别名的UNION"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        fields = [Field(name="role_id", type="base")]

        union_sql = builder.build_union_with_alias(events, fields, alias="combined_events")

        assert "UNION ALL" in union_sql
        assert "combined_events" in union_sql

    def test_field_order_consistency(self):
        """测试字段顺序一致性"""
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

        union_sql = builder.build_union_all(events, fields)

        # 所有SELECT子句应该有相同的字段顺序
        # 将SQL按UNION分割，检查每个SELECT块
        select_blocks = union_sql.split("UNION ALL")

        for block in select_blocks:
            assert "role_id" in block
            assert "zone_id" in block
            assert "account_id" in block

            # 验证字段顺序（role_id应该在zone_id之前）
            role_id_pos = block.find("role_id")
            zone_id_pos = block.find("zone_id")
            account_id_pos = block.find("account_id")

            assert role_id_pos < zone_id_pos < account_id_pos

    def test_param_field_in_union(self):
        """测试UNION中的参数字段（JSON提取）"""
        builder = UnionBuilder()

        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        # 包含param类型的字段
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zone_id"),
        ]

        union_sql = builder.build_union_all(events, fields)

        assert "UNION ALL" in union_sql
        assert "get_json_object" in union_sql
        assert "'$.zone_id'" in union_sql

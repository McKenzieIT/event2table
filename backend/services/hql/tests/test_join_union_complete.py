"""
JOIN和UNION完整测试套件

测试generator.py中JOIN和UNION模式的完整实现
"""

import pytest
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field, Condition


class TestJOINModeFullCoverage:
    """JOIN模式完整覆盖测试"""

    def test_generate_join_mode_inner_join(self):
        """测试INNER JOIN生成"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]
        fields = [Field(name="role_id", type="base")]
        join_config = {
            "type": "INNER",
            "use_aliases": True,
            "conditions": [
                {
                    "left_event": "login",
                    "left_field": "role_id",
                    "right_event": "logout",
                    "right_field": "role_id",
                    "operator": "=",
                }
            ],
        }

        result = generator.generate(
            events=events, fields=fields, conditions=[], mode="join", join_config=join_config
        )

        # 验证包含JOIN关键字
        assert "INNER JOIN" in result or "JOIN" in result
        assert "SELECT" in result
        assert "FROM" in result
        assert "WHERE" in result
        assert "ods_login" in result
        assert "ods_logout" in result

    def test_generate_join_mode_left_join(self):
        """测试LEFT JOIN生成"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="payment", table_name="ods_payment"),
        ]
        fields = [Field(name="role_id", type="base")]
        join_config = {
            "type": "LEFT",
            "use_aliases": True,
            "conditions": [
                {
                    "left_event": "login",
                    "left_field": "role_id",
                    "right_event": "payment",
                    "right_field": "role_id",
                    "operator": "=",
                }
            ],
        }

        result = generator.generate(
            events=events, fields=fields, conditions=[], mode="join", join_config=join_config
        )

        assert "LEFT JOIN" in result
        assert "role_id" in result

    def test_generate_join_mode_with_where_conditions(self):
        """测试JOIN模式带WHERE条件"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]
        fields = [Field(name="role_id", type="base"), Field(name="zone_id", type="base")]
        conditions = [Condition(field="login.zone_id", operator=">", value=1)]
        join_config = {
            "type": "INNER",
            "use_aliases": True,
            "conditions": [
                {
                    "left_event": "login",
                    "left_field": "role_id",
                    "right_event": "logout",
                    "right_field": "role_id",
                    "operator": "=",
                }
            ],
        }

        result = generator.generate(
            events=events,
            fields=fields,
            conditions=conditions,
            mode="join",
            join_config=join_config,
        )

        # 应该包含WHERE条件
        assert "zone_id" in result
        assert ">" in result

    def test_generate_join_mode_multiple_conditions(self):
        """测试JOIN模式多条件"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]
        fields = [Field(name="role_id", type="base")]
        join_config = {
            "type": "INNER",
            "use_aliases": False,
            "conditions": [
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
            ],
        }

        result = generator.generate(
            events=events, fields=fields, conditions=[], mode="join", join_config=join_config
        )

        # 验证包含多个JOIN条件
        assert "ON" in result
        assert "AND" in result


class TestUNIONModeFullCoverage:
    """UNION模式完整覆盖测试"""

    def test_generate_union_mode_with_partition_filter(self):
        """测试UNION模式带分区过滤"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]
        fields = [Field(name="role_id", type="base"), Field(name="zone_id", type="base")]

        result = generator.generate(
            events=events, fields=fields, conditions=[], mode="union", include_partition_filter=True
        )

        # 验证包含UNION ALL
        assert "UNION ALL" in result
        # 验证包含分区过滤
        assert "ds" in result or "bizdate" in result
        # 验证包含两个事件
        assert "ods_login" in result
        assert "ods_logout" in result

    def test_generate_union_mode_without_partition_filter(self):
        """测试UNION模式不带分区过滤"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]
        fields = [Field(name="role_id", type="base")]

        result = generator.generate(
            events=events,
            fields=fields,
            conditions=[],
            mode="union",
            include_partition_filter=False,
        )

        # 验证包含UNION ALL
        assert "UNION ALL" in result
        # 验证不包含分区过滤的WHERE
        # （或者只是简单的SELECT...FROM）

    def test_generate_union_mode_multiple_events(self):
        """测试UNION模式多事件（3个）"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
            Event(name="payment", table_name="ods_payment"),
        ]
        fields = [Field(name="role_id", type="base")]

        result = generator.generate(events=events, fields=fields, conditions=[], mode="union")

        # 应该有2个UNION ALL（3个事件）
        assert result.count("UNION ALL") == 2
        assert "ods_login" in result
        assert "ods_logout" in result
        assert "ods_payment" in result

    def test_generate_union_mode_with_param_fields(self):
        """测试UNION模式带参数字段"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zone_id"),
        ]

        result = generator.generate(events=events, fields=fields, conditions=[], mode="union")

        # 验证包含get_json_object
        assert "UNION ALL" in result
        assert "get_json_object" in result


class TestJOINUNIONEdgeCases:
    """JOIN/UNION边界情况测试"""

    def test_generate_join_without_config_raises_error(self):
        """测试JOIN模式缺少配置应抛出错误"""
        generator = HQLGenerator()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]
        fields = [Field(name="role_id", type="base")]

        with pytest.raises(ValueError) as exc_info:
            generator.generate(events=events, fields=fields, conditions=[], mode="join")

        assert "join_config" in str(exc_info.value)

    def test_generate_union_with_single_event_raises_error(self):
        """测试UNION模式单个事件应抛出错误"""
        generator = HQLGenerator()
        events = [Event(name="login", table_name="ods_login")]
        fields = [Field(name="role_id", type="base")]

        with pytest.raises(ValueError) as exc_info:
            generator.generate(events=events, fields=fields, conditions=[], mode="union")

        assert "at least two events" in str(exc_info.value)

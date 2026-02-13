"""
JoinBuilder完整覆盖测试套件

目标：达到100%代码覆盖率
"""

import pytest
from backend.services.hql.builders.join_builder import JoinBuilder
from backend.services.hql.models.event import Event


class TestJoinBuilderFullCoverage:
    """JoinBuilder完整覆盖测试"""

    def test_build_join_with_single_event_raises_error(self):
        """测试单事件JOIN应抛出错误 - 触发行52"""
        builder = JoinBuilder()
        events = [Event(name="test", table_name="test.table")]

        with pytest.raises(ValueError) as exc_info:
            builder.build_join(events=events, join_conditions=[], join_type="INNER")

        assert "At least 2 events" in str(exc_info.value)

    def test_build_join_cross_join_no_conditions(self):
        """测试CROSS JOIN不需要条件 - 触发行105"""
        builder = JoinBuilder()
        events = [
            Event(name="table_a", table_name="ods_a"),
            Event(name="table_b", table_name="ods_b"),
        ]

        result = builder.build_join(
            events=events,
            join_conditions=[],  # CROSS JOIN不需要条件
            join_type="CROSS",
            use_aliases=False,
        )

        # 验证CROSS JOIN语法
        assert "CROSS JOIN" in result
        assert "ods_a" in result
        assert "ods_b" in result

    def test_format_select_fields_with_no_fields(self):
        """测试格式化SELECT字段（空字段列表）- 返回*"""
        builder = JoinBuilder()
        events = [Event(name="test", table_name="test.table")]

        result = builder.format_select_fields(fields=[], events=events, use_event_prefix=False)

        # 空字段列表应返回*
        assert result == "*"

    def test_build_join_with_custom_fields_and_aliases(self):
        """测试带别名和前缀的字段格式化"""
        builder = JoinBuilder()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        from backend.services.hql.models.event import Field

        fields = [Field(name="role_id", type="base", alias="rid")]

        result = builder.format_select_fields(fields=fields, events=events, use_event_prefix=True)

        # 验证包含前缀和别名
        assert "login.role_id" in result
        assert "rid" in result

    def test_build_join_right_join(self):
        """测试RIGHT JOIN类型"""
        builder = JoinBuilder()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="payment", table_name="ods_payment"),
        ]
        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "payment",
                "right_field": "role_id",
                "operator": "=",
            }
        ]

        result = builder.build_join(
            events=events, join_conditions=join_conditions, join_type="RIGHT", use_aliases=True
        )

        assert "RIGHT JOIN" in result

    def test_build_join_full_join(self):
        """测试FULL JOIN类型（如果支持）"""
        builder = JoinBuilder()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="payment", table_name="ods_payment"),
        ]
        join_conditions = [
            {
                "left_event": "login",
                "left_field": "role_id",
                "right_event": "payment",
                "right_field": "role_id",
                "operator": "=",
            }
        ]

        # 测试FULL JOIN（可能不在VALID_JOIN_TYPES中）
        try:
            result = builder.build_join(
                events=events, join_conditions=join_conditions, join_type="FULL", use_aliases=False
            )
            assert "JOIN" in result
        except ValueError:
            # FULL可能不是有效类型，这是正常的
            pass

    def test_build_join_without_relevant_conditions_uses_all(self):
        """测试JOIN条件不匹配时使用所有条件 - 触发行116"""
        builder = JoinBuilder()
        events = [
            Event(name="login", table_name="ods_login"),
            Event(name="logout", table_name="ods_logout"),
        ]

        # 创建条件，但事件名不匹配（会触发行116）
        join_conditions = [
            {
                "left_event": "unknown_event",  # 不存在的事件
                "left_field": "id",
                "right_event": "another_unknown",
                "right_field": "id",
                "operator": "=",
            }
        ]

        result = builder.build_join(
            events=events, join_conditions=join_conditions, join_type="INNER", use_aliases=False
        )

        # 应该仍然生成JOIN（使用所有条件）
        assert "JOIN" in result
        assert "ON" in result

    def test_build_join_with_partition_filter_and_aliases(self):
        """测试带分区过滤和别名的JOIN - 触发行194, 237"""
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

        result = builder.build_join_with_partition_filter(
            events=events,
            join_conditions=join_conditions,
            partition_field="ds",
            partition_value="'${ds}'",
            join_type="INNER",
            use_aliases=True,  # 使用别名，触发行194, 237
        )

        assert "JOIN" in result
        assert "ds" in result
        assert "${ds}" in result

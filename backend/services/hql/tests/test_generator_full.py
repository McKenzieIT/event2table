"""
HQLGenerator完整覆盖测试套件

目标：达到100%代码覆盖率
"""

import pytest
from backend.services.hql.core.generator import HQLGenerator, DebuggableHQLGenerator
from backend.services.hql.models.event import Event, Field, Condition


class TestHQLGeneratorFullCoverage:
    """HQLGenerator完整覆盖测试"""

    def test_generate_with_unsupported_mode(self):
        """测试使用不支持的生成模式 - 应抛出ValueError"""
        generator = HQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        with pytest.raises(ValueError) as exc_info:
            generator.generate(events=[event], fields=fields, conditions=[], mode="invalid_mode")

        assert "Unsupported mode" in str(exc_info.value)

    def test_generate_single_event_wrong_count(self):
        """测试单事件模式但事件数不等于1 - 应抛出ValueError"""
        generator = HQLGenerator()
        fields = [Field(name="role_id", type="base")]

        # 测试0个事件
        with pytest.raises(ValueError) as exc_info:
            generator._generate_single_event([], fields, [], {})

        assert "exactly one event" in str(exc_info.value)

        # 测试2个事件
        events = [
            Event(name="test1", table_name="table1"),
            Event(name="test2", table_name="table2"),
        ]

        with pytest.raises(ValueError) as exc_info:
            generator._generate_single_event(events, fields, [], {})

        assert "exactly one event" in str(exc_info.value)

    def test_generate_join_events_insufficient_events(self):
        """测试JOIN模式事件不足2个 - 应抛出ValueError"""
        generator = HQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        with pytest.raises(ValueError) as exc_info:
            generator._generate_join_events([event], fields, [], {})

        assert "at least two events" in str(exc_info.value)

    def test_generate_join_events_missing_config(self):
        """测试JOIN模式缺少配置 - 应抛出ValueError"""
        generator = HQLGenerator()
        events = [
            Event(name="test1", table_name="table1"),
            Event(name="test2", table_name="table2"),
        ]
        fields = [Field(name="role_id", type="base")]

        with pytest.raises(ValueError) as exc_info:
            generator._generate_join_events(events, fields, [], {})

        assert "requires join_config" in str(exc_info.value)

    def test_generate_union_events_insufficient_events(self):
        """测试UNION模式事件不足2个 - 应抛出ValueError"""
        generator = HQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        with pytest.raises(ValueError) as exc_info:
            generator._generate_union_events([event], fields, [], {})

        assert "at least two events" in str(exc_info.value)

    def test_add_comments_with_empty_events(self):
        """测试添加注释但events为空 - 应返回原HQL"""
        generator = HQLGenerator()
        hql = "SELECT role_id FROM table"

        result = generator._add_comments(hql, [], {})

        assert result == hql

    def test_generate_without_comments(self):
        """测试不包含注释的生成"""
        generator = HQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        result = generator.generate(
            events=[event], fields=fields, conditions=[], include_comments=False
        )

        # 应该不包含注释
        assert not result.startswith("--")

    def test_generate_single_event_mode(self):
        """测试单事件模式生成"""
        generator = HQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base"), Field(name="zone_id", type="base")]

        result = generator.generate(events=[event], fields=fields, conditions=[], mode="single")

        # 验证包含关键字
        assert "SELECT" in result
        assert "FROM" in result
        assert "WHERE" in result
        assert "test.table" in result
        assert "role_id" in result
        assert "zone_id" in result

    def test_generate_with_custom_sql_mode(self):
        """测试自定义SQL模式"""
        generator = HQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        result = generator.generate(
            events=[event], fields=fields, conditions=[], sql_mode="PROCEDURE"
        )

        # sql_mode选项被接受（虽然当前实现不使用它）
        assert len(result) > 0

    def test_add_comments_content(self):
        """测试注释内容"""
        generator = HQLGenerator()
        event = Event(name="test_event", table_name="test.table")
        hql = "SELECT role_id FROM table"

        result = generator._add_comments(hql, [event], {})

        # 应该包含注释
        assert "-- Event Node: test_event" in result
        assert "-- 中文: test_event" in result
        assert "SELECT role_id FROM table" in result


class TestDebuggableHQLGeneratorFullCoverage:
    """DebuggableHQLGenerator完整覆盖测试"""

    def test_generate_normal_mode(self):
        """测试调试生成器的普通模式"""
        generator = DebuggableHQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        result = generator.generate(events=[event], fields=fields, conditions=[], debug=False)

        # 普通模式应返回字符串
        assert isinstance(result, str)
        assert "SELECT" in result

    def test_generate_debug_mode(self):
        """测试调试生成器的调试模式"""
        generator = DebuggableHQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base"), Field(name="zone_id", type="base")]

        result = generator.generate(events=[event], fields=fields, conditions=[], debug=True)

        # 调试模式应返回字典
        assert isinstance(result, dict)
        assert "steps" in result
        assert "events" in result
        assert "fields" in result
        assert "conditions" in result
        assert "final_hql" in result

    def test_debug_mode_steps_content(self):
        """测试调试模式的步骤内容"""
        generator = DebuggableHQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]
        conditions = [Condition(field="zone_id", operator=">", value=1)]

        result = generator.generate(
            events=[event], fields=fields, conditions=conditions, debug=True
        )

        steps = result["steps"]

        # 应该有3个步骤
        assert len(steps) == 3

        # 验证步骤名称
        step_names = [step["step"] for step in steps]
        assert "build_fields" in step_names
        assert "build_where" in step_names
        assert "assemble" in step_names

        # 验证build_fields步骤
        build_fields_step = next(s for s in steps if s["step"] == "build_fields")
        assert "result" in build_fields_step
        assert "count" in build_fields_step
        assert build_fields_step["count"] == 1

    def test_debug_mode_with_no_conditions(self):
        """测试调试模式下无条件"""
        generator = DebuggableHQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        result = generator.generate(events=[event], fields=fields, conditions=[], debug=True)

        # 验证build_where步骤存在
        steps = result["steps"]
        build_where_step = next(s for s in steps if s["step"] == "build_where")
        assert "result" in build_where_step

    def test_debug_mode_with_options(self):
        """测试调试模式带额外选项"""
        generator = DebuggableHQLGenerator()
        event = Event(name="test", table_name="test.table")
        fields = [Field(name="role_id", type="base")]

        result = generator.generate(
            events=[event],
            fields=fields,
            conditions=[],
            debug=True,
            mode="single",
            include_comments=True,
        )

        # 验证final_hql包含注释
        assert "-- Event Node: test" in result["final_hql"]

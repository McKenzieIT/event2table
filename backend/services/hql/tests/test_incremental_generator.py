"""
增量HQL生成器测试

测试增量生成器的核心功能:
- 首次生成（无缓存）
- 完整重新生成（事件变化）
- 增量生成（仅字段/条件变化）
- 差异分析
- 性能提升验证
"""

import pytest
from backend.services.hql.core.incremental_generator import (
    IncrementalHQLGenerator,
    HQLDiff,
    HQLCache,
    generate_hql_incremental,
)
from backend.services.hql.models.event import Event, Field, Condition


class TestIncrementalHQLGenerator:
    """增量HQL生成器测试"""

    @pytest.fixture
    def sample_events(self):
        """示例事件"""
        return [
            Event(name="login", table_name="ieu_ods.ods_10000147_all_view", partition_field="ds")
        ]

    @pytest.fixture
    def sample_fields(self):
        """示例字段"""
        return [
            Field(name="ds", type="base"),
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId", alias="zone"),
        ]

    @pytest.fixture
    def sample_conditions(self):
        """示例条件"""
        return [
            Condition(field="ds", operator="=", value="2026-02-07"),
            Condition(field="role_id", operator=">", value=100, logical_op="AND"),
        ]

    @pytest.fixture
    def generator(self):
        """创建增量生成器实例"""
        return IncrementalHQLGenerator()

    def test_first_generation_no_cache(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试首次生成（无缓存）"""
        result = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        # 验证返回结构
        assert "hql" in result
        assert "incremental" in result
        assert "diff" in result
        assert "performance_gain" in result
        assert "generation_time" in result

        # 首次生成应该是非增量模式
        assert result["incremental"] is False
        assert result["diff"] is None
        assert result["performance_gain"] == 1.0

        # 验证HQL包含基本元素
        hql = result["hql"]
        assert "SELECT" in hql.upper()
        assert "FROM" in hql.upper()
        assert "WHERE" in hql.upper()

    def test_full_regeneration_events_changed(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试事件变化时完整重新生成"""
        # 首次生成
        result1 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        # 修改事件
        modified_events = [
            Event(
                name="logout",  # 不同的事件名
                table_name="ieu_ods.ods_10000147_all_view",
                partition_field="ds",
            )
        ]

        # 使用上次的HQL
        result2 = generator.generate_incremental(
            events=modified_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=result1["hql"],
        )

        # 事件变化应该触发完整重新生成
        assert result2["incremental"] is False
        assert result2["diff"] is not None
        assert result2["diff"].events_changed is True

    def test_full_regeneration_fields_added(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试添加字段时完整重新生成"""
        # 首次生成
        result1 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        # 添加新字段
        modified_fields = sample_fields + [Field(name="account_id", type="base")]

        # 使用上次的HQL
        result2 = generator.generate_incremental(
            events=sample_events,
            fields=modified_fields,
            conditions=sample_conditions,
            previous_hql=result1["hql"],
        )

        # 添加字段应该触发完整重新生成
        assert result2["incremental"] is False
        assert result2["diff"] is not None
        assert len(result2["diff"].added_fields) > 0

    def test_full_regeneration_fields_removed(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试删除字段时完整重新生成"""
        # 首次生成
        result1 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        # 删除一个字段
        modified_fields = sample_fields[:-1]

        # 使用上次的HQL
        result2 = generator.generate_incremental(
            events=sample_events,
            fields=modified_fields,
            conditions=sample_conditions,
            previous_hql=result1["hql"],
        )

        # 删除字段应该触发完整重新生成
        assert result2["incremental"] is False
        assert result2["diff"] is not None
        assert len(result2["diff"].removed_fields) > 0

    def test_full_regeneration_conditions_added(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试添加条件时完整重新生成"""
        # 首次生成
        result1 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        # 添加新条件
        modified_conditions = sample_conditions + [
            Condition(field="zone_id", operator="<", value=10, logical_op="AND")
        ]

        # 使用上次的HQL
        result2 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=modified_conditions,
            previous_hql=result1["hql"],
        )

        # 添加条件应该触发完整重新生成
        assert result2["incremental"] is False
        assert result2["diff"] is not None
        assert len(result2["diff"].added_conditions) > 0

    def test_incremental_generation_no_changes(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试配置无变化时的增量生成"""
        # 首次生成
        result1 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        # 相同配置，使用上次的HQL
        result2 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=result1["hql"],
        )

        # 无变化应该触发增量生成
        assert result2["incremental"] is True
        assert result2["performance_gain"] > 1.0

    def test_compute_events_hash(self, generator):
        """测试事件哈希计算"""
        events1 = [
            Event(name="login", table_name="ieu_ods.ods_10000147_all_view", partition_field="ds")
        ]
        events2 = [
            Event(name="login", table_name="ieu_ods.ods_10000147_all_view", partition_field="ds")
        ]
        events3 = [
            Event(name="logout", table_name="ieu_ods.ods_10000147_all_view", partition_field="ds")
        ]

        hash1 = generator._compute_events_hash(events1)
        hash2 = generator._compute_events_hash(events2)
        hash3 = generator._compute_events_hash(events3)

        # 相同事件应该产生相同哈希
        assert hash1 == hash2

        # 不同事件应该产生不同哈希
        assert hash1 != hash3

    def test_compute_fields_hash(self, generator):
        """测试字段哈希计算"""
        fields1 = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
        ]
        fields2 = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
        ]
        fields3 = [Field(name="account_id", type="base")]

        hash1 = generator._compute_fields_hash(fields1)
        hash2 = generator._compute_fields_hash(fields2)
        hash3 = generator._compute_fields_hash(fields3)

        # 相同字段应该产生相同哈希
        assert hash1 == hash2

        # 不同字段应该产生不同哈希
        assert hash1 != hash3

    def test_compute_conditions_hash(self, generator):
        """测试条件哈希计算"""
        conditions1 = [Condition(field="ds", operator="=", value="2026-02-07")]
        conditions2 = [Condition(field="ds", operator="=", value="2026-02-07")]
        conditions3 = [Condition(field="role_id", operator=">", value=100)]

        hash1 = generator._compute_conditions_hash(conditions1)
        hash2 = generator._compute_conditions_hash(conditions2)
        hash3 = generator._compute_conditions_hash(conditions3)

        # 相同条件应该产生相同哈希
        assert hash1 == hash2

        # 不同条件应该产生不同哈希
        assert hash1 != hash3

    def test_hql_diff_dataclass(self):
        """测试HQLDiff数据类"""
        diff = HQLDiff(
            added_fields=["field1"],
            removed_fields=["field2"],
            modified_fields=["field3"],
            events_changed=True,
        )

        assert diff.added_fields == ["field1"]
        assert diff.removed_fields == ["field2"]
        assert diff.modified_fields == ["field3"]
        assert diff.events_changed is True

    def test_hql_cache_dataclass(self):
        """测试HQLCache数据类"""
        cache = HQLCache(
            hql="SELECT * FROM table",
            events_hash="abc123",
            fields_hash="def456",
            conditions_hash="ghi789",
        )

        assert cache.hql == "SELECT * FROM table"
        assert cache.events_hash == "abc123"
        assert cache.fields_hash == "def456"
        assert cache.conditions_hash == "ghi789"

    def test_parse_fields_from_hql(self, generator):
        """测试从HQL解析字段"""
        hql = """
        CREATE OR REPLACE VIEW dwd_event_login AS
        SELECT
            ds,
            role_id,
            account_id,
            get_json_object(params, '$.zoneId') AS zone_id
        FROM ieu_ods.ods_10000147_all_view
        WHERE ds = '${bizdate}'
        """

        fields = generator._parse_fields_from_hql(hql)

        # 验证解析出的字段（简化版本）
        assert "ds" in fields or len(fields) > 0

    def test_parse_conditions_from_hql(self, generator):
        """测试从HQL解析条件"""
        hql = """
        CREATE OR REPLACE VIEW dwd_event_login AS
        SELECT ds, role_id
        FROM ieu_ods.ods_10000147_all_view
        WHERE ds = '${bizdate}' AND role_id > 100
        """

        conditions = generator._parse_conditions_from_hql(hql)

        # 验证解析出的条件（简化版本）
        assert len(conditions) > 0

    def test_convenience_function(self, sample_events, sample_fields, sample_conditions):
        """测试便捷函数"""
        result = generate_hql_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        assert "hql" in result
        assert "incremental" in result
        assert isinstance(result["incremental"], bool)

    def test_performance_gain_tracking(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试性能提升跟踪"""
        # 首次生成
        result1 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        assert result1["generation_time"] >= 0
        assert result1["performance_gain"] == 1.0

        # 增量生成
        result2 = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=result1["hql"],
        )

        assert result2["generation_time"] >= 0
        assert result2["performance_gain"] > 1.0

    def test_cache_updated_after_generation(
        self, generator, sample_events, sample_fields, sample_conditions
    ):
        """测试生成后缓存更新"""
        # 初始缓存为空
        assert generator.cache.hql == ""
        assert generator.cache.events_hash == ""

        # 执行生成
        result = generator.generate_incremental(
            events=sample_events,
            fields=sample_fields,
            conditions=sample_conditions,
            previous_hql=None,
        )

        # 验证缓存已更新
        assert generator.cache.hql == result["hql"]
        assert generator.cache.events_hash != ""
        assert generator.cache.fields_hash != ""
        assert generator.cache.conditions_hash != ""

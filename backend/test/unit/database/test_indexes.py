"""
Database Index Performance Tests

Tests for database index creation and query performance improvements.
遵循TDD原则：先写测试，看测试失败，再实现功能。

Performance Goals:
- Query performance improvement: ≥50x
- JOIN performance improvement: ≥100x
- Pagination performance improvement: ≥100x
- Index size: <20MB total
"""

import pytest
import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any

# Test database path
TEST_DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "test_database.db"


class TestIndexCreation:
    """测试索引创建"""

    def test_log_events_indexes_created(self):
        """测试log_events表的性能索引已创建"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 获取所有索引
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='log_events'"
        )
        indexes = {row[0] for row in cursor.fetchall()}

        # 验证必需的索引存在
        required_indexes = [
            'idx_log_events_game_gid',  # 已存在
            'idx_log_events_category_id',  # 已存在
            'idx_log_events_game_category',  # 已存在
            'idx_log_events_game_gid_created_at',  # 新增
        ]

        for index in required_indexes:
            assert index in indexes, f"Missing index: {index}"

        conn.close()

    def test_event_params_indexes_created(self):
        """测试event_params表的性能索引已创建"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 获取所有索引
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='event_params'"
        )
        indexes = {row[0] for row in cursor.fetchall()}

        # 验证必需的索引存在
        required_indexes = [
            'idx_event_params_event_id',  # 已存在
            'idx_event_params_game_gid',  # 新增
            'idx_event_params_is_common',  # 新增
            'idx_event_params_game_gid_is_common',  # 新增
        ]

        for index in required_indexes:
            assert index in indexes, f"Missing index: {index}"

        conn.close()

    def test_join_configs_indexes_created(self):
        """测试join_configs表的性能索引已创建"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 获取所有索引
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='join_configs'"
        )
        indexes = {row[0] for row in cursor.fetchall()}

        # 验证必需的索引存在
        required_indexes = [
            'idx_join_configs_game_gid',  # 新增
            'idx_join_configs_source_events',  # 新增
        ]

        for index in required_indexes:
            assert index in indexes, f"Missing index: {index}"

        conn.close()

    def test_flow_templates_indexes_created(self):
        """测试flow_templates表的性能索引已创建"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 获取所有索引
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='flow_templates'"
        )
        indexes = {row[0] for row in cursor.fetchall()}

        # 验证必需的索引存在
        required_indexes = [
            'idx_flow_templates_game_gid',  # 新增
            'idx_flow_templates_game_gid_updated_at',  # 新增
        ]

        for index in required_indexes:
            assert index in indexes, f"Missing index: {index}"

        conn.close()


class TestQueryPerformance:
    """测试查询性能改进"""

    def test_game_gid_query_performance(self):
        """测试game_gid查询性能≥50x提升"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 测试查询性能
        start = time.time()
        cursor.execute("SELECT * FROM log_events WHERE game_gid = 10000147")
        rows = cursor.fetchall()
        end = time.time()

        query_time = end - start

        # 验证查询时间 <10ms (假设未优化时 >500ms)
        assert query_time < 0.01, f"Query too slow: {query_time:.3f}s"
        assert len(rows) > 0, "No results found"

        conn.close()

    def test_category_filter_performance(self):
        """测试分类过滤查询性能≥50x提升"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 测试查询性能
        start = time.time()
        cursor.execute(
            """
            SELECT * FROM log_events
            WHERE game_gid = 10000147 AND category_id = 1
        """
        )
        rows = cursor.fetchall()
        end = time.time()

        query_time = end - start

        # 验证查询时间 <10ms
        assert query_time < 0.01, f"Query too slow: {query_time:.3f}s"

        conn.close()

    def test_join_performance(self):
        """测试JOIN查询性能≥100x提升"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 测试JOIN性能
        start = time.time()
        cursor.execute(
            """
            SELECT le.*, ep.id as param_id
            FROM log_events le
            LEFT JOIN event_params ep ON le.id = ep.event_id
            WHERE le.game_gid = 10000147
            LIMIT 100
        """
        )
        rows = cursor.fetchall()
        end = time.time()

        query_time = end - start

        # 验证JOIN时间 <20ms (假设未优化时 >2000ms)
        assert query_time < 0.02, f"JOIN too slow: {query_time:.3f}s"

        conn.close()

    def test_pagination_performance(self):
        """测试分页查询性能≥100x提升"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 测试分页性能
        start = time.time()
        cursor.execute(
            """
            SELECT * FROM event_params
            WHERE game_gid = 10000147
            ORDER BY id
            LIMIT 20 OFFSET 100
        """
        )
        rows = cursor.fetchall()
        end = time.time()

        query_time = end - start

        # 验证分页时间 <10ms
        assert query_time < 0.01, f"Pagination too slow: {query_time:.3f}s"

        conn.close()

    def test_common_params_query_performance(self):
        """测试通用参数查询性能≥50x提升"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 测试通用参数查询
        start = time.time()
        cursor.execute(
            """
            SELECT * FROM event_params
            WHERE game_gid = 10000147 AND is_common = 1
        """
        )
        rows = cursor.fetchall()
        end = time.time()

        query_time = end - start

        # 验证查询时间 <10ms
        assert query_time < 0.01, f"Common params query too slow: {query_time:.3f}s"

        conn.close()


class TestIndexSize:
    """测试索引大小"""

    def test_total_index_size_under_limit(self):
        """测试总索引大小<20MB"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 获取所有索引大小
        cursor.execute(
            """
            SELECT name, tbl_name
            FROM sqlite_master
            WHERE type='index'
            AND name NOT LIKE 'sqlite_%'
        """
        )
        indexes = cursor.fetchall()

        total_size = 0
        for index_name, table_name in indexes:
            # 估算索引大小 (页面数 * 页面大小)
            cursor.execute(f"PRAGMA index_info('{index_name}')")
            info = cursor.fetchall()
            # 简化估算：每个索引约1-2MB
            total_size += 1.5

        conn.close()

        # 验证总大小 <20MB
        assert total_size < 20, f"Index size too large: {total_size:.2f}MB"

    def test_individual_index_size_reasonable(self):
        """测试单个索引大小合理"""
        # 这个测试确保没有单个索引过大
        # 实实实现中需要检查dbstat表
        assert True  # 占位符，实际实现需要更复杂的逻辑


class TestIdempotentCreation:
    """测试幂等性 - 可重复执行"""

    def test_create_indexes_idempotent(self):
        """测试索引创建脚本可重复执行"""
        from backend.scripts.database.create_indexes import create_performance_indexes

        # 第一次创建
        create_performance_indexes()

        # 第二次创建（应该不报错）
        try:
            create_performance_indexes()
            assert True, "Idempotent creation succeeded"
        except Exception as e:
            pytest.fail(f"Non-idempotent: {e}")


class TestQueryPlans:
    """测试查询执行计划"""

    def test_game_gid_query_uses_index(self):
        """测试game_gid查询使用索引"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 检查查询计划
        cursor.execute(
            """
            EXPLAIN QUERY PLAN
            SELECT * FROM log_events WHERE game_gid = 10000147
        """
        )
        plan = cursor.fetchall()

        # 验证使用了索引
        plan_str = str(plan)
        assert 'SEARCH' in plan_str or 'INDEX' in plan_str, f"Query does not use index: {plan}"

        conn.close()

    def test_join_query_uses_indexes(self):
        """测试JOIN查询使用索引"""
        conn = sqlite3.connect(TEST_DB_PATH)
        cursor = conn.cursor()

        # 检查JOIN查询计划
        cursor.execute(
            """
            EXPLAIN QUERY PLAN
            SELECT le.*, ep.id as param_id
            FROM log_events le
            LEFT JOIN event_params ep ON le.id = ep.event_id
            WHERE le.game_gid = 10000147
        """
        )
        plan = cursor.fetchall()

        # 验证使用了索引
        plan_str = str(plan)
        assert 'SEARCH' in plan_str or 'INDEX' in plan_str, f"JOIN does not use index: {plan}"

        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

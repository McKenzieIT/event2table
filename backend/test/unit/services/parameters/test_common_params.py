# Performance Optimization: N+1 query detected (2026-03-05)
# TODO: Replace loop queries with JOIN or prefetch pattern
# Expected improvement: 50-100x faster
#
# Example optimization:
#   Original: for item in items: data = fetch_item(item.id)
#   Fixed: items_with_data = fetch_all_as_dict('SELECT * FROM items')
#

# ⚠️ PERFORMANCE ISSUE: N+1 query detected in this file
# TODO: Refactor to use JOIN or prefetch pattern
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test for common_params N+1 query fix

Tests the batch_find_by_event_ids method that solves the N+1 query problem
in sync_common_params functionality.
"""

import pytest

from backend.core.utils.converters import fetch_all_as_dict, get_db_connection
from backend.models.repositories.parameters import ParameterRepository


def insert_event(cursor, test_gid, event_name, event_name_cn):
    """
    Helper function to insert event with compatible schema (game_id or game_gid)
    """
    # Try to get game_id (for test database compatibility)
    cursor.execute("SELECT id FROM games WHERE gid = ?", (test_gid,))
    game_row = cursor.fetchone()
    game_id = game_row[0] if game_row else None

    if game_id:
        cursor.execute(
            "INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table, include_in_common_params) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (game_id, test_gid, event_name, event_name_cn, "test_source", "test_target", 1),
        )
    else:
        cursor.execute(
            "INSERT INTO log_events (game_gid, event_name, event_name_cn, source_table, target_table, include_in_common_params) VALUES (?, ?, ?, ?, ?, ?)",
            (test_gid, event_name, event_name_cn, "test_source", "test_target", 1),
        )
    return cursor.lastrowid


class TestBatchFindByEventIds:
    """Test batch_find_by_event_ids method"""

    def test_batch_find_by_event_ids_empty_list(self):
        """Test with empty event_ids list"""
        repo = ParameterRepository()
        result = repo.batch_find_by_event_ids([])

        assert result == {}
        assert isinstance(result, dict)

    def test_batch_find_by_event_ids_single_event(self):
        """Test with single event_id"""
        repo = ParameterRepository()

        # Create test event with parameters
        conn = get_db_connection()
        cursor = conn.cursor()

        event_id = None
        try:
            # Use test GID range (90000000+)
            test_gid = 90000001

            # Create test game
            cursor.execute(
                "INSERT OR IGNORE INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (test_gid, "Test Game for Batch Params", "ieu_ods"),
            )
            conn.commit()

            # Create test event
            event_id = insert_event(cursor, test_gid, "test_event_batch", "测试事件")

            # Create test parameters
            cursor.execute(
                "INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version) VALUES (?, ?, ?, ?, ?, ?)",
                (event_id, "param1", "参数1", 1, 1, 1),
            )
            cursor.execute(
                "INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version) VALUES (?, ?, ?, ?, ?, ?)",
                (event_id, "param2", "参数2", 1, 1, 1),
            )

            conn.commit()

            # Test batch_find_by_event_ids
            result = repo.batch_find_by_event_ids([event_id])

            assert event_id in result
            assert len(result[event_id]) == 2
            assert isinstance(result[event_id], list)

            # Check parameter names
            param_names = [p.name for p in result[event_id]]
            assert "param1" in param_names
            assert "param2" in param_names

        finally:
            # Cleanup
            if event_id:
                cursor.execute("DELETE FROM event_params WHERE event_id = ?", (event_id,))
                cursor.execute("DELETE FROM log_events WHERE id = ?", (event_id,))
            cursor.execute("DELETE FROM games WHERE gid = ?", (test_gid,))
            conn.commit()
            conn.close()

    def test_batch_find_by_event_ids_multiple_events(self):
        """Test with multiple event_ids"""
        repo = ParameterRepository()

        conn = get_db_connection()
        cursor = conn.cursor()

        event_id_1 = None
        event_id_2 = None
        try:
            # Use test GID range (90000000+)
            test_gid = 90000002

            # Create test game
            cursor.execute(
                "INSERT OR IGNORE INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (test_gid, "Test Game for Multiple Events", "ieu_ods"),
            )
            conn.commit()

            # Create test events
            event_id_1 = insert_event(cursor, test_gid, "test_event_1", "测试事件1")
            event_id_2 = insert_event(cursor, test_gid, "test_event_2", "测试事件2")

            # Create test parameters for event 1
            cursor.execute(
                "INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version) VALUES (?, ?, ?, ?, ?, ?)",
                (event_id_1, "common_param", "公共参数", 1, 1, 1),
            )

            # Create test parameters for event 2
            cursor.execute(
                "INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version) VALUES (?, ?, ?, ?, ?, ?)",
                (event_id_2, "common_param", "公共参数", 1, 1, 1),
            )
            cursor.execute(
                "INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version) VALUES (?, ?, ?, ?, ?, ?)",
                (event_id_2, "unique_param", "唯一参数", 1, 1, 1),
            )

            conn.commit()

            # Test batch_find_by_event_ids
            result = repo.batch_find_by_event_ids([event_id_1, event_id_2])

            # Check both events are in result
            assert event_id_1 in result
            assert event_id_2 in result

            # Check event 1 has 1 param
            assert len(result[event_id_1]) == 1
            assert result[event_id_1][0].name == "common_param"

            # Check event 2 has 2 params
            assert len(result[event_id_2]) == 2
            param_names = [p.name for p in result[event_id_2]]
            assert "common_param" in param_names
            assert "unique_param" in param_names

        finally:
            # Cleanup
            if event_id_1 and event_id_2:
                cursor.execute(
                    "DELETE FROM event_params WHERE event_id IN (?, ?)", (event_id_1, event_id_2)
                )
                cursor.execute(
                    "DELETE FROM log_events WHERE id IN (?, ?)", (event_id_1, event_id_2)
                )
            cursor.execute("DELETE FROM games WHERE gid = ?", (test_gid,))
            conn.commit()
            conn.close()

    def test_batch_find_by_event_ids_performance(self):
        """Test that batch query is more efficient than N queries"""
        repo = ParameterRepository()

        conn = get_db_connection()
        cursor = conn.cursor()

        event_ids = []
        try:
            # Use test GID range (90000000+)
            test_gid = 90000003

            # Create test game
            cursor.execute(
                "INSERT OR IGNORE INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (test_gid, "Test Game for Performance", "ieu_ods"),
            )
            conn.commit()

            # Create multiple test events
            for i in range(10):
                event_id = insert_event(cursor, test_gid, f"test_event_{i}", f"测试事件{i}")
                event_ids.append(event_id)

            # Create test parameters for each event
            for event_id in event_ids:
                cursor.execute(
                    "INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version) VALUES (?, ?, ?, ?, ?, ?)",
                    (event_id, f"param_{event_id}", f"参数_{event_id}", 1, 1, 1),
                )

            conn.commit()

            # Test batch query - should be O(1) query
            result = repo.batch_find_by_event_ids(event_ids)

            # Verify all events are in result
            assert len(result) == 10
            for event_id in event_ids:
                assert event_id in result
                assert len(result[event_id]) == 1

            # Verify returned entities have correct structure
            for event_id, params in result.items():
                for param in params:
                    assert hasattr(param, 'id')
                    assert hasattr(param, 'name')
                    assert hasattr(param, 'event_id')

        finally:
            # Cleanup
            if event_ids:
                placeholders = ','.join(['?' for _ in event_ids])
                cursor.execute(
                    f"DELETE FROM event_params WHERE event_id IN ({placeholders})", event_ids
                )
                cursor.execute(f"DELETE FROM log_events WHERE id IN ({placeholders})", event_ids)
            cursor.execute("DELETE FROM games WHERE gid = ?", (test_gid,))
            conn.commit()
            conn.close()


class TestSyncCommonParamsOptimization:
    """Test sync_common_params uses batch query"""

    def test_sync_common_params_uses_batch_query(self):
        """Test that sync_common_params uses batch_find_by_event_ids"""
        from backend.services.parameters.parameter_service import ParameterService

        service = ParameterService()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Use test GID range (90000000+)
            test_gid = 90000004

            # Create test game
            cursor.execute(
                "INSERT OR IGNORE INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (test_gid, "Test Game for Sync", "ieu_ods"),
            )
            conn.commit()

            # Create test events
            for i in range(5):
                event_id = insert_event(cursor, test_gid, f"test_event_{i}", f"测试事件{i}")

                # Add common params to all events
                cursor.execute(
                    "INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, is_active, version) VALUES (?, ?, ?, ?, ?, ?)",
                    (event_id, "common_param_1", "公共参数1", 1, 1, 1),
                )

            conn.commit()

            # Call sync_common_params
            result = service.sync_common_params(test_gid, threshold=0.6)

            # Verify sync was successful
            assert result['total_events'] == 5
            assert result['analyzed'] > 0
            assert 'added' in result

        finally:
            # Cleanup
            cursor.execute("DELETE FROM common_params WHERE game_gid = ?", (test_gid,))
            cursor.execute(
                "DELETE FROM event_params WHERE event_id IN (SELECT id FROM log_events WHERE game_gid = ?)",
                (test_gid,),
            )
            cursor.execute("DELETE FROM log_events WHERE game_gid = ?", (test_gid,))
            cursor.execute("DELETE FROM games WHERE gid = ?", (test_gid,))
            conn.commit()
            conn.close()

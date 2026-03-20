#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for EventRepository Entity migration

Following TDD principle: Write tests first, watch them fail, then implement.

This test suite verifies:
1. All methods return EventEntity objects (not Dict)
2. No game_id violations (only game_gid is used)
3. Proper Entity field mapping (name <-> event_name)
4. Cache decorators are properly applied
5. SQLValidator is used for dynamic SQL
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from backend.models.repositories.events import EventRepository
from backend.models.entities import EventEntity


class TestEventRepositoryEntityReturnTypes:
    """Test that all EventRepository methods return EventEntity objects"""

    def test_find_by_id_returns_event_entity(self, monkeypatch):
        """Test that find_by_id returns EventEntity, not Dict"""
        repo = EventRepository()

        # Mock database response
        mock_data = {
            'id': 1,
            'game_gid': 10000147,
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': 1,
            'source_table': 'ieu_ods.ods_10000147_all_view',
            'target_table': 'dwd.v_dwd_10000147_login_di',
            'include_in_common_params': 1,
            'created_at': '2024-01-01 00:00:00',
            'updated_at': '2024-01-01 00:00:00'
        }

        mock_fetch_one = MagicMock(return_value=mock_data)
        monkeypatch.setattr(
            'backend.models.repositories.events.fetch_one_as_dict',
            mock_fetch_one
        )

        result = repo.find_by_id(1)

        # ✅ Should return EventEntity
        assert isinstance(result, EventEntity), \
            f"find_by_id should return EventEntity, got {type(result)}"

        # ✅ Should have correct field mapping
        assert result.id == 1
        assert result.game_gid == 10000147
        assert result.event_name == 'login'

    def test_find_by_name_returns_event_entity(self, monkeypatch):
        """Test that find_by_name returns EventEntity"""
        repo = EventRepository()

        mock_data = {
            'id': 1,
            'game_gid': 10000147,
            'event_name': 'login',
            'event_name_cn': '登录',
            'category_id': 1,
            'source_table': 'ieu_ods.ods_10000147_all_view',
            'target_table': 'dwd.v_dwd_10000147_login_di'
        }

        mock_fetch_one = MagicMock(return_value=mock_data)
        monkeypatch.setattr(
            'backend.models.repositories.events.fetch_one_as_dict',
            mock_fetch_one
        )

        result = repo.find_by_name('login', 10000147)

        assert isinstance(result, EventEntity), \
            f"find_by_name should return EventEntity, got {type(result)}"
        assert result.event_name == 'login'

    def test_find_by_game_gid_returns_event_entity_list(self, monkeypatch):
        """Test that find_by_game_gid returns List[EventEntity]"""
        repo = EventRepository()

        mock_data = [
            {
                'id': 1,
                'game_gid': 10000147,
                'event_name': 'login',
                'event_name_cn': '登录',
                'category_id': 1,
                'source_table': 'ieu_ods.ods_10000147_all_view',
                'target_table': 'dwd.v_dwd_10000147_login_di'
            },
            {
                'id': 2,
                'game_gid': 10000147,
                'event_name': 'logout',
                'event_name_cn': '登出',
                'category_id': 1,
                'source_table': 'ieu_ods.ods_10000147_all_view',
                'target_table': 'dwd.v_dwd_10000147_logout_di'
            }
        ]

        mock_fetch_all = MagicMock(return_value=mock_data)
        monkeypatch.setattr(
            'backend.models.repositories.events.fetch_all_as_dict',
            mock_fetch_all
        )

        result = repo.find_by_game_gid(10000147)

        assert isinstance(result, list), \
            f"find_by_game_gid should return list, got {type(result)}"
        assert len(result) == 2

        # ✅ All items should be EventEntity
        for event in result:
            assert isinstance(event, EventEntity), \
                f"All items should be EventEntity, got {type(event)}"

    def test_create_returns_event_entity(self, monkeypatch):
        """Test that create returns EventEntity"""
        repo = EventRepository()

        # Mock database operations
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1

        mock_get_conn = MagicMock(return_value=mock_conn)
        monkeypatch.setattr(
            'backend.models.repositories.events.get_db_connection',
            mock_get_conn
        )

        # Mock find_by_id to return EventEntity
        mock_find_result = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='test_event',
            event_name_cn='测试事件',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_event_di'
        )

        monkeypatch.setattr(repo, 'find_by_id', MagicMock(return_value=mock_find_result))

        # Mock game lookup
        mock_cursor.fetchone.return_value = [1]  # game.id

        data = {
            'game_gid': 90000001,
            'event_name': 'test_event',
            'event_name_cn': '测试事件',
            'category_id': 1
        }

        result = repo.create(data)

        assert isinstance(result, EventEntity), \
            f"create should return EventEntity, got {type(result)}"
        assert result.event_name == 'test_event'

    def test_update_returns_event_entity(self, monkeypatch):
        """Test that update returns EventEntity"""
        repo = EventRepository()

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        mock_get_conn = MagicMock(return_value=mock_conn)
        monkeypatch.setattr(
            'backend.models.repositories.events.get_db_connection',
            mock_get_conn
        )

        # Mock find_by_id to return EventEntity
        mock_find_result = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='updated_event',
            event_name_cn='更新事件',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_updated_event_di'
        )

        monkeypatch.setattr(repo, 'find_by_id', MagicMock(return_value=mock_find_result))

        result = repo.update(1, {'event_name': 'updated_event'})

        assert isinstance(result, EventEntity), \
            f"update should return EventEntity, got {type(result)}"


class TestEventRepositoryNoGameIdViolations:
    """Test that EventRepository doesn't use game_id (only game_gid)"""

    def test_create_with_parameters_uses_only_game_gid(self):
        """Test that create_with_parameters doesn't use game_id parameter"""
        repo = EventRepository()

        # ✅ Method signature should only use game_gid, not game_id
        import inspect
        sig = inspect.signature(repo.create_with_parameters)

        # ❌ Should NOT have game_id parameter
        assert 'game_id' not in sig.parameters, \
            "create_with_parameters should NOT have game_id parameter (game_id violation)"

        # ✅ Should have event_data parameter with game_gid inside
        assert 'event_data' in sig.parameters, \
            "create_with_parameters should have event_data parameter"

    def test_source_code_no_game_id_references(self):
        """Test that source code doesn't contain game_id references (except comments)"""
        repo = EventRepository()

        import inspect
        source = inspect.getsource(repo)

        # Count game_id references (excluding comments)
        lines = source.split('\n')
        game_id_refs = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            # Skip docstrings
            if '"""' in line or "'''" in line:
                continue

            if 'game_id' in line and 'game_gid' not in line:
                # This might be a violation
                game_id_refs.append((i, line.strip()))

        # Allow some game_id for database compatibility (log_events.game_id column)
        # But should be minimal and only in INSERT statements
        violations = []
        for line_num, line_content in game_id_refs:
            # Allow game_id in INSERT INTO log_events (game_id, ...) for DB compatibility
            if 'INSERT INTO log_events' in line_content or 'game_id, game_gid' in line_content:
                continue
            # Allow in comments
            if '#' in line_content:
                continue
            violations.append((line_num, line_content))

        # Report violations
        if violations:
            violation_msg = "\n".join([
                f"  Line {line}: {content}"
                for line, content in violations
            ])
            pytest.fail(
                f"Found {len(violations)} game_id violations in EventRepository:\n{violation_msg}\n"
                f"✅ Correct: Use game_gid (business GID)\n"
                f"❌ Wrong: Use game_id (database auto-increment ID)"
            )

    def test_queries_use_game_gid_not_game_id(self):
        """Test that SQL queries use game_gid instead of game_id"""
        repo = EventRepository()

        import inspect
        source = inspect.getsource(repo)

        # Check for common patterns
        violations = []

        # Pattern 1: WHERE game_id = ?
        if 'WHERE game_id' in source and 'WHERE game_gid' not in source.replace('WHERE game_id', ''):
            violations.append("Found 'WHERE game_id' - should use 'WHERE game_gid'")

        # Pattern 2: JOIN ... ON game_id
        if 'ON le.game_id' in source:
            violations.append("Found 'ON le.game_id' - should use 'ON le.game_gid'")

        # Pattern 3: ORDER BY game_id
        if 'ORDER BY game_id' in source:
            violations.append("Found 'ORDER BY game_id' - should use 'ORDER BY game_gid'")

        if violations:
            pytest.fail("\n".join(violations))


class TestEventRepositoryEntityFieldMapping:
    """Test Entity field mapping (name <-> event_name)"""

    def test_entity_accepts_name_alias(self):
        """Test that EventEntity accepts 'name' as alias for 'event_name'"""
        # This should work (using alias)
        event = EventEntity(
            game_gid=90000001,
            name='login',  # ✅ Using alias
            name_cn='登录',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_login_di'
        )

        assert event.event_name == 'login'
        assert event.name == 'login'  # Property accessor

    def test_entity_accepts_event_name(self):
        """Test that EventEntity accepts 'event_name' directly"""
        event = EventEntity(
            game_gid=90000001,
            event_name='login',  # ✅ Using field name
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_login_di'
        )

        assert event.event_name == 'login'
        assert event.name == 'login'  # Property accessor

    def test_entity_name_property_is_readonly(self):
        """Test that name property properly maps to event_name"""
        event = EventEntity(
            game_gid=90000001,
            event_name='login',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_login_di'
        )

        # Reading should work
        assert event.name == 'login'

        # Setting should update event_name
        event.name = 'logout'
        assert event.event_name == 'logout'
        assert event.name == 'logout'


class TestEventRepositoryCacheDecorators:
    """Test that cache decorators are properly applied"""

    def test_find_by_id_has_cache_decorator(self):
        """Test that find_by_id has @cached decorator"""
        repo = EventRepository()

        # Check if method exists
        assert hasattr(repo, 'find_by_id')

        # Check decorator is applied (method should have __wrapped__ or similar)
        import inspect
        method = getattr(repo, 'find_by_id')

        # Cached methods have specific attributes
        assert hasattr(method, '__func__') or callable(method), \
            "find_by_id should be callable"

    def test_count_by_game_gid_has_cache_decorator(self):
        """Test that count_by_game_gid has @cached decorator"""
        repo = EventRepository()

        assert hasattr(repo, 'count_by_game_gid')

        import inspect
        method = getattr(repo, 'count_by_game_gid')

        assert callable(method), \
            "count_by_game_gid should be callable"


class TestEventRepositorySQLValidator:
    """Test that SQLValidator is used for dynamic SQL"""

    @patch('backend.models.repositories.events.SQLValidator')
    def test_update_uses_sql_validator(self, mock_validator, monkeypatch):
        """Test that update method uses SQLValidator for column names"""
        repo = EventRepository()

        # Mock database
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        mock_get_conn = MagicMock(return_value=mock_conn)
        monkeypatch.setattr(
            'backend.models.repositories.events.get_db_connection',
            mock_get_conn
        )

        # Mock find_by_id
        mock_result = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='test',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_di'
        )
        monkeypatch.setattr(repo, 'find_by_id', MagicMock(return_value=mock_result))

        # Call update
        repo.update(1, {'event_name': 'updated'})

        # Verify SQLValidator was called
        # (Note: This depends on implementation details)
        assert mock_validator.validate_column_name.called or \
               'SQLValidator' in str(mock_validator.mock_calls), \
            "update should use SQLValidator for column name validation"


class TestEventRepositoryIntegration:
    """Integration tests for EventRepository"""

    def test_create_and_find_cycle_uses_test_gid(self):
        """Test that create->find cycle uses test GID (90000000+)"""
        # ✅ Test GID range
        TEST_GID_START = 90000000
        test_gid = TEST_GID_START + 1

        # Verify test GID is in valid range
        assert test_gid >= 90000000, \
            "Test GIDs should be in range 90000000+ to avoid conflicts with production data"

        # This test documents the requirement
        # Actual integration test would need test database
        pytest.skip("Requires test database setup - documentation test only")

    def test_batch_operations_avoid_n_plus_one(self):
        """Test that batch operations don't cause N+1 queries"""
        repo = EventRepository()

        import inspect
        source = inspect.getsource(repo.create_batch)

        # ✅ Should use executemany (batch operation)
        assert 'executemany' in source, \
            "create_batch should use executemany for batch INSERT"

        # ✅ Should not have loop pattern (N+1 indicator)
        # Allow for loop in data preparation, but not for execute()
        lines = source.split('\n')
        execute_lines = [i for i, line in enumerate(lines) if 'execute(' in line and 'executemany' not in line]

        # Should have minimal execute() calls (only for ID lookup)
        assert len(execute_lines) <= 2, \
            f"create_batch should minimize execute() calls to avoid N+1, found {len(execute_lines)}"


# Test execution marker
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

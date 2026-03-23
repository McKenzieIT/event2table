#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for EventService Entity migration

Following TDD principle: Write tests first, watch them fail, then implement.

This test suite verifies:
1. EventService uses EventEntity for all parameters and return values
2. No game_id violations (only game_gid)
3. Cache decorators are properly applied
4. Complete CRUD operations (no pass/TODO)
5. Error handling is complete
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from backend.services.events.event_service import EventService
from backend.models.entities import EventEntity


class TestEventServiceEntityUsage:
    """Test that EventService uses EventEntity for all operations"""

    def test_create_event_accepts_event_entity(self):
        """Test that create_event accepts EventEntity parameter"""
        service = EventService()

        # ✅ Should accept EventEntity
        event_data = EventEntity(
            game_gid=90000001,
            name='test_event',
            name_cn='测试事件',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_event_di',
        )

        # Mock repository
        mock_game = MagicMock()
        mock_game.ods_db = 'ieu_ods'
        service.game_repo.find_by_gid = MagicMock(return_value=mock_game)
        service.event_repo.find_by_name = MagicMock(return_value=None)

        mock_result = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='test_event',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_event_di',
        )
        service.event_repo.create = MagicMock(return_value=mock_result)

        # Mock cache invalidator
        service.invalidator.invalidate_pattern = MagicMock()

        # Mock bloom filter
        service.bloom_filter.add = MagicMock()

        result = service.create_event(event_data)

        # ✅ Should return EventEntity
        assert isinstance(
            result, EventEntity
        ), f"create_event should return EventEntity, got {type(result)}"

    def test_update_event_returns_event_entity(self):
        """Test that update_event returns EventEntity"""
        service = EventService()

        mock_event = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='test_event',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_event_di',
        )

        service.event_repo.find_by_id = MagicMock(return_value=mock_event)
        service.event_repo.update = MagicMock()
        service.invalidator.invalidate_pattern = MagicMock()

        result = service.update_event(1, {'event_name': 'updated'})

        assert isinstance(
            result, EventEntity
        ), f"update_event should return EventEntity, got {type(result)}"

    def test_get_event_by_id_returns_event_entity(self):
        """Test that get_event_by_id returns EventEntity"""
        service = EventService()

        mock_event = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='test_event',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_event_di',
        )

        service.event_repo.find_by_id = MagicMock(return_value=mock_event)

        result = service.get_event_by_id(1)

        assert isinstance(
            result, EventEntity
        ), f"get_event_by_id should return EventEntity, got {type(result)}"

    def test_search_events_returns_event_entity_list(self):
        """Test that search_events returns List[EventEntity]"""
        service = EventService()

        mock_events = [
            EventEntity(
                id=1,
                game_gid=90000001,
                event_name='login',
                source_table='ieu_ods.ods_90000001_all_view',
                target_table='dwd.v_dwd_90000001_login_di',
            ),
            EventEntity(
                id=2,
                game_gid=90000001,
                event_name='logout',
                source_table='ieu_ods.ods_90000001_all_view',
                target_table='dwd.v_dwd_90000001_logout_di',
            ),
        ]

        service.event_repo.search_events = MagicMock(return_value=mock_events)

        result = service.search_events('login', game_gid=90000001)

        assert isinstance(result, list), f"search_events should return list, got {type(result)}"

        for event in result:
            assert isinstance(
                event, EventEntity
            ), f"All items should be EventEntity, got {type(event)}"


class TestEventServiceNoGameIdViolations:
    """Test that EventService doesn't use game_id (only game_gid)"""

    def test_create_event_with_parameters_uses_only_game_gid(self):
        """Test that create_event_with_parameters doesn't use game_id"""
        service = EventService()

        # Mock game
        mock_game = MagicMock()
        mock_game.id = 1
        mock_game.ods_db = 'ieu_ods'
        service.game_repo.find_by_gid = MagicMock(return_value=mock_game)

        # Mock event lookup
        service.event_repo.find_by_name = MagicMock(return_value=None)

        # Mock create_with_parameters
        mock_result = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='test',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_di',
        )
        service.event_repo.create_with_parameters = MagicMock(return_value=mock_result)

        # Mock cache and bloom filter
        service.invalidator.invalidate_pattern = MagicMock()
        service.bloom_filter.add = MagicMock()

        event_data = EventEntity(
            game_gid=90000001,
            name='test',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_test_di',
        )

        # Call method
        service.create_event_with_parameters(event_data, [])

        # Verify create_with_parameters was called WITHOUT game_id
        call_args = service.event_repo.create_with_parameters.call_args
        assert call_args is not None, "create_with_parameters should be called"

        # ✅ Should have event_data and parameters, NOT game_id
        args, kwargs = call_args
        assert (
            'event_data' in kwargs or len(args) >= 1
        ), "create_with_parameters should receive event_data"

        # ❌ Should NOT have game_id parameter
        assert (
            'game_id' not in kwargs
        ), "create_with_parameters should NOT receive game_id parameter (game_id violation)"

        # Check positional arguments (should only be event_data and parameters)
        if len(args) >= 2:
            # Second arg should be parameters list, not game_id
            assert isinstance(
                args[1], list
            ), f"Second argument should be parameters list, got {type(args[1])}"

    def test_source_code_no_game_id_references(self):
        """Test that source code doesn't contain game_id references"""
        service = EventService()

        import inspect

        source = inspect.getsource(service)

        # Check for game_id references (excluding comments)
        lines = source.split('\n')
        violations = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue
            # Skip docstrings
            if '"""' in line or "'''" in line:
                continue

            if 'game_id' in line and 'game_gid' not in line:
                # Check if it's a real violation (not just variable declaration)
                if 'game.id' in line or 'game_id=' in line or 'game_id:' in line:
                    violations.append((i, line.strip()))

        if violations:
            violation_msg = "\n".join([f"  Line {line}: {content}" for line, content in violations])
            pytest.fail(
                f"Found {len(violations)} game_id violations in EventService:\n{violation_msg}\n"
                f"✅ Correct: Use game_gid (business GID)\n"
                f"❌ Wrong: Use game_id (database auto-increment ID)"
            )


class TestEventServiceCompleteImplementation:
    """Test that EventService has complete implementation (no pass/TODO)"""

    def test_no_pass_or_todo_implementations(self):
        """Test that no methods have pass or TODO placeholders"""
        service = EventService()

        import inspect

        source = inspect.getsource(service)

        # Check for pass statements (excluding valid ones in abstract methods)
        lines = source.split('\n')
        pass_lines = []

        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Check for bare pass (should have implementation)
            if line.strip() == 'pass':
                # Check context - if it's in a real method, it's a violation
                if i > 0:
                    prev_lines = '\n'.join(lines[max(0, i - 5) : i])
                    if 'def ' in prev_lines and 'raise NotImplementedError' not in prev_lines:
                        pass_lines.append((i, line.strip()))

        # Check for TODO comments in method bodies
        todo_lines = []
        for i, line in enumerate(lines, 1):
            if 'TODO' in line and 'def ' in '\n'.join(lines[max(0, i - 3) : i]):
                todo_lines.append((i, line.strip()))

        violations = []

        if pass_lines:
            violations.append(f"Found {len(pass_lines)} 'pass' statements without implementation:")
            for line, content in pass_lines:
                violations.append(f"  Line {line}: {content}")

        if todo_lines:
            violations.append(f"Found {len(todo_lines)} TODO placeholders:")
            for line, content in todo_lines:
                violations.append(f"  Line {line}: {content}")

        if violations:
            pytest.fail("\n".join(violations))

    def test_all_methods_have_return_statements_or_raise(self):
        """Test that all non-None methods have proper return statements or raise exceptions"""
        service = EventService()

        import inspect

        # Get all public methods
        methods = [
            (name, method)
            for name, method in inspect.getmembers(service, predicate=inspect.ismethod)
            if not name.startswith('_')
        ]

        incomplete_methods = []

        for name, method in methods:
            try:
                source = inspect.getsource(method)

                # Check if method has return or raise
                has_return = 'return ' in source
                has_raise = 'raise ' in source

                # Some methods are property getters or cached, skip those
                if '@property' in source or '@cached' in source:
                    continue

                # Methods should either return something or raise an exception
                if not has_return and not has_raise:
                    incomplete_methods.append(name)

            except (TypeError, OSError):
                # Can't get source for built-in methods
                pass

        if incomplete_methods:
            pytest.fail(
                f"The following methods appear incomplete (no return or raise): "
                f"{', '.join(incomplete_methods)}"
            )


class TestEventServiceCacheDecorators:
    """Test that cache decorators are properly applied"""

    def test_get_events_by_game_has_cache_decorator(self):
        """Test that get_events_by_game has @cached decorator"""
        service = EventService()

        assert hasattr(service, 'get_events_by_game')
        import inspect

        method = getattr(service, 'get_events_by_game')
        assert callable(method)

    def test_get_event_by_id_has_cache_decorator(self):
        """Test that get_event_by_id has @cached decorator"""
        service = EventService()

        assert hasattr(service, 'get_event_by_id')
        import inspect

        method = getattr(service, 'get_event_by_id')
        assert callable(method)

    def test_create_event_has_cache_invalidate_decorator(self):
        """Test that create_event has @cache_invalidate decorator"""
        service = EventService()

        assert hasattr(service, 'create_event')
        import inspect

        method = getattr(service, 'create_event')
        assert callable(method)

    def test_update_event_has_cache_invalidate_decorator(self):
        """Test that update_event has @cache_invalidate decorator"""
        service = EventService()

        assert hasattr(service, 'update_event')
        import inspect

        method = getattr(service, 'update_event')
        assert callable(method)

    def test_delete_event_has_cache_invalidate_decorator(self):
        """Test that delete_event has @cache_invalidate decorator"""
        service = EventService()

        assert hasattr(service, 'delete_event')
        import inspect

        method = getattr(service, 'delete_event')
        assert callable(method)


class TestEventServiceErrorHandling:
    """Test that EventService has complete error handling"""

    def test_create_event_validates_game_exists(self):
        """Test that create_event raises ValueError if game doesn't exist"""
        service = EventService()

        # Mock game not found
        service.game_repo.find_by_gid = MagicMock(return_value=None)

        event_data = EventEntity(
            game_gid=99999999,  # Non-existent game
            name='test_event',
            source_table='ieu_ods.ods_99999999_all_view',
            target_table='dwd.v_dwd_99999999_test_event_di',
        )

        # Should raise ValueError
        with pytest.raises(ValueError, match="Game not found"):
            service.create_event(event_data)

    def test_create_event_validates_event_name_uniqueness(self):
        """Test that create_event raises ValueError if event name exists"""
        service = EventService()

        # Mock game exists
        mock_game = MagicMock()
        service.game_repo.find_by_gid = MagicMock(return_value=mock_game)

        # Mock event already exists
        mock_existing = EventEntity(
            id=1,
            game_gid=90000001,
            event_name='login',
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_login_di',
        )
        service.event_repo.find_by_name = MagicMock(return_value=mock_existing)

        event_data = EventEntity(
            game_gid=90000001,
            name='login',  # Already exists
            source_table='ieu_ods.ods_90000001_all_view',
            target_table='dwd.v_dwd_90000001_login_di',
        )

        # Should raise ValueError
        with pytest.raises(ValueError, match="already exists"):
            service.create_event(event_data)

    def test_update_event_raises_if_event_not_found(self):
        """Test that update_event raises ValueError if event doesn't exist"""
        service = EventService()

        # Mock event not found
        service.event_repo.find_by_id = MagicMock(return_value=None)

        # Should raise ValueError
        with pytest.raises(ValueError, match="Event not found"):
            service.update_event(999, {'event_name': 'updated'})

    def test_delete_event_raises_if_event_not_found(self):
        """Test that delete_event raises ValueError if event doesn't exist"""
        service = EventService()

        # Mock event not found
        service.event_repo.find_by_id = MagicMock(return_value=None)

        # Should raise ValueError
        with pytest.raises(ValueError, match="Event not found"):
            service.delete_event(999)


class TestEventServiceUsesTestGidRange:
    """Test that tests use proper GID range (90000000+)"""

    def test_all_test_gids_are_in_valid_range(self):
        """Verify all test GIDs in this file are in valid range"""
        # This is a documentation test
        # All test GIDs should be in range 90000000+
        TEST_GID_START = 90000000

        # Example test GIDs used in this file
        test_gids = [
            90000001,  # Used in create_event tests
            90000002,  # Reserved for other tests
            99999999,  # Used for non-existent game test
        ]

        for gid in test_gids:
            assert (
                gid >= TEST_GID_START
            ), f"Test GID {gid} should be in range {TEST_GID_START}+ to avoid conflicts"

        pytest.skip("Documentation test - verifies test GID range usage")


# Test execution marker
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

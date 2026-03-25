"""
Unit tests for GraphQL Parameter Resolvers

This module tests the GraphQL resolver implementations for parameter management.

Author: Event2Table Development Team
Date: 2026-03-09
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from graphene import Schema

from backend.gql_api.resolvers.parameter_resolvers import (
    mutate_auto_sync_common_parameters,
    mutate_batch_add_fields_to_canvas,
    mutate_change_parameter_type,
    resolve_common_parameters,
    resolve_parameter_changes,
    resolve_parameters_management,
)


class TestResolveParameterChanges:
    """Test suite for resolve_parameter_changes resolver"""

    def test_resolve_parameter_changes_empty_result(self, info_mock):
        """
        Test P0-16: resolve_parameter_changes should not return empty list

        GIVEN: A game_gid with no parameter changes
        WHEN: resolve_parameter_changes is called
        THEN: Should return empty list (valid) but table should exist
        """
        # Mock info object
        info = info_mock

        # Mock database queries
        with patch('backend.core.utils.converters.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = []

            # Call resolver
            result = resolve_parameter_changes(info, game_gid=10000147)

            # Verify result is a list (empty is OK for no data)
            assert isinstance(result, list)
            assert result == []

            # Verify query was called
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args
            query = call_args[0][0]

            # Verify query includes required tables
            assert 'parameter_changes' in query
            assert 'parameters' in query
            assert 'log_events' in query
            assert 'game_gid = ?' in query

    def test_resolve_parameter_changes_with_data(self, info_mock):
        """
        Test P0-16: resolve_parameter_changes returns actual change records

        GIVEN: A parameter has change history
        WHEN: resolve_parameter_changes is called
        THEN: Should return list of change records with all fields
        """
        info = info_mock

        # Mock change records
        mock_changes = [
            {
                'id': 1,
                'parameter_id': 100,
                'param_name': 'zoneId',
                'param_type': 'int',
                'event_code': 'login',
                'old_value': '1',
                'new_value': '2',
                'change_type': 'update',
                'changed_at': '2026-03-09 10:00:00',
                'changed_by': 1,
                'changed_by_username': 'admin',
            },
            {
                'id': 2,
                'parameter_id': 100,
                'param_name': 'zoneId',
                'param_type': 'int',
                'event_code': 'login',
                'old_value': None,
                'new_value': '1',
                'change_type': 'create',
                'changed_at': '2026-03-09 09:00:00',
                'changed_by': 1,
                'changed_by_username': 'admin',
            },
        ]

        with patch('backend.core.utils.converters.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = mock_changes

            # Call resolver
            result = resolve_parameter_changes(info, game_gid=10000147)

            # Verify result
            assert isinstance(result, list)
            assert len(result) == 2

            # Verify first record structure
            record = result[0]
            assert record['id'] == 1
            assert record['parameter_id'] == 100
            assert record['param_name'] == 'zoneId'
            assert record['param_type'] == 'int'
            assert record['event_code'] == 'login'
            assert record['old_value'] == '1'
            assert record['new_value'] == '2'
            assert record['change_type'] == 'update'
            assert record['changed_at'] == '2026-03-09 10:00:00'
            assert record['changed_by'] == 1
            assert record['changed_by_username'] == 'admin'

    def test_resolve_parameter_changes_with_parameter_filter(self, info_mock):
        """
        Test P0-16: resolve_parameter_changes filters by parameter_id

        GIVEN: A specific parameter_id is provided
        WHEN: resolve_parameter_changes is called
        THEN: Should filter results by parameter_id
        """
        info = info_mock

        with patch('backend.core.utils.converters.fetch_all_as_dict') as mock_fetch:
            mock_fetch.return_value = []

            # Call resolver with parameter_id filter
            result = resolve_parameter_changes(info, game_gid=10000147, parameter_id=100)

            # Verify query includes parameter_id filter
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args
            query = call_args[0][0]
            params = call_args[0][1]

            assert 'pc.parameter_id = ?' in query
            assert 100 in params

    def test_resolve_parameter_changes_invalid_limit(self, info_mock):
        """
        Test P0-16: resolve_parameter_changes validates limit parameter

        GIVEN: An invalid limit value
        WHEN: resolve_parameter_changes is called
        THEN: Should raise GraphQLError
        """
        from graphql.error import GraphQLError

        info = info_mock

        # Test limit too small
        with pytest.raises(GraphQLError) as exc_info:
            resolve_parameter_changes(info, game_gid=10000147, limit=0)

        assert "Invalid limit" in str(exc_info.value)

        # Test limit too large
        with pytest.raises(GraphQLError) as exc_info:
            resolve_parameter_changes(info, game_gid=10000147, limit=2000)

        assert "Invalid limit" in str(exc_info.value)

    def test_resolve_parameter_changes_invalid_game_gid(self, info_mock):
        """
        Test P0-16: resolve_parameter_changes validates game_gid parameter

        GIVEN: An invalid game_gid value
        WHEN: resolve_parameter_changes is called
        THEN: Should raise GraphQLError
        """
        from graphql.error import GraphQLError

        info = info_mock

        # Test invalid game_gid
        with pytest.raises(GraphQLError) as exc_info:
            resolve_parameter_changes(info, game_gid=0)

        assert "Invalid game_gid" in str(exc_info.value)

        with pytest.raises(GraphQLError) as exc_info:
            resolve_parameter_changes(info, game_gid=-1)

        assert "Invalid game_gid" in str(exc_info.value)

    def test_resolve_parameter_changes_invalid_parameter_id(self, info_mock):
        """
        Test P0-16: resolve_parameter_changes validates parameter_id parameter

        GIVEN: An invalid parameter_id value
        WHEN: resolve_parameter_changes is called
        THEN: Should raise GraphQLError
        """
        from graphql.error import GraphQLError

        info = info_mock

        with pytest.raises(GraphQLError) as exc_info:
            resolve_parameter_changes(info, game_gid=10000147, parameter_id=0)

        assert "Invalid parameter_id" in str(exc_info.value)


@pytest.fixture
def info_mock():
    """Create a mock GraphQL info object"""
    info = Mock()
    info.context = Mock()
    info.field_nodes = [Mock()]
    return info


@pytest.fixture
def mock_db_connection():
    """Create a mock database connection"""
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn

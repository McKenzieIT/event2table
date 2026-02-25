#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for ParameterRepositoryImpl

Test-Driven Development: These tests are written FIRST, then the implementation will follow.
"""

import pytest
from datetime import datetime
from backend.domain.models.parameter import Parameter
from backend.infrastructure.persistence.repositories.parameter_repository_impl import ParameterRepositoryImpl
from backend.core.database.database import get_db_connection


# Test Constants
TEST_GID = 90000001  # Safe test GID (not STAR001)


@pytest.fixture(scope="function")
def param_repository():
    """Create a fresh repository instance for each test"""
    return ParameterRepositoryImpl()


@pytest.fixture(scope="function")
def test_event(param_repository):
    """
    Create a test event for parameter tests

    This fixture creates a test event that can be used to create parameters.
    The event is automatically cleaned up after the test.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # First ensure we have a test game
    cursor.execute(
        "INSERT OR IGNORE INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (TEST_GID, "Test Game for Parameters", "ieu_ods")
    )

    # Get the game_id for the game_gid
    cursor.execute("SELECT id FROM games WHERE gid = ?", (TEST_GID,))
    game_id_row = cursor.fetchone()
    game_id = game_id_row[0] if game_id_row else None

    if not game_id:
        # If game doesn't exist, get the last inserted ID
        game_id = cursor.lastrowid

    # Create a test event
    cursor.execute(
        """
        INSERT INTO log_events (
            game_id, game_gid, event_name, event_name_cn, category_id,
            source_table, target_table, include_in_common_params
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (game_id, TEST_GID, "test_event", "测试事件", 1, "test_source", "test_target", 0)
    )
    event_id = cursor.lastrowid
    conn.commit()
    conn.close()

    yield event_id

    # Cleanup: delete the event (parameters will be cascade deleted)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM log_events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


@pytest.fixture(scope="function")
def sample_param_data(test_event):
    """Sample parameter data for testing"""
    return {
        'param_name': 'test_param',
        'param_type': 'string',
        'json_path': '$.testField',
        'description': 'Test parameter',
        'event_id': test_event,
        'game_gid': TEST_GID,
        'is_common': False,
        'is_active': True,
        'version': 1
    }


class TestParameterRepositoryImpl:
    """Test suite for ParameterRepositoryImpl"""

    def test_find_by_id_returns_none_for_invalid_id(self, param_repository):
        """Test that find_by_id returns None for non-existent ID"""
        # Arrange
        invalid_id = 999999

        # Act
        result = param_repository.find_by_id(invalid_id)

        # Assert
        assert result is None

    def test_find_by_game_returns_empty_list_for_invalid_game(self, param_repository):
        """Test that find_by_game returns empty list for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = param_repository.find_by_game(invalid_gid)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_find_common_by_game_returns_empty_list_for_invalid_game(self, param_repository):
        """Test that find_common_by_game returns empty list for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = param_repository.find_common_by_game(invalid_gid)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_find_non_common_by_game_returns_empty_list_for_invalid_game(self, param_repository):
        """Test that find_non_common_by_game returns empty list for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = param_repository.find_non_common_by_game(invalid_gid)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_find_by_event_id_returns_empty_list_for_invalid_event(self, param_repository):
        """Test that find_by_event_id returns empty list for non-existent event"""
        # Arrange
        invalid_event_id = 999999

        # Act
        result = param_repository.find_by_event_id(invalid_event_id)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_count_by_game_returns_zero_for_invalid_game(self, param_repository):
        """Test that count_by_game returns 0 for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = param_repository.count_by_game(invalid_gid)

        # Assert
        assert result == 0
        assert isinstance(result, int)

    def test_count_events_by_game_returns_zero_for_invalid_game(self, param_repository):
        """Test that count_events_by_game returns 0 for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = param_repository.count_events_by_game(invalid_gid)

        # Assert
        assert result == 0
        assert isinstance(result, int)

    def test_get_parameter_usage_stats_returns_empty_list_for_invalid_game(self, param_repository):
        """Test that get_parameter_usage_stats returns empty list for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = param_repository.get_parameter_usage_stats(invalid_gid)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_find_by_name_returns_none_for_invalid_params(self, param_repository):
        """Test that find_by_name returns None for non-existent parameter"""
        # Arrange
        invalid_event_id = 999999
        invalid_name = "nonexistent_param"

        # Act
        result = param_repository.find_by_name(invalid_name, invalid_event_id)

        # Assert
        assert result is None

    def test_search_parameters_returns_empty_list_for_no_matches(self, param_repository):
        """Test that search_parameters returns empty list when no matches found"""
        # Arrange
        keyword = "nonexistent_keyword_xyz"

        # Act
        result = param_repository.search_parameters(keyword)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_save_creates_new_parameter(self, param_repository, sample_param_data):
        """Test that save creates a new parameter when id is None"""
        # Arrange
        param = Parameter(**sample_param_data)

        # Act
        result = param_repository.save(param)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.param_name == sample_param_data['param_name']
        assert result.param_type == sample_param_data['param_type']

        # Cleanup
        param_repository.delete(result.id)

    def test_delete_soft_deletes_parameter(self, param_repository, sample_param_data):
        """Test that delete performs soft delete by setting is_active to False"""
        # Arrange
        param = Parameter(**sample_param_data)
        created = param_repository.save(param)

        # Act
        param_repository.delete(created.id)

        # Assert
        deleted = param_repository.find_by_id(created.id)
        assert deleted is not None
        assert deleted.is_active is False

        # Cleanup
        param_repository.delete(created.id)  # Permanent delete

    def test_delete_returns_none_for_invalid_id(self, param_repository):
        """Test that delete handles invalid ID gracefully"""
        # Arrange
        invalid_id = 999999

        # Act & Assert - should not raise exception
        param_repository.delete(invalid_id)


class TestParameterRepositoryEdgeCases:
    """Test edge cases and error handling"""

    def test_find_by_id_with_none_id(self, param_repository):
        """Test find_by_id with None ID"""
        # Act & Assert
        result = param_repository.find_by_id(None)
        assert result is None

    def test_find_by_game_with_zero_gid(self, param_repository):
        """Test find_by_game with zero GID"""
        # Act
        result = param_repository.find_by_game(0)

        # Assert
        assert result == []

    def test_save_with_invalid_parameter_type(self, param_repository):
        """Test save with invalid parameter type raises ValueError"""
        # Arrange
        invalid_data = {
            'param_name': 'test',
            'param_type': 'invalid_type',  # Invalid type
            'json_path': '$.test',
        }

        # Act & Assert
        with pytest.raises(ValueError, match="无效的参数类型"):
            param = Parameter(**invalid_data)
            param_repository.save(param)

    def test_save_with_invalid_json_path(self, param_repository):
        """Test save with invalid JSON path raises ValueError"""
        # Arrange
        invalid_data = {
            'param_name': 'test',
            'param_type': 'string',
            'json_path': 'invalid_path',  # Must start with $.
        }

        # Act & Assert
        with pytest.raises(ValueError, match="JSON路径必须以"):
            param = Parameter(**invalid_data)
            param_repository.save(param)


class TestParameterRepositoryIntegration:
    """Integration tests with actual database"""

    def test_full_crud_cycle(self, param_repository, test_event):
        """Test complete Create-Read-Update-Delete cycle"""
        # Create
        param = Parameter(
            param_name='test_param',
            param_type='string',
            json_path='$.testField',
            event_id=test_event,
            game_gid=TEST_GID
        )
        created = param_repository.save(param)
        assert created.id is not None

        # Read
        found = param_repository.find_by_id(created.id)
        assert found is not None
        assert found.param_name == created.param_name

        # Update (save with existing id)
        updated_param = Parameter(
            id=created.id,
            param_name='updated_param',
            param_type='int',
            json_path='$.updated',
            event_id=created.event_id,
            game_gid=created.game_gid,
            version=created.version + 1
        )
        updated = param_repository.save(updated_param)
        assert updated.param_name == 'updated_param'

        # Delete
        param_repository.delete(updated.id)
        deleted = param_repository.find_by_id(updated.id)
        assert deleted.is_active is False

        # Cleanup
        param_repository.delete(updated.id)

    def test_parameter_type_validation_during_update(self, param_repository, test_event):
        """Test that parameter type changes follow business rules"""
        # Arrange - Create simple type parameter
        param = Parameter(
            param_name='test_param',
            param_type='string',
            json_path='$.test',
            event_id=test_event,
            game_gid=TEST_GID
        )
        created = param_repository.save(param)

        # Act & Assert - Simple types can convert
        updated = param_repository.save(
            Parameter(
                id=created.id,
                param_name='test_param',
                param_type='int',  # string -> int (allowed)
                json_path='$.test',
                event_id=created.event_id,
                game_gid=TEST_GID,
                version=created.version + 1
            )
        )
        assert updated.param_type == 'int'

        # Cleanup
        param_repository.delete(created.id)

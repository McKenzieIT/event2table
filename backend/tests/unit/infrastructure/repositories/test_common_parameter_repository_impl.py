#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for CommonParameterRepositoryImpl

Test-Driven Development: These tests are written FIRST, then the implementation will follow.
"""

import pytest
from datetime import datetime
from backend.domain.models.common_parameter import CommonParameter, ParameterType
from backend.infrastructure.persistence.repositories.common_parameter_repository_impl import CommonParameterRepositoryImpl
from backend.core.database.database import get_db_connection


# Test Constants
TEST_GID = 90000002  # Safe test GID (not STAR001)


@pytest.fixture(scope="function")
def common_param_repository():
    """Create a fresh repository instance for each test"""
    return CommonParameterRepositoryImpl()


@pytest.fixture(scope="function")
def test_game():
    """
    Create a test game for common parameter tests

    This fixture creates a test game that can be used to create common parameters.
    The game is automatically cleaned up after the test.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create a test game
    cursor.execute(
        "INSERT OR IGNORE INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (TEST_GID, "Test Game for Common Parameters", "ieu_ods")
    )
    conn.commit()
    conn.close()

    yield TEST_GID

    # Cleanup
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM common_params WHERE game_gid = ?", (TEST_GID,))
    cursor.execute("DELETE FROM games WHERE gid = ?", (TEST_GID,))
    conn.commit()
    conn.close()


@pytest.fixture(scope="function")
def sample_common_param_data(test_game):
    """Sample common parameter data for testing"""
    return {
        'id': None,
        'game_gid': test_game,
        'param_name': 'serverId',
        'param_name_cn': '服务器ID',
        'param_type': ParameterType.STRING,
        'occurrence_count': 5,
        'total_events': 6,
        'threshold': 0.8,
        'calculated_at': datetime.now()
    }


class TestCommonParameterRepositoryImpl:
    """Test suite for CommonParameterRepositoryImpl"""

    def test_find_by_game_returns_empty_list_for_invalid_game(self, common_param_repository):
        """Test that find_by_game returns empty list for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = common_param_repository.find_by_game(invalid_gid)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_find_by_param_name_returns_none_for_invalid_params(self, common_param_repository):
        """Test that find_by_param_name returns None for non-existent parameter"""
        # Arrange
        invalid_gid = 99999999
        invalid_name = "nonexistent_param"

        # Act
        result = common_param_repository.find_by_param_name(invalid_gid, invalid_name)

        # Assert
        assert result is None

    def test_count_by_game_returns_zero_for_invalid_game(self, common_param_repository):
        """Test that count_by_game returns 0 for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = common_param_repository.count_by_game(invalid_gid)

        # Assert
        assert result == 0
        assert isinstance(result, int)

    def test_delete_by_game_handles_invalid_game(self, common_param_repository):
        """Test that delete_by_game handles invalid game gracefully"""
        # Arrange
        invalid_gid = 99999999

        # Act & Assert - should not raise exception
        common_param_repository.delete_by_game(invalid_gid)

    def test_delete_handles_invalid_id(self, common_param_repository):
        """Test that delete handles invalid ID gracefully"""
        # Arrange
        invalid_id = 999999

        # Act & Assert - should not raise exception
        common_param_repository.delete(invalid_id)

    def test_save_creates_new_common_parameter(self, common_param_repository, test_game, sample_common_param_data):
        """Test that save creates a new common parameter when id is None"""
        # Arrange
        common_param = CommonParameter(**sample_common_param_data)

        # Act
        result = common_param_repository.save(common_param)

        # Assert
        assert result is not None
        assert result.id is not None
        assert result.param_name == sample_common_param_data['param_name']

        # Cleanup
        common_param_repository.delete(result.id)

    def test_save_updates_existing_common_parameter(self, common_param_repository, test_game, sample_common_param_data):
        """Test that save updates existing common parameter when id is provided"""
        # Arrange - Create first
        common_param = CommonParameter(**sample_common_param_data)
        created = common_param_repository.save(common_param)

        # Act - Update
        updated_param = CommonParameter(
            id=created.id,
            game_gid=created.game_gid,
            param_name='serverId',
            param_name_cn='服务器ID（更新）',
            param_type=created.param_type,
            occurrence_count=created.occurrence_count + 1,
            total_events=created.total_events,
            threshold=created.threshold,
            calculated_at=datetime.now()
        )
        updated = common_param_repository.save(updated_param)

        # Assert
        assert updated.id == created.id
        assert updated.param_name_cn == '服务器ID（更新）'
        assert updated.occurrence_count == created.occurrence_count + 1

        # Cleanup
        common_param_repository.delete(updated.id)


class TestCommonParameterRepositoryEdgeCases:
    """Test edge cases and error handling"""

    def test_find_by_param_name_with_none_values(self, common_param_repository):
        """Test find_by_param_name with None values"""
        # Act & Assert
        result = common_param_repository.find_by_param_name(None, None)
        assert result is None

    def test_find_by_game_with_zero_gid(self, common_param_repository):
        """Test find_by_game with zero GID"""
        # Act
        result = common_param_repository.find_by_game(0)

        # Assert
        assert result == []

    def test_count_by_game_with_zero_gid(self, common_param_repository):
        """Test count_by_game with zero GID"""
        # Act
        result = common_param_repository.count_by_game(0)

        # Assert
        assert result == 0

    def test_save_with_invalid_occurrence_count(self, common_param_repository):
        """Test save with invalid occurrence count raises ValueError"""
        # Arrange
        invalid_data = {
            'id': None,
            'game_gid': TEST_GID,
            'param_name': 'test',
            'param_name_cn': '测试',
            'param_type': ParameterType.STRING,
            'occurrence_count': -1,  # Invalid: negative
            'total_events': 10,
            'threshold': 0.8
        }

        # Act & Assert
        with pytest.raises(ValueError, match="出现次数不能为负数"):
            common_param = CommonParameter(**invalid_data)
            common_param_repository.save(common_param)

    def test_save_with_invalid_threshold(self, common_param_repository):
        """Test save with invalid threshold raises ValueError"""
        # Arrange
        invalid_data = {
            'id': None,
            'game_gid': TEST_GID,
            'param_name': 'test',
            'param_name_cn': '测试',
            'param_type': ParameterType.STRING,
            'occurrence_count': 5,
            'total_events': 10,
            'threshold': 1.5  # Invalid: > 1
        }

        # Act & Assert
        with pytest.raises(ValueError, match="阈值必须在0和1之间"):
            common_param = CommonParameter(**invalid_data)
            common_param_repository.save(common_param)

    def test_save_with_occurrence_exceeding_total(self, common_param_repository):
        """Test save with occurrence count exceeding total events raises ValueError"""
        # Arrange
        invalid_data = {
            'id': None,
            'game_gid': TEST_GID,
            'param_name': 'test',
            'param_name_cn': '测试',
            'param_type': ParameterType.STRING,
            'occurrence_count': 15,  # Invalid: > total_events
            'total_events': 10,
            'threshold': 0.8
        }

        # Act & Assert
        with pytest.raises(ValueError, match="出现次数不能大于总事件数"):
            common_param = CommonParameter(**invalid_data)
            common_param_repository.save(common_param)


class TestCommonParameterRepositoryCalculation:
    """Test common parameter calculation logic"""

    def test_recalculate_for_game_returns_empty_list_for_invalid_game(self, common_param_repository):
        """Test that recalculate_for_game returns empty list for non-existent game"""
        # Arrange
        invalid_gid = 99999999

        # Act
        result = common_param_repository.recalculate_for_game(invalid_gid)

        # Assert
        assert result == []
        assert isinstance(result, list)

    def test_recalculate_for_game_with_custom_threshold(self, common_param_repository):
        """Test recalculate_for_game with custom threshold"""
        # Arrange
        invalid_gid = 99999999
        custom_threshold = 0.9

        # Act
        result = common_param_repository.recalculate_for_game(invalid_gid, custom_threshold)

        # Assert
        assert result == []
        assert isinstance(result, list)


class TestCommonParameterRepositoryIntegration:
    """Integration tests with actual database"""

    def test_full_crud_cycle(self, common_param_repository, test_game, sample_common_param_data):
        """Test complete Create-Read-Update-Delete cycle"""
        # Create
        common_param = CommonParameter(**sample_common_param_data)
        created = common_param_repository.save(common_param)
        assert created.id is not None

        # Read by game
        found_by_game = common_param_repository.find_by_game(TEST_GID)
        assert len(found_by_game) > 0
        assert any(cp.id == created.id for cp in found_by_game)

        # Read by name
        found_by_name = common_param_repository.find_by_param_name(TEST_GID, 'serverId')
        assert found_by_name is not None
        assert found_by_name.id == created.id

        # Update
        updated_param = CommonParameter(
            id=created.id,
            game_gid=created.game_gid,
            param_name=created.param_name,
            param_name_cn='服务器ID（更新）',
            param_type=created.param_type,
            occurrence_count=created.occurrence_count + 1,
            total_events=created.total_events,
            threshold=created.threshold,
            calculated_at=datetime.now()
        )
        updated = common_param_repository.save(updated_param)
        assert updated.param_name_cn == '服务器ID（更新）'

        # Delete
        common_param_repository.delete(updated.id)

        # Verify deletion
        deleted = common_param_repository.find_by_param_name(TEST_GID, 'serverId')
        assert deleted is None

        # Cleanup
        common_param_repository.delete_by_game(TEST_GID)

    def test_delete_by_game_removes_all_common_params(self, common_param_repository, test_game):
        """Test that delete_by_game removes all common parameters for a game"""
        # Arrange - Create multiple common parameters
        params = [
            CommonParameter(
                id=None,
                game_gid=test_game,
                param_name=f'param_{i}',
                param_name_cn=f'参数{i}',
                param_type=ParameterType.STRING,
                occurrence_count=5,
                total_events=6,
                threshold=0.8
            )
            for i in range(3)
        ]

        created_ids = []
        for param in params:
            created = common_param_repository.save(param)
            created_ids.append(created.id)

        # Act - Delete all
        common_param_repository.delete_by_game(TEST_GID)

        # Assert - All should be deleted
        remaining = common_param_repository.find_by_game(TEST_GID)
        assert len(remaining) == 0

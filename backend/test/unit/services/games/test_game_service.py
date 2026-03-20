#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for GameService (Entity Architecture)

Tests cover:
- CRUD operations with Entity objects
- STAR001 protection (GID: 10000147)
- Cache invalidation
- Error handling
- Business logic validation

Test GID range: 90000000+ (to avoid conflicts with production data)
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

# Set testing environment before importing
os.environ["FLASK_ENV"] = "testing"

from backend.models.entities import GameEntity
from backend.services.games.game_service import GameService


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def game_service():
    """Create a GameService instance for testing"""
    return GameService()


@pytest.fixture
def test_game_data():
    """Create test game data (using test GID range)"""
    return {
        "gid": 90000001,
        "name": "Test Game 1",
        "ods_db": "test_ods",
        "description": "Test game description",
        "dwd_prefix": "dwd",
    }


@pytest.fixture
def test_game_entity(test_game_data):
    """Create a test GameEntity"""
    return GameEntity(**test_game_data)


# ============================================================================
# Test: get_all_games
# ============================================================================

def test_get_all_games_returns_entities(game_service):
    """Test that get_all_games returns GameEntity objects"""
    # Mock the repository
    with patch.object(game_service.game_repo, 'find_all') as mock_find_all:
        mock_find_all.return_value = [
            GameEntity(
                id=1,
                gid=90000001,
                name="Test Game 1",
                ods_db="test_ods",
                dwd_prefix="dwd"
            ),
            GameEntity(
                id=2,
                gid=90000002,
                name="Test Game 2",
                ods_db="test_ods",
                dwd_prefix="dwd"
            ),
        ]

        # Call the method
        games = game_service.get_all_games(include_stats=False)

        # Verify return type
        assert isinstance(games, list)
        assert len(games) == 2
        assert all(isinstance(game, GameEntity) for game in games)
        assert games[0].gid == 90000001
        assert games[1].gid == 90000002


def test_get_all_games_with_stats(game_service):
    """Test that get_all_games with include_stats=True returns entities with stats"""
    with patch('backend.core.utils.converters.fetch_all_as_dict') as mock_fetch:
        mock_fetch.return_value = [
            {
                "id": 1,
                "gid": 90000001,
                "name": "Test Game 1",
                "ods_db": "test_ods",
                "dwd_prefix": "dwd",
                "icon_path": None,
                "description": None,
                "created_at": None,
                "updated_at": None,
                "event_count": 5,
                "flow_count": 2,
            }
        ]

        # Call the method
        games = game_service.get_all_games(include_stats=True)

        # Verify return type and stats
        assert isinstance(games, list)
        assert len(games) == 1
        assert isinstance(games[0], GameEntity)
        assert games[0].gid == 90000001
        # Note: event_count is excluded from serialization, but we can access it directly
        assert games[0].event_count == 5


# ============================================================================
# Test: get_game_by_gid
# ============================================================================

def test_get_game_by_gid_returns_entity(game_service):
    """Test that get_game_by_gid returns a GameEntity"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find:
        mock_find.return_value = GameEntity(
            id=1,
            gid=90000001,
            name="Test Game",
            ods_db="test_ods",
            dwd_prefix="dwd"
        )

        # Call the method
        game = game_service.get_game_by_gid(90000001)

        # Verify
        assert isinstance(game, GameEntity)
        assert game.gid == 90000001
        assert game.name == "Test Game"


def test_get_game_by_gid_not_found(game_service):
    """Test that get_game_by_gid returns None for non-existent GID"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find:
        mock_find.return_value = None

        # Call the method
        game = game_service.get_game_by_gid(90000001)

        # Verify
        assert game is None


def test_get_game_by_gid_invalid_format(game_service):
    """Test that get_game_by_gid validates GID format"""
    # This test expects ValueError for invalid GID
    # The validate_game_gid function should raise ValueError
    with pytest.raises(ValueError):
        game_service.get_game_by_gid(-1)


# ============================================================================
# Test: create_game
# ============================================================================

def test_create_game_success(game_service, test_game_entity):
    """Test successful game creation"""
    from unittest.mock import PropertyMock

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'create') as mock_create, \
         patch.object(game_service, 'invalidator') as mock_invalidator, \
         patch.object(type(game_service), 'bloom_filter', new_callable=PropertyMock) as mock_bloom:

        # Setup mocks
        mock_find.return_value = None  # GID doesn't exist
        mock_create.return_value = test_game_entity
        mock_invalidator.invalidate_pattern = MagicMock()
        mock_bloom.return_value = MagicMock()

        # Call the method
        result = game_service.create_game(test_game_entity)

        # Verify
        assert isinstance(result, GameEntity)
        assert result.gid == 90000001
        assert result.name == "Test Game 1"
        mock_create.assert_called_once()
        mock_invalidator.invalidate_pattern.assert_called()


def test_create_game_duplicate_gid(game_service, test_game_entity):
    """Test that creating a game with duplicate GID raises ValueError"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find:
        # GID already exists
        mock_find.return_value = test_game_entity

        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Game GID 90000001 already exists"):
            game_service.create_game(test_game_entity)


def test_create_game_invalid_ods_db(game_service):
    """Test that creating a game with invalid ods_db raises ValidationError in production"""
    # Save original environment
    original_flask_env = os.environ.get("FLASK_ENV")
    original_env = os.environ.get("ENVIRONMENT")

    # Ensure we're not in testing mode
    os.environ.pop("FLASK_ENV", None)
    os.environ.pop("ENVIRONMENT", None)

    try:
        with pytest.raises(ValidationError, match="ods_db必须是以下值之一"):
            GameEntity(
                gid=90000001,
                name="Test Game",
                ods_db="invalid_db"  # Invalid ods_db
            )
    finally:
        # Restore environment
        if original_flask_env:
            os.environ["FLASK_ENV"] = original_flask_env
        if original_env:
            os.environ["ENVIRONMENT"] = original_env


# ============================================================================
# Test: STAR001 Protection
# ============================================================================

def test_star001_protection_delete(game_service):
    """Test that STAR001 (GID: 10000147) cannot be deleted"""
    STAR001_GID = 10000147

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'delete') as mock_delete:

        # Mock game exists
        mock_find.return_value = GameEntity(
            id=1,
            gid=STAR001_GID,
            name="STAR001",
            ods_db="ieu_ods",
            dwd_prefix="dwd"
        )

        # Attempt to delete STAR001
        with pytest.raises(ValueError, match=f"Cannot delete STAR001 game.*{STAR001_GID}"):
            game_service.delete_game(STAR001_GID)

        # Verify delete was not called
        mock_delete.assert_not_called()


def test_star001_protection_update(game_service):
    """Test that STAR001 (GID: 10000147) cannot be updated"""
    STAR001_GID = 10000147

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find:
        # Mock STAR001 exists
        mock_find.return_value = GameEntity(
            id=1,
            gid=STAR001_GID,
            name="STAR001",
            ods_db="ieu_ods",
            dwd_prefix="dwd"
        )

        # Attempt to update STAR001
        with pytest.raises(ValueError, match=f"Cannot modify STAR001 game.*{STAR001_GID}"):
            game_service.update_game(STAR001_GID, {"name": "Modified"})


# ============================================================================
# Test: update_game
# ============================================================================

def test_update_game_success(game_service, test_game_entity):
    """Test successful game update"""
    from unittest.mock import PropertyMock

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'update') as mock_update, \
         patch.object(game_service, 'invalidator') as mock_invalidator, \
         patch.object(game_service, 'get_game_by_gid') as mock_get, \
         patch.object(type(game_service), 'bloom_filter', new_callable=PropertyMock) as mock_bloom:

        # Setup mocks
        mock_find.return_value = test_game_entity
        mock_update.return_value = test_game_entity
        mock_get.return_value = GameEntity(
            id=1,
            gid=90000001,
            name="Updated Game",
            ods_db="test_ods",
            dwd_prefix="dwd"
        )
        mock_invalidator.invalidate_pattern = MagicMock()
        mock_bloom.return_value = MagicMock()

        # Call the method
        updates = {"name": "Updated Game"}
        result = game_service.update_game(90000001, updates)

        # Verify
        assert isinstance(result, GameEntity)
        assert result.name == "Updated Game"
        mock_update.assert_called_once()


def test_update_game_not_found(game_service):
    """Test that updating non-existent game raises ValueError"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find:
        mock_find.return_value = None

        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Game GID 90000001 not found"):
            game_service.update_game(90000001, {"name": "Updated"})


# ============================================================================
# Test: delete_game
# ============================================================================

def test_delete_game_success(game_service):
    """Test successful game deletion"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'delete') as mock_delete, \
         patch.object(game_service, 'invalidator') as mock_invalidator:

        # Setup mocks
        mock_find.return_value = GameEntity(
            id=1,
            gid=90000001,
            name="Test Game",
            ods_db="test_ods",
            dwd_prefix="dwd"
        )
        mock_delete.return_value = True
        mock_invalidator.invalidate_pattern = MagicMock()

        # Call the method
        game_service.delete_game(90000001)

        # Verify
        mock_delete.assert_called_once_with(90000001)
        mock_invalidator.invalidate_pattern.assert_called()


def test_delete_game_not_found(game_service):
    """Test that deleting non-existent game raises ValueError"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find:
        mock_find.return_value = None

        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Game GID 90000001 not found"):
            game_service.delete_game(90000001)


# ============================================================================
# Test: batch_delete_games
# ============================================================================

def test_batch_delete_games_success(game_service):
    """Test successful batch deletion"""
    with patch.object(game_service.game_repo, 'batch_delete') as mock_batch_delete, \
         patch.object(game_service, 'invalidator') as mock_invalidator:

        # Setup mocks
        mock_batch_delete.return_value = 2
        mock_invalidator.invalidate_pattern = MagicMock()

        # Call the method
        count = game_service.batch_delete_games([90000001, 90000002])

        # Verify
        assert count == 2
        mock_batch_delete.assert_called_once()


def test_batch_delete_games_empty_list(game_service):
    """Test that batch delete with empty list returns 0"""
    count = game_service.batch_delete_games([])
    assert count == 0


# ============================================================================
# Test: batch_update_games
# ============================================================================

def test_batch_update_games_success(game_service):
    """Test successful batch update"""
    with patch.object(game_service.game_repo, 'batch_update_by_gid') as mock_batch_update, \
         patch.object(game_service, 'invalidator') as mock_invalidator:

        # Setup mocks
        mock_batch_update.return_value = 2
        mock_invalidator.invalidate_pattern = MagicMock()

        # Call the method
        updates = {"name": "Updated"}
        count = game_service.batch_update_games([90000001, 90000002], updates)

        # Verify
        assert count == 2
        mock_batch_update.assert_called_once()


def test_batch_update_games_no_updates(game_service):
    """Test that batch update with no updates raises ValueError"""
    with pytest.raises(ValueError, match="No update fields provided"):
        game_service.batch_update_games([90000001], {})


# ============================================================================
# Test: Cache Invalidation
# ============================================================================

def test_create_game_invalidates_cache(game_service, test_game_entity):
    """Test that create_game invalidates cache"""
    from unittest.mock import PropertyMock

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'create') as mock_create, \
         patch.object(game_service, 'invalidator') as mock_invalidator, \
         patch.object(type(game_service), 'bloom_filter', new_callable=PropertyMock) as mock_bloom:

        # Setup mocks
        mock_find.return_value = None
        mock_create.return_value = test_game_entity
        mock_invalidator.invalidate_pattern = MagicMock()
        mock_bloom.return_value = MagicMock()

        # Call the method
        game_service.create_game(test_game_entity)

        # Verify cache was invalidated
        mock_invalidator.invalidate_pattern.assert_called_with("games.list")


def test_update_game_invalidates_cache(game_service, test_game_entity):
    """Test that update_game invalidates cache"""
    from unittest.mock import PropertyMock

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'update') as mock_update, \
         patch.object(game_service, 'invalidator') as mock_invalidator, \
         patch.object(game_service, 'get_game_by_gid') as mock_get, \
         patch.object(type(game_service), 'bloom_filter', new_callable=PropertyMock) as mock_bloom:

        # Setup mocks
        mock_find.return_value = test_game_entity
        mock_update.return_value = test_game_entity
        mock_get.return_value = test_game_entity
        mock_invalidator.invalidate_pattern = MagicMock()
        mock_bloom.return_value = MagicMock()

        # Call the method
        game_service.update_game(90000001, {"name": "Updated"})

        # Verify cache was invalidated
        mock_invalidator.invalidate_pattern.assert_any_call("games.list")
        mock_invalidator.invalidate_pattern.assert_any_call("games.detail:90000001")


def test_delete_game_invalidates_cache(game_service):
    """Test that delete_game invalidates cache"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'delete') as mock_delete, \
         patch.object(game_service, 'invalidator') as mock_invalidator:

        # Setup mocks
        mock_find.return_value = GameEntity(
            id=1,
            gid=90000001,
            name="Test Game",
            ods_db="test_ods",
            dwd_prefix="dwd"
        )
        mock_delete.return_value = True
        mock_invalidator.invalidate_pattern = MagicMock()

        # Call the method
        game_service.delete_game(90000001)

        # Verify cache was invalidated
        mock_invalidator.invalidate_pattern.assert_any_call("games.list")
        mock_invalidator.invalidate_pattern.assert_any_call("games.detail:90000001")


# ============================================================================
# Test: Bloom Filter Integration
# ============================================================================

def test_create_game_adds_to_bloom_filter(game_service, test_game_entity):
    """Test that create_game adds GID to Bloom Filter"""
    from unittest.mock import PropertyMock

    mock_bloom_obj = MagicMock()

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'create') as mock_create, \
         patch.object(game_service, 'invalidator') as mock_invalidator, \
         patch.object(type(game_service), 'bloom_filter', new_callable=PropertyMock) as mock_bloom_prop:

        # Setup mocks
        mock_find.return_value = None
        mock_create.return_value = test_game_entity
        mock_invalidator.invalidate_pattern = MagicMock()
        mock_bloom_prop.return_value = mock_bloom_obj

        # Call the method
        game_service.create_game(test_game_entity)

        # Verify Bloom Filter was updated
        mock_bloom_obj.add.assert_called_once_with("games:90000001")


# ============================================================================
# Test: Error Handling
# ============================================================================

def test_create_game_repository_error(game_service, test_game_entity):
    """Test that repository error is handled correctly"""
    from unittest.mock import PropertyMock

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'create') as mock_create, \
         patch.object(type(game_service), 'bloom_filter', new_callable=PropertyMock) as mock_bloom:

        # Setup mocks
        mock_find.return_value = None
        mock_create.return_value = None  # Create failed
        mock_bloom.return_value = MagicMock()

        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Failed to create game"):
            game_service.create_game(test_game_entity)


def test_update_game_repository_error(game_service, test_game_entity):
    """Test that repository error in update is handled correctly"""
    from unittest.mock import PropertyMock

    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service.game_repo, 'update') as mock_update, \
         patch.object(game_service, 'get_game_by_gid') as mock_get, \
         patch.object(type(game_service), 'bloom_filter', new_callable=PropertyMock) as mock_bloom:

        # Setup mocks
        mock_find.return_value = test_game_entity
        mock_update.return_value = test_game_entity
        mock_get.return_value = None  # Failed to retrieve updated game
        mock_bloom.return_value = MagicMock()

        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Failed to retrieve updated game"):
            game_service.update_game(90000001, {"name": "Updated"})


# ============================================================================
# Test: get_game_by_database_id
# ============================================================================

def test_get_game_by_database_id(game_service):
    """Test get_game_by_database_id returns Entity"""
    with patch.object(game_service.game_repo, 'find_by_id') as mock_find:
        mock_find.return_value = GameEntity(
            id=1,
            gid=90000001,
            name="Test Game",
            ods_db="test_ods",
            dwd_prefix="dwd"
        )

        # Call the method
        game = game_service.get_game_by_database_id(1)

        # Verify
        assert isinstance(game, GameEntity)
        assert game.id == 1
        assert game.gid == 90000001


# ============================================================================
# Test: check_deletion_impact
# ============================================================================

def test_check_deletion_impact_no_data(game_service):
    """Test deletion impact check for game with no associated data"""
    with patch('backend.core.utils.converters.fetch_one_as_dict') as mock_fetch:
        # Mock no associated data
        mock_fetch.side_effect = [
            {"count": 0},  # event_count
            {"count": 0},  # param_count
            {"count": 0},  # node_config_count
        ]

        # Call the method
        impact = game_service.check_deletion_impact(90000001)

        # Verify
        assert impact["game_gid"] == 90000001
        assert impact["event_count"] == 0
        assert impact["param_count"] == 0
        assert impact["node_config_count"] == 0
        assert impact["has_associated_data"] is False


def test_check_deletion_impact_with_data(game_service):
    """Test deletion impact check for game with associated data"""
    with patch('backend.core.utils.converters.fetch_one_as_dict') as mock_fetch:
        # Mock has associated data
        mock_fetch.side_effect = [
            {"count": 5},  # event_count
            {"count": 10},  # param_count
            {"count": 2},  # node_config_count
        ]

        # Call the method
        impact = game_service.check_deletion_impact(90000001)

        # Verify
        assert impact["game_gid"] == 90000001
        assert impact["event_count"] == 5
        assert impact["param_count"] == 10
        assert impact["node_config_count"] == 2
        assert impact["has_associated_data"] is True


# ============================================================================
# Test: cascade_delete_game
# ============================================================================

def test_cascade_delete_game_with_data_no_force(game_service):
    """Test cascade delete raises error when game has data and force=False"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service, 'check_deletion_impact') as mock_impact:

        # Setup mocks
        mock_find.return_value = GameEntity(
            id=1,
            gid=90000001,
            name="Test Game",
            ods_db="test_ods",
            dwd_prefix="dwd"
        )
        mock_impact.return_value = {
            "has_associated_data": True,
            "event_count": 5,
            "param_count": 10,
            "node_config_count": 2
        }

        # Call the method and expect ValueError
        with pytest.raises(ValueError, match="Set force=True to delete"):
            game_service.cascade_delete_game(90000001, force=False)


@pytest.mark.skip(reason="Requires database connection - better suited for integration tests")
def test_cascade_delete_game_with_data_force(game_service):
    """Test cascade delete succeeds when game has data and force=True"""
    with patch.object(game_service.game_repo, 'find_by_gid') as mock_find, \
         patch.object(game_service, 'check_deletion_impact') as mock_impact, \
         patch('backend.core.database.database.get_db_connection') as mock_get_conn:

        # Setup mocks
        mock_find.return_value = GameEntity(
            id=1,
            gid=90000001,
            name="Test Game",
            ods_db="test_ods",
            dwd_prefix="dwd"
        )
        mock_impact.return_value = {
            "has_associated_data": True,
            "event_count": 5,
            "param_count": 10,
            "node_config_count": 2
        }

        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = [1]  # Game exists

        # Call the method
        result = game_service.cascade_delete_game(90000001, force=True)

        # Verify
        assert result["success"] is True
        assert result["deleted_event_count"] == 5
        assert result["deleted_param_count"] == 10
        assert result["deleted_node_config_count"] == 2
        mock_conn.commit.assert_called()


# ============================================================================
# Test: get_games_with_detailed_stats
# ============================================================================

def test_get_games_with_detailed_stats(game_service):
    """Test get_games_with_detailed_stats returns list with stats"""
    with patch('backend.core.utils.converters.fetch_all_as_dict') as mock_fetch:
        mock_fetch.return_value = [
            {
                "id": 1,
                "gid": 90000001,
                "name": "Test Game",
                "ods_db": "test_ods",
                "icon_path": None,
                "created_at": None,
                "updated_at": None,
                "event_count": 5,
                "param_count": 10,
                "event_node_count": 2,
                "flow_template_count": 1
            }
        ]

        # Call the method
        games = game_service.get_games_with_detailed_stats()

        # Verify
        assert isinstance(games, list)
        assert len(games) == 1
        assert games[0]["gid"] == 90000001
        assert games[0]["event_count"] == 5
        assert games[0]["param_count"] == 10


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

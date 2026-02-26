#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for GameService

Tests for business logic including:
- Game CRUD operations
- Validation logic
- Cache integration
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.models.entities import GameEntity
from backend.services.games.game_service import GameService


class TestGameServiceInitialization:
    """Test GameService initialization"""

    def test_initialization(self):
        """Test service initializes correctly"""
        service = GameService()
        assert service.game_repo is not None
        assert service.cache is not None


class TestGameServiceGetByGid:
    """Test get_by_gid method"""

    @patch('backend.services.games.game_service.GameRepository')
    def test_get_by_gid_existing(self, mock_repo_class):
        """Test getting existing game by GID"""
        # Setup mock
        mock_repo = Mock()
        mock_game = GameEntity(
            id=1,
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods'
        )
        mock_repo.find_by_gid.return_value = mock_game
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        result = service.get_by_gid(90000001)

        # Verify
        assert result is not None
        assert result.gid == 90000001
        assert result.name == 'Test Game'
        mock_repo.find_by_gid.assert_called_once_with(90000001)

    @patch('backend.services.games.game_service.GameRepository')
    def test_get_by_gid_not_found(self, mock_repo_class):
        """Test getting non-existent game returns None"""
        # Setup mock
        mock_repo = Mock()
        mock_repo.find_by_gid.return_value = None
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        result = service.get_by_gid(99999999)

        # Verify
        assert result is None
        mock_repo.find_by_gid.assert_called_once_with(99999999)


class TestGameServiceCreate:
    """Test create method"""

    @patch('backend.services.games.game_service.GameRepository')
    def test_create_valid_game(self, mock_repo_class):
        """Test creating a valid game"""
        # Setup mock
        mock_repo = Mock()
        mock_repo.find_by_gid.return_value = None  # No existing game
        mock_repo.create.return_value = 1  # New ID
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        game_data = GameEntity(
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods'
        )
        result = service.create(game_data)

        # Verify
        assert result is not None
        assert result.gid == 90000001
        mock_repo.find_by_gid.assert_called_once()
        mock_repo.create.assert_called_once()

    @patch('backend.services.games.game_service.GameRepository')
    def test_create_duplicate_gid_raises_error(self, mock_repo_class):
        """Test creating game with duplicate GID raises error"""
        # Setup mock
        mock_repo = Mock()
        existing_game = GameEntity(
            id=1,
            gid=90000001,
            name='Existing Game',
            ods_db='ieu_ods'
        )
        mock_repo.find_by_gid.return_value = existing_game
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        game_data = GameEntity(
            gid=90000001,
            name='New Game',
            ods_db='ieu_ods'
        )

        # Verify raises error
        with pytest.raises(ValueError, match="Game gid .* already exists"):
            service.create(game_data)


class TestGameServiceUpdate:
    """Test update method"""

    @patch('backend.services.games.game_service.GameRepository')
    def test_update_existing_game(self, mock_repo_class):
        """Test updating existing game"""
        # Setup mock
        mock_repo = Mock()
        existing_game = GameEntity(
            id=1,
            gid=90000001,
            name='Old Name',
            ods_db='ieu_ods'
        )
        updated_game = GameEntity(
            id=1,
            gid=90000001,
            name='New Name',
            ods_db='ieu_ods'
        )
        mock_repo.find_by_id.return_value = existing_game
        mock_repo.update.return_value = updated_game
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        result = service.update(1, updated_game)

        # Verify
        assert result.name == 'New Name'
        mock_repo.find_by_id.assert_called_once_with(1)
        mock_repo.update.assert_called_once()

    @patch('backend.services.games.game_service.GameRepository')
    def test_update_nonexistent_game_raises_error(self, mock_repo_class):
        """Test updating non-existent game raises error"""
        # Setup mock
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        game_data = GameEntity(
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods'
        )

        # Verify raises error
        with pytest.raises(ValueError, match="Game not found"):
            service.update(999, game_data)


class TestGameServiceDelete:
    """Test delete method"""

    @patch('backend.services.games.game_service.GameRepository')
    def test_delete_existing_game(self, mock_repo_class):
        """Test deleting existing game"""
        # Setup mock
        mock_repo = Mock()
        existing_game = GameEntity(
            id=1,
            gid=90000001,
            name='Test Game',
            ods_db='ieu_ods'
        )
        mock_repo.find_by_id.return_value = existing_game
        mock_repo.delete.return_value = True
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        result = service.delete(1)

        # Verify
        assert result is True
        mock_repo.find_by_id.assert_called_once_with(1)
        mock_repo.delete.assert_called_once_with(1)

    @patch('backend.services.games.game_service.GameRepository')
    def test_delete_nonexistent_game(self, mock_repo_class):
        """Test deleting non-existent game returns False"""
        # Setup mock
        mock_repo = Mock()
        mock_repo.find_by_id.return_value = None
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        result = service.delete(999)

        # Verify
        assert result is False
        mock_repo.find_by_id.assert_called_once_with(999)
        mock_repo.delete.assert_not_called()


class TestGameServiceListAll:
    """Test list_all method"""

    @patch('backend.services.games.game_service.GameRepository')
    def test_list_all_returns_games(self, mock_repo_class):
        """Test listing all games"""
        # Setup mock
        mock_repo = Mock()
        games = [
            GameEntity(id=1, gid=90000001, name='Game 1', ods_db='ieu_ods'),
            GameEntity(id=2, gid=90000002, name='Game 2', ods_db='ieu_ods'),
            GameEntity(id=3, gid=90000003, name='Game 3', ods_db='ieu_ods')
        ]
        mock_repo.get_all.return_value = games
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        result = service.list_all()

        # Verify
        assert len(result) == 3
        assert result[0].name == 'Game 1'
        assert result[1].name == 'Game 2'
        assert result[2].name == 'Game 3'
        mock_repo.get_all.assert_called_once()


class TestGameServiceValidation:
    """Test validation logic in service"""

    @patch('backend.services.games.game_service.GameRepository')
    def test_validate_gid_unique(self, mock_repo_class):
        """Test GID uniqueness validation"""
        # Setup mock
        mock_repo = Mock()
        mock_repo.find_by_gid.return_value = None
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        is_valid = service.is_gid_unique(90000001)

        # Verify
        assert is_valid is True
        mock_repo.find_by_gid.assert_called_once_with(90000001)

    @patch('backend.services.games.game_service.GameRepository')
    def test_validate_gid_not_unique(self, mock_repo_class):
        """Test GID uniqueness check when GID exists"""
        # Setup mock
        mock_repo = Mock()
        existing_game = GameEntity(
            id=1,
            gid=90000001,
            name='Existing Game',
            ods_db='ieu_ods'
        )
        mock_repo.find_by_gid.return_value = existing_game
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()
        is_valid = service.is_gid_unique(90000001)

        # Verify
        assert is_valid is False


class TestGameServiceErrorHandling:
    """Test error handling"""

    @patch('backend.services.games.game_service.GameRepository')
    def test_handle_repository_exception(self, mock_repo_class):
        """Test service handles repository exceptions"""
        # Setup mock
        mock_repo = Mock()
        mock_repo.find_by_gid.side_effect = Exception("Database error")
        mock_repo_class.return_value = mock_repo

        # Execute
        service = GameService()

        # Should re-raise or handle error
        with pytest.raises(Exception, match="Database error"):
            service.get_by_gid(90000001)

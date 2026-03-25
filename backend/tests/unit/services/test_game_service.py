#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for GameService

Tests cover all public methods with ≥80% coverage target
Uses mock to avoid dependencies
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.models.entities import GameEntity
from backend.services.games.game_service import GameService


class TestGameService:
    """Test suite for GameService"""

    @pytest.fixture
    def service(self):
        """Create a GameService instance"""
        return GameService()

    @pytest.fixture
    def mock_game_entity(self):
        """Mock GameEntity"""
        return GameEntity(
            id=1,
            gid='10000147',
            name='Test Game',
            ods_db='ieu_ods',
            description='Test Description',
            dwd_prefix='dwd',
            icon_path=None,
            created_at='2026-01-01 00:00:00',
            updated_at='2026-01-01 00:00:00',
            event_count=10,
            param_count=50,
        )

    @pytest.fixture
    def mock_game_list(self):
        """Mock list of GameEntity"""
        return [
            GameEntity(
                id=1,
                gid='10000147',
                name='Game One',
                ods_db='ieu_ods',
                description='Description 1',
                dwd_prefix='dwd',
                icon_path=None,
                created_at='2026-01-01 00:00:00',
                updated_at='2026-01-01 00:00:00',
            ),
            GameEntity(
                id=2,
                gid='10000148',
                name='Game Two',
                ods_db='overseas_ods',
                description='Description 2',
                dwd_prefix='dwd',
                icon_path=None,
                created_at='2026-01-02 00:00:00',
                updated_at='2026-01-02 00:00:00',
            ),
        ]

    # ==================== get_games ====================

    @patch.object(GameService, '_get_repository')
    def test_get_games_success(self, mock_repo, service, mock_game_list):
        """Test successful get games"""
        mock_repo.return_value.find_all.return_value = mock_game_list

        result = service.get_games()

        assert len(result) == 2
        assert all(isinstance(game, GameEntity) for game in result)
        mock_repo.return_value.find_all.assert_called_once()

    @patch.object(GameService, '_get_repository')
    def test_get_games_empty(self, mock_repo, service):
        """Test get games with no results"""
        mock_repo.return_value.find_all.return_value = []

        result = service.get_games()

        assert result == []

    # ==================== get_game_by_gid ====================

    @patch.object(GameService, '_get_repository')
    def test_get_game_by_gid_success(self, mock_repo, service, mock_game_entity):
        """Test successful get game by gid"""
        mock_repo.return_value.find_by_gid.return_value = mock_game_entity

        result = service.get_game_by_gid('10000147')

        assert result is not None
        assert isinstance(result, GameEntity)
        assert result.gid == '10000147'
        mock_repo.return_value.find_by_gid.assert_called_once_with('10000147')

    @patch.object(GameService, '_get_repository')
    def test_get_game_by_gid_not_found(self, mock_repo, service):
        """Test get game by gid when not found"""
        mock_repo.return_value.find_by_gid.return_value = None

        result = service.get_game_by_gid('99999999')

        assert result is None

    # ==================== get_game_by_id ====================

    @patch.object(GameService, '_get_repository')
    def test_get_game_by_id_success(self, mock_repo, service, mock_game_entity):
        """Test successful get game by id"""
        mock_repo.return_value.find_by_id.return_value = mock_game_entity

        result = service.get_game_by_id(1)

        assert result is not None
        assert isinstance(result, GameEntity)
        assert result.id == 1

    @patch.object(GameService, '_get_repository')
    def test_get_game_by_id_not_found(self, mock_repo, service):
        """Test get game by id when not found"""
        mock_repo.return_value.find_by_id.return_value = None

        result = service.get_game_by_id(999)

        assert result is None

    # ==================== create_game ====================

    @patch.object(GameService, '_get_repository')
    def test_create_game_success(self, mock_repo, service, mock_game_entity):
        """Test successful game creation"""
        mock_repo.return_value.find_by_gid.return_value = None
        mock_repo.return_value.create.return_value = 1
        mock_repo.return_value.find_by_id.return_value = mock_game_entity

        game_data = {'gid': '10000147', 'name': 'New Game', 'ods_db': 'ieu_ods'}

        result = service.create_game(GameEntity(**game_data))

        assert result is not None
        assert isinstance(result, GameEntity)
        mock_repo.return_value.create.assert_called_once()

    @patch.object(GameService, '_get_repository')
    def test_create_game_duplicate_gid(self, mock_repo, service, mock_game_entity):
        """Test create game with duplicate gid"""
        mock_repo.return_value.find_by_gid.return_value = mock_game_entity

        game_data = {'gid': '10000147', 'name': 'Duplicate Game', 'ods_db': 'ieu_ods'}

        with pytest.raises(ValueError, match='Game gid 10000147 already exists'):
            service.create_game(GameEntity(**game_data))

    # ==================== update_game ====================

    @patch.object(GameService, '_get_repository')
    def test_update_game_success(self, mock_repo, service, mock_game_entity):
        """Test successful game update"""
        mock_repo.return_value.find_by_gid.return_value = mock_game_entity
        mock_repo.return_value.update.return_value = mock_game_entity

        update_data = {'name': 'Updated Name', 'description': 'Updated Description'}

        result = service.update_game('10000147', update_data)

        assert result is not None
        assert isinstance(result, GameEntity)
        mock_repo.return_value.update.assert_called_once()

    @patch.object(GameService, '_get_repository')
    def test_update_game_not_found(self, mock_repo, service):
        """Test update game when not found"""
        mock_repo.return_value.find_by_gid.return_value = None

        update_data = {'name': 'Updated Name'}

        result = service.update_game('99999999', update_data)

        assert result is None

    # ==================== delete_game ====================

    @patch.object(GameService, '_get_repository')
    def test_delete_game_success(self, mock_repo, service):
        """Test successful game deletion"""
        mock_repo.return_value.find_by_gid.return_value = Mock()
        mock_repo.return_value.delete.return_value = True

        result = service.delete_game('10000147')

        assert result is True
        mock_repo.return_value.delete.assert_called_once_with('10000147')

    @patch.object(GameService, '_get_repository')
    def test_delete_game_not_found(self, mock_repo, service):
        """Test delete game when not found"""
        mock_repo.return_value.find_by_gid.return_value = None

        result = service.delete_game('99999999')

        assert result is False

    # ==================== get_games_with_stats ====================

    @patch.object(GameService, '_get_repository')
    def test_get_games_with_stats(self, mock_repo, service, mock_game_list):
        """Test get games with statistics"""
        mock_repo.return_value.get_all_with_stats.return_value = mock_game_list

        result = service.get_games_with_stats()

        assert len(result) == 2
        mock_repo.return_value.get_all_with_stats.assert_called_once()

    # ==================== search_games ====================

    @patch.object(GameService, '_get_repository')
    def test_search_games_by_name(self, mock_repo, service, mock_game_list):
        """Test search games by name"""
        mock_repo.return_value.search_by_name.return_value = mock_game_list

        result = service.search_games(name_pattern='%Game%')

        assert len(result) == 2
        mock_repo.return_value.search_by_name.assert_called_once_with('%Game%')

    @patch.object(GameService, '_get_repository')
    def test_search_games_by_ods_db(self, mock_repo, service, mock_game_list):
        """Test search games by ODS database"""
        mock_repo.return_value.find_by_ods_db.return_value = [mock_game_list[0]]

        result = service.search_games(ods_db='ieu_ods')

        assert len(result) >= 1
        mock_repo.return_value.find_by_ods_db.assert_called_once_with('ieu_ods')

    # ==================== batch_create_games ====================

    @patch.object(GameService, '_get_repository')
    def test_batch_create_games_success(self, mock_repo, service):
        """Test successful batch create"""
        mock_repo.return_value.find_by_gid.return_value = None
        mock_repo.return_value.create_batch.return_value = [1, 2]

        games_data = [
            GameEntity(**{'gid': '10000147', 'name': 'Game 1', 'ods_db': 'ieu_ods'}),
            GameEntity(**{'gid': '10000148', 'name': 'Game 2', 'ods_db': 'ieu_ods'}),
        ]

        result = service.batch_create_games(games_data)

        assert len(result) == 2
        mock_repo.return_value.create_batch.assert_called_once()

    @patch.object(GameService, '_get_repository')
    def test_batch_create_games_with_duplicates(self, mock_repo, service):
        """Test batch create with duplicate gids"""
        # First call returns existing (duplicate), second call returns None (new)
        mock_repo.return_value.find_by_gid.side_effect = [Mock(), None]
        mock_repo.return_value.create_batch.return_value = [2]

        games_data = [
            GameEntity(**{'gid': '10000147', 'name': 'Game 1', 'ods_db': 'ieu_ods'}),
            GameEntity(**{'gid': '10000148', 'name': 'Game 2', 'ods_db': 'ieu_ods'}),
        ]

        with pytest.raises(ValueError, match='Game gid 10000147 already exists'):
            service.batch_create_games(games_data)

    # ==================== batch_delete_games ====================

    @patch.object(GameService, '_get_repository')
    def test_batch_delete_games_success(self, mock_repo, service):
        """Test successful batch delete"""
        mock_repo.return_value.batch_delete.return_value = 3

        result = service.batch_delete_games([10000147, 10000148, 10000149])

        assert result == 3
        mock_repo.return_value.batch_delete.assert_called_once()

    # ==================== batch_update_games ====================

    @patch.object(GameService, '_get_repository')
    def test_batch_update_games_success(self, mock_repo, service):
        """Test successful batch update"""
        mock_repo.return_value.batch_update_by_gid.return_value = 2

        updates = {'name': 'Updated Name'}

        result = service.batch_update_games([10000147, 10000148], updates)

        assert result == 2
        mock_repo.return_value.batch_update_by_gid.assert_called_once()

    # ==================== get_game_categories_summary ====================

    @patch.object(GameService, '_get_repository')
    def test_get_game_categories_summary(self, mock_repo, service):
        """Test get game categories summary"""
        mock_repo.return_value.get_game_categories_summary.return_value = [
            {'category_id': 1, 'category_name': 'Combat', 'event_count': 5},
            {'category_id': 2, 'category_name': 'Economy', 'event_count': 3},
        ]

        result = service.get_game_categories_summary('10000147')

        assert len(result) == 2
        assert result[0]['category_name'] == 'Combat'
        mock_repo.return_value.get_game_categories_summary.assert_called_once_with('10000147')

    # ==================== game_exists ====================

    @patch.object(GameService, '_get_repository')
    def test_game_exists_true(self, mock_repo, service):
        """Test game exists returns True"""
        mock_repo.return_value.exists_by_gid.return_value = True

        result = service.game_exists('10000147')

        assert result is True

    @patch.object(GameService, '_get_repository')
    def test_game_exists_false(self, mock_repo, service):
        """Test game exists returns False"""
        mock_repo.return_value.exists_by_gid.return_value = False

        result = service.game_exists('99999999')

        assert result is False

    # ==================== validate_game_data ====================

    def test_validate_game_data_valid(self, service):
        """Test validate game data with valid input"""
        game_data = {'gid': '10000147', 'name': 'Valid Game', 'ods_db': 'ieu_ods'}

        # Should not raise exception
        service.validate_game_data(GameEntity(**game_data))

    def test_validate_game_data_missing_required(self, service):
        """Test validate game data with missing required fields"""
        game_data = {
            'gid': '10000147'
            # Missing 'name' and 'ods_db'
        }

        with pytest.raises(Exception):  # Pydantic ValidationError
            service.validate_game_data(GameEntity(**game_data))

    def test_validate_game_data_invalid_ods_db(self, service):
        """Test validate game data with invalid ODS database"""
        game_data = {
            'gid': '10000147',
            'name': 'Invalid Game',
            'ods_db': 'invalid_db',  # Should be 'ieu_ods' or 'overseas_ods'
        }

        with pytest.raises(Exception):  # Pydantic ValidationError
            service.validate_game_data(GameEntity(**game_data))

    # ==================== get_games_for_export ====================

    @patch.object(GameService, '_get_repository')
    def test_get_games_for_export(self, mock_repo, service, mock_game_list):
        """Test get games for export"""
        mock_repo.return_value.find_all.return_value = mock_game_list

        result = service.get_games_for_export()

        assert len(result) == 2
        # Verify export format
        assert all('gid' in game.model_dump() for game in result)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for GameRepository

Tests cover all public methods with ≥80% coverage target
Uses mock to avoid database dependencies
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from backend.models.repositories.games import GameRepository
from backend.models.entities import GameEntity


class TestGameRepository:
    """Test suite for GameRepository"""

    @pytest.fixture
    def repository(self):
        """Create a GameRepository instance"""
        return GameRepository()

    @pytest.fixture
    def mock_game_data(self):
        """Mock game data"""
        return {
            'id': 1,
            'gid': '10000147',
            'name': 'Test Game',
            'ods_db': 'ieu_ods',
            'description': 'Test Description',
            'dwd_prefix': 'dwd',
            'icon_path': None,
            'created_at': '2026-01-01 00:00:00',
            'updated_at': '2026-01-01 00:00:00',
        }

    @pytest.fixture
    def mock_game_list_data(self):
        """Mock list of game data"""
        return [
            {
                'id': 1,
                'gid': '10000147',
                'name': 'Game One',
                'ods_db': 'ieu_ods',
                'description': 'Description 1',
                'dwd_prefix': 'dwd',
                'icon_path': None,
                'created_at': '2026-01-01 00:00:00',
                'updated_at': '2026-01-01 00:00:00',
            },
            {
                'id': 2,
                'gid': '10000148',
                'name': 'Game Two',
                'ods_db': 'overseas_ods',
                'description': 'Description 2',
                'dwd_prefix': 'dwd',
                'icon_path': None,
                'created_at': '2026-01-02 00:00:00',
                'updated_at': '2026-01-02 00:00:00',
            },
        ]

    # ==================== find_by_gid ====================

    @patch('backend.models.repositories.games.fetch_one_as_dict')
    def test_find_by_gid_success(self, mock_fetch, repository, mock_game_data):
        """Test successful find by gid"""
        mock_fetch.return_value = mock_game_data

        result = repository.find_by_gid('10000147')

        assert result is not None
        assert isinstance(result, GameEntity)
        assert result.gid == '10000147'
        assert result.name == 'Test Game'
        mock_fetch.assert_called_once_with("SELECT * FROM games WHERE gid = ?", ('10000147',))

    @patch('backend.models.repositories.games.fetch_one_as_dict')
    def test_find_by_gid_not_found(self, mock_fetch, repository):
        """Test find by gid when not found"""
        mock_fetch.return_value = None

        result = repository.find_by_gid('99999999')

        assert result is None
        mock_fetch.assert_called_once()

    # ==================== find_all ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_find_all_success(self, mock_fetch, repository, mock_game_list_data):
        """Test successful find all"""
        mock_fetch.return_value = mock_game_list_data

        result = repository.find_all()

        assert len(result) == 2
        assert all(isinstance(game, GameEntity) for game in result)
        assert result[0].name == 'Game One'
        assert result[1].name == 'Game Two'

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_find_all_empty(self, mock_fetch, repository):
        """Test find all with no results"""
        mock_fetch.return_value = []

        result = repository.find_all()

        assert result == []

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_find_all_filters_invalid_data(self, mock_fetch, repository):
        """Test find all filters out invalid data"""
        mock_fetch.return_value = [
            {'id': 1, 'gid': '10000147', 'name': 'Valid Game', 'ods_db': 'ieu_ods'},
            {'id': 2, 'gid': None, 'name': 'Invalid Game'},  # Missing required fields
        ]

        result = repository.find_all()

        # Should only return valid games
        assert len(result) == 1
        assert result[0].gid == '10000147'

    # ==================== find_by_id ====================

    @patch('backend.models.repositories.games.fetch_one_as_dict')
    def test_find_by_id_success(self, mock_fetch, repository, mock_game_data):
        """Test successful find by id"""
        mock_fetch.return_value = mock_game_data

        result = repository.find_by_id(1)

        assert result is not None
        assert isinstance(result, GameEntity)
        assert result.id == 1
        mock_fetch.assert_called_once_with("SELECT * FROM games WHERE id = ?", (1,))

    @patch('backend.models.repositories.games.fetch_one_as_dict')
    def test_find_by_id_not_found(self, mock_fetch, repository):
        """Test find by id when not found"""
        mock_fetch.return_value = None

        result = repository.find_by_id(999)

        assert result is None

    # ==================== get_all_with_event_count ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_get_all_with_event_count(self, mock_fetch, repository):
        """Test get all with event count"""
        mock_fetch.return_value = [
            {
                'id': 1,
                'gid': '10000147',
                'name': 'Game One',
                'ods_db': 'ieu_ods',
                'event_count': 10,
            },
            {'id': 2, 'gid': '10000148', 'name': 'Game Two', 'ods_db': 'ieu_ods', 'event_count': 5},
        ]

        result = repository.get_all_with_event_count()

        assert len(result) == 2
        assert result[0].event_count == 10
        assert result[1].event_count == 5

    # ==================== get_all_with_stats ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_get_all_with_stats(self, mock_fetch, repository):
        """Test get all with detailed stats"""
        mock_fetch.return_value = [
            {
                'id': 1,
                'gid': '10000147',
                'name': 'Game One',
                'ods_db': 'ieu_ods',
                'event_count': 10,
                'param_count': 50,
                'last_event_update': '2026-01-01 12:00:00',
            }
        ]

        result = repository.get_all_with_stats()

        assert len(result) == 1
        assert result[0].event_count == 10
        assert result[0].param_count == 50

    # ==================== batch_delete ====================

    @patch('backend.models.repositories.games.get_db_connection')
    def test_batch_delete_success(self, mock_get_conn, repository):
        """Test successful batch delete"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 3
        mock_get_conn.return_value = mock_conn

        result = repository.batch_delete([10000147, 10000148, 10000149])

        assert result == 3
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('backend.models.repositories.games.get_db_connection')
    def test_batch_delete_empty_list(self, mock_get_conn, repository):
        """Test batch delete with empty list"""
        result = repository.batch_delete([])

        assert result == 0
        mock_get_conn.assert_not_called()

    # ==================== update ====================

    @patch('backend.models.repositories.games.get_db_connection')
    @patch.object(GameRepository, 'find_by_gid')
    def test_update_success(self, mock_find, mock_get_conn, repository, mock_game_data):
        """Test successful update"""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_find.return_value = GameEntity(**mock_game_data)

        result = repository.update('10000147', {'name': 'Updated Name'})

        assert result is not None
        assert isinstance(result, GameEntity)
        mock_conn.commit.assert_called_once()
        mock_find.assert_called_with('10000147')

    def test_update_empty_data(self, repository):
        """Test update with empty data"""
        result = repository.update('10000147', {})

        assert result is None

    # ==================== delete ====================

    @patch('backend.models.repositories.games.get_db_connection')
    def test_delete_success(self, mock_get_conn, repository):
        """Test successful delete"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_get_conn.return_value = mock_conn

        result = repository.delete('10000147')

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('backend.models.repositories.games.get_db_connection')
    def test_delete_not_found(self, mock_get_conn, repository):
        """Test delete when game not found"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        mock_get_conn.return_value = mock_conn

        result = repository.delete('99999999')

        assert result is False

    # ==================== batch_update_by_gid ====================

    @patch('backend.models.repositories.games.get_db_connection')
    def test_batch_update_by_gid_success(self, mock_get_conn, repository):
        """Test successful batch update"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 2
        mock_get_conn.return_value = mock_conn

        result = repository.batch_update_by_gid([10000147, 10000148], {'name': 'Updated Name'})

        assert result == 2
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_batch_update_by_gid_empty_inputs(self, repository):
        """Test batch update with empty inputs"""
        result = repository.batch_update_by_gid([], {'name': 'Updated'})
        assert result == 0

        result = repository.batch_update_by_gid([10000147], {})
        assert result == 0

    # ==================== find_by_ods_db ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_find_by_ods_db(self, mock_fetch, repository, mock_game_list_data):
        """Test find by ODS database"""
        mock_fetch.return_value = [mock_game_list_data[0]]

        result = repository.find_by_ods_db('ieu_ods')

        assert len(result) >= 1
        mock_fetch.assert_called_once_with(
            "SELECT * FROM games WHERE ods_db = ? ORDER BY name", ('ieu_ods',)
        )

    # ==================== search_by_name ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_search_by_name(self, mock_fetch, repository, mock_game_list_data):
        """Test search by name pattern"""
        mock_fetch.return_value = mock_game_list_data

        result = repository.search_by_name('%Game%')

        assert len(result) >= 1
        mock_fetch.assert_called_once()

    # ==================== get_game_categories_summary ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_get_game_categories_summary(self, mock_fetch, repository):
        """Test get game categories summary"""
        mock_fetch.return_value = [{'category_id': 1, 'category_name': 'Combat', 'event_count': 5}]

        result = repository.get_game_categories_summary(10000147)

        assert len(result) == 1
        assert result[0]['category_name'] == 'Combat'

    # ==================== exists_by_gid ====================

    @patch.object(GameRepository, 'find_by_gid')
    def test_exists_by_gid_true(self, mock_find, repository, mock_game_data):
        """Test exists by gid returns True"""
        mock_find.return_value = GameEntity(**mock_game_data)

        result = repository.exists_by_gid('10000147')

        assert result is True

    @patch.object(GameRepository, 'find_by_gid')
    def test_exists_by_gid_false(self, mock_find, repository):
        """Test exists by gid returns False"""
        mock_find.return_value = None

        result = repository.exists_by_gid('99999999')

        assert result is False

    # ==================== get_game_for_update ====================

    @patch('backend.models.repositories.games.fetch_one_as_dict')
    def test_get_game_for_update(self, mock_fetch, repository, mock_game_data):
        """Test get game for update"""
        mock_fetch.return_value = mock_game_data

        result = repository.get_game_for_update(1)

        assert result is not None
        assert isinstance(result, GameEntity)

    # ==================== get_gids_by_list ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_get_gids_by_list(self, mock_fetch, repository):
        """Test get gids by list"""
        mock_fetch.return_value = [{'gid': '10000147'}, {'gid': '10000148'}]

        result = repository.get_gids_by_list(['10000147', '10000148', '10000149'])

        assert len(result) == 2
        assert '10000147' in result
        assert '10000148' in result

    def test_get_gids_by_list_empty(self, repository):
        """Test get gids by list with empty input"""
        result = repository.get_gids_by_list([])

        assert result == []

    # ==================== get_by_ids ====================

    @patch('backend.models.repositories.games.fetch_all_as_dict')
    def test_get_by_ids(self, mock_fetch, repository, mock_game_list_data):
        """Test get by ids"""
        mock_fetch.return_value = mock_game_list_data

        result = repository.get_by_ids([1, 2])

        assert len(result) == 2
        assert all(isinstance(game, GameEntity) for game in result)

    def test_get_by_ids_empty(self, repository):
        """Test get by ids with empty list"""
        result = repository.get_by_ids([])

        assert result == []

    # ==================== delete_batch ====================

    @patch('backend.models.repositories.games.get_db_connection')
    def test_delete_batch_success(self, mock_get_conn, repository):
        """Test successful batch delete by ids"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 2
        mock_get_conn.return_value = mock_conn

        result = repository.delete_batch([1, 2])

        assert result == 2
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_delete_batch_empty(self, repository):
        """Test delete batch with empty list"""
        result = repository.delete_batch([])

        assert result == 0

    # ==================== create_batch ====================

    @patch('backend.models.repositories.games.get_db_connection')
    def test_create_batch_success(self, mock_get_conn, repository):
        """Test successful batch create"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = [(1,), (2,)]
        mock_get_conn.return_value = mock_conn

        games_data = [
            {'gid': '10000147', 'name': 'Game 1', 'ods_db': 'ieu_ods'},
            {'gid': '10000148', 'name': 'Game 2', 'ods_db': 'ieu_ods'},
        ]

        result = repository.create_batch(games_data)

        assert len(result) == 2
        assert result == [1, 2]
        mock_cursor.executemany.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_create_batch_empty(self, repository):
        """Test create batch with empty list"""
        result = repository.create_batch([])

        assert result == []

    @patch('backend.models.repositories.games.get_db_connection')
    def test_create_batch_rollback_on_error(self, mock_get_conn, repository):
        """Test create batch rolls back on error"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.executemany.side_effect = Exception("DB Error")
        mock_get_conn.return_value = mock_conn

        games_data = [{'gid': '10000147', 'name': 'Game 1', 'ods_db': 'ieu_ods'}]

        with pytest.raises(Exception):
            repository.create_batch(games_data)

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

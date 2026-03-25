#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for EventRepository

Tests cover all public methods with ≥80% coverage target
Uses mock to avoid database dependencies
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.models.entities import EventEntity
from backend.models.repositories.events import EventRepository


class TestEventRepository:
    """Test suite for EventRepository"""

    @pytest.fixture
    def repository(self):
        """Create an EventRepository instance"""
        return EventRepository()

    @pytest.fixture
    def mock_event_data(self):
        """Mock event data"""
        return {
            'id': 1,
            'event_name': 'login',
            'game_gid': 10000147,
            'game_name': 'Test Game',
            'ods_db': 'ieu_ods',
            'category_id': 1,
            'category_name': 'Authentication',
            'table_name': 'ieu_ods.ods_10000147_all_view',
            'description': 'User login event',
            'created_at': '2026-01-01 00:00:00',
            'updated_at': '2026-01-01 00:00:00',
        }

    @pytest.fixture
    def mock_event_list_data(self):
        """Mock list of event data"""
        return [
            {
                'id': 1,
                'event_name': 'login',
                'game_gid': 10000147,
                'game_name': 'Test Game',
                'ods_db': 'ieu_ods',
                'category_name': 'Authentication',
                'table_name': 'ieu_ods.ods_10000147_all_view',
                'param_count': 5,
            },
            {
                'id': 2,
                'event_name': 'logout',
                'game_gid': 10000147,
                'game_name': 'Test Game',
                'ods_db': 'ieu_ods',
                'category_name': 'Authentication',
                'table_name': 'ieu_ods.ods_10000147_all_view',
                'param_count': 3,
            },
        ]

    # ==================== find_by_id ====================

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_find_by_id_success(self, mock_fetch, repository, mock_event_data):
        """Test successful find by id"""
        mock_fetch.return_value = mock_event_data

        result = repository.find_by_id(1)

        assert result is not None
        assert isinstance(result, EventEntity)
        assert result.id == 1
        assert result.event_name == 'login'
        mock_fetch.assert_called_once_with("SELECT * FROM log_events WHERE id = ?", (1,))

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_find_by_id_not_found(self, mock_fetch, repository):
        """Test find by id when not found"""
        mock_fetch.return_value = None

        result = repository.find_by_id(999)

        assert result is None
        mock_fetch.assert_called_once()

    # ==================== find_by_name ====================

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_find_by_name_success(self, mock_fetch, repository, mock_event_data):
        """Test successful find by name and game gid"""
        mock_fetch.return_value = mock_event_data

        result = repository.find_by_name('login', 10000147)

        assert result is not None
        assert isinstance(result, EventEntity)
        assert result.event_name == 'login'
        assert result.game_gid == 10000147
        mock_fetch.assert_called_once()

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_find_by_name_not_found(self, mock_fetch, repository):
        """Test find by name when not found"""
        mock_fetch.return_value = None

        result = repository.find_by_name('nonexistent', 10000147)

        assert result is None

    # ==================== find_by_game_gid ====================

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_find_by_game_gid_success(self, mock_fetch, repository, mock_event_list_data):
        """Test successful find by game gid with pagination"""
        mock_fetch.return_value = mock_event_list_data

        result = repository.find_by_game_gid(10000147, page=1, per_page=20)

        assert len(result) == 2
        assert all(isinstance(event, EventEntity) for event in result)
        assert result[0].event_name == 'login'
        assert result[1].event_name == 'logout'
        mock_fetch.assert_called_once()

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_find_by_game_gid_pagination(self, mock_fetch, repository):
        """Test pagination works correctly"""
        mock_fetch.return_value = []

        # First page
        result = repository.find_by_game_gid(10000147, page=1, per_page=10)
        args = mock_fetch.call_args[0]
        assert args[2] == 0  # offset = (1-1) * 10

        # Second page
        result = repository.find_by_game_gid(10000147, page=2, per_page=10)
        args = mock_fetch.call_args[0]
        assert args[2] == 10  # offset = (2-1) * 10

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_find_by_game_gid_empty(self, mock_fetch, repository):
        """Test find by game gid with no results"""
        mock_fetch.return_value = []

        result = repository.find_by_game_gid(99999999)

        assert result == []

    # ==================== find_all ====================

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_find_all_with_filter(self, mock_fetch, repository, mock_event_list_data):
        """Test find all with game filter"""
        mock_fetch.return_value = mock_event_list_data

        result = repository.find_all(game_gid=10000147)

        assert len(result) == 2
        mock_fetch.assert_called_once()
        # Verify query includes game filter
        query = mock_fetch.call_args[0][0]
        assert 'WHERE g.gid = ?' in query

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_find_all_without_filter(self, mock_fetch, repository, mock_event_list_data):
        """Test find all without game filter"""
        mock_fetch.return_value = mock_event_list_data

        result = repository.find_all()

        assert len(result) == 2
        mock_fetch.assert_called_once()
        # Verify query doesn't include WHERE clause
        query = mock_fetch.call_args[0][0]
        assert 'WHERE' not in query

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_find_all_empty(self, mock_fetch, repository):
        """Test find all with no results"""
        mock_fetch.return_value = []

        result = repository.find_all()

        assert result == []

    # ==================== count_by_game_gid ====================

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_count_by_game_gid_success(self, mock_fetch, repository):
        """Test successful count by game gid"""
        mock_fetch.return_value = {'total': 42}

        result = repository.count_by_game_gid(10000147)

        assert result == 42
        mock_fetch.assert_called_once()

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_count_by_game_gid_zero(self, mock_fetch, repository):
        """Test count by game gid with no events"""
        mock_fetch.return_value = {'total': 0}

        result = repository.count_by_game_gid(10000147)

        assert result == 0

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_count_by_game_gid_none(self, mock_fetch, repository):
        """Test count by game gid with None result"""
        mock_fetch.return_value = None

        result = repository.count_by_game_gid(10000147)

        assert result == 0

    # ==================== get_with_parameters ====================

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_get_with_parameters_success(
        self, mock_fetch_all, mock_fetch_one, repository, mock_event_data
    ):
        """Test successful get with parameters"""
        mock_fetch_one.return_value = mock_event_data
        mock_fetch_all.return_value = [
            {'id': 1, 'param_name': 'user_id', 'param_type': 'base'},
            {'id': 2, 'param_name': 'zone_id', 'param_type': 'param'},
        ]

        result = repository.get_with_parameters(1)

        assert result is not None
        assert isinstance(result, dict)
        assert 'event' in result
        assert 'parameters' in result
        assert len(result['parameters']) == 2

    @patch('backend.models.repositories.events.fetch_one_as_dict')
    def test_get_with_parameters_not_found(self, mock_fetch, repository):
        """Test get with parameters when event not found"""
        mock_fetch.return_value = None

        result = repository.get_with_parameters(999)

        assert result is None

    # ==================== create ====================

    @patch('backend.models.repositories.events.get_db_connection')
    def test_create_success(self, mock_get_conn, repository):
        """Test successful event creation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        mock_get_conn.return_value = mock_conn

        event_data = {
            'event_name': 'test_event',
            'game_gid': 10000147,
            'table_name': 'ieu_ods.ods_10000147_all_view',
            'category_id': 1,
        }

        result = repository.create(event_data)

        assert result == 123
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('backend.models.repositories.events.get_db_connection')
    def test_create_failure(self, mock_get_conn, repository):
        """Test event creation with error"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")
        mock_get_conn.return_value = mock_conn

        event_data = {'event_name': 'test_event', 'game_gid': 10000147}

        with pytest.raises(Exception):
            repository.create(event_data)

        mock_conn.rollback.assert_called_once()

    # ==================== update ====================

    @patch('backend.models.repositories.events.get_db_connection')
    def test_update_success(self, mock_get_conn, repository):
        """Test successful event update"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_get_conn.return_value = mock_conn

        result = repository.update(1, {'event_name': 'updated_event'})

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('backend.models.repositories.events.get_db_connection')
    def test_update_not_found(self, mock_get_conn, repository):
        """Test update when event not found"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        mock_get_conn.return_value = mock_conn

        result = repository.update(999, {'event_name': 'updated_event'})

        assert result is False

    def test_update_empty_data(self, repository):
        """Test update with empty data"""
        result = repository.update(1, {})

        assert result is False

    # ==================== delete ====================

    @patch('backend.models.repositories.events.get_db_connection')
    def test_delete_success(self, mock_get_conn, repository):
        """Test successful event deletion"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1
        mock_get_conn.return_value = mock_conn

        result = repository.delete(1)

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('backend.models.repositories.events.get_db_connection')
    def test_delete_not_found(self, mock_get_conn, repository):
        """Test delete when event not found"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0
        mock_get_conn.return_value = mock_conn

        result = repository.delete(999)

        assert result is False

    # ==================== create_batch ====================

    @patch('backend.models.repositories.events.get_db_connection')
    def test_create_batch_success(self, mock_get_conn, repository):
        """Test successful batch creation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 1
        mock_get_conn.return_value = mock_conn

        events_data = [
            {
                'event_name': 'event1',
                'game_gid': 10000147,
                'table_name': 'ieu_ods.ods_10000147_all_view',
            },
            {
                'event_name': 'event2',
                'game_gid': 10000147,
                'table_name': 'ieu_ods.ods_10000147_all_view',
            },
        ]

        result = repository.create_batch(events_data)

        assert len(result) == 2
        mock_cursor.executemany.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_create_batch_empty(self, repository):
        """Test create batch with empty list"""
        result = repository.create_batch([])

        assert result == []

    @patch('backend.models.repositories.events.get_db_connection')
    def test_create_batch_rollback_on_error(self, mock_get_conn, repository):
        """Test create batch rolls back on error"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.executemany.side_effect = Exception("DB Error")
        mock_get_conn.return_value = mock_conn

        events_data = [{'event_name': 'event1', 'game_gid': 10000147}]

        with pytest.raises(Exception):
            repository.create_batch(events_data)

        mock_conn.rollback.assert_called_once()

    # ==================== batch_delete_by_game ====================

    @patch('backend.models.repositories.events.get_db_connection')
    def test_batch_delete_by_game_success(self, mock_get_conn, repository):
        """Test successful batch delete by game"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 5
        mock_get_conn.return_value = mock_conn

        result = repository.batch_delete_by_game(10000147)

        assert result == 5
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    # ==================== search_by_name ====================

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_search_by_name(self, mock_fetch, repository, mock_event_list_data):
        """Test search by name pattern"""
        mock_fetch.return_value = mock_event_list_data

        result = repository.search_by_name('log', 10000147)

        assert len(result) >= 1
        mock_fetch.assert_called_once()

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_search_by_name_empty(self, mock_fetch, repository):
        """Test search by name with no results"""
        mock_fetch.return_value = []

        result = repository.search_by_name('nonexistent', 10000147)

        assert result == []

    # ==================== get_by_category ====================

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_get_by_category(self, mock_fetch, repository, mock_event_list_data):
        """Test get events by category"""
        mock_fetch.return_value = mock_event_list_data

        result = repository.get_by_category(1, 10000147)

        assert len(result) >= 1
        mock_fetch.assert_called_once()

    # ==================== get_event_stats_by_game ====================

    @patch('backend.models.repositories.events.fetch_all_as_dict')
    def test_get_event_stats_by_game(self, mock_fetch, repository):
        """Test get event stats by game"""
        mock_fetch.return_value = [
            {'category_name': 'Authentication', 'event_count': 5},
            {'category_name': 'Combat', 'event_count': 10},
        ]

        result = repository.get_event_stats_by_game(10000147)

        assert len(result) == 2
        assert result[0]['category_name'] == 'Authentication'
        assert result[1]['event_count'] == 10

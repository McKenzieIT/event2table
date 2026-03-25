#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for EventService

Tests cover all public methods with ≥80% coverage target
Uses mock to avoid dependencies
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.models.entities import EventEntity
from backend.services.events.event_service import EventService


class TestEventService:
    """Test suite for EventService"""

    @pytest.fixture
    def service(self):
        """Create an EventService instance"""
        return EventService()

    @pytest.fixture
    def mock_event_entity(self):
        """Mock EventEntity"""
        return EventEntity(
            id=1,
            event_name='login',
            game_gid=10000147,
            game_name='Test Game',
            ods_db='ieu_ods',
            category_id=1,
            category_name='Authentication',
            table_name='ieu_ods.ods_10000147_all_view',
            description='User login event',
            created_at='2026-01-01 00:00:00',
            updated_at='2026-01-01 00:00:00',
        )

    @pytest.fixture
    def mock_event_list(self):
        """Mock list of EventEntity"""
        return [
            EventEntity(
                id=1,
                event_name='login',
                game_gid=10000147,
                game_name='Test Game',
                ods_db='ieu_ods',
                category_name='Authentication',
                table_name='ieu_ods.ods_10000147_all_view',
                created_at='2026-01-01 00:00:00',
                updated_at='2026-01-01 00:00:00',
            ),
            EventEntity(
                id=2,
                event_name='logout',
                game_gid=10000147,
                game_name='Test Game',
                ods_db='ieu_ods',
                category_name='Authentication',
                table_name='ieu_ods.ods_10000147_all_view',
                created_at='2026-01-01 00:00:00',
                updated_at='2026-01-01 00:00:00',
            ),
        ]

    # ==================== get_events ====================

    @patch.object(EventService, '_get_repository')
    def test_get_events_success(self, mock_repo, service, mock_event_list):
        """Test successful get events"""
        mock_repo.return_value.find_all.return_value = mock_event_list

        result = service.get_events()

        assert len(result) == 2
        assert all(isinstance(event, EventEntity) for event in result)

    @patch.object(EventService, '_get_repository')
    def test_get_events_by_game(self, mock_repo, service, mock_event_list):
        """Test get events filtered by game"""
        mock_repo.return_value.find_all.return_value = mock_event_list

        result = service.get_events(game_gid=10000147)

        assert len(result) == 2
        mock_repo.return_value.find_all.assert_called_once_with(game_gid=10000147)

    # ==================== get_event_by_id ====================

    @patch.object(EventService, '_get_repository')
    def test_get_event_by_id_success(self, mock_repo, service, mock_event_entity):
        """Test successful get event by id"""
        mock_repo.return_value.find_by_id.return_value = mock_event_entity

        result = service.get_event_by_id(1)

        assert result is not None
        assert isinstance(result, EventEntity)
        assert result.id == 1

    @patch.object(EventService, '_get_repository')
    def test_get_event_by_id_not_found(self, mock_repo, service):
        """Test get event by id when not found"""
        mock_repo.return_value.find_by_id.return_value = None

        result = service.get_event_by_id(999)

        assert result is None

    # ==================== get_event_by_name ====================

    @patch.object(EventService, '_get_repository')
    def test_get_event_by_name_success(self, mock_repo, service, mock_event_entity):
        """Test successful get event by name"""
        mock_repo.return_value.find_by_name.return_value = mock_event_entity

        result = service.get_event_by_name('login', 10000147)

        assert result is not None
        assert result.event_name == 'login'
        assert result.game_gid == 10000147

    @patch.object(EventService, '_get_repository')
    def test_get_event_by_name_not_found(self, mock_repo, service):
        """Test get event by name when not found"""
        mock_repo.return_value.find_by_name.return_value = None

        result = service.get_event_by_name('nonexistent', 10000147)

        assert result is None

    # ==================== get_events_by_game ====================

    @patch.object(EventService, '_get_repository')
    def test_get_events_by_game_paginated(self, mock_repo, service, mock_event_list):
        """Test get events by game with pagination"""
        mock_repo.return_value.find_by_game_gid.return_value = mock_event_list

        result = service.get_events_by_game(10000147, page=1, per_page=20)

        assert len(result) == 2
        mock_repo.return_value.find_by_game_gid.assert_called_once_with(
            10000147, page=1, per_page=20
        )

    @patch.object(EventService, '_get_repository')
    def test_get_events_by_game_empty(self, mock_repo, service):
        """Test get events by game with no results"""
        mock_repo.return_value.find_by_game_gid.return_value = []

        result = service.get_events_by_game(99999999)

        assert result == []

    # ==================== create_event ====================

    @patch.object(EventService, '_get_repository')
    @patch.object(EventService, '_validate_game_exists')
    def test_create_event_success(self, mock_validate, mock_repo, service, mock_event_entity):
        """Test successful event creation"""
        mock_validate.return_value = True
        mock_repo.return_value.find_by_name.return_value = None
        mock_repo.return_value.create.return_value = 123
        mock_repo.return_value.find_by_id.return_value = mock_event_entity

        event_data = {
            'event_name': 'test_event',
            'game_gid': 10000147,
            'table_name': 'ieu_ods.ods_10000147_all_view',
            'category_id': 1,
        }

        result = service.create_event(EventEntity(**event_data))

        assert result is not None
        assert isinstance(result, EventEntity)
        mock_repo.return_value.create.assert_called_once()

    @patch.object(EventService, '_get_repository')
    @patch.object(EventService, '_validate_game_exists')
    def test_create_event_game_not_found(self, mock_validate, mock_repo, service):
        """Test create event when game doesn't exist"""
        mock_validate.return_value = False

        event_data = {'event_name': 'test_event', 'game_gid': 99999999}

        with pytest.raises(ValueError, match='Game 99999999 not found'):
            service.create_event(EventEntity(**event_data))

    @patch.object(EventService, '_get_repository')
    @patch.object(EventService, '_validate_game_exists')
    def test_create_event_duplicate_name(
        self, mock_validate, mock_repo, service, mock_event_entity
    ):
        """Test create event with duplicate name"""
        mock_validate.return_value = True
        mock_repo.return_value.find_by_name.return_value = mock_event_entity

        event_data = {'event_name': 'login', 'game_gid': 10000147}

        with pytest.raises(ValueError, match='Event login already exists for game 10000147'):
            service.create_event(EventEntity(**event_data))

    # ==================== update_event ====================

    @patch.object(EventService, '_get_repository')
    def test_update_event_success(self, mock_repo, service, mock_event_entity):
        """Test successful event update"""
        mock_repo.return_value.find_by_id.return_value = mock_event_entity
        mock_repo.return_value.update.return_value = True
        mock_repo.return_value.find_by_id.return_value = mock_event_entity

        update_data = {'event_name': 'updated_event', 'description': 'Updated description'}

        result = service.update_event(1, update_data)

        assert result is not None
        mock_repo.return_value.update.assert_called_once()

    @patch.object(EventService, '_get_repository')
    def test_update_event_not_found(self, mock_repo, service):
        """Test update event when not found"""
        mock_repo.return_value.find_by_id.return_value = None

        update_data = {'event_name': 'updated_event'}

        result = service.update_event(999, update_data)

        assert result is None

    # ==================== delete_event ====================

    @patch.object(EventService, '_get_repository')
    def test_delete_event_success(self, mock_repo, service):
        """Test successful event deletion"""
        mock_repo.return_value.find_by_id.return_value = Mock()
        mock_repo.return_value.delete.return_value = True

        result = service.delete_event(1)

        assert result is True
        mock_repo.return_value.delete.assert_called_once_with(1)

    @patch.object(EventService, '_get_repository')
    def test_delete_event_not_found(self, mock_repo, service):
        """Test delete event when not found"""
        mock_repo.return_value.find_by_id.return_value = None

        result = service.delete_event(999)

        assert result is False

    # ==================== batch_create_events ====================

    @patch.object(EventService, '_get_repository')
    @patch.object(EventService, '_validate_game_exists')
    def test_batch_create_events_success(self, mock_validate, mock_repo, service):
        """Test successful batch create"""
        mock_validate.return_value = True
        mock_repo.return_value.find_by_name.return_value = None
        mock_repo.return_value.create_batch.return_value = [1, 2]

        events_data = [
            EventEntity(
                **{
                    'event_name': 'event1',
                    'game_gid': 10000147,
                    'table_name': 'ieu_ods.ods_10000147_all_view',
                }
            ),
            EventEntity(
                **{
                    'event_name': 'event2',
                    'game_gid': 10000147,
                    'table_name': 'ieu_ods.ods_10000147_all_view',
                }
            ),
        ]

        result = service.batch_create_events(events_data)

        assert len(result) == 2
        mock_repo.return_value.create_batch.assert_called_once()

    # ==================== batch_delete_events ====================

    @patch.object(EventService, '_get_repository')
    def test_batch_delete_events_by_game(self, mock_repo, service):
        """Test batch delete events by game"""
        mock_repo.return_value.batch_delete_by_game.return_value = 10

        result = service.batch_delete_events(game_gid=10000147)

        assert result == 10
        mock_repo.return_value.batch_delete_by_game.assert_called_once_with(10000147)

    @patch.object(EventService, '_get_repository')
    def test_batch_delete_events_by_ids(self, mock_repo, service):
        """Test batch delete events by ids"""
        mock_repo.return_value.delete_batch.return_value = 3

        result = service.batch_delete_events(event_ids=[1, 2, 3])

        assert result == 3
        mock_repo.return_value.delete_batch.assert_called_once_with([1, 2, 3])

    # ==================== count_events_by_game ====================

    @patch.object(EventService, '_get_repository')
    def test_count_events_by_game(self, mock_repo, service):
        """Test count events by game"""
        mock_repo.return_value.count_by_game_gid.return_value = 42

        result = service.count_events_by_game(10000147)

        assert result == 42
        mock_repo.return_value.count_by_game_gid.assert_called_once_with(10000147)

    # ==================== search_events ====================

    @patch.object(EventService, '_get_repository')
    def test_search_events_by_name(self, mock_repo, service, mock_event_list):
        """Test search events by name"""
        mock_repo.return_value.search_by_name.return_value = mock_event_list

        result = service.search_events('log', 10000147)

        assert len(result) >= 1
        mock_repo.return_value.search_by_name.assert_called_once_with('log', 10000147)

    @patch.object(EventService, '_get_repository')
    def test_search_events_empty(self, mock_repo, service):
        """Test search events with no results"""
        mock_repo.return_value.search_by_name.return_value = []

        result = service.search_events('nonexistent', 10000147)

        assert result == []

    # ==================== get_events_by_category ====================

    @patch.object(EventService, '_get_repository')
    def test_get_events_by_category(self, mock_repo, service, mock_event_list):
        """Test get events by category"""
        mock_repo.return_value.get_by_category.return_value = mock_event_list

        result = service.get_events_by_category(1, 10000147)

        assert len(result) >= 1
        mock_repo.return_value.get_by_category.assert_called_once()

    # ==================== get_event_stats_by_game ====================

    @patch.object(EventService, '_get_repository')
    def test_get_event_stats_by_game(self, mock_repo, service):
        """Test get event stats by game"""
        mock_repo.return_value.get_event_stats_by_game.return_value = [
            {'category_name': 'Authentication', 'event_count': 5},
            {'category_name': 'Combat', 'event_count': 10},
        ]

        result = service.get_event_stats_by_game(10000147)

        assert len(result) == 2
        assert result[0]['category_name'] == 'Authentication'
        assert result[1]['event_count'] == 10

    # ==================== get_event_with_parameters ====================

    @patch.object(EventService, '_get_repository')
    def test_get_event_with_parameters(self, mock_repo, service):
        """Test get event with parameters"""
        mock_repo.return_value.get_with_parameters.return_value = {
            'event': Mock(id=1, event_name='login'),
            'parameters': [
                {'param_name': 'user_id', 'param_type': 'base'},
                {'param_name': 'zone_id', 'param_type': 'param'},
            ],
        }

        result = service.get_event_with_parameters(1)

        assert result is not None
        assert 'event' in result
        assert 'parameters' in result
        assert len(result['parameters']) == 2

    @patch.object(EventService, '_get_repository')
    def test_get_event_with_parameters_not_found(self, mock_repo, service):
        """Test get event with parameters when not found"""
        mock_repo.return_value.get_with_parameters.return_value = None

        result = service.get_event_with_parameters(999)

        assert result is None

    # ==================== validate_event_data ====================

    def test_validate_event_data_valid(self, service):
        """Test validate event data with valid input"""
        event_data = {
            'event_name': 'test_event',
            'game_gid': 10000147,
            'table_name': 'ieu_ods.ods_10000147_all_view',
        }

        # Should not raise exception
        service.validate_event_data(EventEntity(**event_data))

    def test_validate_event_data_missing_required(self, service):
        """Test validate event data with missing required fields"""
        event_data = {
            'event_name': 'test_event'
            # Missing 'game_gid'
        }

        with pytest.raises(Exception):  # Pydantic ValidationError
            service.validate_event_data(EventEntity(**event_data))

    # ==================== export_events ====================

    @patch.object(EventService, '_get_repository')
    def test_export_events_by_game(self, mock_repo, service, mock_event_list):
        """Test export events by game"""
        mock_repo.return_value.find_all.return_value = mock_event_list

        result = service.export_events(game_gid=10000147)

        assert len(result) == 2
        # Verify export format
        assert all('event_name' in event.model_dump() for event in result)

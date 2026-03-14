#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for EventImporter Service

Tests the migration from direct DB access to Repository pattern
and fixes N+1 query issues
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from backend.models.entities import EventEntity
from backend.models.repositories.events import EventRepository
from backend.services.events.event_importer import EventImporter


@pytest.fixture
def test_game_gid():
    """Test game GID (90000000+ range)"""
    return 90000001


@pytest.fixture
def mock_event_service():
    """Mock EventService"""
    with patch('backend.services.events.event_importer.EventService') as mock:
        yield mock


@pytest.fixture
def mock_category_repo():
    """Mock CategoryRepository"""
    with patch('backend.services.events.event_importer.CategoryRepository') as mock:
        yield mock


@pytest.fixture
def event_importer(mock_event_service, mock_category_repo):
    """Create EventImporter instance with mocked dependencies"""
    return EventImporter()


class TestEventImporterRepositoryMigration:
    """Test Repository pattern migration and N+1 query fix"""

    def test_get_existing_event_names_uses_batch_query(self, event_importer, test_game_gid):
        """
        Test that _get_existing_event_names uses batch query
        instead of fetching all events
        """
        # Arrange: Import data with specific event names
        events_data = [
            {"event_code": "login"},
            {"event_code": "logout"},
            {"event_code": "purchase"},
        ]

        # Mock the repository's batch_find_by_names method (should exist)
        with patch.object(EventRepository, 'batch_find_by_names') as mock_batch_find:
            # Setup mock to return existing events
            mock_batch_find.return_value = [
                EventEntity(
                    id=1,
                    game_gid=test_game_gid,
                    event_name="login",
                    event_name_cn="Login",
                    source_table="test",
                    target_table="test",
                )
            ]

            # Act
            result = event_importer._get_existing_event_names(test_game_gid, events_data)

            # Assert: batch_find_by_names should be called with exact names
            mock_batch_find.assert_called_once()
            call_args = mock_batch_find.call_args

            # Verify it was called with the event names and game_gid
            assert call_args[0][0] == ["login", "logout", "purchase"]
            assert call_args[0][1] == test_game_gid

            # Verify result contains the existing event name
            assert "login" in result

    def test_get_existing_event_names_empty_list(self, event_importer, test_game_gid):
        """
        Test that _get_existing_event_names handles empty list
        """
        # Act
        result = event_importer._get_existing_event_names(test_game_gid, [])

        # Assert: Should return empty set and not query database
        assert result == set()

    def test_get_existing_event_names_filters_correctly(self, event_importer, test_game_gid):
        """
        Test that _get_existing_event_names returns only matching names
        """
        # Arrange
        events_data = [
            {"event_code": "login"},
            {"event_code": "logout"},
            {"event_code": "purchase"},  # This one doesn't exist
        ]

        with patch.object(EventRepository, 'batch_find_by_names') as mock_batch_find:
            # Mock returns only "login" as existing
            mock_batch_find.return_value = [
                EventEntity(
                    id=1,
                    game_gid=test_game_gid,
                    event_name="login",
                    event_name_cn="Login",
                    source_table="test",
                    target_table="test",
                )
            ]

            # Act
            result = event_importer._get_existing_event_names(test_game_gid, events_data)

            # Assert: Should only contain "login", not "logout" or "purchase"
            assert result == {"login"}

    def test_import_events_validates_game_exists(
        self, event_importer, test_game_gid, mock_event_service
    ):
        """
        Test that import_events validates game exists before importing
        """
        # Arrange: Mock game not found
        mock_event_service.return_value.get_events_by_game.side_effect = ValueError(
            "Game not found"
        )

        events_data = [{"event_code": "login"}]

        # Act
        result = event_importer.import_events(test_game_gid, events_data)

        # Assert
        assert result["imported"] == 0
        assert result["failed"] == 1
        assert "Game with gid" in result["errors"][0]

    def test_import_events_skips_existing_events(
        self, event_importer, test_game_gid, mock_event_service
    ):
        """
        Test that import_events skips events that already exist
        """
        # Arrange: Mock game exists
        mock_event_service.return_value.get_events_by_game.return_value = []

        # Mock that "login" already exists
        with patch.object(EventImporter, '_get_existing_event_names') as mock_existing:
            mock_existing.return_value = {"login"}

            events_data = [
                {"event_code": "login"},
                {"event_code": "logout"},
            ]

            # Act
            result = event_importer.import_events(test_game_gid, events_data)

            # Assert
            assert result["failed"] == 1  # login failed
            assert "already exists" in result["errors"][0]
            assert "login" in result["errors"][0]

    def test_convert_to_event_entity_validates_data(self, event_importer, test_game_gid):
        """
        Test that _convert_to_event_entity creates valid EventEntity
        """
        # Arrange
        event_data = {
            "event_code": "test_event",
            "event_name_cn": "测试事件",
            "category": "测试分类",
            "source_table": "ieu_ods.test_source",
            "target_table": "dwd.test_target",
        }

        # Mock category repo
        with patch.object(event_importer.category_repo, 'find_by_name') as mock_find_category:
            mock_category = Mock()
            mock_category.id = 42
            mock_find_category.return_value = mock_category

            # Act
            entity = event_importer._convert_to_event_entity(test_game_gid, event_data)

            # Assert: Verify Entity fields
            assert isinstance(entity, EventEntity)
            assert entity.game_gid == test_game_gid
            assert entity.event_name == "test_event"
            assert entity.event_name_cn == "测试事件"
            # Note: EventEntity doesn't have category_id field directly
            # It's managed through the database schema
            assert entity.source_table == "ieu_ods.test_source"
            assert entity.target_table == "dwd.test_target"


class TestEventRepositoryBatchMethods:
    """Test new batch methods in EventRepository"""

    def test_batch_find_by_names_returns_matching_events(self, test_game_gid):
        """
        Test that batch_find_by_names returns only events matching names
        """
        # Arrange
        event_repo = EventRepository()
        event_names = ["login", "logout", "purchase"]

        # Act: Call the batch_find_by_names method
        result = event_repo.batch_find_by_names(event_names, test_game_gid)

        # Assert: Should return List[EventEntity]
        assert isinstance(result, list)
        # Should only return events matching the names
        for event in result:
            assert event.event_name in event_names
            assert event.game_gid == test_game_gid

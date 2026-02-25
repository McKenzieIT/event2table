#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event DDD Architecture Unit Tests

Tests for the Event domain model, repository, and application service.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from backend.domain.models.event import Event
from backend.domain.models.parameter import Parameter
from backend.domain.repositories.event_repository import IEventRepository
from backend.domain.exceptions.domain_exceptions import (
    EventAlreadyExists,
    InvalidEventName,
    ParameterAlreadyExists,
)
from backend.application.services.event_app_service import EventAppService


class TestEventEntity:
    """Tests for Event domain entity"""

    def test_create_event_with_valid_data(self):
        """Test creating an event with valid data"""
        event = Event(
            id=None,
            name="test_event",
            category="login",
            game_gid=1001,
            description="Test event"
        )

        assert event.name == "test_event"
        assert event.category == "login"
        assert event.game_gid == 1001
        assert event.description == "Test event"
        assert event.created_at is not None
        assert len(event.parameters) == 0

    def test_create_event_with_invalid_name_raises_error(self):
        """Test that invalid event name raises InvalidEventName"""
        with pytest.raises(InvalidEventName):
            Event(
                id=None,
                name="123invalid",
                category="login",
                game_gid=1001
            )

    def test_create_event_with_empty_category_raises_error(self):
        """Test that empty category raises ValueError"""
        with pytest.raises(ValueError):
            Event(
                id=None,
                name="test_event",
                category="",
                game_gid=1001
            )

    def test_add_parameter_to_event(self):
        """Test adding a parameter to an event"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )

        param = Parameter(
            name="user_id",
            type="string",
            json_path="$.userId",
            description="User ID"
        )

        event.add_parameter(param)

        assert len(event.parameters) == 1
        assert event.parameters[0].name == "user_id"
        assert event.updated_at > event.created_at

    def test_add_duplicate_parameter_raises_error(self):
        """Test that adding duplicate parameter raises ParameterAlreadyExists"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )

        param1 = Parameter(
            name="user_id",
            type="string",
            json_path="$.userId"
        )

        param2 = Parameter(
            name="user_id",
            type="int",
            json_path="$.uid"
        )

        event.add_parameter(param1)

        with pytest.raises(ParameterAlreadyExists):
            event.add_parameter(param2)

    def test_remove_parameter_from_event(self):
        """Test removing a parameter from an event"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )

        param = Parameter(
            name="user_id",
            type="string",
            json_path="$.userId"
        )

        event.add_parameter(param)
        event.remove_parameter("user_id")

        assert len(event.parameters) == 0

    def test_remove_nonexistent_parameter_raises_error(self):
        """Test that removing nonexistent parameter raises ValueError"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )

        with pytest.raises(ValueError):
            event.remove_parameter("nonexistent")

    def test_has_parameter(self):
        """Test checking if parameter exists"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )

        param = Parameter(
            name="user_id",
            type="string",
            json_path="$.userId"
        )

        event.add_parameter(param)

        assert event.has_parameter("user_id") is True
        assert event.has_parameter("other_param") is False

    def test_update_event_info(self):
        """Test updating event information"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )

        original_updated_at = event.updated_at
        event.update_info(category="payment", description="Updated description")

        assert event.category == "payment"
        assert event.description == "Updated description"
        assert event.updated_at > original_updated_at


class TestEventAppService:
    """Tests for EventAppService"""

    @pytest.fixture
    def mock_repo(self):
        """Create a mock repository"""
        return Mock(spec=IEventRepository)

    @pytest.fixture
    def service(self, mock_repo):
        """Create a service with mock repository"""
        return EventAppService(mock_repo)

    def test_create_event_success(self, service, mock_repo):
        """Test successful event creation"""
        # Setup mocks
        mock_repo.get_game_by_gid.return_value = {"gid": 1001, "name": "Test Game"}
        mock_repo.find_by_name.return_value = None

        created_event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )
        mock_repo.save.return_value = created_event

        # Execute
        result = service.create_event(
            game_gid=1001,
            event_name="test_event",
            category="login",
            description="Test event"
        )

        # Verify
        assert result["name"] == "test_event"
        assert result["category"] == "login"
        mock_repo.get_game_by_gid.assert_called_once_with(1001)
        mock_repo.find_by_name.assert_called_once_with("test_event", 1001)
        mock_repo.save.assert_called_once()

    def test_create_event_game_not_found(self, service, mock_repo):
        """Test event creation with nonexistent game"""
        mock_repo.get_game_by_gid.return_value = None

        with pytest.raises(ValueError, match="游戏不存在"):
            service.create_event(
                game_gid=9999,
                event_name="test_event",
                category="login"
            )

    def test_create_event_already_exists(self, service, mock_repo):
        """Test event creation when event already exists"""
        mock_repo.get_game_by_gid.return_value = {"gid": 1001}
        mock_repo.find_by_name.return_value = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )

        with pytest.raises(EventAlreadyExists):
            service.create_event(
                game_gid=1001,
                event_name="test_event",
                category="login"
            )

    def test_get_event_by_id(self, service, mock_repo):
        """Test getting event by ID"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )
        mock_repo.find_by_id.return_value = event

        result = service.get_event_by_id(1)

        assert result is not None
        assert result["name"] == "test_event"
        mock_repo.find_by_id.assert_called_once_with(1)

    def test_get_event_by_id_not_found(self, service, mock_repo):
        """Test getting nonexistent event"""
        mock_repo.find_by_id.return_value = None

        result = service.get_event_by_id(999)

        assert result is None

    def test_delete_event_success(self, service, mock_repo):
        """Test successful event deletion"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )
        mock_repo.find_by_id.return_value = event

        result = service.delete_event(1)

        assert result is True
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_event_not_found(self, service, mock_repo):
        """Test deleting nonexistent event"""
        mock_repo.find_by_id.return_value = None

        with pytest.raises(ValueError, match="事件不存在"):
            service.delete_event(999)

    def test_add_parameter_success(self, service, mock_repo):
        """Test adding parameter to event"""
        event = Event(
            id=1,
            name="test_event",
            category="login",
            game_gid=1001
        )
        mock_repo.find_by_id.return_value = event
        mock_repo.save.return_value = event

        result = service.add_parameter(
            event_id=1,
            param_name="user_id",
            param_type="string",
            json_path="$.userId",
            description="User ID"
        )

        assert result is not None
        mock_repo.save.assert_called_once()

    def test_search_events(self, service, mock_repo):
        """Test searching events"""
        events = [
            Event(id=1, name="login_event", category="login", game_gid=1001),
            Event(id=2, name="logout_event", category="logout", game_gid=1001),
        ]
        mock_repo.search_events.return_value = events

        result = service.search_events("event", game_gid=1001)

        assert len(result) == 2
        mock_repo.search_events.assert_called_once_with("event", 1001)


class TestEventRepository:
    """Tests for EventRepository implementation"""

    @pytest.fixture
    def repo(self):
        """Create repository instance"""
        from backend.infrastructure.persistence.event_repository_impl import EventRepositoryImpl
        return EventRepositoryImpl()

    def test_repository_interface_methods(self, repo):
        """Test that repository implements all interface methods"""
        assert hasattr(repo, 'find_by_id')
        assert hasattr(repo, 'find_by_name')
        assert hasattr(repo, 'find_by_game_gid')
        assert hasattr(repo, 'count_by_game_gid')
        assert hasattr(repo, 'save')
        assert hasattr(repo, 'delete')
        assert hasattr(repo, 'search_events')
        assert hasattr(repo, 'get_game_by_gid')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

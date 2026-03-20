"""
Unit tests for GameService caching (Task 1.3)

Tests that _get_event_count and _get_flow_count methods use caching properly.
"""
import pytest
from unittest.mock import MagicMock


def test_get_event_count_uses_cache(monkeypatch):
    """Test that _get_event_count uses cache decorator"""
    from backend.services.games.game_service import GameService

    service = GameService()

    # Mock fetch_one_as_dict to track calls
    mock_fetch = MagicMock(return_value={"count": 42})
    monkeypatch.setattr('backend.services.games.game_service.fetch_one_as_dict', mock_fetch)

    # First call should hit the database
    result1 = service._get_event_count(10000147)
    assert result1 == 42
    assert mock_fetch.call_count == 1

    # Second call should use cache (no additional DB call)
    result2 = service._get_event_count(10000147)
    assert result2 == 42
    # With caching, call count should still be 1 (not 2)
    assert mock_fetch.call_count == 1, "Cache should prevent second DB call"

    print("✓ Test passed: _get_event_count uses cache (1 DB call for 2 requests)")


def test_get_flow_count_uses_cache(monkeypatch):
    """Test that _get_flow_count uses cache decorator"""
    from backend.services.games.game_service import GameService

    service = GameService()

    # Mock fetch_one_as_dict to track calls
    mock_fetch = MagicMock(return_value={"count": 10})
    monkeypatch.setattr('backend.services.games.game_service.fetch_one_as_dict', mock_fetch)

    # First call should hit the database
    result1 = service._get_flow_count(10000147)
    assert result1 == 10
    assert mock_fetch.call_count == 1

    # Second call should use cache (no additional DB call)
    result2 = service._get_flow_count(10000147)
    assert result2 == 10
    # With caching, call count should still be 1 (not 2)
    assert mock_fetch.call_count == 1, "Cache should prevent second DB call"

    print("✓ Test passed: _get_flow_count uses cache (1 DB call for 2 requests)")


def test_get_event_count_different_games(monkeypatch):
    """Test that cache key includes game_gid parameter"""
    from backend.services.games.game_service import GameService

    service = GameService()

    # Mock fetch_one_as_dict to track calls
    mock_fetch = MagicMock()
    mock_fetch.side_effect = [
        {"count": 42},  # First call for game 10000147
        {"count": 50},  # First call for game 10000148
    ]
    monkeypatch.setattr('backend.services.games.game_service.fetch_one_as_dict', mock_fetch)

    # Call for different games
    result1a = service._get_event_count(10000147)
    result2a = service._get_event_count(10000148)
    result1b = service._get_event_count(10000147)  # From cache
    result2b = service._get_event_count(10000148)  # From cache

    assert result1a == 42
    assert result2a == 50
    assert result1b == 42
    assert result2b == 50

    # Should only call database twice (once per game), not 4 times
    assert mock_fetch.call_count == 2, f"Expected 2 DB calls (one per game), got {mock_fetch.call_count}"

    print("✓ Test passed: Cache key includes game_gid (2 DB calls for 4 requests across 2 games)")


def test_cache_decorator_present():
    """Test that @cached decorator is present on both methods"""
    from backend.services.games.game_service import GameService
    import inspect

    service = GameService()

    # Check _get_event_count has caching
    method = getattr(service, '_get_event_count')
    # The wrapped method should have __wrapped__ indicating it's decorated
    assert hasattr(method, '__wrapped__'), "_get_event_count should have @cached decorator"

    # Check _get_flow_count has caching
    method = getattr(service, '_get_flow_count')
    assert hasattr(method, '__wrapped__'), "_get_flow_count should have @cached decorator"

    print("✓ Test passed: Both methods have @cached decorator")

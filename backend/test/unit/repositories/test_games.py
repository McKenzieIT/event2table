"""
Unit tests for GameRepository

This module contains tests for the GameRepository class, focusing on
performance optimizations such as N+1 query prevention.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any


def test_get_all_with_event_count_no_n_plus_one(monkeypatch):
    """
    Test that get_all_with_event_count doesn't cause N+1 queries

    This test verifies that the get_all_with_event_count method uses
    a single JOIN query instead of N+1 separate queries (one query per
    game to get its event count).

    The method should use LEFT JOIN to fetch games and their event counts
    in a single database query.

    Args:
        monkeypatch: Pytest fixture for mocking

    Expected:
        - Database should be called exactly once (not N+1 times)
        - Query should use LEFT JOIN with log_events table
        - Results should include event_count for each game
    """
    from backend.models.repositories.games import GameRepository
    from backend.models.entities import GameEntity

    repo = GameRepository()

    # Mock fetch_all_as_dict in the games module itself (since it's imported at module level)
    mock_fetch_all = MagicMock()
    monkeypatch.setattr(
        'backend.models.repositories.games.fetch_all_as_dict',
        mock_fetch_all
    )

    # Mock response with 3 games and their event counts
    mock_response = [
        {
            'id': 1,
            'gid': '10000147',
            'name': 'STAR001',
            'ods_db': 'ieu_ods',
            'description': 'Test Game 1',
            'dwd_prefix': 'dwd',
            'created_at': '2026-01-01 00:00:00',
            'updated_at': '2026-01-01 00:00:00',
            'event_count': 5
        },
        {
            'id': 2,
            'gid': '10000148',
            'name': 'STAR002',
            'ods_db': 'ieu_ods',
            'description': 'Test Game 2',
            'dwd_prefix': 'dwd',
            'created_at': '2026-01-01 00:00:00',
            'updated_at': '2026-01-01 00:00:00',
            'event_count': 3
        },
        {
            'id': 3,
            'gid': '10000149',
            'name': 'STAR003',
            'ods_db': 'overseas_ods',
            'description': 'Test Game 3',
            'dwd_prefix': 'dwd',
            'created_at': '2026-01-01 00:00:00',
            'updated_at': '2026-01-01 00:00:00',
            'event_count': 0
        }
    ]

    mock_fetch_all.return_value = mock_response

    # Call the method
    results = repo.get_all_with_event_count()

    # Verify database was called exactly once (single JOIN query)
    assert mock_fetch_all.call_count == 1, (
        f"Expected 1 DB call (single JOIN query), got {mock_fetch_all.call_count}. "
        "This suggests N+1 query pattern is being used."
    )

    # Verify the query includes LEFT JOIN
    call_args = mock_fetch_all.call_args
    query = call_args[0][0] if call_args[0] else call_args.kwargs.get('query', '')

    assert 'LEFT JOIN' in query.upper(), (
        "Query should use LEFT JOIN to fetch games and event counts in single query"
    )

    assert 'LOG_EVENTS' in query.upper(), (
        "Query should join with log_events table"
    )

    assert 'COUNT' in query.upper(), (
        "Query should use COUNT to aggregate events"
    )

    # Verify results are GameEntity objects
    assert len(results) == 3, "Should return 3 games"
    assert all(isinstance(game, GameEntity) for game in results), (
        "All results should be GameEntity instances"
    )

    # Verify event counts are present
    assert results[0].event_count == 5, "First game should have 5 events"
    assert results[1].event_count == 3, "Second game should have 3 events"
    assert results[2].event_count == 0, "Third game should have 0 events"

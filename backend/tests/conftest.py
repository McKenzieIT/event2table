"""
Pytest Configuration and Shared Fixtures

This module provides shared fixtures and configuration for all unit tests.
It ensures test isolation and provides common test data.
"""

import pytest
import os
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database module carefully to avoid import errors
try:
    from backend.core.database import get_db_connection
except ImportError:
    # For testing without full backend import
    import sqlite3
    def get_db_connection(db_path):
        """Fallback database connection"""
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

# Test database path
TEST_DB = "/Users/mckenzie/Documents/event2table/data/test_database.db"
TEST_GID_START = 90000000  # Never use 10000147 (STAR001)


# =============================================================================
# Database Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Test database fixture

    Provides a clean database connection for each test function.
    Database is NOT cleaned up automatically - tests should clean up after themselves.
    """
    # Ensure test database exists
    if not os.path.exists(TEST_DB):
        raise FileNotFoundError(f"Test database not found: {TEST_DB}")

    conn = get_db_connection(TEST_DB)
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def clean_db(test_db):
    """
    Clean database fixture

    Provides a database with all test data cleaned.
    Use this when you need a completely fresh database.
    """
    # Clean all test data
    test_db.execute("DELETE FROM event_params WHERE game_gid >= ?", (TEST_GID_START,))
    test_db.execute("DELETE FROM common_parameters WHERE game_gid >= ?", (TEST_GID_START,))
    test_db.execute("DELETE FROM log_events WHERE game_gid >= ?", (TEST_GID_START,))
    test_db.execute("DELETE FROM games WHERE gid >= ?", (TEST_GID_START,))
    test_db.commit()

    return test_db


# =============================================================================
# Game and Event Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_game(clean_db):
    """
    Create a test game

    Returns:
        int: Test game GID
    """
    test_gid = TEST_GID_START + 1
    clean_db.execute(
        "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (test_gid, "Test Game", "ieu_ods")
    )
    clean_db.commit()
    return test_gid


@pytest.fixture(scope="function")
def test_game_with_events(clean_db):
    """
    Create a test game with multiple events

    Returns:
        dict: {'game_gid': int, 'events': [event_ids]}
    """
    test_gid = TEST_GID_START + 2

    # Insert game
    clean_db.execute(
        "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (test_gid, "Test Game with Events", "ieu_ods")
    )

    # Insert 5 events
    event_ids = []
    for i in range(1, 6):
        clean_db.execute(
            "INSERT INTO log_events (game_gid, name, ods_table) VALUES (?, ?, ?)",
            (test_gid, f"test_event_{i}", f"ods_test_event_{i}")
        )
        event_ids.append(clean_db.lastrowid)

    clean_db.commit()

    return {
        'game_gid': test_gid,
        'events': event_ids
    }


@pytest.fixture(scope="function")
def test_event(clean_db, test_game):
    """
    Create a test event

    Returns:
        int: Event ID
    """
    clean_db.execute(
        "INSERT INTO log_events (game_gid, name, ods_table) VALUES (?, ?, ?)",
        (test_game, "test_event", "ods_test_event")
    )
    clean_db.commit()
    return clean_db.lastrowid


# =============================================================================
# Parameter Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_parameter_data(test_game, test_event):
    """
    Create test parameter data

    Returns:
        dict: Parameter data dictionary
    """
    return {
        'param_name': 'test_param',
        'param_type': 'string',
        'json_path': '$.testParam',
        'description': 'Test parameter',
        'event_id': test_event,
        'game_gid': test_game,
        'is_common': False,
        'is_active': True
    }


@pytest.fixture(scope="function")
def test_parameters(clean_db, test_game_with_events):
    """
    Create test parameters for common parameter calculation

    Creates parameters that appear in different numbers of events:
    - zone_id: appears in 5/5 events (100% - common)
    - guild_id: appears in 4/5 events (80% - common)
    - role_id: appears in 3/5 events (60% - not common)
    - level: appears in 2/5 events (40% - not common)

    Returns:
        dict: {'game_gid': int, 'params': {'zone_id': [event_ids], ...}}
    """
    game_gid = test_game_with_events['game_gid']
    events = test_game_with_events['game_gid']

    param_data = {
        'zone_id': {'type': 'int', 'events': [0, 1, 2, 3, 4]},  # 5/5 = 100%
        'guild_id': {'type': 'string', 'events': [0, 1, 2, 3]},   # 4/5 = 80%
        'role_id': {'type': 'int', 'events': [0, 1, 2]},          # 3/5 = 60%
        'level': {'type': 'int', 'events': [0, 1]},               # 2/5 = 40%
    }

    created_params = {}

    for param_name, data in param_data.items():
        for event_idx in data['events']:
            event_id = test_game_with_events['events'][event_idx]

            clean_db.execute(
                """INSERT INTO event_params
                   (param_name, param_name_cn, param_type, json_path, event_id, game_gid)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (param_name, f"{param_name}_cn", data['type'], f"$.{param_name}",
                 event_id, game_gid)
            )

            if param_name not in created_params:
                created_params[param_name] = []
            created_params[param_name].append(event_id)

    clean_db.commit()

    return {
        'game_gid': game_gid,
        'params': created_params
    }


# =============================================================================
# Mock Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def mock_parameter_repository():
    """
    Mock parameter repository

    Returns:
        Mock: Mocked parameter repository
    """
    mock_repo = Mock()

    # Setup default return values
    mock_repo.find_by_id.return_value = None
    mock_repo.find_by_game.return_value = []
    mock_repo.find_common_by_game.return_value = []
    mock_repo.find_non_common_by_game.return_value = []
    mock_repo.count_by_game.return_value = 0
    mock_repo.count_events_by_game.return_value = 0
    mock_repo.get_parameter_usage_stats.return_value = []

    return mock_repo


@pytest.fixture(scope="function")
def mock_common_param_repository():
    """
    Mock common parameter repository

    Returns:
        Mock: Mocked common parameter repository
    """
    mock_repo = Mock()

    mock_repo.find_by_game.return_value = []
    mock_repo.save.return_value = None
    mock_repo.delete_by_game.return_value = 0

    return mock_repo


@pytest.fixture(scope="function")
def mock_uow(mock_parameter_repository, mock_common_param_repository):
    """
    Mock Unit of Work

    Returns:
        Mock: Mocked Unit of Work with repositories
    """
    mock_uow = Mock()

    mock_uow.parameters = mock_parameter_repository
    mock_uow.common_params = mock_common_param_repository
    mock_uow.register_event = Mock()
    mock_uow.commit = Mock()
    mock_uow.rollback = Mock()

    return mock_uow


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_parameter():
    """
    Sample parameter for testing

    Returns:
        Parameter: Sample parameter instance
    """
    from backend.domain.models.parameter import Parameter

    return Parameter(
        id=1,
        param_name='guild_id',
        param_type='string',
        json_path='$.guildId',
        description='Guild ID',
        event_id=1,
        game_gid=TEST_GID_START + 1,
        is_common=True,
        is_active=True,
        version=1
    )


@pytest.fixture(scope="function")
def sample_common_parameter():
    """
    Sample common parameter for testing

    Returns:
        CommonParameter: Sample common parameter instance
    """
    from backend.domain.models.common_parameter import CommonParameter
    from backend.domain.models.parameter import ParameterType

    return CommonParameter(
        id=1,
        game_gid=TEST_GID_START + 1,
        param_name='guild_id',
        param_name_cn='公会ID',
        param_type=ParameterType.STRING,
        occurrence_count=4,
        total_events=5,
        threshold=0.8,
        calculated_at=datetime.now()
    )


# =============================================================================
# Test Configuration
# =============================================================================

def pytest_configure(config):
    """
    Pytest configuration hook

    Sets up custom markers and configuration.
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, uses database)"
    )
    config.addinivalue_line(
        "markers", "domain: Domain layer tests"
    )
    config.addinivalue_line(
        "markers", "application: Application layer tests"
    )


@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """
    Set test environment for all tests

    This fixture runs automatically at the beginning of the test session.
    """
    os.environ["FLASK_ENV"] = "testing"
    os.environ["ENVIRONMENT"] = "testing"

    yield

    # Cleanup after all tests
    os.environ["FLASK_ENV"] = "development"
    os.environ["ENVIRONMENT"] = "development"

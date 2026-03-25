#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests Configuration

Shared fixtures for integration tests

IMPORTANT: Integration tests now use TEST_DATABASE to avoid polluting production data.
"""

import os
import sys

import pytest

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Set testing environment BEFORE importing any backend modules
os.environ['FLASK_ENV'] = 'testing'


def pytest_configure(config):
    """
    Pytest configuration hook - runs before test collection
    Ensures environment variables are set before any modules are imported
    """
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['ENVIRONMENT'] = 'testing'


@pytest.fixture(scope="session", autouse=True)
def test_db():
    """
    Initialize test database for integration tests

    This fixture ensures tests use a separate test database,
    preventing pollution of production data.

    The test database is created by copying the schema from
    the production database and then deleting all data.
    """
    import shutil
    import sqlite3
    from pathlib import Path

    from backend.core.config import DB_PATH, TEST_DB_PATH

    # Ensure test database directory exists
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # ALWAYS delete old test database to ensure clean state
    if TEST_DB_PATH.exists():
        print(f"[CONFTEST] Deleting old test database: {TEST_DB_PATH}")
        TEST_DB_PATH.unlink()

    # Create test database by dumping schema from production database
    print(f"[CONFTEST] Creating test database from schema: {DB_PATH} -> {TEST_DB_PATH}")

    import sqlite3

    conn_prod = sqlite3.connect(DB_PATH)
    conn_test = sqlite3.connect(TEST_DB_PATH)

    # Dump schema (no data) from production to test
    for line in conn_prod.iterdump():
        if line.startswith('CREATE') or line.startswith('COMMIT') or line.startswith('BEGIN'):
            try:
                conn_test.execute(line)
            except Exception as e:
                # Skip problematic lines
                pass

    conn_prod.close()
    conn_test.close()

    # Delete all data from test database (keep schema)
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # Disable foreign keys for truncation
    cursor.execute("PRAGMA foreign_keys = OFF")

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    # Delete all data from each table
    for (table_name,) in tables:
        if table_name != 'sqlite_sequence':
            try:
                cursor.execute(f"DELETE FROM {table_name}")
                print(f"[CONFTEST] Cleared table: {table_name}")
            except sqlite3.DatabaseError as e:
                print(f"[CONFTEST] WARNING: Failed to clear table {table_name}: {e}")
                # Continue with other tables

    # Re-enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Reset autoincrement sequences (表可能不存在)
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
    except sqlite3.OperationalError:
        # sqlite_sequence表不存在(没有AUTOINCREMENT表), 跳过
        pass

    # Create test data for integration tests
    print("[CONFTEST] Creating test data...")

    # Create test games (GID range: 92000000-92000099)
    # Changed from 91000000+ to avoid conflicts with tests that use 91000000-91000099 range
    for i in range(100):
        try:
            cursor.execute(
                "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
                (92000000 + i, f"Test Game {i}", "ieu_ods"),
            )
        except Exception as e:
            pass  # Ignore if game already exists

    # Create test events for join config tests
    for game_gid in [92000001, 92000002, 92000003]:
        for i in range(5):
            try:
                cursor.execute(
                    "INSERT INTO log_events (game_gid, name, table_name) VALUES (?, ?, ?)",
                    (game_gid, f"test_event_{i}", f"test_table_{i}"),
                )
            except Exception:
                pass

    conn.commit()
    print(f"[CONFTEST] Created test data successfully")

    conn.commit()
    conn.close()

    print(f"[CONFTEST] Test database created successfully")

    yield TEST_DB_PATH

    # Clean up after all tests complete
    if TEST_DB_PATH.exists():
        print(f"[CONFTEST] Cleaning up test database: {TEST_DB_PATH}")
        TEST_DB_PATH.unlink()


@pytest.fixture(scope="session")
def integration_client(test_db):
    """
    Fixture for integration tests that need a Flask test client

    Uses test database instead of production database.
    """
    from web_app import app

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="session")
def client(integration_client):
    """
    Alias for integration_client - for API tests that use 'client' fixture name
    """
    yield integration_client


@pytest.fixture(scope="function")
def sample_game(integration_client):
    """
    Fixture providing a sample game for testing

    Returns the first game from the database or creates a test game
    """
    response = integration_client.get('/api/games')
    data = response.get_json()

    if data.get('data') and len(data['data']) > 0:
        return data['data'][0]

    # If no games exist, create one (使用不同的GID避免冲突)
    response = integration_client.post(
        '/api/games',
        json={
            'gid': 91000100,  # 使用91000100避免与fixture范围(92000000+)冲突
            'name': 'Integration Test Game',
            'ods_db': 'ieu_ods',
        },
    )

    if response.status_code == 200:
        return response.get_json()['data']

    return None


@pytest.fixture(scope="function")
def hql_v2_test_data(test_db):
    """
    为HQL V2测试提供测试数据

    遵循测试隔离规范, 使用91000000+测试GID范围
    确保测试不依赖生产数据（GID 10000147）
    """
    import sqlite3

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()

    # 创建测试游戏(使用测试GID范围)
    test_gid = 91000147
    cursor.execute(
        "INSERT OR IGNORE INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (test_gid, "HQL V2 Test Game", "ieu_ods"),
    )

    # 创建测试事件(使用正确的字段名: event_name, event_name_cn, source_table, target_table)
    cursor.execute(
        """INSERT OR IGNORE INTO log_events
           (game_gid, event_name, event_name_cn, source_table, target_table)
           VALUES (?, ?, ?, ?, ?)""",
        (
            test_gid,
            "hql_test_event",
            "HQL测试事件",
            f"ieu_ods.ods_{test_gid}_all_view",
            f"dwd.v_dwd_{test_gid}_hql_test_event_di",
        ),
    )

    conn.commit()

    # 获取event_id
    event_id = cursor.lastrowid
    if event_id == 0:
        cursor.execute(
            "SELECT id FROM log_events WHERE game_gid = ? AND event_name = ?",
            (test_gid, "hql_test_event"),
        )
        result = cursor.fetchone()
        event_id = result[0] if result else None

    conn.close()

    return {
        "game_gid": test_gid,
        "event_id": event_id,
        "event_name": "hql_test_event",
        "source_table": f"ieu_ods.ods_{test_gid}_all_view",
        "target_table": f"dwd.v_dwd_{test_gid}_hql_test_event_di",
        "ods_db": "ieu_ods",
    }

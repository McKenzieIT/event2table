#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for Unit of Work
"""

import pytest
import sqlite3
import os

from backend.infrastructure.persistence.unit_of_work_enhanced import UnitOfWork
from backend.domain.events.parameter_events import ParameterTypeChanged


TEST_DB_PATH = "/tmp/test_uow_integration.db"


@pytest.fixture(scope="function")
def integration_db():
    """Create test database with full schema"""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid INTEGER UNIQUE NOT NULL,
            name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE event_params (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            param_name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    # Insert test data
    cursor.execute("INSERT INTO games (gid, name) VALUES (90000001, 'Test Game')")

    conn.commit()
    conn.close()

    yield TEST_DB_PATH

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


class TestUnitOfWorkCrudCycle:
    """Test complete CRUD cycles with Unit of Work"""

    def test_create_parameter_with_uow(self, integration_db):
        """Test creating a parameter with Unit of Work"""
        with UnitOfWork(integration_db) as uow:
            uow.connection.execute(
                "INSERT INTO event_params (event_id, param_name) VALUES (?, ?)",
                (1, "test_param")
            )

        # Verify
        conn = sqlite3.connect(integration_db)
        cursor = conn.cursor()
        cursor.execute("SELECT param_name FROM event_params WHERE id = 1")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == "test_param"

    def test_rollback_on_exception(self, integration_db):
        """Test rollback on exception"""
        try:
            with UnitOfWork(integration_db) as uow:
                uow.connection.execute(
                    "INSERT INTO event_params (event_id, param_name) VALUES (?, ?)",
                    (1, "test_param")
                )
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Verify rollback
        conn = sqlite3.connect(integration_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM event_params")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0

    def test_event_published_after_commit(self, integration_db):
        """Test event is published after successful commit"""
        handler_called = []

        def mock_handler(event):
            handler_called.append(event)

        # Subscribe mock handler
        from backend.infrastructure.events.domain_event_publisher import DomainEventPublisher
        publisher = DomainEventPublisher()
        publisher.subscribe(ParameterTypeChanged, mock_handler)

        with UnitOfWork(integration_db) as uow:
            uow.connection.execute(
                "INSERT INTO event_params (event_id, param_name) VALUES (?, ?)",
                (1, "test_param")
            )

            uow.register_event(ParameterTypeChanged(
                parameter_id=1,
                old_type='string',
                new_type='int',
                game_gid=90000001
            ))

        # Verify handler was called
        assert len(handler_called) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

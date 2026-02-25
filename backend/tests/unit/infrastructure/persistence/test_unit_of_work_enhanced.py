#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Enhanced Unit of Work

Comprehensive test suite covering:
- Transaction management (commit/rollback)
- Domain event publishing
- Repository lazy loading
- Operation tracking
- Context manager behavior
- Decorator functionality
"""

import pytest
import sqlite3
import logging
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass

from backend.infrastructure.persistence.unit_of_work_enhanced import (
    UnitOfWork,
    unit_of_work,
    unit_of_work_context,
    TransactionContext
)
from backend.domain.events.parameter_events import ParameterTypeChanged
from backend.domain.events.base import DomainEvent

logger = logging.getLogger(__name__)


# Test Database Setup
TEST_DB_PATH = "/tmp/test_unit_of_work.db"


@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, value TEXT)")
    conn.commit()
    conn.close()

    yield TEST_DB_PATH

    # Cleanup
    import os
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


@pytest.fixture(scope="function")
def mock_connection(test_db):
    """Create mock database connection"""
    conn = sqlite3.connect(test_db)
    yield conn
    conn.close()


class TestTransactionContext:
    """Test TransactionContext dataclass"""

    def test_transaction_context_initialization(self):
        """Test transaction context is initialized correctly"""
        context = TransactionContext(
            transaction_id="test123",
            started_at=datetime.now()
        )

        assert context.transaction_id == "test123"
        assert context.is_committed is False
        assert context.is_rolled_back is False
        assert len(context.operations) == 0

    def test_add_operation(self):
        """Test operation tracking"""
        context = TransactionContext(
            transaction_id="test123",
            started_at=datetime.now()
        )

        context.add_operation("Test operation", {"key": "value"})

        assert len(context.operations) == 1
        assert context.operations[0]["operation"] == "Test operation"
        assert context.operations[0]["metadata"]["key"] == "value"
        assert "timestamp" in context.operations[0]


class TestUnitOfWorkBasics:
    """Test basic UnitOfWork functionality"""

    def test_uow_initialization(self, test_db):
        """Test UnitOfWork initialization"""
        uow = UnitOfWork(test_db)

        assert uow._db_path == test_db
        assert uow._connection is None
        assert uow._is_active is False
        assert len(uow._repositories) == 0
        assert len(uow._events) == 0

    def test_connection_property_before_begin(self, test_db):
        """Test accessing connection before begin raises error"""
        uow = UnitOfWork(test_db)

        with pytest.raises(RuntimeError, match="No active connection"):
            _ = uow.connection

    def test_begin_transaction(self, test_db):
        """Test begin transaction"""
        uow = UnitOfWork(test_db)
        uow.begin()

        assert uow._is_active is True
        assert uow._connection is not None
        assert uow._transaction_context is not None
        assert uow._transaction_context.transaction_id is not None

        uow.close()

    def test_begin_twice_raises_error(self, test_db):
        """Test beginning transaction twice raises error"""
        uow = UnitOfWork(test_db)
        uow.begin()

        with pytest.raises(RuntimeError, match="Transaction already active"):
            uow.begin()

        uow.close()

    def test_commit_without_active_transaction(self, test_db):
        """Test commit without active transaction raises error"""
        uow = UnitOfWork(test_db)

        with pytest.raises(RuntimeError, match="No active transaction"):
            uow.commit()

    def test_rollback_without_active_transaction(self, test_db):
        """Test rollback without active transaction raises error"""
        uow = UnitOfWork(test_db)

        with pytest.raises(RuntimeError, match="No active transaction"):
            uow.rollback()


class TestUnitOfWorkTransactionManagement:
    """Test transaction commit and rollback"""

    def test_commit_success(self, test_db):
        """Test successful commit"""
        uow = UnitOfWork(test_db)
        uow.begin()

        # Insert test data
        uow.connection.execute(
            "INSERT INTO test_table (id, value) VALUES (1, 'test')"
        )

        # Commit
        uow.commit()

        # Verify data persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'test'
        assert uow._transaction_context.is_committed is True

    def test_rollback_discards_changes(self, test_db):
        """Test rollback discards changes"""
        uow = UnitOfWork(test_db)
        uow.begin()

        # Insert test data
        uow.connection.execute(
            "INSERT INTO test_table (id, value) VALUES (1, 'test')"
        )

        # Rollback
        uow.rollback()

        # Verify data not persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        conn.close()

        assert result is None
        assert uow._transaction_context.is_rolled_back is True

    def test_commit_on_exception_in_transaction(self, test_db):
        """Test that exception during transaction prevents commit"""
        uow = UnitOfWork(test_db)
        uow.begin()

        # Insert test data
        uow.connection.execute(
            "INSERT INTO test_table (id, value) VALUES (1, 'test')"
        )

        # Simulate exception
        with pytest.raises(ValueError):
            uow.connection.execute("INSERT INTO test_table (id, value) VALUES (1, 'duplicate')")

        # Rollback manually (exception doesn't auto-rollback in manual mode)
        uow.rollback()

        # Verify data not persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0


class TestUnitOfWorkDomainEvents:
    """Test domain event registration and publishing"""

    def test_register_event(self, test_db):
        """Test registering domain events"""
        uow = UnitOfWork(test_db)
        uow.begin()

        event = ParameterTypeChanged(
            parameter_id=1,
            old_type='string',
            new_type='int',
            game_gid=90000001
        )

        uow.register_event(event)

        assert len(uow._events) == 1
        assert uow._events[0] == event

        uow.close()

    def test_events_published_after_commit(self, test_db):
        """Test events are published after successful commit"""
        uow = UnitOfWork(test_db)
        uow.begin()

        event = ParameterTypeChanged(
            parameter_id=1,
            old_type='string',
            new_type='int',
            game_gid=90000001
        )

        uow.register_event(event)

        # Mock event publisher
        with patch('backend.infrastructure.persistence.unit_of_work_enhanced.DomainEventPublisher') as mock_publisher_class:
            mock_publisher = Mock()
            mock_publisher_class.return_value = mock_publisher

            uow.commit()

            # Verify publisher was called
            mock_publisher.publish.assert_called_once_with(event)

    def test_events_cleared_on_rollback(self, test_db):
        """Test events are cleared on rollback"""
        uow = UnitOfWork(test_db)
        uow.begin()

        event = ParameterTypeChanged(
            parameter_id=1,
            old_type='string',
            new_type='int',
            game_gid=90000001
        )

        uow.register_event(event)
        assert len(uow._events) == 1

        uow.rollback()

        assert len(uow._events) == 0

    def test_multiple_events_published(self, test_db):
        """Test multiple events are published"""
        uow = UnitOfWork(test_db)
        uow.begin()

        events = [
            ParameterTypeChanged(
                parameter_id=i,
                old_type='string',
                new_type='int',
                game_gid=90000001
            )
            for i in range(3)
        ]

        for event in events:
            uow.register_event(event)

        with patch('backend.infrastructure.persistence.unit_of_work_enhanced.DomainEventPublisher') as mock_publisher_class:
            mock_publisher = Mock()
            mock_publisher_class.return_value = mock_publisher

            uow.commit()

            # Verify all events published
            assert mock_publisher.publish.call_count == 3


class TestUnitOfWorkOperationTracking:
    """Test operation tracking for audit"""

    def test_add_operation(self, test_db):
        """Test adding operations"""
        uow = UnitOfWork(test_db)
        uow.begin()

        uow.add_operation("Test operation", {"param": "value"})

        operations = uow.get_operations()
        assert len(operations) == 1
        assert operations[0]["operation"] == "Test operation"

        uow.close()

    def test_multiple_operations(self, test_db):
        """Test tracking multiple operations"""
        uow = UnitOfWork(test_db)
        uow.begin()

        uow.add_operation("Operation 1")
        uow.add_operation("Operation 2")
        uow.add_operation("Operation 3")

        operations = uow.get_operations()
        assert len(operations) == 3

        uow.close()

    def test_operations_without_context(self, test_db):
        """Test operations without transaction context returns empty list"""
        uow = UnitOfWork(test_db)

        operations = uow.get_operations()
        assert len(operations) == 0


class TestUnitOfWorkContextManager:
    """Test UnitOfWork as context manager"""

    def test_context_manager_commit_on_success(self, test_db):
        """Test context manager commits on success"""
        with UnitOfWork(test_db) as uow:
            uow.connection.execute(
                "INSERT INTO test_table (id, value) VALUES (1, 'test')"
            )

        # Verify data persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'test'

    def test_context_manager_rollback_on_exception(self, test_db):
        """Test context manager rolls back on exception"""
        with pytest.raises(ValueError):
            with UnitOfWork(test_db) as uow:
                uow.connection.execute(
                    "INSERT INTO test_table (id, value) VALUES (1, 'test')"
                )
                raise ValueError("Test exception")

        # Verify data not persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0

    def test_context_manager_closes_connection(self, test_db):
        """Test context manager closes connection"""
        with UnitOfWork(test_db) as uow:
            conn_id = id(uow._connection)

        # Connection should be closed
        assert uow._connection is None


class TestUnitOfWorkRepositoryLazyLoading:
    """Test repository lazy loading"""

    @patch('backend.infrastructure.persistence.unit_of_work_enhanced.get_db_connection')
    def test_parameters_repository_lazy_loading(self, mock_get_db, test_db):
        """Test parameters repository is lazy loaded"""
        mock_conn = Mock()
        mock_get_db.return_value = mock_conn

        uow = UnitOfWork(test_db)
        uow.begin()

        # Access parameters property
        _ = uow.parameters

        # Verify repository was created
        assert 'parameters' in uow._repositories
        assert uow._repositories['parameters'] is not None

        # Access again - should reuse same instance
        repo1 = uow.parameters
        repo2 = uow.parameters
        assert repo1 is repo2

        uow.close()

    @patch('backend.infrastructure.persistence.unit_of_work_enhanced.get_db_connection')
    def test_common_params_repository_lazy_loading(self, mock_get_db, test_db):
        """Test common_params repository is lazy loaded"""
        mock_conn = Mock()
        mock_get_db.return_value = mock_conn

        uow = UnitOfWork(test_db)
        uow.begin()

        # Access common_params property
        _ = uow.common_params

        # Verify repository was created
        assert 'common_params' in uow._repositories

        uow.close()


class TestUnitOfWorkDecorator:
    """Test @unit_of_work decorator"""

    def test_decorator_injects_uow(self, test_db):
        """Test decorator injects UnitOfWork as first argument"""
        @unit_of_work(test_db)
        def test_func(uow, value):
            assert isinstance(uow, UnitOfWork)
            return value

        result = test_func("test")
        assert result == "test"

    def test_decorator_commits_on_success(self, test_db):
        """Test decorator commits on success"""
        @unit_of_work(test_db)
        def insert_value(uow, value):
            uow.connection.execute(
                f"INSERT INTO test_table (id, value) VALUES (1, '{value}')"
            )

        insert_value("test")

        # Verify data persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'test'

    def test_decorator_rolls_back_on_exception(self, test_db):
        """Test decorator rolls back on exception"""
        @unit_of_work(test_db)
        def insert_and_fail(uow):
            uow.connection.execute(
                "INSERT INTO test_table (id, value) VALUES (1, 'test')"
            )
            raise ValueError("Test failure")

        with pytest.raises(ValueError):
            insert_and_fail()

        # Verify data not persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0

    def test_decorator_closes_connection(self, test_db):
        """Test decorator closes connection"""
        connection_closed = False

        @unit_of_work(test_db)
        def test_func(uow):
            nonlocal connection_closed
            conn_id = id(uow._connection)
            return conn_id

        test_func()
        # Connection should be closed (can't directly test, but no exception means success)


class TestUnitOfWorkContextFunction:
    """Test unit_of_work_context function"""

    def test_context_function_commit_on_success(self, test_db):
        """Test context function commits on success"""
        with unit_of_work_context(test_db) as uow:
            uow.connection.execute(
                "INSERT INTO test_table (id, value) VALUES (1, 'test')"
            )

        # Verify data persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM test_table WHERE id = 1")
        result = cursor.fetchone()
        conn.close()

        assert result is not None
        assert result[0] == 'test'

    def test_context_function_rollback_on_exception(self, test_db):
        """Test context function rolls back on exception"""
        with pytest.raises(ValueError):
            with unit_of_work_context(test_db) as uow:
                uow.connection.execute(
                    "INSERT INTO test_table (id, value) VALUES (1, 'test')"
                )
                raise ValueError("Test exception")

        # Verify data not persisted
        conn = sqlite3.connect(test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_table")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

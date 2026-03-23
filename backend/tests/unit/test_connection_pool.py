#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQLite Connection Pool Tests

Tests for the SQLite connection pool implementation.

Performance Goals:
- Connection reuse: ≥90% (avoid creating new connections)
- Pool efficiency: ≤10ms per connection acquisition
- Thread safety: Support concurrent connections without errors

Author: Event2Table Performance Optimization Team
Version: 1.0.0 (2026-03-18)
"""

import pytest
import threading
import time
from pathlib import Path
from typing import List

# Import the connection pool module (will be created)
from backend.core.database.connection_pool import (
    ConnectionPool,
    get_connection_pool,
    ConnectionPoolConfig,
    PoolExhaustedError,
)


class TestConnectionPoolConfig:
    """Test connection pool configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = ConnectionPoolConfig()

        assert config.max_connections == 10
        assert config.min_connections == 1
        assert config.max_idle_time == 300
        assert config.connection_timeout == 30

    def test_custom_config(self):
        """Test custom configuration values"""
        config = ConnectionPoolConfig(
            max_connections=20, min_connections=5, max_idle_time=600, connection_timeout=60
        )

        assert config.max_connections == 20
        assert config.min_connections == 5
        assert config.max_idle_time == 600
        assert config.connection_timeout == 60

    def test_config_validation(self):
        """Test configuration validation"""
        # max_connections must be >= min_connections
        with pytest.raises(ValueError):
            ConnectionPoolConfig(max_connections=5, min_connections=10)  # Invalid: min > max

        # max_connections must be positive
        with pytest.raises(ValueError):
            ConnectionPoolConfig(max_connections=0)

        # min_connections must be non-negative
        with pytest.raises(ValueError):
            ConnectionPoolConfig(min_connections=-1)


class TestConnectionPool:
    """Test connection pool functionality"""

    @pytest.fixture
    def test_db_path(self, tmp_path):
        """Create a temporary test database"""
        return tmp_path / "test_pool.db"

    @pytest.fixture
    def pool_config(self):
        """Test configuration"""
        return ConnectionPoolConfig(
            max_connections=5, min_connections=1, max_idle_time=60, connection_timeout=10
        )

    @pytest.fixture
    def pool(self, test_db_path, pool_config):
        """Create a connection pool for testing"""
        pool = ConnectionPool(db_path=str(test_db_path), config=pool_config)
        yield pool
        pool.close()

    def test_pool_initialization(self, pool):
        """Test pool initializes correctly"""
        assert pool.max_connections == 5
        assert pool.min_connections == 1
        assert pool.total_connections >= 0
        assert pool.idle_connections >= 0

    def test_get_connection(self, pool):
        """Test acquiring a connection from the pool"""
        conn = pool.get_connection()
        assert conn is not None
        assert pool.idle_connections == 0  # Connection is in use

        # Return connection to pool
        pool.return_connection(conn)
        assert pool.idle_connections == 1

    def test_connection_reuse(self, pool):
        """Test that connections are reused"""
        conn1 = pool.get_connection()
        pool.return_connection(conn1)

        conn2 = pool.get_connection()
        # Should get the same connection back (reused)
        assert conn2 is conn1
        pool.return_connection(conn2)

    def test_max_connections_limit(self, pool):
        """Test that max_connections limit is enforced"""
        connections: List = []

        # Acquire all available connections
        for _ in range(pool.max_connections):
            conn = pool.get_connection()
            connections.append(conn)

        assert pool.idle_connections == 0
        assert pool.total_connections == pool.max_connections

        # Try to acquire one more connection (should fail or raise error)
        with pytest.raises((PoolExhaustedError, TimeoutError)):
            pool.get_connection(timeout=1)

        # Return all connections
        for conn in connections:
            pool.return_connection(conn)

        assert pool.idle_connections == pool.max_connections

    def test_connection_timeout(self, pool):
        """Test connection timeout when pool is exhausted"""
        connections: List = []

        # Acquire all connections
        for _ in range(pool.max_connections):
            conn = pool.get_connection()
            connections.append(conn)

        # Try to acquire with timeout (should fail)
        start_time = time.time()
        with pytest.raises((PoolExhaustedError, TimeoutError)):
            pool.get_connection(timeout=2)
        elapsed = time.time() - start_time

        # Should have waited approximately the timeout duration
        assert elapsed >= 1.5  # Allow some margin

        # Cleanup
        for conn in connections:
            pool.return_connection(conn)

    def test_connection_health_check(self, pool):
        """Test that unhealthy connections are discarded"""
        conn = pool.get_connection()

        # Simulate a broken connection
        conn.close()

        # Return broken connection (should be detected and discarded)
        pool.return_connection(conn)

        # Get a new connection (should be healthy)
        new_conn = pool.get_connection()
        assert new_conn is not conn
        assert new_conn.execute("SELECT 1").fetchone()[0] == 1

        pool.return_connection(new_conn)

    def test_close_pool(self, pool):
        """Test closing the pool"""
        conn = pool.get_connection()

        # Close pool (should close all connections)
        pool.close()

        assert pool.total_connections == 0
        assert pool.idle_connections == 0

        # Try to get connection after pool is closed
        with pytest.raises(RuntimeError):
            pool.get_connection()

    def test_context_manager(self, test_db_path, pool_config):
        """Test using pool as context manager"""
        with ConnectionPool(db_path=str(test_db_path), config=pool_config) as pool:
            conn = pool.get_connection()
            assert conn is not None
            pool.return_connection(conn)

        # Pool should be closed after context
        assert pool.total_connections == 0


class TestConnectionPoolThreadSafety:
    """Test connection pool thread safety"""

    @pytest.fixture
    def test_db_path(self, tmp_path):
        """Create a temporary test database"""
        return tmp_path / "test_concurrent.db"

    @pytest.fixture
    def pool_config(self):
        """Test configuration"""
        return ConnectionPoolConfig(
            max_connections=10, min_connections=2, max_idle_time=60, connection_timeout=30
        )

    @pytest.fixture
    def pool(self, test_db_path, pool_config):
        """Create a connection pool for testing"""
        pool = ConnectionPool(db_path=str(test_db_path), config=pool_config)
        yield pool
        pool.close()

    def test_concurrent_connections(self, pool):
        """Test concurrent connection acquisition"""
        results = []
        errors = []

        def worker(worker_id):
            try:
                # Acquire connection
                conn = pool.get_connection(timeout=5)
                results.append(worker_id)

                # Simulate some work
                time.sleep(0.1)

                # Return connection
                pool.return_connection(conn)

            except Exception as e:
                errors.append((worker_id, e))

        # Spawn multiple threads
        threads = []
        num_threads = 20

        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # All threads should succeed
        assert len(results) == num_threads
        assert len(errors) == 0

        # All connections should be returned
        assert pool.idle_connections == pool.total_connections

    def test_concurrent_queries(self, pool):
        """Test concurrent database queries"""
        # Create test table
        conn = pool.get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                value TEXT
            )
        """
        )
        conn.commit()
        pool.return_connection(conn)

        errors = []

        def worker(worker_id):
            try:
                conn = pool.get_connection(timeout=5)

                # Insert data
                conn.execute("INSERT INTO test_table (value) VALUES (?)", (f"worker_{worker_id}",))
                conn.commit()

                # Query data
                result = conn.execute("SELECT COUNT(*) FROM test_table").fetchone()

                pool.return_connection(conn)

                return result[0]

            except Exception as e:
                errors.append((worker_id, e))
                return None

        # Spawn multiple threads
        threads = []
        num_threads = 10

        for i in range(num_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # All threads should succeed
        assert len(errors) == 0

        # Verify data integrity
        conn = pool.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM test_table").fetchone()[0]
        pool.return_connection(conn)

        assert count == num_threads


class TestConnectionPoolPerformance:
    """Test connection pool performance"""

    @pytest.fixture
    def test_db_path(self, tmp_path):
        """Create a temporary test database"""
        return tmp_path / "test_perf.db"

    @pytest.fixture
    def pool_config(self):
        """Test configuration"""
        return ConnectionPoolConfig(
            max_connections=10, min_connections=2, max_idle_time=60, connection_timeout=30
        )

    @pytest.fixture
    def pool(self, test_db_path, pool_config):
        """Create a connection pool for testing"""
        pool = ConnectionPool(db_path=str(test_db_path), config=pool_config)
        yield pool
        pool.close()

    def test_connection_reuse_rate(self, pool):
        """Test that connection reuse rate is ≥90%"""
        num_iterations = 100

        # First acquisition creates a connection
        conn1 = pool.get_connection()
        initial_count = pool.total_connections
        pool.return_connection(conn1)

        # Subsequent acquisitions should reuse
        reuse_count = 0
        for _ in range(num_iterations):
            conn = pool.get_connection()
            if pool.total_connections == initial_count:
                reuse_count += 1
            pool.return_connection(conn)

        reuse_rate = (reuse_count / num_iterations) * 100
        assert reuse_rate >= 90, f"Connection reuse rate: {reuse_rate:.1f}% (target: ≥90%)"

    def test_acquisition_performance(self, pool):
        """Test that connection acquisition is ≤10ms"""
        num_iterations = 50

        # Warm up the pool
        conn = pool.get_connection()
        pool.return_connection(conn)

        # Measure acquisition time
        start_time = time.time()
        for _ in range(num_iterations):
            conn = pool.get_connection()
            pool.return_connection(conn)
        elapsed = time.time() - start_time

        avg_time = (elapsed / num_iterations) * 1000  # Convert to ms
        assert avg_time <= 10, f"Average acquisition time: {avg_time:.2f}ms (target: ≤10ms)"

    def test_pool_efficiency(self, pool):
        """Test overall pool efficiency"""
        # Simulate realistic workload
        operations = 100

        start_time = time.time()
        for _ in range(operations):
            conn = pool.get_connection()
            # Simulate some work
            _ = conn.execute("SELECT 1").fetchone()
            pool.return_connection(conn)
        elapsed = time.time() - start_time

        # Calculate efficiency metric
        avg_op_time = (elapsed / operations) * 1000  # ms

        # Should be very fast with connection pooling
        assert avg_op_time <= 20, f"Average operation time: {avg_op_time:.2f}ms (target: ≤20ms)"


class TestGlobalConnectionPool:
    """Test global connection pool singleton"""

    def test_get_singleton_pool(self):
        """Test that get_connection_pool returns singleton"""
        pool1 = get_connection_pool()
        pool2 = get_connection_pool()

        assert pool1 is pool2

    def test_singleton_pool_initialized(self):
        """Test that singleton pool is properly initialized"""
        pool = get_connection_pool()

        assert pool is not None
        assert hasattr(pool, 'get_connection')
        assert hasattr(pool, 'return_connection')
        assert hasattr(pool, 'close')


class TestConnectionPoolIntegration:
    """Integration tests with database operations"""

    @pytest.fixture
    def test_db_path(self, tmp_path):
        """Create a temporary test database"""
        return tmp_path / "test_integration.db"

    @pytest.fixture
    def pool(self, test_db_path):
        """Create a connection pool for testing"""
        pool = ConnectionPool(
            db_path=str(test_db_path), config=ConnectionPoolConfig(max_connections=5)
        )
        yield pool
        pool.close()

    def test_crud_operations(self, pool):
        """Test CRUD operations with connection pool"""
        # Create table
        conn = pool.get_connection()
        conn.execute(
            """
            CREATE TABLE test_users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        """
        )
        conn.commit()
        pool.return_connection(conn)

        # Insert data
        conn = pool.get_connection()
        conn.execute(
            "INSERT INTO test_users (name, email) VALUES (?, ?)", ("Alice", "alice@example.com")
        )
        conn.execute(
            "INSERT INTO test_users (name, email) VALUES (?, ?)", ("Bob", "bob@example.com")
        )
        conn.commit()
        pool.return_connection(conn)

        # Query data
        conn = pool.get_connection()
        users = conn.execute("SELECT * FROM test_users").fetchall()
        pool.return_connection(conn)

        assert len(users) == 2
        assert users[0]["name"] == "Alice"
        assert users[1]["name"] == "Bob"

        # Update data
        conn = pool.get_connection()
        conn.execute(
            "UPDATE test_users SET email = ? WHERE name = ?", ("alice@updated.com", "Alice")
        )
        conn.commit()
        pool.return_connection(conn)

        # Verify update
        conn = pool.get_connection()
        user = conn.execute("SELECT * FROM test_users WHERE name = ?", ("Alice",)).fetchone()
        pool.return_connection(conn)

        assert user["email"] == "alice@updated.com"

        # Delete data
        conn = pool.get_connection()
        conn.execute("DELETE FROM test_users WHERE name = ?", ("Bob",))
        conn.commit()
        pool.return_connection(conn)

        # Verify deletion
        conn = pool.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM test_users").fetchone()[0]
        pool.return_connection(conn)

        assert count == 1

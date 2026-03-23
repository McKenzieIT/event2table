"""
Event Nodes API Consistency Test Suite
TDD Red Phase - Failing test for P0 bug fix

Bug: Statistics show "1 node" but search returns empty list
Root Cause: Stats API uses 30-min cache returning stale data, search API returns real-time data
Database state: Only 1 node with is_active=0 (soft deleted)
"""

import pytest
import sqlite3
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.services.event_node_builder import event_node_service, game_service
from backend.models.repositories.event_node_repository import EventNodeRepository
from backend.core.database.database import get_db_connection
from backend.models.entities import EventNodeEntity


class TestEventNodesConsistency:
    """Test suite for Event Nodes API data consistency (P0 #2)"""

    @pytest.fixture
    def db_connection(self):
        """Provide test database connection"""
        test_db_path = "data/test_database.db"
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()

    @pytest.fixture
    def test_game_gid(self):
        """Use test game GID (not STAR001 10000147)"""
        return 90000001  # Test GID range

    @pytest.fixture
    def clean_test_data(self, db_connection, test_game_gid):
        """Clean up test data before and after each test"""
        # Cleanup before
        db_connection.execute("DELETE FROM event_nodes WHERE game_gid = ?", (test_game_gid,))
        db_connection.commit()

        yield

        # Cleanup after
        db_connection.execute("DELETE FROM event_nodes WHERE game_gid = ?", (test_game_gid,))
        db_connection.commit()

    def test_stats_and_search_consistency_with_active_node(
        self, clean_test_data, db_connection, test_game_gid
    ):
        """
        Test Case: Verify stats and search APIs return consistent counts

        Given: A game has 1 active event node (is_active=1)
        When: Calling stats API and search API
        Then: Both should return count=1 (not cached stale data)
        """
        # Arrange: Create test game and event
        self._create_test_game_and_event(db_connection, test_game_gid)

        # Arrange: Create 1 active event node
        node_id = self._create_active_event_node(db_connection, test_game_gid)

        # Act: Call stats API
        stats = event_node_service.get_nodes_stats(test_game_gid)

        # Act: Call search API
        repo = EventNodeRepository()
        search_results = repo.search_nodes(game_gid=test_game_gid, keyword="", limit=100, offset=0)

        # Assert: Stats should show 1 node
        assert stats["total_nodes"] == 1, (
            f"Expected stats.total_nodes=1, got {stats['total_nodes']}. "
            "Stats API returning stale cached data?"
        )

        # Assert: Search should return 1 node
        assert len(search_results) == 1, (
            f"Expected search to return 1 node, got {len(search_results)}. "
            f"Search results: {[n.model_dump() for n in search_results]}"
        )

        # Assert: Both counts should match (critical consistency check)
        assert stats["total_nodes"] == len(search_results), (
            f"Data inconsistency detected! "
            f"Stats show {stats['total_nodes']} nodes, search returns {len(search_results)} nodes. "
            "This indicates cache staleness in stats API."
        )

    def test_stats_and_search_consistency_with_soft_deleted_node(
        self, clean_test_data, db_connection, test_game_gid
    ):
        """
        Test Case: Verify stats and search APIs handle soft-deleted nodes correctly

        Given: A game has 1 soft-deleted event node (is_active=0)
        When: Calling stats API and search API
        Then: Both should return count=0 (not 1 from cached data)
        """
        # Arrange: Create test game and event
        self._create_test_game_and_event(db_connection, test_game_gid)

        # Arrange: Create 1 soft-deleted event node
        node_id = self._create_soft_deleted_event_node(db_connection, test_game_gid)

        # Act: Call stats API
        stats = event_node_service.get_nodes_stats(test_game_gid)

        # Act: Call search API
        repo = EventNodeRepository()
        search_results = repo.search_nodes(game_gid=test_game_gid, keyword="", limit=100, offset=0)

        # Assert: Stats should show 0 nodes (not 1 from cache)
        assert stats["total_nodes"] == 0, (
            f"Expected stats.total_nodes=0 for soft-deleted node, got {stats['total_nodes']}. "
            "Stats API likely returning stale cached data from before soft delete."
        )

        # Assert: Search should return 0 nodes
        assert len(search_results) == 0, (
            f"Expected search to return 0 nodes for soft-deleted, got {len(search_results)}. "
            "Search API incorrectly returning soft-deleted nodes?"
        )

        # Assert: Both counts should match (critical consistency check)
        assert stats["total_nodes"] == len(search_results), (
            f"Data inconsistency detected with soft-deleted nodes! "
            f"Stats show {stats['total_nodes']} nodes, search returns {len(search_results)} nodes."
        )

    def test_stats_cache_invalidation_after_node_creation(
        self, clean_test_data, db_connection, test_game_gid
    ):
        """
        Test Case: Verify stats cache is invalidated after node creation

        Given: A game with 0 nodes
        When: Creating a new active node
        Then: Stats API should immediately reflect the new count (not cached stale data)
        """
        # Arrange: Create test game and event
        self._create_test_game_and_event(db_connection, test_game_gid)

        # Act: Get initial stats (should be 0)
        stats_before = event_node_service.get_nodes_stats(test_game_gid)
        assert stats_before["total_nodes"] == 0, "Initial stats should be 0"

        # Act: Create new active node
        node_id = self._create_active_event_node(db_connection, test_game_gid)

        # Act: Get stats immediately after creation
        # Note: This tests cache invalidation or short TTL
        stats_after = event_node_service.get_nodes_stats(test_game_gid)

        # Assert: Stats should reflect new node immediately
        assert stats_after["total_nodes"] == 1, (
            f"Expected stats.total_nodes=1 after node creation, got {stats_after['total_nodes']}. "
            "Cache invalidation not working or TTL too long (currently 1800s = 30 min)"
        )

    def test_stats_cache_invalidation_after_node_deletion(
        self, clean_test_data, db_connection, test_game_gid
    ):
        """
        Test Case: Verify stats cache is invalidated after node deletion

        Given: A game with 1 active node
        When: Soft-deleting the node
        Then: Stats API should immediately reflect count=0 (not cached stale data)
        """
        # Arrange: Create test game and event
        self._create_test_game_and_event(db_connection, test_game_gid)

        # Arrange: Create active node
        node_id = self._create_active_event_node(db_connection, test_game_gid)

        # Act: Get initial stats (should be 1)
        stats_before = event_node_service.get_nodes_stats(test_game_gid)
        assert stats_before["total_nodes"] == 1, "Initial stats should be 1"

        # Act: Soft-delete the node
        event_node_service.soft_delete_node(node_id)

        # Act: Get stats immediately after deletion
        # Note: This tests cache invalidation or short TTL
        stats_after = event_node_service.get_nodes_stats(test_game_gid)

        # Assert: Stats should reflect deletion immediately
        assert stats_after["total_nodes"] == 0, (
            f"Expected stats.total_nodes=0 after node deletion, got {stats_after['total_nodes']}. "
            "Cache invalidation not working or TTL too long (currently 1800s = 30 min)"
        )

    # Helper methods

    def _create_test_game_and_event(self, db_connection, game_gid):
        """Create test game and event for testing"""
        # Create test game
        db_connection.execute(
            """INSERT INTO games (gid, name, ods_db, dwd_prefix)
            VALUES (?, ?, ?, ?)""",
            (game_gid, "Test Game", "ieu_ods", "dwd"),
        )

        # Create test event
        cursor = db_connection.execute(
            """INSERT INTO log_events (game_gid, name, name_cn)
            VALUES (?, ?, ?)""",
            (game_gid, "test.event", "测试事件"),
        )
        return cursor.lastrowid

    def _create_active_event_node(self, db_connection, game_gid):
        """Create an active event node (is_active=1)"""
        # Get event_id
        event_row = db_connection.execute(
            "SELECT id FROM log_events WHERE game_gid = ? LIMIT 1", (game_gid,)
        ).fetchone()

        if not event_row:
            raise ValueError("No event found for test game")

        event_id = event_row[0]

        # Create active node
        config_json = '{"fields": [{"name": "test_field"}]}'
        cursor = db_connection.execute(
            """INSERT INTO event_nodes (game_gid, name, event_id, config_json, is_active)
            VALUES (?, ?, ?, ?, 1)""",
            (game_gid, "Test Node", event_id, config_json),
        )
        db_connection.commit()
        return cursor.lastrowid

    def _create_soft_deleted_event_node(self, db_connection, game_gid):
        """Create a soft-deleted event node (is_active=0)"""
        # Get event_id
        event_row = db_connection.execute(
            "SELECT id FROM log_events WHERE game_gid = ? LIMIT 1", (game_gid,)
        ).fetchone()

        if not event_row:
            raise ValueError("No event found for test game")

        event_id = event_row[0]

        # Create soft-deleted node
        config_json = '{"fields": [{"name": "test_field"}]}'
        cursor = db_connection.execute(
            """INSERT INTO event_nodes (game_gid, name, event_id, config_json, is_active)
            VALUES (?, ?, ?, ?, 0)""",
            (game_gid, "Deleted Node", event_id, config_json),
        )
        db_connection.commit()
        return cursor.lastrowid


class TestEventNodesRepositoryDirect:
    """Direct repository tests to verify SQL query correctness"""

    @pytest.fixture
    def db_connection(self):
        """Provide test database connection"""
        test_db_path = "data/test_database.db"
        conn = sqlite3.connect(test_db_path)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.close()

    @pytest.fixture
    def test_game_gid(self):
        """Use test game GID"""
        return 90000002

    @pytest.fixture
    def clean_test_data(self, db_connection, test_game_gid):
        """Clean up test data"""
        db_connection.execute("DELETE FROM event_nodes WHERE game_gid = ?", (test_game_gid,))
        db_connection.execute("DELETE FROM log_events WHERE game_gid = ?", (test_game_gid,))
        db_connection.execute("DELETE FROM games WHERE gid = ?", (test_game_gid,))
        db_connection.commit()

        yield

        # Cleanup
        db_connection.execute("DELETE FROM event_nodes WHERE game_gid = ?", (test_game_gid,))
        db_connection.commit()

    def test_repository_stats_query_filters_is_active(
        self, clean_test_data, db_connection, test_game_gid
    ):
        """
        Direct test: Verify repository stats query correctly filters is_active=1

        This test bypasses caching to verify SQL query is correct
        """
        # Arrange: Create test data
        db_connection.execute(
            "INSERT INTO games (gid, name, ods_db, dwd_prefix) VALUES (?, ?, ?, ?)",
            (test_game_gid, "Test Game", "ieu_ods", "dwd"),
        )

        event_id = db_connection.execute(
            "INSERT INTO log_events (game_gid, name) VALUES (?, ?)", (test_game_gid, "test.event")
        ).lastrowid

        # Create 2 active nodes
        for i in range(2):
            db_connection.execute(
                """INSERT INTO event_nodes (game_gid, name, event_id, config_json, is_active)
                VALUES (?, ?, ?, ?, 1)""",
                (test_game_gid, f"Active Node {i}", event_id, '{"test": "data"}'),
            )

        # Create 1 soft-deleted node
        db_connection.execute(
            """INSERT INTO event_nodes (game_gid, name, event_id, config_json, is_active)
            VALUES (?, ?, ?, ?, 0)""",
            (test_game_gid, "Deleted Node", event_id, '{"test": "data"}'),
        )

        db_connection.commit()

        # Act: Query stats directly using repository
        repo = EventNodeRepository()
        stats = repo.get_nodes_stats(test_game_gid)

        # Assert: Should only count active nodes (is_active=1)
        assert stats["total_nodes"] == 2, (
            f"Repository stats query should count only is_active=1 nodes. "
            f"Expected 2, got {stats['total_nodes']}. "
            "SQL query may not have correct WHERE clause."
        )

        assert stats["unique_events"] == 1, "Should count unique events"

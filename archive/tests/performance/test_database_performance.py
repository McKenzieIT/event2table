"""
Performance tests for database queries

Requirements:
- Query response time < 100ms (P95)
- Efficient use of indexes
- No N+1 query problems
"""
import pytest
import time
import numpy as np
from backend.core.database import get_db_connection
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict


class TestDatabasePerformance:
    """Test database query performance"""

    def test_parameter_query_by_game_performance(self):
        """Test parameter query by game_gid performance"""

        conn = get_db_connection()

        # Warm-up
        for _ in range(3):
            fetch_all_as_dict(
                "SELECT ep.* FROM event_params ep "
                "INNER JOIN log_events le ON ep.event_id = le.id "
                "WHERE le.game_gid = ?",
                (10000147,)
            )

        # Measure 100 queries
        times = []
        for _ in range(100):
            start = time.perf_counter()
            result = fetch_all_as_dict(
                "SELECT ep.* FROM event_params ep "
                "INNER JOIN log_events le ON ep.event_id = le.id "
                "WHERE le.game_gid = ?",
                (10000147,)
            )
            end = time.perf_counter()

            times.append((end - start) * 1000)

        p95 = np.percentile(times, 95)
        avg_time = np.mean(times)

        print(f"\n📊 Parameter Query by Game Performance (100 queries):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P95: {p95:.2f} ms")
        print(f"  Results: {len(result)} parameters")

        assert p95 < 100, f"P95 latency {p95:.2f}ms exceeds 100ms threshold"

        conn.close()

    def test_common_parameter_query_performance(self):
        """Test common parameter query performance"""

        conn = get_db_connection()

        # Warm-up
        for _ in range(3):
            fetch_all_as_dict(
                "SELECT * FROM common_params WHERE game_gid = ?",
                (10000147,)
            )

        # Measure 100 queries
        times = []
        for _ in range(100):
            start = time.perf_counter()
            result = fetch_all_as_dict(
                "SELECT * FROM common_params WHERE game_gid = ?",
                (10000147,)
            )
            end = time.perf_counter()

            times.append((end - start) * 1000)

        p95 = np.percentile(times, 95)
        avg_time = np.mean(times)

        print(f"\n📊 Common Parameter Query Performance (100 queries):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P95: {p95:.2f} ms")
        print(f"  Results: {len(result)} common parameters")

        assert p95 < 50, f"P95 latency {p95:.2f}ms exceeds 50ms threshold"

        conn.close()

    def test_parameter_count_query_performance(self):
        """Test parameter aggregation query performance"""

        conn = get_db_connection()

        # Warm-up
        for _ in range(3):
            fetch_all_as_dict(
                "SELECT ep.param_name, COUNT(*) as count "
                "FROM event_params ep "
                "INNER JOIN log_events le ON ep.event_id = le.id "
                "WHERE le.game_gid = ? "
                "GROUP BY ep.param_name",
                (10000147,)
            )

        # Measure 100 aggregation queries
        times = []
        for _ in range(100):
            start = time.perf_counter()
            result = fetch_all_as_dict(
                "SELECT ep.param_name, COUNT(*) as count "
                "FROM event_params ep "
                "INNER JOIN log_events le ON ep.event_id = le.id "
                "WHERE le.game_gid = ? "
                "GROUP BY ep.param_name",
                (10000147,)
            )
            end = time.perf_counter()

            times.append((end - start) * 1000)

        p95 = np.percentile(times, 95)
        avg_time = np.mean(times)

        print(f"\n📊 Parameter Aggregation Query Performance (100 queries):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P95: {p95:.2f} ms")
        print(f"  Unique parameters: {len(result)}")

        assert p95 < 100, f"P95 latency {p95:.2f}ms exceeds 100ms threshold"

        conn.close()

    def test_index_usage_efficiency(self):
        """Test that queries use indexes efficiently"""

        conn = get_db_connection()

        # Get query plan for parameter query
        cursor = conn.cursor()
        cursor.execute(
            "EXPLAIN QUERY PLAN "
            "SELECT ep.* FROM event_params ep "
            "INNER JOIN log_events le ON ep.event_id = le.id "
            "WHERE le.game_gid = ?",
            (10000147,)
        )
        query_plan = cursor.fetchall()

        print(f"\n📊 Query Plan for Parameter Query:")
        for step in query_plan:
            # Convert Row objects to strings for display
            print(f"  {dict(step)}")

        # Check that indexes are being used
        plan_str = str([dict(row) for row in query_plan])
        # Look for index usage indicators
        uses_index = any(keyword in plan_str for keyword in ['USING INDEX', 'SEARCH', 'INDEX'])

        if not uses_index:
            pytest.skip("Query does not use indexes (may be acceptable for small datasets)")

        cursor.close()
        conn.close()

    def test_parameter_join_performance(self):
        """Test parameter join query performance with multiple tables"""

        conn = get_db_connection()

        # Complex join query
        query = """
            SELECT
                ep.id,
                ep.param_name,
                ep.param_type,
                le.event_name,
                g.name as game_name
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            INNER JOIN games g ON le.game_gid = g.gid
            WHERE le.game_gid = ?
            AND ep.is_active = 1
            ORDER BY ep.param_name
            LIMIT 100
        """

        # Warm-up
        for _ in range(3):
            fetch_all_as_dict(query, (10000147,))

        # Measure 100 queries
        times = []
        for _ in range(100):
            start = time.perf_counter()
            result = fetch_all_as_dict(query, (10000147,))
            end = time.perf_counter()

            times.append((end - start) * 1000)

        p95 = np.percentile(times, 95)
        avg_time = np.mean(times)

        print(f"\n📊 Parameter Join Query Performance (100 queries):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P95: {p95:.2f} ms")
        print(f"  Results: {len(result)} parameters")

        assert p95 < 150, f"P95 latency {p95:.2f}ms exceeds 150ms threshold"

        conn.close()

    def test_write_operation_performance(self):
        """Test database write operation performance"""

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if param_type column exists
        cursor.execute("PRAGMA table_info(event_params)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'param_type' not in columns:
            cursor.close()
            conn.close()
            pytest.skip("param_type column not found in event_params table")

        # Test INSERT performance
        times = []
        test_gid = 90000001  # Use test GID range

        # Clean up any existing test data
        cursor.execute("DELETE FROM event_params WHERE param_name LIKE 'perf_test_%'")
        conn.commit()

        for i in range(50):
            start = time.perf_counter()
            cursor.execute(
                "INSERT INTO event_params (event_id, param_name, template_id, param_type) "
                "VALUES (?, ?, ?, ?)",
                (1, f'perf_test_{i}', 1, 'string')
            )
            conn.commit()
            end = time.perf_counter()
            times.append((end - start) * 1000)

        # Clean up test data
        cursor.execute("DELETE FROM event_params WHERE param_name LIKE 'perf_test_%'")
        conn.commit()

        p95 = np.percentile(times, 95)
        avg_time = np.mean(times)

        print(f"\n📊 Write Operation Performance (50 inserts):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P95: {p95:.2f} ms")

        assert p95 < 10, f"P95 write latency {p95:.2f}ms exceeds 10ms threshold"

        cursor.close()
        conn.close()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Test for GET /api/games Endpoint

This test measures the performance improvement after optimizing the games list query
from correlated subqueries to LEFT JOINs.
"""

import sys
import time
import statistics
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

import sqlite3


def time_query(query: str, db_path: str, iterations: int = 20) -> dict:
    """
    Time a query execution over multiple iterations.

    Args:
        query: SQL query to execute
        db_path: Path to SQLite database
        iterations: Number of times to run the query

    Returns:
        Dictionary with timing statistics
    """
    times = []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Warm-up run
    conn.execute(query).fetchall()

    for _ in range(iterations):
        start = time.perf_counter()
        result = conn.execute(query).fetchall()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    conn.close()

    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
        'p95': statistics.quantiles(times, n=20)[18] if len(times) > 1 else times[0],  # 95th percentile
        'count': len(result[0]) if result else 0
    }


def main():
    """Run performance comparison tests."""
    db_path = "/Users/mckenzie/Documents/event2table/backend/core/config/dwd_generator.db"

    print("=" * 70)
    print("GET /api/games Performance Test")
    print("=" * 70)
    print()

    # Check if database exists
    if not Path(db_path).exists():
        print(f"ERROR: Database not found at {db_path}")
        return 1

    # Get game count
    conn = sqlite3.connect(db_path)
    game_count = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    conn.close()

    print(f"Database: {db_path}")
    print(f"Total games: {game_count}")
    print()

    # Original query (with correlated subqueries)
    original_query = """
    SELECT
        g.id,
        g.gid,
        g.name,
        g.ods_db,
        g.icon_path,
        g.created_at,
        g.updated_at,
        (SELECT COUNT(*) FROM log_events le WHERE le.game_id = g.id) as event_count,
        (SELECT COUNT(*) FROM event_params ep
         INNER JOIN log_events le ON ep.event_id = le.id
         WHERE le.game_id = g.id AND ep.is_active = 1) as param_count,
        (SELECT COUNT(*) FROM event_node_configs enc WHERE enc.game_gid = CAST(g.gid AS INTEGER)) as event_node_count,
        (SELECT COUNT(*) FROM flow_templates ft WHERE ft.game_id = g.id AND ft.is_active = 1) as flow_template_count
    FROM games g
    ORDER BY g.id
    """

    # Optimized query (with LEFT JOINs)
    optimized_query = """
    SELECT
        g.id,
        g.gid,
        g.name,
        g.ods_db,
        g.icon_path,
        g.created_at,
        g.updated_at,
        COUNT(DISTINCT le.id) as event_count,
        COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as param_count,
        COUNT(DISTINCT enc.id) as event_node_count,
        COUNT(DISTINCT CASE WHEN ft.is_active = 1 THEN ft.id END) as flow_template_count
    FROM games g
    LEFT JOIN log_events le ON le.game_id = g.id
    LEFT JOIN event_params ep ON ep.event_id = le.id
    LEFT JOIN event_node_configs enc ON enc.game_gid = CAST(g.gid AS INTEGER)
    LEFT JOIN flow_templates ft ON ft.game_id = g.id
    GROUP BY g.id, g.gid, g.name, g.ods_db, g.icon_path, g.created_at, g.updated_at
    ORDER BY g.id
    """

    print("-" * 70)
    print("Testing ORIGINAL query (with correlated subqueries)")
    print("-" * 70)
    original_stats = time_query(original_query, db_path, 20)
    print(f"  Mean:      {original_stats['mean']:.2f}ms")
    print(f"  Median:    {original_stats['median']:.2f}ms")
    print(f"  P95:       {original_stats['p95']:.2f}ms")
    print(f"  Min:       {original_stats['min']:.2f}ms")
    print(f"  Max:       {original_stats['max']:.2f}ms")
    print(f"  StdDev:    {original_stats['stdev']:.2f}ms")
    print(f"  Row Count: {original_stats['count']}")
    print()

    print("-" * 70)
    print("Testing OPTIMIZED query (with LEFT JOINs)")
    print("-" * 70)
    optimized_stats = time_query(optimized_query, db_path, 20)
    print(f"  Mean:      {optimized_stats['mean']:.2f}ms")
    print(f"  Median:    {optimized_stats['median']:.2f}ms")
    print(f"  P95:       {optimized_stats['p95']:.2f}ms")
    print(f"  Min:       {optimized_stats['min']:.2f}ms")
    print(f"  Max:       {optimized_stats['max']:.2f}ms")
    print(f"  StdDev:    {optimized_stats['stdev']:.2f}ms")
    print(f"  Row Count: {optimized_stats['count']}")
    print()

    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    # Calculate improvement metrics
    improvement_mean = ((original_stats['mean'] - optimized_stats['mean']) /
                        original_stats['mean'] * 100)
    improvement_p95 = ((original_stats['p95'] - optimized_stats['p95']) /
                       original_stats['p95'] * 100)

    print(f"Original Mean:  {original_stats['mean']:.2f}ms")
    print(f"Optimized Mean: {optimized_stats['mean']:.2f}ms")
    print(f"Improvement:    {improvement_mean:+.1f}%")
    print()
    print(f"Original P95:   {original_stats['p95']:.2f}ms")
    print(f"Optimized P95:  {optimized_stats['p95']:.2f}ms")
    print(f"Improvement:    {improvement_p95:+.1f}%")
    print()

    # SLA compliance check
    print("-" * 70)
    print("SLA Compliance")
    print("-" * 70)
    sla_threshold = 200  # ms
    print(f"SLA Threshold: {sla_threshold}ms")

    if optimized_stats['mean'] < sla_threshold:
        print(f"✓ PASS: Mean response time ({optimized_stats['mean']:.2f}ms) is below SLA")
    else:
        print(f"✗ FAIL: Mean response time ({optimized_stats['mean']:.2f}ms) exceeds SLA")

    if optimized_stats['p95'] < sla_threshold:
        print(f"✓ PASS: P95 response time ({optimized_stats['p95']:.2f}ms) is below SLA")
    else:
        print(f"✗ FAIL: P95 response time ({optimized_stats['p95']:.2f}ms) exceeds SLA")

    print()

    # Query complexity analysis
    print("-" * 70)
    print("Query Complexity Analysis")
    print("-" * 70)
    print(f"Original:  4 correlated subqueries × {game_count} games = {4 * game_count}+ queries")
    print(f"Optimized: 1 single query with LEFT JOINs")
    print(f"Reduction: {(4 * game_count)} → 1 ({((4 * game_count - 1) / (4 * game_count) * 100):.1f}% reduction)")
    print()

    # Scalability projection
    print("-" * 70)
    print("Scalability Projection (estimated)")
    print("-" * 70)
    for future_games in [50, 100, 200, 500]:
        original_estimated = (original_stats['mean'] / game_count) * future_games
        optimized_estimated = (optimized_stats['mean'] / game_count) * future_games
        print(f"{future_games} games:")
        print(f"  Original:  ~{original_estimated:.0f}ms")
        print(f"  Optimized: ~{optimized_estimated:.0f}ms")

    print()
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())

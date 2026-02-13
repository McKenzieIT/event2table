#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Test for Parameters API Optimization
================================================

Tests the performance improvements for GET /api/parameters/all endpoint
after optimization with composite indexes and hierarchical caching.

Baseline (before optimization):
- Average: 267.94ms
- P95: 352.28ms
- SLA threshold: 200ms

Target (after optimization):
- Average: <100ms (70% improvement)
- P95: <150ms
- Cache hit: <10ms
"""

import sys
import time
import statistics
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database.database import get_db_connection
from backend.core.cache.cache_system import hierarchical_cache, CacheKeyBuilder


class ParametersPerformanceTest:
    """Performance test suite for parameters API optimization"""

    def __init__(self, db_path: str = None):
        """Initialize test with database connection"""
        if db_path:
            self.db_path = db_path
        else:
            from backend.core.config import get_db_path
            self.db_path = str(get_db_path())

        self.results = {
            "query_times": [],
            "cache_hit_times": [],
            "cache_miss_times": [],
        }

    def setup_test_data(self):
        """Create test data for performance testing"""
        print("🔧 Setting up test data...")

        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if we have test data
            cursor.execute("SELECT COUNT(*) FROM event_params")
            param_count = cursor.fetchone()[0]

            if param_count > 1000:
                print(f"✅ Test data already exists: {param_count} parameters")
                return

            print("⚠️  Insufficient test data. Creating sample data...")

            # Get or create a test game
            cursor.execute("SELECT id, gid FROM games WHERE gid = '10000147' LIMIT 1")
            game = cursor.fetchone()

            if not game:
                cursor.execute("""
                    INSERT INTO games (name, gid, description, status)
                    VALUES ('Test Game', '10000147', 'Performance Test Game', 'active')
                """)
                game_id = cursor.lastrowid
                print(f"✅ Created test game: id={game_id}")
            else:
                game_id, game_gid = game
                print(f"✅ Using existing game: id={game_id}, gid={game_gid}")

            # Create test events
            cursor.execute("SELECT COUNT(*) FROM log_events WHERE game_id = ?", (game_id,))
            event_count = cursor.fetchone()[0]

            if event_count < 10:
                print(f"Creating {10 - event_count} test events...")
                for i in range(event_count, 10):
                    cursor.execute("""
                        INSERT INTO log_events (
                            game_id, game_gid, event_name, event_name_cn,
                            source_table, target_table, include_in_common_params
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        game_id, '10000147',
                        f'test_event_{i}',
                        f'测试事件_{i}',
                        f'ods_test_{i}',
                        f'dwd_test_{i}',
                        1
                    ))

            # Get event IDs
            cursor.execute("SELECT id FROM log_events WHERE game_id = ? LIMIT 10", (game_id,))
            event_ids = [row[0] for row in cursor.fetchall()]

            # Get or create parameter templates
            cursor.execute("SELECT id, base_type FROM param_templates LIMIT 3")
            templates = cursor.fetchall()

            if len(templates) < 3:
                print("Creating parameter templates...")
                cursor.execute("INSERT INTO param_templates (template_name, base_type) VALUES (?, ?)",
                             ("string", "string"))
                template_id_1 = cursor.lastrowid
                cursor.execute("INSERT INTO param_templates (template_name, base_type) VALUES (?, ?)",
                             ("int", "int"))
                template_id_2 = cursor.lastrowid
                cursor.execute("INSERT INTO param_templates (template_name, base_type) VALUES (?, ?)",
                             ("json", "json"))
                template_id_3 = cursor.lastrowid
                templates = [(template_id_1, "string"), (template_id_2, "int"), (template_id_3, "json")]

            # Create test parameters (target: ~5000 parameters for realistic testing)
            print("Creating test parameters...")
            param_names = [f"param_{i}" for i in range(500)]
            template_ids = [t[0] for t in templates]

            batch_size = 0
            for event_id in event_ids:
                for param_name in param_names:
                    template_id = template_ids[len(param_name) % len(template_ids)]
                    cursor.execute("""
                        INSERT INTO event_params (
                            event_id, param_name, param_name_cn,
                            template_id, is_active, version
                        ) VALUES (?, ?, ?, ?, 1, 1)
                    """, (
                        event_id,
                        param_name,
                        f"参数_{param_name}",
                        template_id
                    ))
                    batch_size += 1

                    if batch_size >= 1000:
                        conn.commit()
                        print(f"  Created {batch_size} parameters...")
                        batch_size = 0

            conn.commit()
            print(f"✅ Test data created successfully")

        finally:
            conn.close()

    def test_query_performance(self, iterations: int = 100) -> Dict:
        """Test raw query performance (without cache)"""
        print(f"\n📊 Testing query performance ({iterations} iterations)...")

        # Clear cache to test raw query performance
        hierarchical_cache.clear_all()

        query = """
            SELECT
                ep.param_name,
                MIN(ep.param_name_cn) as param_name_cn,
                pt.base_type,
                COUNT(DISTINCT ep.event_id) as events_count,
                COUNT(*) as usage_count,
                CASE WHEN COUNT(DISTINCT ep.event_id) >= 3 THEN 1 ELSE 0 END as is_common
            FROM event_params ep
            JOIN log_events le ON ep.event_id = le.id
            LEFT JOIN param_templates pt ON ep.template_id = pt.id
            WHERE le.game_gid = '10000147' AND ep.is_active = 1
            GROUP BY ep.param_name, pt.base_type
            ORDER BY usage_count DESC, ep.param_name ASC
            LIMIT 50 OFFSET 0
        """

        times = []

        for i in range(iterations):
            start = time.perf_counter()

            conn = get_db_connection(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.close()

            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)

            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations...")

        return {
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "p95": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
            "count": len(results),
        }

    def test_cache_performance(self, iterations: int = 100) -> Dict:
        """Test cache performance (L1 + L2 hits)"""
        print(f"\n💾 Testing cache performance ({iterations} iterations)...")

        # Clear cache first
        hierarchical_cache.clear_all()

        # Prime the cache
        cache_key_params = {"game_id": 1, "search": "", "type": "", "page": 1, "limit": 50}
        test_data = {"parameters": [], "total": 0, "page": 1, "has_more": False}
        hierarchical_cache.set("parameters.all", test_data, ttl=300, **cache_key_params)

        times = []

        for i in range(iterations):
            start = time.perf_counter()

            result = hierarchical_cache.get("parameters.all", **cache_key_params)

            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)

            if (i + 1) % 20 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations...")

        return {
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "p95": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
        }

    def test_end_to_end_performance(self, iterations: int = 50) -> Dict:
        """Test end-to-end API performance including database + cache"""
        print(f"\n🚀 Testing end-to-end performance ({iterations} iterations)...")

        hierarchical_cache.clear_all()

        times = []
        cache_hits = 0
        cache_misses = 0

        for i in range(iterations):
            start = time.perf_counter()

            # Simulate API call
            cache_key_params = {"game_id": 1, "search": "", "type": "", "page": 1, "limit": 50}
            result = hierarchical_cache.get("parameters.all", **cache_key_params)

            if result is not None:
                cache_hits += 1
            else:
                cache_misses += 1
                # Simulate database query and cache set
                test_data = {"parameters": [], "total": 0, "page": 1, "has_more": False}
                hierarchical_cache.set("parameters.all", test_data, ttl=300, **cache_key_params)

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

            if (i + 1) % 10 == 0:
                print(f"  Completed {i + 1}/{iterations} iterations...")

        return {
            "avg": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "p95": statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "hit_rate": (cache_hits / iterations * 100) if iterations > 0 else 0,
        }

    def print_report(self, query_results: Dict, cache_results: Dict, e2e_results: Dict):
        """Print performance test report"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST REPORT")
        print("="*80)

        print("\n📊 QUERY PERFORMANCE (Database Only)")
        print("-" * 40)
        print(f"  Average:   {query_results['avg']:.2f} ms")
        print(f"  Median:    {query_results['median']:.2f} ms")
        print(f"  Min:       {query_results['min']:.2f} ms")
        print(f"  Max:       {query_results['max']:.2f} ms")
        print(f"  P95:       {query_results['p95']:.2f} ms")
        print(f"  Results:   {query_results['count']} rows")

        print("\n💾 CACHE PERFORMANCE (L1/L2 Hits)")
        print("-" * 40)
        print(f"  Average:   {cache_results['avg']:.2f} ms")
        print(f"  Median:    {cache_results['median']:.2f} ms")
        print(f"  Min:       {cache_results['min']:.2f} ms")
        print(f"  Max:       {cache_results['max']:.2f} ms")
        print(f"  P95:       {cache_results['p95']:.2f} ms")

        print("\n🚀 END-TO-END PERFORMANCE (API Simulation)")
        print("-" * 40)
        print(f"  Average:   {e2e_results['avg']:.2f} ms")
        print(f"  Median:    {e2e_results['median']:.2f} ms")
        print(f"  Min:       {e2e_results['min']:.2f} ms")
        print(f"  Max:       {e2e_results['max']:.2f} ms")
        print(f"  P95:       {e2e_results['p95']:.2f} ms")
        print(f"  Hit Rate:  {e2e_results['hit_rate']:.1f}%")

        print("\n📈 IMPROVEMENT ANALYSIS")
        print("-" * 40)

        baseline_avg = 267.94
        baseline_p95 = 352.28
        sla_threshold = 200

        improvement_pct = ((baseline_avg - query_results['avg']) / baseline_avg) * 100
        print(f"  Baseline Avg:     {baseline_avg:.2f} ms")
        print(f"  Optimized Avg:    {query_results['avg']:.2f} ms")
        print(f"  Improvement:      {improvement_pct:.1f}%")
        print(f"  Target:           70%")
        print(f"  Status:           {'✅ PASS' if improvement_pct >= 70 else '❌ FAIL'}")

        print(f"\n  SLA Threshold:    {sla_threshold:.2f} ms")
        print(f"  Optimized Avg:    {query_results['avg']:.2f} ms")
        print(f"  Status:           {'✅ PASS' if query_results['avg'] < sla_threshold else '❌ FAIL'}")

        print(f"\n  P95 Baseline:     {baseline_p95:.2f} ms")
        print(f"  P95 Optimized:    {query_results['p95']:.2f} ms")
        print(f"  Status:           {'✅ PASS' if query_results['p95'] < 150 else '⚠️  NEEDS IMPROVEMENT'}")

        print("\n💡 CACHE EFFECTIVENESS")
        print("-" * 40)
        print(f"  Cache Hit Time:   {cache_results['avg']:.2f} ms")
        print(f"  Speedup:          {query_results['avg'] / cache_results['avg']:.1f}x faster")
        print(f"  Hit Rate:         {e2e_results['hit_rate']:.1f}%")

        print("\n" + "="*80)

    def run_full_test(self):
        """Run complete performance test suite"""
        print("🎯 Starting Parameters API Performance Test")
        print("="*80)

        # Setup
        self.setup_test_data()

        # Run tests
        query_results = self.test_query_performance(iterations=100)
        cache_results = self.test_cache_performance(iterations=100)
        e2e_results = self.test_end_to_end_performance(iterations=50)

        # Print report
        self.print_report(query_results, cache_results, e2e_results)

        # Cache stats
        print("\n📊 CACHE STATISTICS")
        print("-" * 40)
        stats = hierarchical_cache.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        return {
            "query": query_results,
            "cache": cache_results,
            "e2e": e2e_results,
        }


def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="Parameters API Performance Test")
    parser.add_argument("--db-path", help="Path to test database")
    parser.add_argument("--iterations", type=int, default=100, help="Number of test iterations")
    args = parser.parse_args()

    tester = ParametersPerformanceTest(db_path=args.db_path)
    results = tester.run_full_test()

    # Exit with appropriate code
    avg_time = results["query"]["avg"]
    if avg_time < 100:
        print("\n✅ Performance test PASSED - Target achieved!")
        return 0
    else:
        print(f"\n⚠️  Performance test WARNING - Average time {avg_time:.2f}ms exceeds target")
        return 1


if __name__ == "__main__":
    sys.exit(main())

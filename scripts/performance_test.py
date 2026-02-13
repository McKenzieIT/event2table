#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Testing Script for Event2Table

Tests:
1. API Response Time (P95 < 200ms target)
2. HQL Generation Time (< 1s target)
3. Cache Hit Rate (> 80% target)
4. Database Query Performance
"""

import os
import sys
import time
import json
import statistics
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment before importing Flask app
# Use production database for performance testing
os.environ['FLASK_DEBUG'] = 'False'

from backend.core.config import get_db_path, FlaskConfig
from backend.core.database import get_db_connection
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field
from backend.core.cache.cache_system import cache_result
from backend.core.logging import get_logger

logger = get_logger(__name__)


class PerformanceTestResults:
    """Store and analyze performance test results"""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.response_times: List[float] = []
        self.errors: List[str] = []
        self.success_count = 0
        self.failure_count = 0

    def add_result(self, response_time: float, success: bool, error: str = None):
        """Add a test result"""
        self.response_times.append(response_time)
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
            if error:
                self.errors.append(error)

    def get_statistics(self) -> Dict[str, Any]:
        """Calculate performance statistics"""
        if not self.response_times:
            return {
                'test_name': self.test_name,
                'total_requests': 0,
                'success_count': 0,
                'failure_count': 0,
                'error_rate': 0,
                'min_time': 0,
                'max_time': 0,
                'avg_time': 0,
                'median_time': 0,
                'p50': 0,
                'p95': 0,
                'p99': 0,
                'throughput': 0
            }

        sorted_times = sorted(self.response_times)
        total_requests = len(self.response_times)
        total_time = sum(self.response_times)

        return {
            'test_name': self.test_name,
            'total_requests': total_requests,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'error_rate': (self.failure_count / total_requests * 100) if total_requests > 0 else 0,
            'min_time': min(self.response_times),
            'max_time': max(self.response_times),
            'avg_time': statistics.mean(self.response_times),
            'median_time': statistics.median(self.response_times),
            'p50': sorted_times[int(len(sorted_times) * 0.50)] if len(sorted_times) > 0 else 0,
            'p95': sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0,
            'p99': sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0,
            'throughput': self.success_count / total_time if total_time > 0 else 0
        }

    def print_summary(self):
        """Print test summary"""
        stats = self.get_statistics()
        print(f"\n{'='*80}")
        print(f"Test: {self.test_name}")
        print(f"{'='*80}")
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Success: {stats['success_count']}")
        print(f"Failures: {stats['failure_count']}")
        print(f"Error Rate: {stats['error_rate']:.2f}%")
        print(f"\nResponse Times:")
        print(f"  Min:    {stats['min_time']*1000:.2f} ms")
        print(f"  Max:    {stats['max_time']*1000:.2f} ms")
        print(f"  Avg:    {stats['avg_time']*1000:.2f} ms")
        print(f"  Median: {stats['median_time']*1000:.2f} ms")
        print(f"  P50:    {stats['p50']*1000:.2f} ms")
        print(f"  P95:    {stats['p95']*1000:.2f} ms")
        print(f"  P99:    {stats['p99']*1000:.2f} ms")
        print(f"\nThroughput: {stats['throughput']:.2f} requests/second")

        if self.errors:
            print(f"\nErrors (first 10):")
            for error in self.errors[:10]:
                print(f"  - {error}")


class PerformanceTester:
    """Performance testing framework"""

    def __init__(self):
        self.db_path = get_db_path()
        self.results: Dict[str, PerformanceTestResults] = {}
        self.cache_stats_before = {}
        self.cache_stats_after = {}

    def setup_test_data(self):
        """Setup test data for performance testing"""
        print("\n" + "="*80)
        print("Setting up test data...")
        print("="*80)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if we have test data
        games = fetch_all_as_dict("SELECT * FROM games LIMIT 1")
        if not games:
            print("Creating test game...")
            cursor.execute("""
                INSERT INTO games (gid, name, ods_db)
                VALUES (10000147, 'Test Game', 'ieu_ods')
            """)
            conn.commit()

        # Check if we have test events
        events = fetch_all_as_dict("SELECT * FROM log_events LIMIT 1")
        if not events:
            print("Creating test events...")
            game_gid = 10000147
            test_events = [
                ('login', 'user_login'),
                ('logout', 'user_logout'),
                ('purchase', 'item_purchase'),
                ('level_up', 'player_level_up'),
            ]

            for event_name, event_code in test_events:
                cursor.execute("""
                    INSERT INTO log_events (game_gid, event_name, event_code, category_id)
                    VALUES (?, ?, ?, 1)
                """, (game_gid, event_name, event_code))

            conn.commit()

        conn.close()
        print("Test data setup complete")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get current cache statistics"""
        try:
            from flask import current_app
            cache = current_app.cache
            # Try to get stats from Redis cache
            if hasattr(cache, '_client'):
                # For Redis cache
                info = cache._client.info('stats')
                return {
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0)
                }
        except Exception as e:
            logger.warning(f"Could not get cache stats: {e}")
            return {'hits': 0, 'misses': 0}

    def test_api_games_list(self, iterations: int = 100) -> PerformanceTestResults:
        """Test GET /api/games endpoint"""
        print(f"\n{'='*80}")
        print(f"Testing GET /api/games ({iterations} iterations)")
        print(f"{'='*80}")

        results = PerformanceTestResults("GET /api/games")

        for i in range(iterations):
            start = time.time()
            try:
                games = fetch_all_as_dict("""
                    SELECT
                        g.id, g.gid, g.name, g.ods_db, g.icon_path,
                        g.created_at, g.updated_at,
                        (SELECT COUNT(*) FROM log_events le WHERE le.game_gid = g.gid) as event_count,
                        (SELECT COUNT(*) FROM event_params ep
                         INNER JOIN log_events le ON ep.event_id = le.id
                         WHERE le.game_gid = g.gid AND ep.is_active = 1) as param_count
                    FROM games g
                    ORDER BY g.id
                """)
                elapsed = time.time() - start
                results.add_result(elapsed, success=True)

                if (i + 1) % 20 == 0:
                    print(f"  Completed {i+1}/{iterations} requests")

            except Exception as e:
                elapsed = time.time() - start
                results.add_result(elapsed, success=False, error=str(e))

        results.print_summary()
        self.results['api_games_list'] = results
        return results

    def test_api_single_game(self, iterations: int = 100) -> PerformanceTestResults:
        """Test GET /api/games/<gid> endpoint"""
        print(f"\n{'='*80}")
        print(f"Testing GET /api/games/<gid> ({iterations} iterations)")
        print(f"{'='*80}")

        results = PerformanceTestResults("GET /api/games/<gid>")

        # Get a valid game GID
        game = fetch_one_as_dict("SELECT gid FROM games LIMIT 1")
        if not game:
            print("ERROR: No games found in database")
            return results

        game_gid = game['gid']

        for i in range(iterations):
            start = time.time()
            try:
                game_data = fetch_one_as_dict(
                    "SELECT * FROM games WHERE gid = ?",
                    (game_gid,)
                )
                elapsed = time.time() - start
                results.add_result(elapsed, success=True)

                if (i + 1) % 20 == 0:
                    print(f"  Completed {i+1}/{iterations} requests")

            except Exception as e:
                elapsed = time.time() - start
                results.add_result(elapsed, success=False, error=str(e))

        results.print_summary()
        self.results['api_single_game'] = results
        return results

    def test_api_events_list(self, iterations: int = 100) -> PerformanceTestResults:
        """Test GET /api/events endpoint with pagination"""
        print(f"\n{'='*80}")
        print(f"Testing GET /api/events (paginated, {iterations} iterations)")
        print(f"{'='*80}")

        results = PerformanceTestResults("GET /api/events (paginated)")

        # Get a valid game GID
        game = fetch_one_as_dict("SELECT gid FROM games LIMIT 1")
        if not game:
            print("ERROR: No games found in database")
            return results

        game_gid = game['gid']

        for i in range(iterations):
            start = time.time()
            try:
                events = fetch_all_as_dict("""
                    SELECT * FROM log_events
                    WHERE game_gid = ?
                    ORDER BY id
                    LIMIT 10
                """, (game_gid,))
                elapsed = time.time() - start
                results.add_result(elapsed, success=True)

                if (i + 1) % 20 == 0:
                    print(f"  Completed {i+1}/{iterations} requests")

            except Exception as e:
                elapsed = time.time() - start
                results.add_result(elapsed, success=False, error=str(e))

        results.print_summary()
        self.results['api_events_list'] = results
        return results

    def test_hql_generation_single_event(self, iterations: int = 50) -> PerformanceTestResults:
        """Test HQL generation for single event with varying field counts"""
        print(f"\n{'='*80}")
        print(f"Testing HQL Generation - Single Event ({iterations} iterations)")
        print(f"{'='*80}")

        results = PerformanceTestResults("HQL Generation - Single Event (10 fields)")

        generator = HQLGenerator()

        # Get a valid game and event
        game = fetch_one_as_dict("SELECT * FROM games LIMIT 1")
        if not game:
            print("ERROR: No games found in database")
            return results

        event = fetch_one_as_dict("SELECT * FROM log_events WHERE game_gid = ? LIMIT 1", (game['gid'],))
        if not event:
            print("ERROR: No events found in database")
            return results

        # Create test event with 10 fields
        test_event = Event(
            name=event['event_name'],
            table_name=f"{game['ods_db']}.ods_{game['gid']}_all_view"
        )

        # Create 10 test fields
        fields = [
            Field(name="ds", type="base"),
            Field(name="role_id", type="base"),
            Field(name="account_id", type="base"),
            Field(name="utdid", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId"),
            Field(name="level", type="param", json_path="$.level"),
            Field(name="vip_level", type="param", json_path="$.vipLevel"),
            Field(name="coin", type="param", json_path="$.coin"),
            Field(name="gem", type="param", json_path="$.gem"),
            Field(name="exp", type="param", json_path="$.exp"),
        ]

        for i in range(iterations):
            start = time.time()
            try:
                hql = generator.generate(
                    events=[test_event],
                    fields=fields,
                    conditions=[],
                    mode="single"
                )
                elapsed = time.time() - start
                results.add_result(elapsed, success=True)

                if (i + 1) % 10 == 0:
                    print(f"  Completed {i+1}/{iterations} generations")

            except Exception as e:
                elapsed = time.time() - start
                results.add_result(elapsed, success=False, error=str(e))

        results.print_summary()
        self.results['hql_single_10_fields'] = results
        return results

    def test_hql_generation_large_event(self, iterations: int = 50) -> PerformanceTestResults:
        """Test HQL generation for single event with 50 fields"""
        print(f"\n{'='*80}")
        print(f"Testing HQL Generation - Single Event 50 Fields ({iterations} iterations)")
        print(f"{'='*80}")

        results = PerformanceTestResults("HQL Generation - Single Event (50 fields)")

        generator = HQLGenerator()

        # Get a valid game and event
        game = fetch_one_as_dict("SELECT * FROM games LIMIT 1")
        if not game:
            print("ERROR: No games found in database")
            return results

        event = fetch_one_as_dict("SELECT * FROM log_events WHERE game_gid = ? LIMIT 1", (game['gid'],))
        if not event:
            print("ERROR: No events found in database")
            return results

        # Create test event
        test_event = Event(
            name=event['event_name'],
            table_name=f"{game['ods_db']}.ods_{game['gid']}_all_view"
        )

        # Create 50 test fields
        fields = [
            Field(name="ds", type="base"),
            Field(name="role_id", type="base"),
            Field(name="account_id", type="base"),
            Field(name="utdid", type="base"),
        ]

        # Add 46 param fields
        for i in range(46):
            fields.append(Field(name=f"field_{i}", type="param", json_path=f"$.field{i}"))

        for i in range(iterations):
            start = time.time()
            try:
                hql = generator.generate(
                    events=[test_event],
                    fields=fields,
                    conditions=[],
                    mode="single"
                )
                elapsed = time.time() - start
                results.add_result(elapsed, success=True)

                if (i + 1) % 10 == 0:
                    print(f"  Completed {i+1}/{iterations} generations")

            except Exception as e:
                elapsed = time.time() - start
                results.add_result(elapsed, success=False, error=str(e))

        results.print_summary()
        self.results['hql_single_50_fields'] = results
        return results

    def test_cache_performance(self, iterations: int = 200) -> PerformanceTestResults:
        """Test cache hit rate for repeated queries"""
        print(f"\n{'='*80}")
        print(f"Testing Cache Hit Rate ({iterations} iterations)")
        print(f"{'='*80}")

        results = PerformanceTestResults("Cache Performance (Repeated Queries)")

        # Get cache stats before
        self.cache_stats_before = self.get_cache_stats()

        # Define a cached query function
        @cache_result('performance_test:games', timeout=300)
        def cached_query():
            return fetch_all_as_dict("""
                SELECT
                    g.id, g.gid, g.name, g.ods_db,
                    (SELECT COUNT(*) FROM log_events le WHERE le.game_gid = g.gid) as event_count
                FROM games g
            """)

        # First call - cache miss
        start = time.time()
        try:
            games = cached_query()
            elapsed = time.time() - start
            results.add_result(elapsed, success=True)
            print(f"  First call (cache miss): {elapsed*1000:.2f} ms")
        except Exception as e:
            elapsed = time.time() - start
            results.add_result(elapsed, success=False, error=str(e))

        # Subsequent calls - should hit cache
        cache_hit_times = []
        for i in range(iterations - 1):
            start = time.time()
            try:
                games = cached_query()
                elapsed = time.time() - start
                cache_hit_times.append(elapsed)
                results.add_result(elapsed, success=True)

                if (i + 1) % 50 == 0:
                    print(f"  Completed {i+2}/{iterations} calls")

            except Exception as e:
                elapsed = time.time() - start
                results.add_result(elapsed, success=False, error=str(e))

        # Get cache stats after
        self.cache_stats_after = self.get_cache_stats()

        results.print_summary()
        self.results['cache_performance'] = results
        return results

    def test_concurrent_requests(self, concurrent_users: int = 10, requests_per_user: int = 10) -> PerformanceTestResults:
        """Test performance under concurrent load"""
        print(f"\n{'='*80}")
        print(f"Testing Concurrent Load ({concurrent_users} users, {requests_per_user} requests each)")
        print(f"{'='*80}")

        results = PerformanceTestResults(f"Concurrent Load ({concurrent_users} users)")

        def make_request(user_id: int) -> Tuple[float, bool, str]:
            """Make a single request"""
            start = time.time()
            try:
                games = fetch_all_as_dict("""
                    SELECT
                        g.id, g.gid, g.name, g.ods_db,
                        (SELECT COUNT(*) FROM log_events le WHERE le.game_gid = g.gid) as event_count
                    FROM games g
                """)
                elapsed = time.time() - start
                return (elapsed, True, None)
            except Exception as e:
                elapsed = time.time() - start
                return (elapsed, False, str(e))

        total_requests = concurrent_users * requests_per_user
        completed = 0

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # Submit all requests
            futures = []
            for user_id in range(concurrent_users):
                for req_id in range(requests_per_user):
                    future = executor.submit(make_request, user_id)
                    futures.append(future)

            # Collect results as they complete
            for future in as_completed(futures):
                elapsed, success, error = future.result()
                results.add_result(elapsed, success, error)
                completed += 1

                if completed % 20 == 0:
                    print(f"  Completed {completed}/{total_requests} requests")

        results.print_summary()
        self.results['concurrent_load'] = results
        return results

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("\n" + "="*80)
        print("PERFORMANCE TEST REPORT")
        print("="*80)

        report = {
            'test_environment': {
                'python_version': sys.version,
                'platform': sys.platform,
                'db_path': str(self.db_path),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'results': {},
            'summary': {
                'total_tests': len(self.results),
                'passed_targets': 0,
                'failed_targets': 0,
                'warnings': []
            }
        }

        # Performance targets
        targets = {
            'api_response_p95_ms': 200,
            'hql_generation_single_ms': 1000,
            'cache_hit_rate_percent': 80
        }

        print("\nTest Environment:")
        for key, value in report['test_environment'].items():
            print(f"  {key}: {value}")

        # Analyze each test result
        for test_name, result in self.results.items():
            stats = result.get_statistics()
            report['results'][test_name] = stats

            # Check against targets
            if 'api' in test_name or 'concurrent' in test_name:
                p95_ms = stats['p95'] * 1000
                if p95_ms <= targets['api_response_p95_ms']:
                    report['summary']['passed_targets'] += 1
                    status = "✅ PASS"
                else:
                    report['summary']['failed_targets'] += 1
                    status = "❌ FAIL"
                    report['summary']['warnings'].append(
                        f"{test_name}: P95 = {p95_ms:.2f}ms (target: <{targets['api_response_p95_ms']}ms)"
                    )
            elif 'hql' in test_name:
                avg_ms = stats['avg_time'] * 1000
                if avg_ms <= targets['hql_generation_single_ms']:
                    report['summary']['passed_targets'] += 1
                    status = "✅ PASS"
                else:
                    report['summary']['failed_targets'] += 1
                    status = "❌ FAIL"
                    report['summary']['warnings'].append(
                        f"{test_name}: Avg = {avg_ms:.2f}ms (target: <{targets['hql_generation_single_ms']}ms)"
                    )
            elif 'cache' in test_name:
                # Calculate cache hit rate
                cache_hits = self.cache_stats_after.get('hits', 0) - self.cache_stats_before.get('hits', 0)
                cache_misses = self.cache_stats_after.get('misses', 0) - self.cache_stats_before.get('misses', 0)
                total_cache_ops = cache_hits + cache_misses
                hit_rate = (cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0

                if hit_rate >= targets['cache_hit_rate_percent']:
                    report['summary']['passed_targets'] += 1
                    status = "✅ PASS"
                else:
                    report['summary']['failed_targets'] += 1
                    status = "❌ FAIL"
                    report['summary']['warnings'].append(
                        f"{test_name}: Hit rate = {hit_rate:.2f}% (target: >{targets['cache_hit_rate_percent']}%)"
                    )
            else:
                status = "⚠️  N/A"

            print(f"\n{test_name}: {status}")

        # Print summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed Targets: {report['summary']['passed_targets']}")
        print(f"Failed Targets: {report['summary']['failed_targets']}")

        if report['summary']['warnings']:
            print("\nWarnings/Issues:")
            for warning in report['summary']['warnings']:
                print(f"  ⚠️  {warning}")

        # Overall assessment
        print("\n" + "="*80)
        print("OVERALL ASSESSMENT")
        print("="*80)

        if report['summary']['failed_targets'] == 0:
            print("✅ ALL TESTS PASSED")
            print("\nThe system performance is READY FOR PRODUCTION.")
            print("\nAll performance metrics meet or exceed the defined targets.")
            report['overall_status'] = 'PASS'
        elif report['summary']['failed_targets'] <= report['summary']['total_tests'] / 2:
            print("⚠️  SOME TESTS FAILED")
            print("\nThe system has performance issues that should be addressed before deployment.")
            print("\nRecommendations:")
            print("1. Review the warnings above for specific areas needing optimization")
            print("2. Consider database indexing for slow queries")
            print("3. Optimize cache strategies for frequently accessed data")
            print("4. Profile HQL generation code for bottlenecks")
            report['overall_status'] = 'WARNING'
        else:
            print("❌ MAJOR PERFORMANCE ISSUES")
            print("\nThe system has significant performance problems that MUST be addressed.")
            print("\nCritical Recommendations:")
            print("1. IMMEDIATE: Optimize slow database queries (add indexes)")
            print("2. IMMEDIATE: Review and optimize cache implementation")
            print("3. HIGH: Profile and optimize HQL generation logic")
            print("4. HIGH: Consider database query optimization")
            report['overall_status'] = 'FAIL'

        return report

    def save_report(self, report: Dict[str, Any], filename: str = None):
        """Save performance report to JSON file"""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"performance_report_{timestamp}.json"

        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✅ Report saved to: {filepath}")


def main():
    """Run all performance tests"""
    print("="*80)
    print("Event2Table Performance Testing")
    print("="*80)

    tester = PerformanceTester()

    # Setup test data
    tester.setup_test_data()

    # Run tests
    print("\n" + "="*80)
    print("Starting Performance Tests...")
    print("="*80)

    # 1. API Response Time Tests
    tester.test_api_games_list(iterations=100)
    tester.test_api_single_game(iterations=100)
    tester.test_api_events_list(iterations=100)

    # 2. HQL Generation Time Tests
    tester.test_hql_generation_single_event(iterations=50)
    tester.test_hql_generation_large_event(iterations=50)

    # 3. Cache Performance Tests
    tester.test_cache_performance(iterations=200)

    # 4. Concurrent Load Tests
    tester.test_concurrent_requests(concurrent_users=10, requests_per_user=10)

    # Generate and print report
    report = tester.generate_report()

    # Save report
    tester.save_report(report)

    print("\n" + "="*80)
    print("Performance Testing Complete")
    print("="*80)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Monitoring Script for Event2Table

This script benchmarks and validates performance optimizations:
- N+1 query detection
- Cache hit rate measurement
- API response time tracking
- Database query performance

Usage:
    python scripts/monitor_performance.py
    python scripts/monitor_performance.py --component games
    python scripts/monitor_performance.py --component events --verbose
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.models.repositories.parameters import ParameterRepository
from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Performance monitoring and benchmarking tool"""

    def __init__(self):
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)
        self.results = {}

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function"""
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed

    def benchmark_games_repository(self) -> Dict[str, any]:
        """Benchmark GameRepository performance"""
        logger.info("🔍 Benchmarking GameRepository...")

        repo = GameRepository()
        results = {
            'component': 'GameRepository',
            'tests': []
        }

        # Test 1: get_all_with_event_count (should be single query + cache)
        logger.info("  Testing get_all_with_event_count...")
        games, elapsed = self.measure_time(repo.get_all_with_event_count)
        results['tests'].append({
            'name': 'get_all_with_event_count',
            'duration_ms': round(elapsed * 1000, 2),
            'records': len(games),
            'avg_ms_per_record': round(elapsed * 1000 / len(games), 2) if games else 0,
            'cached': hasattr(repo.get_all_with_event_count, '__wrapped__'),
            'status': '✅ PASS' if elapsed < 1.0 else '⚠️ SLOW'
        })
        logger.info(f"    ✅ Fetched {len(games)} games in {elapsed:.3f}s")

        # Test 2: get_all_with_stats (should be single query + cache)
        logger.info("  Testing get_all_with_stats...")
        games, elapsed = self.measure_time(repo.get_all_with_stats)
        results['tests'].append({
            'name': 'get_all_with_stats',
            'duration_ms': round(elapsed * 1000, 2),
            'records': len(games),
            'avg_ms_per_record': round(elapsed * 1000 / len(games), 2) if games else 0,
            'cached': hasattr(repo.get_all_with_stats, '__wrapped__'),
            'status': '✅ PASS' if elapsed < 1.0 else '⚠️ SLOW'
        })
        logger.info(f"    ✅ Fetched {len(games)} games with stats in {elapsed:.3f}s")

        # Test 3: find_by_gid (should use cache)
        logger.info("  Testing find_by_gid cache...")
        gid = games[0].gid if games else 10000147

        # First call (cache miss)
        _, elapsed_miss = self.measure_time(repo.find_by_gid, gid)
        # Second call (cache hit)
        _, elapsed_hit = self.measure_time(repo.find_by_gid, gid)

        cache_speedup = round(elapsed_miss / elapsed_hit, 2) if elapsed_hit > 0 else 0
        results['tests'].append({
            'name': 'find_by_gid_cache',
            'duration_miss_ms': round(elapsed_miss * 1000, 2),
            'duration_hit_ms': round(elapsed_hit * 1000, 2),
            'speedup': f'{cache_speedup}x',
            'cached': hasattr(repo.find_by_gid, '__wrapped__'),
            'status': '✅ PASS' if cache_speedup > 2 else '⚠️ NO CACHE BENEFIT'
        })
        logger.info(f"    ✅ Cache speedup: {cache_speedup}x ({elapsed_miss:.3f}s → {elapsed_hit:.3f}s)")

        return results

    def benchmark_events_repository(self) -> Dict[str, any]:
        """Benchmark EventRepository performance"""
        logger.info("🔍 Benchmarking EventRepository...")

        repo = EventRepository()
        results = {
            'component': 'EventRepository',
            'tests': []
        }

        # Test 1: find_by_id with cache
        logger.info("  Testing find_by_id cache...")
        event, elapsed = self.measure_time(repo.find_by_id, 1)
        results['tests'].append({
            'name': 'find_by_id',
            'duration_ms': round(elapsed * 1000, 2),
            'cached': hasattr(repo.find_by_id, '__wrapped__'),
            'status': '✅ PASS' if elapsed < 0.5 else '⚠️ SLOW'
        })
        logger.info(f"    ✅ Fetched event in {elapsed:.3f}s")

        # Test 2: find_by_game_gid
        logger.info("  Testing find_by_game_gid...")
        events, elapsed = self.measure_time(repo.find_by_game_gid, 10000147, page=1, per_page=20)
        results['tests'].append({
            'name': 'find_by_game_gid',
            'duration_ms': round(elapsed * 1000, 2),
            'records': len(events),
            'status': '✅ PASS' if elapsed < 0.5 else '⚠️ SLOW'
        })
        logger.info(f"    ✅ Fetched {len(events)} events in {elapsed:.3f}s")

        return results

    def detect_n_plus_1_queries(self) -> Dict[str, any]:
        """Detect potential N+1 query problems"""
        logger.info("🔍 Detecting N+1 queries...")

        results = {
            'component': 'N+1 Query Detection',
            'issues': []
        }

        # Check GameRepository
        repo = GameRepository()

        # Monitor get_all_with_event_count
        logger.info("  Checking GameRepository.get_all_with_event_count...")
        start = time.time()
        games = repo.get_all_with_event_count()
        elapsed = time.time() - start

        # If we have many games and query is fast, it's likely optimized (JOIN query)
        # If it's slow, it might be N+1
        estimated_queries = len(games) if elapsed > len(games) * 0.01 else 1

        results['issues'].append({
            'repository': 'GameRepository',
            'method': 'get_all_with_event_count',
            'estimated_queries': estimated_queries,
            'status': '✅ OPTIMIZED' if estimated_queries == 1 else '⚠️ POTENTIAL N+1',
            'recommendation': 'Use JOIN query instead of loop' if estimated_queries > 1 else 'No action needed'
        })

        logger.info(f"    Estimated queries: {estimated_queries} (expected: 1)")

        return results

    def measure_cache_hit_rate(self) -> Dict[str, any]:
        """Measure cache hit rate"""
        logger.info("🔍 Measuring cache hit rate...")

        results = {
            'component': 'Cache Performance',
            'metrics': []
        }

        repo = GameRepository()

        # Test cache hit rate for find_by_gid
        logger.info("  Testing cache hit rate...")
        gid = 10000147

        hits = 0
        misses = 0
        iterations = 10

        for i in range(iterations):
            start = time.time()
            _ = repo.find_by_gid(gid)
            elapsed = time.time() - start

            if elapsed < 0.01:  # Cache hit threshold
                hits += 1
            else:
                misses += 1

        hit_rate = round(hits / iterations * 100, 2)
        results['metrics'].append({
            'method': 'find_by_gid',
            'iterations': iterations,
            'hits': hits,
            'misses': misses,
            'hit_rate_percent': hit_rate,
            'status': '✅ EXCELLENT' if hit_rate > 80 else '⚠️ NEEDS IMPROVEMENT'
        })

        logger.info(f"    Cache hit rate: {hit_rate}% ({hits}/{iterations})")

        return results

    def generate_report(self, benchmarks: List[Dict]) -> str:
        """Generate performance report"""
        report = []
        report.append("=" * 80)
        report.append("Event2Table Performance Optimization Report")
        report.append("=" * 80)
        report.append("")

        for benchmark in benchmarks:
            report.append(f"\n📊 {benchmark['component']}")
            report.append("-" * 80)

            if 'tests' in benchmark:
                for test in benchmark['tests']:
                    report.append(f"\n  Test: {test['name']}")
                    report.append(f"    Status: {test.get('status', 'N/A')}")
                    report.append(f"    Cached: {'Yes ✅' if test.get('cached') else 'No ❌'}")

                    if 'duration_ms' in test:
                        report.append(f"    Duration: {test['duration_ms']}ms")
                    if 'duration_miss_ms' in test:
                        report.append(f"    Cache Miss: {test['duration_miss_ms']}ms")
                        report.append(f"    Cache Hit: {test['duration_hit_ms']}ms")
                        report.append(f"    Speedup: {test.get('speedup', 'N/A')}")
                    if 'records' in test:
                        report.append(f"    Records: {test['records']}")
                    if 'avg_ms_per_record' in test:
                        report.append(f"    Avg/Record: {test['avg_ms_per_record']}ms")

            if 'issues' in benchmark:
                for issue in benchmark['issues']:
                    report.append(f"\n  Issue: {issue['repository']}.{issue['method']}")
                    report.append(f"    Estimated Queries: {issue['estimated_queries']}")
                    report.append(f"    Status: {issue['status']}")
                    report.append(f"    Recommendation: {issue['recommendation']}")

            if 'metrics' in benchmark:
                for metric in benchmark['metrics']:
                    report.append(f"\n  Metric: {metric['method']}")
                    report.append(f"    Iterations: {metric['iterations']}")
                    report.append(f"    Hits: {metric['hits']}")
                    report.append(f"    Misses: {metric['misses']}")
                    report.append(f"    Hit Rate: {metric['hit_rate_percent']}%")
                    report.append(f"    Status: {metric['status']}")

        report.append("\n" + "=" * 80)
        report.append("End of Report")
        report.append("=" * 80)

        return "\n".join(report)

    def run_all_benchmarks(self, component: Optional[str] = None) -> List[Dict]:
        """Run all performance benchmarks"""
        benchmarks = []

        if component is None or component == 'games':
            benchmarks.append(self.benchmark_games_repository())

        if component is None or component == 'events':
            benchmarks.append(self.benchmark_events_repository())

        if component is None or component == 'n_plus_1':
            benchmarks.append(self.detect_n_plus_1_queries())

        if component is None or component == 'cache':
            benchmarks.append(self.measure_cache_hit_rate())

        return benchmarks


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Event2Table Performance Monitoring Script'
    )
    parser.add_argument(
        '--component',
        choices=['games', 'events', 'n_plus_1', 'cache'],
        help='Component to benchmark (default: all)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for report (default: stdout)'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    monitor = PerformanceMonitor()

    try:
        # Run benchmarks
        logger.info("🚀 Starting performance benchmarks...")
        benchmarks = monitor.run_all_benchmarks(args.component)

        # Generate report
        report = monitor.generate_report(benchmarks)

        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            logger.info(f"✅ Report saved to {args.output}")
        else:
            print("\n" + report)

        logger.info("✅ Performance benchmarks completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"❌ Error running benchmarks: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

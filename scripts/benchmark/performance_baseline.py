#!/usr/bin/env python3
"""
Performance Baseline Test - V8.0.0

This script establishes a performance baseline before optimization.
It tests API response times, cache hit rate, query performance, and memory usage.

Usage:
    python scripts/benchmark/performance_baseline.py

Output:
    output/performance_baseline_v8.json - Baseline results
"""
import time
import json
import sys
import os
import sqlite3
import requests
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class PerformanceBaseline:
    """Performance baseline testing class"""

    def __init__(self):
        self.results = {
            'version': 'V8.0.0',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {}
        }
        self.api_base = 'http://127.0.0.1:5001'
        self.db_path = 'data/dwd_generator.db'

    def test_api_response_time(self) -> None:
        """
        Test API endpoint response times

        Tests each endpoint 10 times and records:
        - Average response time
        - Minimum response time
        - Maximum response time
        """
        print("\n📡 Testing API Response Times...")
        endpoints = [
            ('/api/games', 'Get all games'),
            ('/api/events?game_gid=10000147', 'Get events for game'),
            ('/api/parameters/all?game_gid=10000147', 'Get parameters for game'),
        ]

        for endpoint, description in endpoints:
            times = []
            errors = 0

            for i in range(10):
                try:
                    start = time.time()
                    response = requests.get(
                        f"{self.api_base}{endpoint}",
                        timeout=5
                    )
                    elapsed = time.time() - start

                    if response.status_code == 200:
                        times.append(elapsed)
                    else:
                        errors += 1
                except requests.exceptions.ConnectionError:
                    print(f"  ❌ Connection failed - Is Flask server running?")
                    return
                except Exception as e:
                    errors += 1

            if times:
                # Generate safe key name
                key = f"api_{endpoint.replace('/', '_').replace('?', '_').replace('=', '_')}"
                self.results['tests'][key] = {
                    'description': description,
                    'endpoint': endpoint,
                    'requests': len(times),
                    'errors': errors,
                    'avg_ms': round(sum(times) / len(times) * 1000, 2),
                    'min_ms': round(min(times) * 1000, 2),
                    'max_ms': round(max(times) * 1000, 2),
                }
                print(f"  ✅ {description}: {self.results['tests'][key]['avg_ms']}ms avg")
            else:
                print(f"  ❌ {description}: All requests failed")

    def test_cache_hit_rate(self) -> None:
        """
        Test Redis cache hit rate

        Records:
        - Total hits
        - Total misses
        - Hit rate percentage
        """
        print("\n💾 Testing Cache Hit Rate...")
        try:
            import redis
            r = redis.Redis(
                host='127.0.0.1',
                port=6379,
                db=0,
                decode_responses=True
            )
            info = r.info('stats')
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0

            self.results['tests']['cache'] = {
                'hits': hits,
                'misses': misses,
                'total_requests': total,
                'hit_rate_percent': round(hit_rate, 2)
            }
            print(f"  ✅ Hit rate: {hit_rate:.2f}% ({hits}/{total})")
        except ImportError:
            print("  ⚠️  Redis not installed - skipping cache test")
            self.results['tests']['cache'] = {
                'skipped': 'redis not installed'
            }
        except Exception as e:
            print(f"  ❌ Cache test failed: {e}")
            self.results['tests']['cache'] = {
                'error': str(e)
            }

    def test_query_performance(self) -> None:
        """
        Test database query performance

        Tests common queries and records execution time in milliseconds
        """
        print("\n🗄️  Testing Database Query Performance...")
        queries = [
            (
                "n1_query_simulation",
                "N+1 query simulation",
                "SELECT * FROM log_events WHERE game_gid = 10000147 LIMIT 100"
            ),
            (
                "count_query",
                "Count query",
                "SELECT COUNT(*) as c FROM event_params"
            ),
            (
                "join_query",
                "Join query",
                """SELECT g.name, COUNT(le.id) as event_count
                   FROM games g
                   LEFT JOIN log_events le ON g.gid = le.game_gid
                   GROUP BY g.id
                   LIMIT 10"""
            ),
        ]

        try:
            if not os.path.exists(self.db_path):
                print(f"  ❌ Database not found: {self.db_path}")
                return

            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("ANALYZE")

            cursor = conn.cursor()

            for key, name, query in queries:
                try:
                    start = time.time()
                    cursor.execute(query)
                    cursor.fetchall()
                    elapsed_ms = round((time.time() - start) * 1000, 2)

                    self.results['tests'][f"db_{key}"] = {
                        'query_name': name,
                        'time_ms': elapsed_ms
                    }
                    print(f"  ✅ {name}: {elapsed_ms}ms")
                except Exception as e:
                    print(f"  ❌ {name}: {e}")
                    self.results['tests'][f"db_{key}"] = {
                        'query_name': name,
                        'error': str(e)
                    }

            conn.close()
        except Exception as e:
            print(f"  ❌ Database test failed: {e}")
            self.results['tests']['database'] = {
                'error': str(e)
            }

    def test_memory_usage(self) -> None:
        """
        Test memory usage

        Records Resident Set Size (RSS) in MB
        """
        print("\n🧠 Testing Memory Usage...")
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()

            self.results['tests']['memory'] = {
                'rss_mb': round(memory_info.rss / 1024 / 1024, 2),
                'vms_mb': round(memory_info.vms / 1024 / 1024, 2),
            }
            print(f"  ✅ Memory: {self.results['tests']['memory']['rss_mb']}MB RSS")
        except ImportError:
            print("  ⚠️  psutil not installed - skipping memory test")
            self.results['tests']['memory'] = {
                'skipped': 'psutil not installed'
            }
        except Exception as e:
            print(f"  ❌ Memory test failed: {e}")
            self.results['tests']['memory'] = {
                'error': str(e)
            }

    def run_all_tests(self) -> None:
        """Run all baseline tests and save results"""
        print("="*60)
        print("🚀 Performance Baseline Test - V8.0.0")
        print("="*60)

        # Run all tests
        self.test_api_response_time()
        self.test_cache_hit_rate()
        self.test_query_performance()
        self.test_memory_usage()

        # Save results
        os.makedirs('output', exist_ok=True)
        output_path = 'output/performance_baseline_v8.json'

        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)

        print("\n" + "="*60)
        print(f"✅ Results saved to: {output_path}")
        print("="*60)

        # Print summary
        print("\n📊 Summary:")
        print("-" * 60)
        for key, value in self.results['tests'].items():
            if 'avg_ms' in value:
                print(f"  {key}: {value['avg_ms']}ms (avg)")
            elif 'hit_rate_percent' in value:
                print(f"  {key}: {value['hit_rate_percent']}% hit rate")
            elif 'time_ms' in value:
                print(f"  {key}: {value['time_ms']}ms")
            elif 'rss_mb' in value:
                print(f"  {key}: {value['rss_mb']}MB RSS")
            elif 'error' in value:
                print(f"  {key}: ERROR - {value['error']}")
            elif 'skipped' in value:
                print(f"  {key}: SKIPPED - {value['skipped']}")
        print("-" * 60)


def main():
    """Main entry point"""
    baseline = PerformanceBaseline()
    baseline.run_all_tests()


if __name__ == '__main__':
    main()

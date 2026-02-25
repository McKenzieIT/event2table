"""
Performance tests for cache system

Requirements:
- Cache GET operations < 1ms (P95)
- Cache hit rate > 80%
- Cache provides at least 2x speedup
"""
import pytest
import time
import numpy as np
from flask_caching import Cache


class TestCachePerformance:
    """Test cache performance"""

    @pytest.fixture(autouse=True)
    def setup_cache(self):
        """Set up cache instance for tests"""
        from flask import Flask
        from backend.core.config import CacheConfig

        app = Flask(__name__)
        app.config.from_object(CacheConfig)
        self.cache = Cache(app)

        # Clear cache before each test
        self.cache.clear()

    def test_cache_get_performance(self):
        """Test cache GET performance"""

        # Set test values
        for i in range(100):
            self.cache.set(f'test_key_{i}', f'test_value_{i}')

        # Warm-up
        for i in range(10):
            self.cache.get(f'test_key_{i}')

        # Measure GET performance
        times = []
        for i in range(1000):
            start = time.perf_counter()
            result = self.cache.get(f'test_key_{i % 100}')
            end = time.perf_counter()

            assert result is not None
            times.append((end - start) * 1000)  # ms

        avg_time = np.mean(times)
        p95 = np.percentile(times, 95)
        p99 = np.percentile(times, 99)

        print(f"\n📊 Cache GET Performance (1000 requests):")
        print(f"  Average: {avg_time:.4f} ms")
        print(f"  P50: {percentile(times, 50):.4f} ms")
        print(f"  P95: {p95:.4f} ms")
        print(f"  P99: {p99:.4f} ms")

        assert p95 < 1, f"Cache GET P95 {p95:.4f}ms exceeds 1ms threshold"

    def test_cache_set_performance(self):
        """Test cache SET performance"""

        # Measure SET performance
        times = []
        for i in range(100):
            start = time.perf_counter()
            cache.set(f'perf_test_key_{i}', f'perf_test_value_{i}' * 10)
            end = time.perf_counter()

            times.append((end - start) * 1000)  # ms

        avg_time = np.mean(times)
        p95 = np.percentile(times, 95)

        print(f"\n📊 Cache SET Performance (100 operations):")
        print(f"  Average: {avg_time:.4f} ms")
        print(f"  P95: {p95:.4f} ms")

        assert p95 < 5, f"Cache SET P95 {p95:.4f}ms exceeds 5ms threshold"

    def test_cache_hit_rate(self):
        """Test cache hit rate in realistic scenario"""

        # Clear cache
        cache.clear()

        # Set some keys
        test_keys = [f'cache_hit_test_{i}' for i in range(20)]
        for key in test_keys:
            cache.set(key, f'value_{key}')

        # Simulate realistic access pattern (80% hits, 20% misses)
        import random
        times = []
        hits = 0
        misses = 0

        for _ in range(100):
            # 80% chance of accessing existing key
            if random.random() < 0.8:
                key = random.choice(test_keys)
            else:
                key = f'nonexistent_key_{random.randint(1000, 9999)}'

            start = time.perf_counter()
            result = cache.get(key)
            end = time.perf_counter()

            times.append((end - start) * 1000)
            if result is not None:
                hits += 1
            else:
                misses += 1

        hit_rate = (hits / (hits + misses)) * 100

        print(f"\n📊 Cache Hit Rate Test:")
        print(f"  Total requests: {hits + misses}")
        print(f"  Hits: {hits}")
        print(f"  Misses: {misses}")
        print(f"  Hit rate: {hit_rate:.1f}%")
        print(f"  Avg response time: {mean(times):.4f} ms")

        assert hit_rate > 70, f"Cache hit rate {hit_rate:.1f}% is too low"

    def test_cache_speedup_factor(self):
        """Test that cache provides significant speedup"""

        from backend.core.database import get_db_connection
        from backend.core.utils import fetch_one_as_dict

        # Simulate expensive database query
        def expensive_query(param_id):
            conn = get_db_connection()
            result = fetch_one_as_dict(
                "SELECT * FROM event_params WHERE id = ?",
                (param_id,)
            )
            conn.close()
            return result

        # Get a real parameter ID
        conn = get_db_connection()
        result = fetch_one_as_dict("SELECT id FROM event_params LIMIT 1")
        conn.close()

        if not result:
            pytest.skip("No parameters found in database")

        param_id = result['id']

        # First call - cache miss (measure DB query time)
        start = time.perf_counter()
        result1 = expensive_query(param_id)
        db_time = (time.perf_counter() - start) * 1000

        # Cache the result
        cache.set(f'param_{param_id}', result1)

        # Second call - cache hit
        start = time.perf_counter()
        result2 = cache.get(f'param_{param_id}')
        cache_time = (time.perf_counter() - start) * 1000

        speedup = db_time / cache_time if cache_time > 0 else 0

        print(f"\n📊 Cache Speedup Test:")
        print(f"  DB query time: {db_time:.2f} ms")
        print(f"  Cache hit time: {cache_time:.4f} ms")
        print(f"  Speedup: {speedup:.1f}x")

        assert cache_time < db_time / 2, "Cache should provide at least 2x speedup"
        assert speedup > 2, f"Cache speedup {speedup:.1f}x is less than 2x target"

    def test_cache_memory_efficiency(self):
        """Test cache memory efficiency"""

        from backend.core.cache.cache_system import cache_stats

        # Clear cache
        cache.clear()

        # Add items of different sizes
        small_items = 100
        large_items = 10

        # Small items (~100 bytes)
        for i in range(small_items):
            cache.set(f'small_{i}', 'x' * 100)

        # Large items (~10KB)
        for i in range(large_items):
            cache.set(f'large_{i}', 'x' * 10000)

        stats = cache_stats.get_stats()

        print(f"\n📊 Cache Memory Efficiency:")
        print(f"  Small items: {small_items}")
        print(f"  Large items: {large_items}")
        print(f"  Total items: {stats.get('l1_size', 0) + stats.get('l2_size', 0)}")
        print(f"  L1 hits: {stats.get('hits', 0)}")
        print(f"  L1 misses: {stats.get('misses', 0)}")

        # Verify all items are cached
        total_items = stats.get('l1_size', 0) + stats.get('l2_size', 0)
        assert total_items >= small_items + large_items, "Not all items were cached"

    def test_cache_expiration_performance(self):
        """Test cache expiration mechanism"""

        cache.clear()

        # Set items with different TTLs
        cache.set('short_ttl', 'value', ttl=1)
        cache.set('long_ttl', 'value', ttl=10)

        # Short TTL item should expire
        import time as time_module
        time_module.sleep(2)

        result = cache.get('short_ttl')
        assert result is None, "Short TTL item should have expired"

        # Long TTL item should still exist
        result = cache.get('long_ttl')
        assert result is not None, "Long TTL item should still exist"

        print(f"\n📊 Cache Expiration Test:")
        print(f"  ✓ Short TTL (1s) expired correctly")
        print(f"  ✓ Long TTL (10s) still accessible")

    def test_concurrent_cache_access(self):
        """Test cache performance under concurrent access"""

        import concurrent.futures

        cache.clear()

        # Prepare cache
        for i in range(50):
            cache.set(f'concurrent_{i}', f'value_{i}')

        def cache_operation():
            """Perform cache get/set operations"""
            import random
            start = time.perf_counter()

            # Mix of reads and writes
            for _ in range(20):
                if random.random() < 0.8:  # 80% reads
                    cache.get(f'concurrent_{random.randint(0, 49)}')
                else:  # 20% writes
                    cache.set(f'concurrent_{random.randint(0, 49)}', f'value_{random.randint(0, 999)}')

            return (time.perf_counter() - start) * 1000

        # Run concurrent operations
        times = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cache_operation) for _ in range(20)]
            for future in concurrent.futures.as_completed(futures):
                times.append(future.result())

        p95 = percentile(times, 95)
        avg_time = np.mean(times)

        print(f"\n📊 Concurrent Cache Access (10 workers, 20 threads):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P95: {p95:.2f} ms")

        assert p95 < 100, f"Concurrent operations P95 {p95:.2f}ms exceeds 100ms"

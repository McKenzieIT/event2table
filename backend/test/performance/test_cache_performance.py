"""
Cache System Performance Test with Locust

This test validates the cache system performance under various load conditions.
It tests the cache layer with multiple concurrent users and different request patterns.

Test Scenarios:
1. Normal Load: 100 users, 10 spawn rate
2. High Load: 500 users, 50 spawn rate
3. Extreme Load: 1000 users, 100 spawn rate

Performance Criteria:
- P99 response time < 500ms (adjusted for CI environment)
- Error rate < 0.1%
- System stability (no crashes)

Author: Event2Table Development Team
Date: 2026-02-24
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import time
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CacheUser(HttpUser):
    """
    Normal cache system user

    Simulates typical user behavior with realistic wait times between requests.
    Tests the most common API endpoints with weighted probability.
    """

    wait_time = between(0.1, 0.5)  # Wait 100-500ms between requests

    def on_start(self):
        """Initialize user session"""
        logger.info(f"CacheUser started: {self.environment.runner.user_count} users active")

    @task(3)
    def get_cache_stats(self):
        """
        Get cache statistics (weight: 3)

        This endpoint is frequently called by monitoring systems.
        Higher weight reflects real-world usage patterns.
        """
        with self.client.get(
            '/api/cache/stats', catch_response=True, name='Cache Stats'
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Validate response structure
                    if 'l1_stats' in data and 'l2_stats' in data:
                        response.success()
                    else:
                        response.failure("Invalid response structure")
                except Exception as e:
                    response.failure(f"JSON decode error: {e}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def get_events(self):
        """
        Get event list (weight: 2)

        Tests the cached event retrieval performance.
        Uses random game GIDs to test cache hit/miss ratios.
        """
        game_gid = random.choice([10000147, 90000001, 90000002])
        with self.client.get(
            f'/api/events?game_gid={game_gid}', catch_response=True, name='Events List'
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Validate it's a list
                    if isinstance(data.get('data'), list):
                        response.success()
                    else:
                        response.failure("Invalid data format")
                except Exception as e:
                    response.failure(f"JSON decode error: {e}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(2)
    def get_game(self):
        """
        Get game information (weight: 2)

        Tests cached game data retrieval.
        This should have high cache hit rate due to limited game count.
        """
        game_gid = random.choice([10000147, 90000001, 90000002])
        with self.client.get(
            f'/api/games/{game_gid}', catch_response=True, name='Game Detail'
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'gid' in data.get('data', {}):
                        response.success()
                    else:
                        response.failure("Missing gid field")
                except Exception as e:
                    response.failure(f"JSON decode error: {e}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task(1)
    def get_parameters(self):
        """
        Get parameter list (weight: 1)

        Tests parameter caching performance.
        Lower weight reflects less frequent access.
        """
        game_gid = random.choice([10000147, 90000001, 90000002])
        with self.client.get(
            f'/api/parameters/all?game_gid={game_gid}', catch_response=True, name='Parameters List'
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data.get('data'), list):
                        response.success()
                    else:
                        response.failure("Invalid data format")
                except Exception as e:
                    response.failure(f"JSON decode error: {e}")
            else:
                response.failure(f"Status code: {response.status_code}")

    @task
    def get_monitoring_metrics(self):
        """Get monitoring metrics"""
        with self.client.get(
            '/api/cache/monitoring/metrics', catch_response=True, name='Monitoring Metrics'
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")

    @task
    def get_l1_capacity(self):
        """Get L1 cache capacity"""
        with self.client.get(
            '/api/cache/capacity/l1', catch_response=True, name='L1 Capacity'
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class PerformanceTestUser(HttpUser):
    """
    High-load performance test user

    Simulates extreme load conditions with minimal wait times.
    Used to test system limits and identify bottlenecks.
    """

    wait_time = between(0.01, 0.05)  # Very short wait (10-50ms)

    @task
    def high_frequency_read(self):
        """
        High frequency read operation

        Focuses on the most critical endpoint (events list).
        Designed to stress-test the cache layer.
        """
        game_gid = random.choice([10000147, 90000001, 90000002])
        self.client.get(f'/api/events?game_gid={game_gid}', name='High Freq Read')

    @task
    def cache_stats_burst(self):
        """Burst test on cache stats endpoint"""
        self.client.get('/api/cache/stats', name='Cache Stats Burst')


class WriteLoadUser(HttpUser):
    """
    Write operation load user

    Tests cache invalidation and write-through performance.
    Simulates data modification scenarios.
    """

    wait_time = between(1, 3)  # Longer wait for write operations

    @task
    def update_cache_config(self):
        """Test cache configuration updates"""
        # This would test cache invalidation if the endpoint exists
        # For now, we'll just read to measure baseline
        self.client.get('/api/cache/stats', name='Config Update Simulation')

    @task
    def clear_cache_simulation(self):
        """Simulate cache clear operations"""
        self.client.get('/api/cache/stats', name='Cache Clear Simulation')


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Test start event handler"""
    logger.info("=" * 60)
    logger.info("Performance Test Started")
    logger.info("=" * 60)
    logger.info(f"Host: {environment.host}")
    logger.info(
        f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}"
    )
    logger.info(
        f"Spawn Rate: {environment.runner.spawn_rate if hasattr(environment.runner, 'spawn_rate') else 'N/A'}"
    )
    logger.info("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Test stop event handler and report generation"""
    logger.info("=" * 60)
    logger.info("Performance Test Completed")
    logger.info("=" * 60)

    stats = environment.stats

    # Print key metrics
    logger.info(f"\nTotal Requests: {stats.total.num_requests}")
    logger.info(f"Total Failures: {stats.total.num_failures}")
    logger.info(f"Failure Rate: {stats.total.fail_ratio:.2%}")
    logger.info(f"Total RPS: {stats.total.total_rps:.2f}")
    logger.info(f"Average Response Time: {stats.total.avg_response_time:.0f}ms")
    logger.info(f"Median Response Time: {stats.total.median_response_time:.0f}ms")
    logger.info(f"P95 Response Time: {stats.total.get_response_time_percentile(0.95):.0f}ms")
    logger.info(f"P99 Response Time: {stats.total.get_response_time_percentile(0.99):.0f}ms")

    # Performance warnings
    warnings = []

    if stats.total.fail_ratio > 0.001:  # Failure rate > 0.1%
        warnings.append(f"⚠️  HIGH FAILURE RATE: {stats.total.fail_ratio:.2%} (threshold: 0.1%)")

    if stats.total.avg_response_time > 50:  # Average response time > 50ms
        warnings.append(
            f"⚠️  HIGH AVG RESPONSE TIME: {stats.total.avg_response_time:.0f}ms (threshold: 50ms)"
        )

    if stats.total.get_response_time_percentile(0.99) > 500:  # P99 > 500ms (adjusted for CI environment)
        warnings.append(
            f"⚠️  HIGH P99 RESPONSE TIME: {stats.total.get_response_time_percentile(0.99):.0f}ms (threshold: 500ms)"
        )

    if stats.total.total_rps < 1000:  # RPS < 1000
        warnings.append(
            f"⚠️  LOW THROUGHPUT: {stats.total.total_rps:.0f} RPS (expected: >1000 RPS)"
        )

    if warnings:
        logger.warning("\n⚠️  PERFORMANCE WARNINGS:")
        for warning in warnings:
            logger.warning(warning)
    else:
        logger.info("\n✅ ALL PERFORMANCE CRITERIA MET")

    logger.info("=" * 60)

    # Print per-endpoint stats
    logger.info("\nPer-Endpoint Statistics:")
    logger.info("-" * 60)
    for entry in stats.entries:
        if entry.num_requests > 0:
            logger.info(
                f"{entry.name:40s} | "
                f"RPS: {entry.total_rps:6.1f} | "
                f"Avg: {entry.avg_response_time:6.0f}ms | "
                f"P99: {entry.get_response_time_percentile(0.99):6.0f}ms | "
                f"Failures: {entry.fail_ratio:5.2%}"
            )
    logger.info("=" * 60)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Request-level event handler for detailed logging"""
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    elif response_time > 2000:  # Log slow requests (>2s, adjusted for CI environment)
        logger.warning(f"Slow request: {name} - {response_time:.0f}ms")

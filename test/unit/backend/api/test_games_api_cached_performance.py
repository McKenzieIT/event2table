#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Test for GET /api/games Endpoint with Caching

This test measures the performance improvement after implementing caching
for the games list API endpoint.
"""

import sys
import time
import statistics
import requests
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))


def time_api_endpoint(url: str, iterations: int = 100) -> dict:
    """
    Time an API endpoint over multiple iterations.

    Args:
        url: API endpoint URL
        iterations: Number of times to call the endpoint

    Returns:
        Dictionary with timing statistics
    """
    times = []
    errors = 0

    # Warm-up run
    try:
        requests.get(url, timeout=5)
    except Exception as e:
        print(f"Warning: Warm-up request failed: {e}")

    for i in range(iterations):
        try:
            start = time.perf_counter()
            response = requests.get(url, timeout=5)
            end = time.perf_counter()

            if response.status_code == 200:
                times.append((end - start) * 1000)  # Convert to ms
            else:
                errors += 1
                print(f"Request {i+1} failed with status {response.status_code}")
        except Exception as e:
            errors += 1
            print(f"Request {i+1} failed: {e}")

    if not times:
        return {
            'mean': 0,
            'median': 0,
            'stdev': 0,
            'min': 0,
            'max': 0,
            'p95': 0,
            'p99': 0,
            'success_rate': 0,
            'total_requests': iterations
        }

    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
        'p95': statistics.quantiles(times, n=20)[18] if len(times) > 1 else times[0],
        'p99': statistics.quantiles(times, n=100)[98] if len(times) > 99 else times[-1],
        'success_rate': (len(times) / iterations) * 100,
        'total_requests': iterations,
        'successful_requests': len(times)
    }


def main():
    """Run performance tests."""
    base_url = "http://localhost:5001"
    endpoint = "/api/games"
    url = f"{base_url}{endpoint}"

    print("=" * 70)
    print("GET /api/games Performance Test with Caching")
    print("=" * 70)
    print()
    print(f"Endpoint: {url}")
    print(f"Iterations: 100")
    print()

    # Check if server is running
    try:
        response = requests.get(url, timeout=2)
        server_running = True
    except Exception as e:
        print(f"ERROR: Cannot connect to server at {url}")
        print(f"Error: {e}")
        print()
        print("Please ensure the Flask server is running:")
        print("  cd /Users/mckenzie/Documents/event2table")
        print("  python3 backend/app.py")
        return 1

    print("-" * 70)
    print("Testing endpoint performance (with caching)")
    print("-" * 70)

    stats = time_api_endpoint(url, 100)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"  Mean:      {stats['mean']:.2f}ms")
    print(f"  Median:    {stats['median']:.2f}ms")
    print(f"  P95:       {stats['p95']:.2f}ms")
    print(f"  P99:       {stats['p99']:.2f}ms")
    print(f"  Min:       {stats['min']:.2f}ms")
    print(f"  Max:       {stats['max']:.2f}ms")
    print(f"  StdDev:    {stats['stdev']:.2f}ms")
    print(f"  Success:   {stats['success_rate']:.1f}% ({stats['successful_requests']}/{stats['total_requests']})")
    print()

    # SLA compliance check
    print("-" * 70)
    print("SLA Compliance")
    print("-" * 70)
    sla_threshold = 200  # ms
    print(f"SLA Threshold: {sla_threshold}ms")
    print()

    if stats['mean'] < sla_threshold:
        print(f"✓ PASS: Mean response time ({stats['mean']:.2f}ms) is below SLA")
    else:
        print(f"✗ FAIL: Mean response time ({stats['mean']:.2f}ms) exceeds SLA")

    if stats['p95'] < sla_threshold:
        print(f"✓ PASS: P95 response time ({stats['p95']:.2f}ms) is below SLA")
    else:
        print(f"✗ FAIL: P95 response time ({stats['p95']:.2f}ms) exceeds SLA")

    if stats['p99'] < sla_threshold:
        print(f"✓ PASS: P99 response time ({stats['p99']:.2f}ms) is below SLA")
    else:
        print(f"✗ FAIL: P99 response time ({stats['p99']:.2f}ms) exceeds SLA")

    print()
    print("=" * 70)
    print("Performance Analysis")
    print("=" * 70)

    # Performance classification
    if stats['mean'] < 10:
        classification = "Excellent (L1 cache hit)"
    elif stats['mean'] < 50:
        classification = "Good (L2 cache hit)"
    elif stats['mean'] < 200:
        classification = "Acceptable (cache miss but optimized)"
    else:
        classification = "Needs improvement"

    print(f"Performance Class: {classification}")
    print()

    # Cache effectiveness
    if stats['mean'] < 10:
        print("✓ L1 Memory Cache: HIT (sub-10ms response time)")
    elif stats['mean'] < 50:
        print("✓ L2 Redis Cache: HIT (sub-50ms response time)")
    else:
        print("⚠ Cache: MISS (query executed, consider cache warming)")

    print()

    # Stability analysis
    if stats['stdev'] < stats['mean'] * 0.2:
        print("✓ Response times are stable (low variance)")
    else:
        print("⚠ Response times have high variance (may indicate inconsistent caching)")

    print()
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""
Performance tests for REST API endpoints

Requirements:
- Query response time < 500ms (P95)
- Mutation response time < 1000ms (P95)
"""
import pytest
import time
import requests
import numpy as np
from typing import List, Dict, Any


class TestAPIPerformance:
    """Test REST API performance"""

    API_BASE = "http://127.0.0.1:5001/api"

    def test_get_all_parameters_performance(self):
        """Test GET /api/parameters/all endpoint performance"""

        # Warm-up requests
        for _ in range(3):
            requests.get(f"{self.API_BASE}/parameters/all?game_gid=10000147")

        # Measure 100 requests
        times = []
        for _ in range(100):
            start = time.perf_counter()
            response = requests.get(f"{self.API_BASE}/parameters/all?game_gid=10000147")
            end = time.perf_counter()

            assert response.status_code == 200
            times.append((end - start) * 1000)  # Convert to ms

        # Calculate statistics
        avg_time = np.mean(times)
        p50 = np.median(times)
        p95 = np.percentile(times, 95)
        p99 = np.percentile(times, 99)

        print(f"\n📊 GET /api/parameters/all Performance (100 requests):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P50: {p50:.2f} ms")
        print(f"  P95: {p95:.2f} ms")
        print(f"  P99: {p99:.2f} ms")

        # Assert P95 < 500ms
        assert p95 < 500, f"P95 latency {p95:.2f}ms exceeds 500ms threshold"

    def test_get_common_parameters_performance(self):
        """Test GET /api/common-params endpoint performance"""

        # Warm-up
        for _ in range(3):
            requests.get(f"{self.API_BASE}/common-params?game_gid=10000147")

        # Measure 100 requests
        times = []
        for _ in range(100):
            start = time.perf_counter()
            response = requests.get(f"{self.API_BASE}/common-params?game_gid=10000147")
            end = time.perf_counter()

            assert response.status_code == 200
            times.append((end - start) * 1000)

        p95 = np.percentile(times, 95)
        print(f"\n📊 GET /api/common-params P95: {p95:.2f} ms")

        assert p95 < 500, f"P95 latency {p95:.2f}ms exceeds 500ms threshold"

    def test_update_parameter_type_performance(self):
        """Test PUT /api/parameters/<id> endpoint performance"""

        # Get a parameter ID first
        response = requests.get(f"{self.API_BASE}/parameters/all?game_gid=10000147&limit=1")
        assert response.status_code == 200
        data = response.json()
        if not data or (isinstance(data, list) and len(data) == 0):
            pytest.skip("No parameters found for testing")

        param_id = data[0]['id'] if isinstance(data, list) else data.get('id')
        original_type = data[0].get('param_type', 'string') if isinstance(data, list) else data.get('param_type', 'string')

        # Measure 50 update requests
        times = []
        for i in range(50):
            start = time.perf_counter()
            response = requests.put(
                f"{self.API_BASE}/parameters/{param_id}",
                json={'param_type': 'int' if i % 2 == 0 else 'string'}
            )
            end = time.perf_counter()

            assert response.status_code in [200, 201]
            times.append((end - start) * 1000)

        # Restore original type
        requests.put(
            f"{self.API_BASE}/parameters/{param_id}",
            json={'param_type': original_type}
        )

        p95 = np.percentile(times, 95)
        print(f"\n📊 PUT /api/parameters/<id> P95: {p95:.2f} ms")

        assert p95 < 1000, f"P95 latency {p95:.2f}ms exceeds 1000ms threshold"

    def test_recalculate_common_params_performance(self):
        """Test POST /api/common-params/recalculate endpoint performance"""

        # Check if endpoint exists
        test_response = requests.post(
            f"{self.API_BASE}/common-params/recalculate",
            json={'game_gid': 10000147, 'threshold': 0.8}
        )

        if test_response.status_code == 404:
            pytest.skip("Recalculate endpoint not found (404)")

        # Measure 20 recalculate requests (expensive operation)
        times = []
        for _ in range(20):
            start = time.perf_counter()
            response = requests.post(
                f"{self.API_BASE}/common-params/recalculate",
                json={'game_gid': 10000147, 'threshold': 0.8}
            )
            end = time.perf_counter()

            assert response.status_code in [200, 202]
            times.append((end - start) * 1000)

        p95 = np.percentile(times, 95)
        print(f"\n📊 POST /api/common-params/recalculate P95: {p95:.2f} ms")

        assert p95 < 2000, f"P95 latency {p95:.2f}ms exceeds 2000ms threshold"

    def test_get_events_performance(self):
        """Test GET /api/events endpoint performance"""

        # Warm-up
        for _ in range(3):
            requests.get(f"{self.API_BASE}/events?game_gid=10000147")

        # Measure 100 requests
        times = []
        for _ in range(100):
            start = time.perf_counter()
            response = requests.get(f"{self.API_BASE}/events?game_gid=10000147")
            end = time.perf_counter()

            assert response.status_code == 200
            times.append((end - start) * 1000)

        p95 = np.percentile(times, 95)
        print(f"\n📊 GET /api/events P95: {p95:.2f} ms")

        assert p95 < 500, f"P95 latency {p95:.2f}ms exceeds 500ms threshold"

    def test_concurrent_requests_performance(self):
        """Test concurrent request handling performance"""

        import concurrent.futures

        def make_request():
            start = time.perf_counter()
            response = requests.get(f"{self.API_BASE}/parameters/all?game_gid=10000147")
            end = time.perf_counter()
            assert response.status_code == 200
            return (end - start) * 1000

        # Test with 10 concurrent requests
        times = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            for future in concurrent.futures.as_completed(futures):
                times.append(future.result())

        p95 = np.percentile(times, 95)
        avg_time = np.mean(times)

        print(f"\n📊 Concurrent Requests (10 workers, 50 requests):")
        print(f"  Average: {avg_time:.2f} ms")
        print(f"  P95: {p95:.2f} ms")

        assert p95 < 1000, f"Concurrent P95 latency {p95:.2f}ms exceeds 1000ms threshold"

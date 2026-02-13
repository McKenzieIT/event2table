#!/usr/bin/env python3
"""
Event2Table Performance Testing Script

This script measures API response times, HQL generation performance,
and database query performance to identify bottlenecks and ensure SLA compliance.
"""

import time
import requests
import statistics
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5001"
TEST_GAME_GID = "10000147"
ITERATIONS = 10
TIMEOUT = 30  # seconds

# Performance Thresholds (SLA)
SLA_THRESHOLDS = {
    "api_games_p95": 200,  # ms
    "api_events_p95": 200,  # ms
    "api_parameters_p95": 200,  # ms
    "hql_single_p95": 1000,  # ms
    "hql_join_p95": 2000,  # ms
    "hql_union_p95": 2000,  # ms
    "db_query_p95": 100,  # ms
    "db_complex_query_p95": 200,  # ms
}


class PerformanceTestResult:
    """Container for test results"""

    def __init__(self, name: str):
        self.name = name
        self.times: List[float] = []
        self.errors: List[str] = []
        self.success_count = 0

    def add_time(self, duration_ms: float):
        self.times.append(duration_ms)

    def add_error(self, error: str):
        self.errors.append(error)

    def get_stats(self) -> Dict[str, Any]:
        if not self.times:
            return {
                "avg": 0,
                "min": 0,
                "max": 0,
                "p95": 0,
                "p99": 0,
                "success_rate": 0,
                "total_runs": len(self.times) + len(self.errors),
                "errors": len(self.errors),
            }

        sorted_times = sorted(self.times)
        return {
            "avg": statistics.mean(self.times),
            "min": min(self.times),
            "max": max(self.times),
            "p95": sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) >= 20 else sorted_times[-1],
            "p99": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) >= 100 else sorted_times[-1],
            "success_rate": (len(self.times) / (len(self.times) + len(self.errors))) * 100,
            "total_runs": len(self.times) + len(self.errors),
            "errors": len(self.errors),
        }


def time_request(func, *args, **kwargs) -> Tuple[float, Any]:
    """Time a function call and return duration and result"""
    start = time.time()
    try:
        result = func(*args, **kwargs)
        duration = (time.time() - start) * 1000  # Convert to ms
        return duration, result
    except Exception as e:
        duration = (time.time() - start) * 1000
        return duration, e


def test_api_get_games(iterations: int = ITERATIONS) -> PerformanceTestResult:
    """Test GET /api/games endpoint"""
    result = PerformanceTestResult("GET /api/games")

    for i in range(iterations):
        duration, response = time_request(
            requests.get, f"{BASE_URL}/api/games", timeout=TIMEOUT
        )

        if isinstance(response, Exception):
            result.add_error(f"Request {i+1}: {str(response)}")
        elif response.status_code == 200:
            result.add_time(duration)
            result.success_count += 1
        else:
            result.add_error(f"Request {i+1}: HTTP {response.status_code}")

    return result


def test_api_get_events(iterations: int = ITERATIONS) -> PerformanceTestResult:
    """Test GET /api/events?game_gid=10000147 endpoint"""
    result = PerformanceTestResult(f"GET /api/events?game_gid={TEST_GAME_GID}")

    for i in range(iterations):
        duration, response = time_request(
            requests.get,
            f"{BASE_URL}/api/events",
            params={"game_gid": TEST_GAME_GID},
            timeout=TIMEOUT,
        )

        if isinstance(response, Exception):
            result.add_error(f"Request {i+1}: {str(response)}")
        elif response.status_code == 200:
            result.add_time(duration)
            result.success_count += 1
        else:
            result.add_error(f"Request {i+1}: HTTP {response.status_code}")

    return result


def test_api_get_parameters(iterations: int = ITERATIONS) -> PerformanceTestResult:
    """Test GET /api/parameters/all?game_gid=10000147 endpoint"""
    result = PerformanceTestResult(f"GET /api/parameters/all?game_gid={TEST_GAME_GID}")

    for i in range(iterations):
        duration, response = time_request(
            requests.get,
            f"{BASE_URL}/api/parameters/all",
            params={"game_gid": TEST_GAME_GID},
            timeout=TIMEOUT,
        )

        if isinstance(response, Exception):
            result.add_error(f"Request {i+1}: {str(response)}")
        elif response.status_code == 200:
            result.add_time(duration)
            result.success_count += 1
        else:
            result.add_error(f"Request {i+1}: HTTP {response.status_code}")

    return result


def test_hql_generate_single(iterations: int = ITERATIONS) -> PerformanceTestResult:
    """Test POST /hql-preview-v2/api/generate - Single event mode"""
    result = PerformanceTestResult("HQL Generation - Single Event Mode")

    # First, get an event_id for testing
    try:
        events_resp = requests.get(
            f"{BASE_URL}/api/events", params={"game_gid": TEST_GAME_GID}, timeout=TIMEOUT
        )
        if events_resp.status_code != 200:
            result.add_error("Failed to fetch events for testing")
            return result

        events_data = events_resp.json()
        if not events_data.get("data", {}).get("events"):
            result.add_error("No events found for testing")
            return result

        event_id = events_data["data"]["events"][0]["id"]

        # Prepare payload for single event HQL generation
        payload = {
            "events": [{"game_gid": TEST_GAME_GID, "event_id": event_id}],
            "fields": [
                {"fieldName": "role_id", "fieldType": "base", "alias": "role"},
                {"fieldName": "zone_id", "fieldType": "param", "jsonPath": "$.zone_id"},
            ],
            "where_conditions": [
                {"field": "zone_id", "operator": "=", "value": 1, "logicalOp": "AND"}
            ],
            "options": {"mode": "single", "sql_mode": "VIEW", "include_comments": True},
        }

        for i in range(iterations):
            duration, response = time_request(
                requests.post,
                f"{BASE_URL}/hql-preview-v2/api/generate",
                json=payload,
                timeout=TIMEOUT,
            )

            if isinstance(response, Exception):
                result.add_error(f"Request {i+1}: {str(response)}")
            elif response.status_code == 200:
                result.add_time(duration)
                result.success_count += 1
            else:
                result.add_error(f"Request {i+1}: HTTP {response.status_code}")

    except Exception as e:
        result.add_error(f"Setup failed: {str(e)}")

    return result


def test_hql_generate_join(iterations: int = ITERATIONS) -> PerformanceTestResult:
    """Test POST /hql-preview-v2/api/generate - Join mode"""
    result = PerformanceTestResult("HQL Generation - Join Mode")

    try:
        # Get multiple events for join
        events_resp = requests.get(
            f"{BASE_URL}/api/events",
            params={"game_gid": TEST_GAME_GID, "per_page": 5},
            timeout=TIMEOUT,
        )
        if events_resp.status_code != 200:
            result.add_error("Failed to fetch events for testing")
            return result

        events_data = events_resp.json()
        events = events_data.get("data", {}).get("events", [])

        if len(events) < 2:
            result.add_error("Need at least 2 events for join mode")
            return result

        # Prepare payload for join mode
        payload = {
            "events": [
                {"game_gid": TEST_GAME_GID, "event_id": events[0]["id"]},
                {"game_gid": TEST_GAME_GID, "event_id": events[1]["id"]},
            ],
            "fields": [
                {"fieldName": "role_id", "fieldType": "base", "alias": "role"},
                {"fieldName": "zone_id", "fieldType": "param", "jsonPath": "$.zone_id"},
            ],
            "options": {
                "mode": "join",
                "join_type": "INNER",
                "join_key": "role_id",
                "sql_mode": "VIEW",
                "include_comments": True,
            },
        }

        for i in range(iterations):
            duration, response = time_request(
                requests.post,
                f"{BASE_URL}/hql-preview-v2/api/generate",
                json=payload,
                timeout=TIMEOUT,
            )

            if isinstance(response, Exception):
                result.add_error(f"Request {i+1}: {str(response)}")
            elif response.status_code == 200:
                result.add_time(duration)
                result.success_count += 1
            else:
                result.add_error(f"Request {i+1}: HTTP {response.status_code}")

    except Exception as e:
        result.add_error(f"Setup failed: {str(e)}")

    return result


def test_hql_generate_union(iterations: int = ITERATIONS) -> PerformanceTestResult:
    """Test POST /hql-preview-v2/api/generate - Union mode"""
    result = PerformanceTestResult("HQL Generation - Union Mode")

    try:
        # Get multiple events for union
        events_resp = requests.get(
            f"{BASE_URL}/api/events",
            params={"game_gid": TEST_GAME_GID, "per_page": 5},
            timeout=TIMEOUT,
        )
        if events_resp.status_code != 200:
            result.add_error("Failed to fetch events for testing")
            return result

        events_data = events_resp.json()
        events = events_data.get("data", {}).get("events", [])

        if len(events) < 2:
            result.add_error("Need at least 2 events for union mode")
            return result

        # Prepare payload for union mode
        payload = {
            "events": [
                {"game_gid": TEST_GAME_GID, "event_id": events[0]["id"]},
                {"game_gid": TEST_GAME_GID, "event_id": events[1]["id"]},
            ],
            "fields": [
                {"fieldName": "role_id", "fieldType": "base", "alias": "role"},
                {"fieldName": "zone_id", "fieldType": "param", "jsonPath": "$.zone_id"},
            ],
            "options": {
                "mode": "union",
                "sql_mode": "VIEW",
                "include_comments": True,
            },
        }

        for i in range(iterations):
            duration, response = time_request(
                requests.post,
                f"{BASE_URL}/hql-preview-v2/api/generate",
                json=payload,
                timeout=TIMEOUT,
            )

            if isinstance(response, Exception):
                result.add_error(f"Request {i+1}: {str(response)}")
            elif response.status_code == 200:
                result.add_time(duration)
                result.success_count += 1
            else:
                result.add_error(f"Request {i+1}: HTTP {response.status_code}")

    except Exception as e:
        result.add_error(f"Setup failed: {str(e)}")

    return result


def test_database_query_performance() -> PerformanceTestResult:
    """Test database query performance via direct SQLite queries"""
    result = PerformanceTestResult("Database Query Performance")

    try:
        import sqlite3

        # Get database path from config
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.core.config import get_db_path

        db_path = get_db_path()

        for i in range(ITERATIONS):
            start = time.time()
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Test a complex JOIN query
                cursor.execute("""
                    SELECT
                        g.name,
                        le.event_name,
                        COUNT(ep.id) as param_count
                    FROM games g
                    INNER JOIN log_events le ON le.game_gid = g.gid
                    LEFT JOIN event_params ep ON ep.event_id = le.id AND ep.is_active = 1
                    WHERE g.gid = ?
                    GROUP BY g.name, le.event_name
                    LIMIT 10
                """, (TEST_GAME_GID,))

                results = cursor.fetchall()
                conn.close()

                duration = (time.time() - start) * 1000
                result.add_time(duration)
                result.success_count += 1

            except Exception as e:
                duration = (time.time() - start) * 1000
                result.add_error(f"Query {i+1}: {str(e)}")

    except ImportError as e:
        result.add_error(f"Failed to import database config: {str(e)}")

    return result


def generate_report(results: List[PerformanceTestResult]) -> str:
    """Generate a comprehensive performance report"""

    report_lines = []
    report_lines.append("=" * 100)
    report_lines.append("EVENT2TABLE PERFORMANCE TEST REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Base URL: {BASE_URL}")
    report_lines.append(f"Test Game GID: {TEST_GAME_GID}")
    report_lines.append(f"Iterations per test: {ITERATIONS}")
    report_lines.append("=" * 100)
    report_lines.append("")

    # Performance Metrics Table
    report_lines.append("PERFORMANCE METRICS")
    report_lines.append("-" * 100)
    report_lines.append(
        f"{'Operation':<50} {'Avg (ms)':<12} {'P95 (ms)':<12} {'Max (ms)':<12} {'Success':<10} {'Status':<10}"
    )
    report_lines.append("-" * 100)

    bottlenecks = []
    recommendations = []

    for result in results:
        stats = result.get_stats()

        # Determine status based on SLA thresholds
        status = "✓ PASS"
        threshold_key = None
        threshold_value = None

        # Map test names to SLA thresholds
        if "api/games" in result.name.lower():
            threshold_key = "api_games_p95"
            threshold_value = SLA_THRESHOLDS["api_games_p95"]
        elif "api/events" in result.name.lower():
            threshold_key = "api_events_p95"
            threshold_value = SLA_THRESHOLDS["api_events_p95"]
        elif "api/parameters" in result.name.lower():
            threshold_key = "api_parameters_p95"
            threshold_value = SLA_THRESHOLDS["api_parameters_p95"]
        elif "single" in result.name.lower():
            threshold_key = "hql_single_p95"
            threshold_value = SLA_THRESHOLDS["hql_single_p95"]
        elif "join" in result.name.lower():
            threshold_key = "hql_join_p95"
            threshold_value = SLA_THRESHOLDS["hql_join_p95"]
        elif "union" in result.name.lower():
            threshold_key = "hql_union_p95"
            threshold_value = SLA_THRESHOLDS["hql_union_p95"]
        elif "database" in result.name.lower():
            threshold_key = "db_query_p95"
            threshold_value = SLA_THRESHOLDS["db_query_p95"]

        if threshold_key and stats["p95"] > threshold_value:
            status = f"✗ FAIL (>{threshold_value}ms)"
            bottlenecks.append(
                f"{result.name}: P95={stats['p95']:.2f}ms exceeds threshold of {threshold_value}ms"
            )

        report_lines.append(
            f"{result.name:<50} {stats['avg']:<12.2f} {stats['p95']:<12.2f} {stats['max']:<12.2f} {stats['success_rate']:<9.1f}% {status:<10}"
        )

        # Identify performance issues
        if stats["avg"] > threshold_value * 0.7 if threshold_value else 1000:
            recommendations.append(
                f"{result.name}: Average response time ({stats['avg']:.2f}ms) is close to threshold"
            )

        if stats["errors"] > 0:
            bottlenecks.append(f"{result.name}: {stats['errors']} errors encountered")

    report_lines.append("-" * 100)
    report_lines.append("")

    # Performance Bottlenecks
    if bottlenecks:
        report_lines.append("PERFORMANCE BOTTLENECKS IDENTIFIED")
        report_lines.append("-" * 100)
        for i, bottleneck in enumerate(bottlenecks, 1):
            report_lines.append(f"{i}. {bottleneck}")
        report_lines.append("")
    else:
        report_lines.append("PERFORMANCE BOTTLENECKS IDENTIFIED")
        report_lines.append("-" * 100)
        report_lines.append("No critical bottlenecks identified. All tests passed SLA thresholds.")
        report_lines.append("")

    # Optimization Recommendations
    if recommendations:
        report_lines.append("OPTIMIZATION RECOMMENDATIONS")
        report_lines.append("-" * 100)
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"{i}. {rec}")
        report_lines.append("")
    else:
        report_lines.append("OPTIMIZATION RECOMMENDATIONS")
        report_lines.append("-" * 100)
        report_lines.append("No immediate optimizations required. System is performing within SLA.")
        report_lines.append("")

    # Cache Effectiveness Analysis
    report_lines.append("CACHE EFFECTIVENESS ANALYSIS")
    report_lines.append("-" * 100)
    report_lines.append("Note: This test script runs all requests sequentially without warm-up.")
    report_lines.append("For cache effectiveness, observe if response times improve in later iterations.")
    report_lines.append("")

    for result in results:
        if len(result.times) >= 5:
            first_half = result.times[: len(result.times) // 2]
            second_half = result.times[len(result.times) // 2 :]

            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            improvement = ((first_avg - second_avg) / first_avg) * 100

            if improvement > 10:
                report_lines.append(
                    f"{result.name}: {improvement:.1f}% improvement in second half "
                    f"(first half: {first_avg:.2f}ms, second half: {second_avg:.2f}ms)"
                )

    report_lines.append("")
    report_lines.append("=" * 100)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 100)

    return "\n".join(report_lines)


def save_report(report: str, output_path: str):
    """Save the report to a file"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✓ Report saved to: {output_path}")


def main():
    """Main test execution"""
    print("=" * 100)
    print("EVENT2TABLE PERFORMANCE TESTING")
    print("=" * 100)
    print(f"Starting tests at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print(f"Iterations: {ITERATIONS}")
    print()

    results = []

    # API Response Time Tests
    print("Running API Response Time Tests...")
    print("-" * 100)

    print("Testing GET /api/games...")
    results.append(test_api_get_games())
    print(f"  ✓ Completed - {results[-1].success_count}/{ITERATIONS} successful")

    print("Testing GET /api/events?game_gid=10000147...")
    results.append(test_api_get_events())
    print(f"  ✓ Completed - {results[-1].success_count}/{ITERATIONS} successful")

    print("Testing GET /api/parameters/all?game_gid=10000147...")
    results.append(test_api_get_parameters())
    print(f"  ✓ Completed - {results[-1].success_count}/{ITERATIONS} successful")

    print()

    # HQL Generation Performance Tests
    print("Running HQL Generation Performance Tests...")
    print("-" * 100)

    print("Testing HQL Generation - Single Event Mode...")
    results.append(test_hql_generate_single())
    print(f"  ✓ Completed - {results[-1].success_count}/{ITERATIONS} successful")

    print("Testing HQL Generation - Join Mode...")
    results.append(test_hql_generate_join())
    print(f"  ✓ Completed - {results[-1].success_count}/{ITERATIONS} successful")

    print("Testing HQL Generation - Union Mode...")
    results.append(test_hql_generate_union())
    print(f"  ✓ Completed - {results[-1].success_count}/{ITERATIONS} successful")

    print()

    # Database Query Performance Tests
    print("Running Database Query Performance Tests...")
    print("-" * 100)

    print("Testing Database Query Performance...")
    results.append(test_database_query_performance())
    print(f"  ✓ Completed - {results[-1].success_count}/{ITERATIONS} successful")

    print()

    # Generate and save report
    print("Generating performance report...")
    report = generate_report(results)

    output_path = "/Users/mckenzie/Documents/event2table/test_results/performance_test_results.txt"
    save_report(report, output_path)

    # Print report to console
    print("\n")
    print(report)

    # Return exit code based on whether all tests passed
    for result in results:
        stats = result.get_stats()
        if stats["errors"] > 0:
            print(f"\n⚠ Some tests had errors. See report for details.")
            return 1

    print(f"\n✓ All tests completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

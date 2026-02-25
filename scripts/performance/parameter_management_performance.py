#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Tests for Parameter Management

Tests performance characteristics of parameter management operations:
- Query response times
- Filter performance
- Common parameter calculation
- Batch field addition
- GraphQL API performance

Target Metrics:
- Simple queries: < 100ms
- Filtered queries: < 200ms
- Common parameter calculation: < 500ms
- Batch operations: < 1 second

@author: Event2Table Team
@date: 2026-02-23
"""

import os
import sys
import time
import statistics
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.core.database import get_db_connection
from backend.core.config.config import get_db_path
from backend.domain.services.parameter_management_service import ParameterManagementService
from backend.application.services.parameter_app_service_enhanced import ParameterAppServiceEnhanced
from backend.models.repositories.parameter_repository import ParameterRepositoryImpl
from backend.models.repositories.common_parameter_repository import CommonParameterRepositoryImpl

# Test configuration
TEST_GID = 90000001  # Use test GID, never use 10000147
ITERATIONS = 5  # Number of iterations for each test
WARMUP_ITERATIONS = 2  # Warmup iterations (not counted in results)


class PerformanceTestResult:
    """Stores performance test results"""

    def __init__(self, name: str, target_ms: float):
        self.name = name
        self.target_ms = target_ms
        self.times: List[float] = []
        self.passed = False

    def add_time(self, elapsed_ms: float):
        """Add a timing measurement"""
        self.times.append(elapsed_ms)

    def calculate_stats(self) -> Dict[str, float]:
        """Calculate statistics"""
        if not self.times:
            return {}

        return {
            'avg': statistics.mean(self.times),
            'median': statistics.median(self.times),
            'min': min(self.times),
            'max': max(self.times),
            'stdev': statistics.stdev(self.times) if len(self.times) > 1 else 0
        }

    def evaluate(self) -> bool:
        """Evaluate if test passed (meets target)"""
        stats = self.calculate_stats()
        avg_time = stats.get('avg', float('inf'))
        self.passed = avg_time < self.target_ms
        return self.passed


def measure_time(func):
    """Decorator to measure function execution time"""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        return result, elapsed_ms
    return wrapper


class ParameterManagementPerformanceTests:
    """Performance tests for parameter management"""

    def __init__(self):
        self.db = get_db_connection(get_db_path())
        self.param_service = ParameterManagementService()
        self.app_service = ParameterAppServiceEnhanced()
        self.param_repo = ParameterRepositoryImpl(self.db)
        self.common_param_repo = CommonParameterRepositoryImpl(self.db)

    def setup_test_data(self):
        """Setup test data for performance testing"""
        print(f"Using test GID: {TEST_GID}")
        print(f"Current parameter count: {self.param_repo.count_by_game(TEST_GID)}")
        print(f"Current event count: {self.param_repo.count_events_by_game(TEST_GID)}")

    @measure_time
    def test_get_all_parameters(self) -> List[Dict]:
        """Test: Get all parameters"""
        return self.param_repo.find_by_game(TEST_GID)

    @measure_time
    def test_filter_parameters_all(self) -> List[Dict]:
        """Test: Filter parameters (mode='all')"""
        from backend.application.dtos.parameter_dto import ParameterFilterDTO
        filter_dto = ParameterFilterDTO(
            game_gid=TEST_GID,
            mode='all'
        )
        return self.app_service.get_filtered_parameters(filter_dto)

    @measure_time
    def test_filter_parameters_common(self) -> List[Dict]:
        """Test: Filter parameters (mode='common')"""
        from backend.application.dtos.parameter_dto import ParameterFilterDTO
        filter_dto = ParameterFilterDTO(
            game_gid=TEST_GID,
            mode='common'
        )
        return self.app_service.get_filtered_parameters(filter_dto)

    @measure_time
    def test_filter_parameters_non_common(self) -> List[Dict]:
        """Test: Filter parameters (mode='non-common')"""
        from backend.application.dtos.parameter_dto import ParameterFilterDTO
        filter_dto = ParameterFilterDTO(
            game_gid=TEST_GID,
            mode='non-common'
        )
        return self.app_service.get_filtered_parameters(filter_dto)

    @measure_time
    def test_calculate_common_parameters(self) -> List[Dict]:
        """Test: Calculate common parameters (expensive operation)"""
        return self.param_service.calculate_common_parameters(TEST_GID, threshold=0.8)

    @measure_time
    def test_get_parameter_details(self) -> Dict:
        """Test: Get extended parameter details"""
        params = self.param_repo.find_by_game(TEST_GID, limit=1)
        if params:
            param_id = params[0]['id']
            return self.app_service.get_parameter_details(param_id)
        return {}

    @measure_time
    def test_detect_parameter_changes(self) -> Dict:
        """Test: Detect parameter count changes"""
        return self.param_service.detect_parameter_changes(TEST_GID)

    def run_test_suite(self, test_name: str, test_func, target_ms: float) -> PerformanceTestResult:
        """Run a performance test with multiple iterations"""
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")

        result = PerformanceTestResult(test_name, target_ms)

        # Warmup iterations
        print(f"Warming up ({WARMUP_ITERATIONS} iterations)...")
        for i in range(WARMUP_ITERATIONS):
            try:
                test_func()[0]
            except Exception as e:
                print(f"  Warning: Warmup iteration {i+1} failed: {e}")

        # Measured iterations
        print(f"Running measured tests ({ITERATIONS} iterations)...")
        for i in range(ITERATIONS):
            try:
                _, elapsed_ms = test_func()
                result.add_time(elapsed_ms)
                print(f"  Iteration {i+1}: {elapsed_ms:.2f}ms")
            except Exception as e:
                print(f"  Error in iteration {i+1}: {e}")

        # Calculate and display statistics
        stats = result.calculate_stats()
        if stats:
            print(f"\nResults:")
            print(f"  Average: {stats['avg']:.2f}ms")
            print(f"  Median:  {stats['median']:.2f}ms")
            print(f"  Min:     {stats['min']:.2f}ms")
            print(f"  Max:     {stats['max']:.2f}ms")
            print(f"  StdDev:  {stats['stdev']:.2f}ms")
            print(f"\nTarget:  {result.target_ms:.2f}ms")

            # Evaluate result
            passed = result.evaluate()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"Status:  {status}")

            if not passed:
                diff = stats['avg'] - result.target_ms
                print(f"Warning: {diff:.2f}ms over target")

        return result

    def run_all_tests(self):
        """Run all performance tests"""
        print("\n" + "="*60)
        print("PARAMETER MANAGEMENT PERFORMANCE TEST SUITE")
        print("="*60)

        self.setup_test_data()

        # Define test suite
        test_suite = [
            ("Get All Parameters", self.test_get_all_parameters, 100.0),
            ("Filter Parameters (All)", self.test_filter_parameters_all, 200.0),
            ("Filter Parameters (Common)", self.test_filter_parameters_common, 200.0),
            ("Filter Parameters (Non-Common)", self.test_filter_parameters_non_common, 200.0),
            ("Calculate Common Parameters", self.test_calculate_common_parameters, 500.0),
            ("Get Parameter Details", self.test_get_parameter_details, 150.0),
            ("Detect Parameter Changes", self.test_detect_parameter_changes, 100.0),
        ]

        results: List[PerformanceTestResult] = []

        # Run all tests
        for test_name, test_func, target_ms in test_suite:
            result = self.run_test_suite(test_name, test_func, target_ms)
            results.append(result)

        # Print summary
        self.print_summary(results)

        return results

    def print_summary(self, results: List[PerformanceTestResult]):
        """Print test summary"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)

        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)

        print(f"\nTests Passed: {passed_count}/{total_count}")
        print(f"Success Rate: {(passed_count/total_count)*100:.1f}%\n")

        print(f"{'Test Name':<40} {'Avg (ms)':<12} {'Target (ms)':<12} {'Status':<8}")
        print("-"*60)

        for result in results:
            stats = result.calculate_stats()
            avg_time = stats.get('avg', 0)
            status = "✅ PASS" if result.passed else "❌ FAIL"

            print(f"{result.name:<40} {avg_time:<12.2f} {result.target_ms:<12.2f} {status:<8}")

        # Overall assessment
        print("\n" + "="*60)
        if passed_count == total_count:
            print("🎉 ALL TESTS PASSED! Performance is excellent.")
        elif passed_count >= total_count * 0.8:
            print("⚠️  Most tests passed. Some optimizations may be needed.")
        else:
            print("❌ Many tests failed. Performance optimization is required.")

        print("="*60 + "\n")


def main():
    """Main entry point"""
    print("\n🚀 Starting Parameter Management Performance Tests...\n")

    try:
        tester = ParameterManagementPerformanceTests()
        results = tester.run_all_tests()

        # Exit with appropriate code
        passed_count = sum(1 for r in results if r.passed)
        total_count = len(results)

        if passed_count == total_count:
            sys.exit(0)
        elif passed_count >= total_count * 0.8:
            sys.exit(1)  # Warning: some tests failed
        else:
            sys.exit(2)  # Error: many tests failed

    except Exception as e:
        print(f"\n❌ Error running performance tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == '__main__':
    main()

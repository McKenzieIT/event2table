#!/usr/bin/env python3
"""
API Performance Benchmark Script
测试所有API端点的响应时间，建立性能基线

Note: Timeout increased from 10s to 30s to accommodate slower API responses in test environment
"""

import time
import requests
import statistics
from typing import List, Dict, Any
from datetime import datetime

# API基础URL
BASE_URL = "http://127.0.0.1:5001"

# 测试的API端点
API_ENDPOINTS = [
    {"method": "GET", "path": "/api/games", "name": "Get All Games"},
    {"method": "GET", "path": "/api/events", "name": "Get All Events"},
    {"method": "GET", "path": "/api/parameters/all", "name": "Get All Parameters"},
    {"method": "GET", "path": "/api/categories", "name": "Get All Categories"},
    {"method": "GET", "path": "/api/join-configs", "name": "Get Join Configs"},
    {"method": "GET", "path": "/api/flows", "name": "Get Flows"},
]


class APIPerformanceTester:
    """API性能测试器"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []

    def test_endpoint(self, endpoint: Dict[str, Any], iterations: int = 10) -> Dict[str, Any]:
        """
        测试单个API端点

        Args:
            endpoint: API端点配置
            iterations: 测试迭代次数

        Returns:
            性能测试结果
        """
        url = f"{self.base_url}{endpoint['path']}"
        method = endpoint['method']
        durations = []
        status_codes = []
        errors = []

        print(f"Testing {endpoint['name']} ({method} {endpoint['path']})")

        for i in range(iterations):
            try:
                start_time = time.perf_counter()
                response = requests.request(method, url, timeout=30)
                end_time = time.perf_counter()

                duration_ms = (end_time - start_time) * 1000
                durations.append(duration_ms)
                status_codes.append(response.status_code)

                if response.status_code >= 400:
                    errors.append(f"HTTP {response.status_code}")

                print(f"  Iteration {i+1}/{iterations}: {duration_ms:.2f}ms (HTTP {response.status_code})")

            except requests.exceptions.Timeout:
                errors.append("Timeout")
                print(f"  Iteration {i+1}/{iterations}: TIMEOUT")
            except Exception as e:
                errors.append(str(e))
                print(f"  Iteration {i+1}/{iterations}: ERROR - {e}")

        # 计算统计数据
        result = {
            "name": endpoint['name'],
            "method": method,
            "path": endpoint['path'],
            "iterations": iterations,
            "successful": len(durations),
            "failed": len(errors),
            "durations": {
                "min": round(min(durations), 2) if durations else 0,
                "max": round(max(durations), 2) if durations else 0,
                "mean": round(statistics.mean(durations), 2) if durations else 0,
                "median": round(statistics.median(durations), 2) if durations else 0,
                "stdev": round(statistics.stdev(durations), 2) if len(durations) > 1 else 0,
            },
            "percentiles": {
                "p50": round(statistics.quantiles(durations, n=2)[0], 2) if len(durations) > 1 else 0,
                "p95": round(statistics.quantiles(durations, n=20)[18], 2) if len(durations) > 1 else 0,
                "p99": round(statistics.quantiles(durations, n=100)[98], 2) if len(durations) > 1 else 0,
            } if len(durations) > 1 else {},
            "errors": errors
        }

        self.results.append(result)
        return result

    def test_all_endpoints(self, iterations: int = 10) -> List[Dict[str, Any]]:
        """
        测试所有API端点

        Args:
            iterations: 每个端点的测试迭代次数

        Returns:
            所有端点的测试结果
        """
        print(f"\n{'='*60}")
        print(f"API Performance Benchmark - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        for endpoint in API_ENDPOINTS:
            self.test_endpoint(endpoint, iterations)
            print()

        return self.results

    def generate_summary(self) -> Dict[str, Any]:
        """
        生成性能测试摘要

        Returns:
            性能测试摘要
        """
        total_requests = sum(r['successful'] + r['failed'] for r in self.results)
        total_successful = sum(r['successful'] for r in self.results)
        total_failed = sum(r['failed'] for r in self.results)

        # 找出最慢的API
        slowest_apis = sorted(
            [r for r in self.results if r['successful'] > 0],
            key=lambda x: x['durations']['mean'],
            reverse=True
        )[:3]

        # 找出最不稳定的API（标准差最大）
        most_variable_apis = sorted(
            [r for r in self.results if r['successful'] > 1],
            key=lambda x: x['durations']['stdev'],
            reverse=True
        )[:3]

        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "failed_requests": total_failed,
            "success_rate": round(total_successful / total_requests * 100, 2) if total_requests > 0 else 0,
            "total_endpoints": len(self.results),
            "slowest_apis": [
                {
                    "name": api['name'],
                    "mean_duration_ms": api['durations']['mean']
                }
                for api in slowest_apis
            ],
            "most_variable_apis": [
                {
                    "name": api['name'],
                    "stdev_ms": api['durations']['stdev']
                }
                for api in most_variable_apis
            ]
        }

        return summary

    def print_summary(self):
        """打印性能测试摘要"""
        summary = self.generate_summary()

        print(f"\n{'='*60}")
        print("Performance Summary")
        print(f"{'='*60}")
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Successful: {summary['successful_requests']}")
        print(f"Failed: {summary['failed_requests']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"\nSlowest APIs:")
        for api in summary['slowest_apis']:
            print(f"  - {api['name']}: {api['mean_duration_ms']}ms")
        print(f"\nMost Variable APIs:")
        for api in summary['most_variable_apis']:
            print(f"  - {api['name']}: {api['stdev_ms']}ms (std dev)")

    def export_results(self, output_file: str = None):
        """
        导出测试结果到JSON文件

        Args:
            output_file: 输出文件路径
        """
        import json

        if output_file is None:
            output_file = f"output/api-baseline-{datetime.now().strftime('%Y-%m-%d')}.json"

        report = {
            "summary": self.generate_summary(),
            "detailed_results": self.results
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nResults exported to: {output_file}")


def main():
    """主函数"""
    tester = APIPerformanceTester()

    # 测试所有API端点
    tester.test_all_endpoints(iterations=10)

    # 打印摘要
    tester.print_summary()

    # 导出结果
    tester.export_results()

    print(f"\n{'='*60}")
    print("Benchmark completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

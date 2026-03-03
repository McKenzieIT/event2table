#!/usr/bin/env python3
"""
API性能基准测试
使用Apache Bench进行性能测试
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
import re

def parse_ab_output(output: str) -> dict:
    """解析Apache Bench输出结果"""
    result = {}

    # 提取关键指标
    patterns = {
        "requests_per_second": r"Requests per second:\s+([\d.]+)",
        "time_per_request": r"Time per request:\s+([\d.]+)\s+\[ms\]\s*\(mean\)",
        "time_per_request_concurrent": r"Time per request:\s+([\d.]+)\s+\[ms\]\s*\(mean, across all concurrent requests\)",
        "transfer_rate": r"Transfer rate:\s+([\d.]+)",
        "failed_requests": r"Failed requests:\s+(\d+)",
        "total_transferred": r"Total transferred:\s+(\d+)\s+bytes",
        "html_transferred": r"HTML transferred:\s+(\d+)\s+bytes",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, output)
        if match:
            result[key] = match.group(1)

    return result

def benchmark_endpoint(url: str, method: str = "GET", data: dict = None) -> dict:
    """
    对单个端点进行基准测试

    Args:
        url: 测试的URL
        method: HTTP方法
        data: POST请求的数据

    Returns:
        包含测试结果的字典
    """
    cmd = [
        "ab", "-n", "1000",  # 总请求数
        "-c", "10",          # 并发数
        "-m", "application/json",
        "-t", "application/json",
        url
    ]

    if method == "POST" and data:
        # 创建临时文件存储POST数据
        post_file = Path("/tmp/ab_post_data.json")
        with open(post_file, 'w') as f:
            json.dump(data, f)
        cmd.extend(["-p", str(post_file)])

    print(f"  Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )

        parsed = parse_ab_output(result.stdout)
        parsed["raw_output"] = result.stdout
        parsed["stderr"] = result.stderr
        parsed["return_code"] = result.returncode

        return parsed

    except subprocess.TimeoutExpired:
        return {"error": "Benchmark timed out after 60 seconds"}
    except FileNotFoundError:
        return {"error": "Apache Bench (ab) not found. Install with: brew install httpd"}
    except Exception as e:
        return {"error": f"Benchmark failed: {str(e)}"}

def run_benchmarks():
    """运行所有基准测试"""
    base_url = "http://127.0.0.1:5001"

    print("=" * 60)
    print("API Performance Benchmark Test")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: {base_url}")
    print("-" * 60)

    results = {
        "timestamp": datetime.now().isoformat(),
        "target": base_url,
        "benchmarks": {}
    }

    # 测试games端点
    print("\n📊 Testing /api/games...")
    results["benchmarks"]["games"] = benchmark_endpoint(
        f"{base_url}/api/games"
    )

    # 测试events端点
    print("\n📊 Testing /api/events...")
    results["benchmarks"]["events"] = benchmark_endpoint(
        f"{base_url}/api/events?game_gid=10000147"
    )

    # 测试parameters端点
    print("\n📊 Testing /api/parameters/all...")
    results["benchmarks"]["parameters"] = benchmark_endpoint(
        f"{base_url}/api/parameters/all?game_gid=10000147"
    )

    # 测试单个游戏端点
    print("\n📊 Testing /api/games/<gid>...")
    results["benchmarks"]["single_game"] = benchmark_endpoint(
        f"{base_url}/api/games/10000147"
    )

    # 测试单个事件端点
    print("\n📊 Testing /api/events/<id>...")
    results["benchmarks"]["single_event"] = benchmark_endpoint(
        f"{base_url}/api/events/1"
    )

    # 保存结果
    output_dir = Path("output/benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"benchmark_results_{timestamp_str}.json"

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ Benchmark completed successfully!")
    print(f"📄 Results saved to: {output_file}")
    print("=" * 60)

    # 打印摘要
    print("\n📊 Summary:")
    for endpoint, data in results["benchmarks"].items():
        if "error" in data:
            print(f"  ❌ {endpoint}: {data['error']}")
        elif "requests_per_second" in data:
            rps = data["requests_per_second"]
            tpr = data.get("time_per_request", "N/A")
            print(f"  ✅ {endpoint}: {rps} req/s, {tpr} ms/req")

    return results

def print_usage():
    """打印使用说明"""
    print("""
API Performance Benchmark Test
===============================

Usage:
    python3 scripts/benchmark/api_performance_test.py

Requirements:
    1. Flask server running on http://127.0.0.1:5001
    2. Apache Bench (ab) installed

Install Apache Bench:
    macOS: brew install httpd
    Ubuntu: sudo apt-get install apache2-utils
    CentOS: sudo yum install httpd-tools

Output:
    Results saved to: output/benchmark/benchmark_results_YYYYMMDD_HHMMSS.json

Metrics:
    - Requests per second: 吞吐量
    - Time per request: 响应时间
    - Failed requests: 失败请求数
    - Transfer rate: 传输速率
    """)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print_usage()
    else:
        run_benchmarks()

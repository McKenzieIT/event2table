#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存监控系统集成验证
====================

验证缓存监控系统的完整功能

版本: 1.0.0
日期: 2026-03-10
"""

import sys
import time

import requests


def test_cache_stats():
    """测试缓存统计API"""
    print("\n" + "=" * 60)
    print("测试1: 缓存统计API")
    print("=" * 60)

    try:
        response = requests.get('http://127.0.0.1:5001/api/cache/stats', timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data['success'] == True, "API should return success"
        assert 'l1_cache' in data, "Should contain l1_cache stats"
        assert 'monitoring' in data, "Should contain monitoring stats"

        print("✅ 缓存统计API正常")
        print(f"   L1缓存使用率: {data['l1_cache']['usage']}")
        if 'monitoring' in data and 'performance_metrics' in data['monitoring']:
            print(f"   当前命中率: {data['monitoring']['performance_metrics'].get('hit_rate', 'N/A')}")
            print(
                f"   平均响应时间: {data['monitoring']['performance_metrics'].get('avg_response_time_ms', 'N/A')} ms"
            )

        return True
    except Exception as e:
        print(f"❌ 缓存统计API测试失败: {e}")
        return False


def test_monitoring_performance():
    """测试监控性能API"""
    print("\n" + "=" * 60)
    print("测试2: 监控性能API")
    print("=" * 60)

    try:
        response = requests.get(
            'http://127.0.0.1:5001/api/cache/monitoring/performance?hours=24', timeout=5
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data['success'] == True, "API should return success"
        assert 'performance_summary' in data, "Should contain performance_summary"
        assert 'current_metrics' in data, "Should contain current_metrics"

        print("✅ 监控性能API正常")
        print(f"   查询时间范围: {data['period_hours']} 小时")
        if 'avg_hit_rate' in data['performance_summary']:
            print(f"   平均命中率: {data['performance_summary']['avg_hit_rate']:.2f}%")
        if 'avg_response_time_ms' in data['performance_summary']:
            print(f"   平均响应时间: {data['performance_summary']['avg_response_time_ms']:.2f} ms")

        return True
    except Exception as e:
        print(f"❌ 监控性能API测试失败: {e}")
        return False


def test_monitoring_snapshot():
    """测试监控快照API"""
    print("\n" + "=" * 60)
    print("测试3: 监控快照API")
    print("=" * 60)

    try:
        response = requests.post('http://127.0.0.1:5001/api/cache/monitoring/snapshot', timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data['success'] == True, "API should return success"
        assert 'message' in data, "Should contain message"

        print("✅ 监控快照API正常")
        print(f"   消息: {data['message']}")

        return True
    except Exception as e:
        print(f"❌ 监控快照API测试失败: {e}")
        return False


def test_cache_headers():
    """测试HTTP缓存响应头"""
    print("\n" + "=" * 60)
    print("测试4: HTTP缓存响应头")
    print("=" * 60)

    try:
        # 第一次请求(应该是MISS)
        response1 = requests.get('http://127.0.0.1:5001/api/games', timeout=5)
        assert response1.status_code == 200

        headers1 = response1.headers
        print("   第一次请求:")
        print(f"     X-Cache-Status: {headers1.get('X-Cache-Status', 'N/A')}")
        print(f"     X-Cache-Key: {headers1.get('X-Cache-Key', 'N/A')}")
        print(f"     X-Response-Time: {headers1.get('X-Response-Time', 'N/A')}")

        # 第二次请求(应该是HIT)
        response2 = requests.get('http://127.0.0.1:5001/api/games', timeout=5)
        assert response2.status_code == 200

        headers2 = response2.headers
        print("   第二次请求:")
        print(f"     X-Cache-Status: {headers2.get('X-Cache-Status', 'N/A')}")
        print(f"     X-Cache-Key: {headers2.get('X-Cache-Key', 'N/A')}")
        print(f"     X-Response-Time: {headers2.get('X-Response-Time', 'N/A')}")

        # 验证响应头存在
        if 'X-Cache-Status' in headers2:
            print("✅ HTTP缓存响应头正常")
            return True
        else:
            print("⚠️  HTTP缓存响应头缺失（可能是中间件未初始化）")
            return False

    except Exception as e:
        print(f"❌ HTTP缓存响应头测试失败: {e}")
        return False


def test_monitoring_integration():
    """测试监控系统集成"""
    print("\n" + "=" * 60)
    print("测试5: 监控系统集成")
    print("=" * 60)

    try:
        # 执行多次API调用以产生监控数据
        print("   执行10次API调用...")
        for i in range(10):
            requests.get('http://127.0.0.1:5001/api/games', timeout=5)
            time.sleep(0.1)

        # 创建快照
        response = requests.post('http://127.0.0.1:5001/api/cache/monitoring/snapshot', timeout=5)
        assert response.status_code == 200

        # 获取监控性能
        response = requests.get(
            'http://127.0.0.1:5001/api/cache/monitoring/performance?hours=1', timeout=5
        )
        assert response.status_code == 200

        data = response.json()
        snapshot_count = data['performance_summary'].get('total_snapshots', 0)

        print(f"   快照数量: {snapshot_count}")
        print("✅ 监控系统集成正常")

        return True
    except Exception as e:
        print(f"❌ 监控系统集成测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("缓存监控系统集成验证")
    print("=" * 60)
    print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 检查后端是否运行
    try:
        response = requests.get('http://127.0.0.1:5001/api/health', timeout=2)
        if response.status_code != 200:
            print("❌ 后端服务未正常响应")
            print("请先启动后端服务: python web_app.py")
            return False
    except Exception:
        print("❌ 无法连接到后端服务")
        print("请先启动后端服务: python web_app.py")
        return False

    # 执行测试
    tests = [
        test_cache_stats,
        test_monitoring_performance,
        test_monitoring_snapshot,
        test_cache_headers,
        test_monitoring_integration,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            results.append(False)

    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")

    if passed == total:
        print("\n✅ 所有测试通过！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试JSON格式的事件导入API

用于验证 /api/events/import 端点的功能
"""

import requests
import json
import sys

API_URL = "http://127.0.0.1:5001/api/events/import"

# 测试数据
test_data = {
    "game_gid": 90000001,  # 使用测试GID
    "events": [
        {
            "event_code": "test_json_001",
            "event_name": "JSON测试事件1",
            "event_name_cn": "JSON测试事件1",
            "description": "通过JSON API导入的测试事件",
            "category": "test"
        },
        {
            "event_code": "test_json_002",
            "event_name": "JSON测试事件2",
            "event_name_cn": "JSON测试事件2",
            "description": "另一个测试事件",
            "category": "test"
        }
    ]
}


def test_json_import():
    """测试JSON事件导入API"""
    print("=" * 80)
    print("Testing JSON Event Import API")
    print("=" * 80)
    print(f"\nURL: {API_URL}")
    print(f"Method: POST")
    print(f"Content-Type: application/json")
    print(f"\nRequest Body:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))

    try:
        # 发送请求
        print("\n" + "-" * 80)
        print("Sending request...")
        response = requests.post(
            API_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")

        # 解析响应
        try:
            result = response.json()
            print(f"\nResponse Body:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except ValueError:
            print(f"\nResponse Text (not JSON):")
            print(response.text)
            result = None

        # 验证结果
        print("\n" + "=" * 80)
        print("Validation Results")
        print("=" * 80)

        if response.status_code == 200 and result:
            if result.get('success'):
                data = result.get('data', {})
                imported = data.get('imported', 0)
                failed = data.get('failed', 0)
                errors = data.get('errors', [])

                print(f"\n✅ Import successful!")
                print(f"   Imported: {imported}")
                print(f"   Failed: {failed}")
                if errors:
                    print(f"   Errors:")
                    for error in errors:
                        print(f"      - {error}")
                else:
                    print(f"   Errors: None")

                # 验证导入数量
                if imported == len(test_data['events']):
                    print(f"\n✅ All events imported successfully!")
                    return True
                else:
                    print(f"\n⚠️  Partial success: {imported}/{len(test_data['events'])} imported")
                    return False
            else:
                print(f"\n❌ Import failed: {result.get('message')}")
                return False
        else:
            print(f"\n❌ API error: HTTP {response.status_code}")
            if result:
                print(f"   Message: {result.get('message', 'Unknown error')}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error: Could not connect to {API_URL}")
        print(f"   Make sure the Flask server is running:")
        print(f"   python web_app.py")
        return False

    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout: Request took longer than 10 seconds")
        return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        return False


def test_duplicate_detection():
    """测试重复事件检测"""
    print("\n" + "=" * 80)
    print("Testing Duplicate Event Detection")
    print("=" * 80)

    # 再次提交相同的数据，应该检测到重复
    print("\nSubmitting same data again (should detect duplicates)...")
    print(f"URL: {API_URL}")

    try:
        response = requests.post(
            API_URL,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            if result.get('success'):
                data = result.get('data', {})
                failed = data.get('failed', 0)
                errors = data.get('errors', [])

                if failed > 0 and errors:
                    print(f"\n✅ Duplicate detection works!")
                    print(f"   {failed} events rejected as duplicates")
                    return True
                else:
                    print(f"\n⚠️  Expected duplicates but none detected")
                    return False

        return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_invalid_game_gid():
    """测试无效的game_gid"""
    print("\n" + "=" * 80)
    print("Testing Invalid game_gid")
    print("=" * 80)

    invalid_data = {
        "game_gid": 99999999,  # 不存在的GID
        "events": [
            {
                "event_code": "test_invalid",
                "event_name": "Invalid Game Test"
            }
        ]
    }

    print(f"\nSubmitting with invalid game_gid: {invalid_data['game_gid']}")

    try:
        response = requests.post(
            API_URL,
            json=invalid_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code != 200:
            result = response.json()
            print(f"Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print(f"\n✅ Correctly rejected invalid game_gid")
            return True
        else:
            print(f"\n⚠️  Expected error but request succeeded")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 80)
    print("JSON Event Import API Test Suite")
    print("=" * 80)

    results = []

    # 测试1: 正常导入
    results.append(("Basic Import", test_json_import()))

    # 测试2: 重复检测
    results.append(("Duplicate Detection", test_duplicate_detection()))

    # 测试3: 无效game_gid
    results.append(("Invalid game_gid", test_invalid_game_gid()))

    # 汇总结果
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

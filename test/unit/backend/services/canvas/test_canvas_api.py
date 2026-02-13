#!/usr/bin/env python3
"""
Canvas API 端点测试脚本

测试新增的 Flow Management API:
- GET /canvas/api/flows/<flow_id>
- POST /canvas/api/flows/save
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_get_flow(flow_id=1):
    """测试获取 Flow 详情"""
    print(f"\n{'='*60}")
    print(f"测试: GET /canvas/api/flows/{flow_id}")
    print(f"{'='*60}")

    response = requests.get(f"{BASE_URL}/canvas/api/flows/{flow_id}")

    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"✅ 成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"响应内容: {response.text[:200]}")
    else:
        print(f"❌ 失败: {response.text[:200]}")

    return response.status_code == 200 and response.headers.get('Content-Type', '').startswith('application/json')

def test_save_flow():
    """测试保存 Flow"""
    print(f"\n{'='*60}")
    print(f"测试: POST /canvas/api/flows/save")
    print(f"{'='*60}")

    flow_data = {
        "game_gid": 10000147,
        "flow_name": "Test Flow",
        "flow_graph": {
            "nodes": [
                {"id": "node1", "type": "event", "data": {"label": "Login Event"}}
            ],
            "edges": []
        },
        "description": "Test flow description"
    }

    response = requests.post(
        f"{BASE_URL}/canvas/api/flows/save",
        json=flow_data,
        headers={"Content-Type": "application/json"}
    )

    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    if response.status_code in [200, 201]:
        try:
            data = response.json()
            print(f"✅ 成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"响应内容: {response.text[:200]}")
    else:
        print(f"❌ 失败: {response.text[:200]}")

    return response.status_code in [200, 201] and response.headers.get('Content-Type', '').startswith('application/json')

def main():
    print("=" * 60)
    print("Canvas API 测试")
    print("=" * 60)
    print(f"服务器地址: {BASE_URL}")
    print(f"测试时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 测试结果
    results = []

    # 测试 1: 获取 Flow
    results.append(("GET /canvas/api/flows/<id>", test_get_flow(1)))

    # 测试 2: 保存 Flow
    results.append(("POST /canvas/api/flows/save", test_save_flow()))

    # 汇总结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")

    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")

    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n✅ 所有测试通过！Canvas API 修复成功！")
        return 0
    else:
        print(f"\n❌ {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    try:
        exit(main())
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器")
        print("请确保 Flask 服务器正在运行: python web_app.py")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        exit(1)

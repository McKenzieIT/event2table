#!/usr/bin/env python3
"""快速验证 Event Nodes API 修复"""

import requests
import json


def test_api_format():
    """测试 API 返回格式是否正确"""
    print("=" * 60)
    print("测试 Event Nodes API 返回格式")
    print("=" * 60)

    base_url = "http://127.0.0.1:5001/event_node_builder/api"

    # Test 1: Search endpoint
    print("\n1. 测试 /search 端点...")
    try:
        response = requests.get(f"{base_url}/search?game_gid=10000147")
        data = response.json()

        print(f"   状态码: {response.status_code}")
        print(f"   成功: {data.get('success')}")

        # 检查 data 的结构
        if 'data' in data:
            response_data = data['data']
            print(f"   data 类型: {type(response_data)}")

            # 期望 data 是字典, 包含 nodes 属性
            if isinstance(response_data, dict):
                if 'nodes' in response_data:
                    print(f"   ✅ data.nodes 存在")
                    print(f"   ✅ data.total = {response_data.get('total')}")
                    print(f"   ✅ data.page = {response_data.get('page')}")
                else:
                    print(f"   ❌ data.nodes 不存在")
            else:
                print(f"   ❌ data 不是字典类型")

        print(f"   完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    # Test 2: Stats endpoint
    print("\n2. 测试 /stats 端点...")
    try:
        response = requests.get(f"{base_url}/stats?game_gid=10000147")
        data = response.json()

        print(f"   状态码: {response.status_code}")
        print(f"   成功: {data.get('success')}")

        # 检查 data 的结构
        if 'data' in data:
            stats = data['data']
            print(f"   ✅ avg_fields = {stats.get('avg_fields')}")
            print(f"   ✅ total_nodes = {stats.get('total_nodes')}")
            print(f"   ✅ unique_events = {stats.get('unique_events')}")

        print(f"   完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    test_api_format()

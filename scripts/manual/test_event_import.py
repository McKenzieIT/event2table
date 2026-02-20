#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试事件导入API

This script tests the event import functionality.
"""

import sys
import json
import requests

# API base URL
BASE_URL = "http://127.0.0.1:5001"

# Test data
TEST_IMPORT_DATA = {
    "game_gid": 10000147,
    "events": [
        {
            "event_code": "test_login_001",
            "event_name": "测试登录事件",
            "event_name_cn": "测试登录事件",
            "description": "这是一个测试导入的登录事件",
            "category": "login"
        },
        {
            "event_code": "test_logout_001",
            "event_name": "测试登出事件",
            "event_name_cn": "测试登出事件",
            "description": "这是一个测试导入的登出事件",
            "category": "logout"
        },
        {
            "event_code": "test_payment_001",
            "event_name": "测试支付事件",
            "event_name_cn": "测试支付事件",
            "description": "这是一个测试导入的支付事件",
            "category": "payment"
        }
    ]
}


def test_import_events():
    """测试事件导入"""
    print("=" * 60)
    print("测试事件导入API")
    print("=" * 60)

    url = f"{BASE_URL}/api/events/import"
    headers = {"Content-Type": "application/json"}

    print(f"\n发送请求到: {url}")
    print(f"请求数据: {json.dumps(TEST_IMPORT_DATA, indent=2, ensure_ascii=False)}")

    try:
        response = requests.post(url, json=TEST_IMPORT_DATA, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("data", {})
                print(f"\n✅ 导入成功!")
                print(f"   成功: {result.get('imported', 0)} 个")
                print(f"   失败: {result.get('failed', 0)} 个")
                if result.get("errors"):
                    print(f"   错误: {result['errors']}")
            else:
                print(f"\n❌ 导入失败: {data.get('message')}")
        else:
            print(f"\n❌ 请求失败: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print(f"\n❌ 连接失败: 请确保后端服务器正在运行 (python web_app.py)")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def test_duplicate_import():
    """测试重复导入（应该失败）"""
    print("\n" + "=" * 60)
    print("测试重复导入（应该失败）")
    print("=" * 60)

    url = f"{BASE_URL}/api/events/import"
    headers = {"Content-Type": "application/json"}

    # 导入相同的数据（应该检测到重复）
    print(f"\n发送请求到: {url}")
    print("预期: 检测到重复事件，导入失败")

    try:
        response = requests.post(url, json=TEST_IMPORT_DATA, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                result = data.get("data", {})
                if result.get("failed", 0) > 0:
                    print(f"\n✅ 重复检测正常工作!")
                    print(f"   检测到 {result.get('failed', 0)} 个重复事件")
                else:
                    print(f"\n⚠️  警告: 重复检测未生效")

    except Exception as e:
        print(f"\n❌ 错误: {e}")


def test_invalid_game_gid():
    """测试无效的游戏GID"""
    print("\n" + "=" * 60)
    print("测试无效的游戏GID")
    print("=" * 60)

    url = f"{BASE_URL}/api/events/import"
    headers = {"Content-Type": "application/json"}

    invalid_data = {
        "game_gid": 99999999,  # 不存在的游戏
        "events": [
            {
                "event_code": "test_event",
                "event_name": "测试事件"
            }
        ]
    }

    print(f"\n发送请求到: {url}")
    print(f"请求数据: {json.dumps(invalid_data, indent=2)}")
    print("预期: 游戏不存在，导入失败")

    try:
        response = requests.post(url, json=invalid_data, headers=headers)
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

        if response.status_code == 200:
            data = response.json()
            result = data.get("data", {})
            if result.get("failed", 0) > 0:
                print(f"\n✅ 游戏验证正常工作!")
            else:
                print(f"\n⚠️  警告: 游戏验证未生效")

    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    print("事件导入API测试脚本")
    print("=" * 60)
    print("请确保后端服务器正在运行: python web_app.py")
    print("=" * 60)

    # 运行测试
    test_import_events()
    test_duplicate_import()
    test_invalid_game_gid()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

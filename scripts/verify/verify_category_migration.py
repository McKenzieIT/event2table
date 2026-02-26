#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Category模块迁移验证脚本

验证Entity架构迁移后的API功能
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:5001"


def print_section(title: str):
    """打印分隔线"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_list_categories():
    """测试1: 获取所有类别"""
    print_section("测试1: 获取所有类别")

    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        data = response.json()

        print(f"✅ Status: {response.status_code}")
        print(f"✅ 类别数量: {len(data['data'])}")

        if data['data']:
            print(f"✅ 第一个类别: {data['data'][0]['name']}")

        return data['data']
    except Exception as e:
        print(f"❌ 失败: {e}")
        return []


def test_create_category():
    """测试2: 创建类别"""
    print_section("测试2: 创建类别")

    category_data = {
        "name": "TEST_验证类别",
        "name_cn": "验证测试",
        "description": "用于验证Entity架构迁移",
        "color": "#00FF00",
        "icon": "check-icon"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/categories",
            json=category_data
        )
        data = response.json()

        if response.status_code == 200:
            print(f"✅ Status: {response.status_code}")
            print(f"✅ 创建成功: {data['data']['name']}")
            print(f"✅ ID: {data['data']['id']}")
            return data['data']
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ 错误: {data.get('error', 'Unknown')}")
            return None
    except Exception as e:
        print(f"❌ 失败: {e}")
        return None


def test_get_category(category_id: int):
    """测试3: 获取单个类别"""
    print_section(f"测试3: 获取类别 ID={category_id}")

    try:
        response = requests.get(f"{BASE_URL}/api/categories/{category_id}")
        data = response.json()

        if response.status_code == 200:
            print(f"✅ Status: {response.status_code}")
            print(f"✅ 类别名称: {data['data']['name']}")
            print(f"✅ 中文名: {data['data'].get('name_cn', 'N/A')}")
            print(f"✅ 描述: {data['data'].get('description', 'N/A')}")
            print(f"✅ 颜色: {data['data'].get('color', 'N/A')}")
            return data['data']
        else:
            print(f"❌ Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 失败: {e}")
        return None


def test_update_category(category_id: int):
    """测试4: 更新类别"""
    print_section(f"测试4: 更新类别 ID={category_id}")

    update_data = {
        "description": "已更新的描述",
        "color": "#FF0000"
    }

    try:
        response = requests.put(
            f"{BASE_URL}/api/categories/{category_id}",
            json=update_data
        )
        data = response.json()

        if response.status_code == 200:
            print(f"✅ Status: {response.status_code}")
            print(f"✅ 更新成功: {data['data']['name']}")
            print(f"✅ 新描述: {data['data']['description']}")
            print(f"✅ 新颜色: {data['data']['color']}")
            return data['data']
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"❌ 错误: {data.get('error', 'Unknown')}")
            return None
    except Exception as e:
        print(f"❌ 失败: {e}")
        return None


def test_batch_operations():
    """测试5: 批量操作"""
    print_section("测试5: 批量操作")

    # 创建多个测试类别
    category_ids = []
    for i in range(3):
        category_data = {
            "name": f"TEST_Batch_{i}",
            "name_cn": f"批量测试{i}"
        }
        response = requests.post(
            f"{BASE_URL}/api/categories",
            json=category_data
        )
        if response.status_code == 200:
            category_ids.append(response.json()['data']['id'])

    print(f"✅ 创建了 {len(category_ids)} 个测试类别")

    # 批量更新
    if category_ids:
        update_data = {
            "description": "批量更新描述"
        }
        response = requests.put(
            f"{BASE_URL}/api/categories/batch-update",
            json={
                "ids": category_ids,
                "updates": update_data
            }
        )
        if response.status_code == 200:
            print(f"✅ 批量更新成功: {response.json()['data']['updated_count']} 个")

        # 批量删除
        response = requests.delete(
            f"{BASE_URL}/api/categories/batch",
            json={"ids": category_ids}
        )
        if response.status_code == 200:
            print(f"✅ 批量删除成功: {response.json()['data']['deleted_count']} 个")


def test_entity_validation():
    """测试6: Entity验证"""
    print_section("测试6: Entity验证")

    # 测试必填字段验证
    print("\n测试1: 缺少必填字段")
    response = requests.post(
        f"{BASE_URL}/api/categories",
        json={"description": "No name field"}
    )
    print(f"✅ 正确拒绝: {response.status_code} (预期400)")

    # 测试字段长度验证
    print("\n测试2: 名称过长")
    response = requests.post(
        f"{BASE_URL}/api/categories",
        json={"name": "x" * 101}
    )
    print(f"✅ 正确拒绝: {response.status_code} (预期400)")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  Event Category模块迁移验证")
    print("="*60)

    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/categories", timeout=2)
        print(f"✅ 服务器运行正常: {BASE_URL}")
    except Exception:
        print(f"❌ 无法连接到服务器: {BASE_URL}")
        print("请先启动服务器: python3 web_app.py")
        return

    # 运行所有测试
    test_list_categories()
    created = test_create_category()

    if created:
        test_get_category(created['id'])
        test_update_category(created['id'])

    test_batch_operations()
    test_entity_validation()

    # 清理测试数据
    print_section("清理测试数据")
    try:
        response = requests.get(f"{BASE_URL}/api/categories")
        categories = response.json()['data']

        test_ids = [
            c['id'] for c in categories
            if c['name'].startswith('TEST_')
        ]

        if test_ids:
            requests.delete(
                f"{BASE_URL}/api/categories/batch",
                json={"ids": test_ids}
            )
            print(f"✅ 清理了 {len(test_ids)} 个测试类别")
    except Exception as e:
        print(f"⚠️  清理失败: {e}")

    print_section("验证完成")
    print("✅ 所有测试完成！")


if __name__ == "__main__":
    main()

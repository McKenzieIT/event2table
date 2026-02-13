#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canvas Template APIs 自动化测试脚本
测试所有Canvas模板管理API端点

版本: 1.0
日期: 2026-01-29
"""

import sys
import os
import json
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置
API_BASE_URL = "http://127.0.0.1:5001"
TEST_GAME_GID = 10000147


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(message):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    """打印信息消息"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def print_section(message):
    """打印章节标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def test_api_health():
    """测试API健康检查"""
    print_section("1. API健康检查")

    try:
        response = requests.get(f"{API_BASE_URL}/canvas/api/canvas/health", timeout=5)
        if response.status_code == 200:
            print_success("API服务运行正常")
            data = response.json()
            print_info(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print_error(f"API健康检查失败: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"无法连接到API服务: {e}")
        print_info("请确保Flask服务器正在运行: python web_app.py")
        return False


def test_create_template():
    """测试创建模板"""
    print_section("2. 测试创建模板")

    template_data = {
        "name": "测试模板 - 用户登录分析",
        "game_gid": TEST_GAME_GID,
        "canvas_data": {
            "nodes": [
                {
                    "id": "event1",
                    "type": "event",
                    "position": {"x": 100, "y": 100},
                    "data": {
                        "label": "登录事件",
                        "description": "用户登录事件"
                    }
                },
                {
                    "id": "output1",
                    "type": "output",
                    "position": {"x": 400, "y": 100},
                    "data": {"label": "输出"}
                }
            ],
            "edges": [
                {"id": "e1", "source": "event1", "target": "output1"}
            ]
        },
        "description": "这是一个测试模板，用于分析用户登录行为",
        "category": "用户行为",
        "tags": ["登录", "测试", "用户行为"],
        "is_public": False
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/templates",
            json=template_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            print_success("模板创建成功")
            data = response.json()
            print_info(f"模板ID: {data['data'].get('id')}")
            print_info(f"模板名称: {data['data'].get('name')}")
            return data['data'].get('id')
        else:
            print_error(f"模板创建失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return None


def test_list_templates():
    """测试获取模板列表"""
    print_section("3. 测试获取模板列表")

    try:
        # 测试基本列表
        response = requests.get(
            f"{API_BASE_URL}/api/templates",
            params={"page": 1, "per_page": 10},
            timeout=10
        )

        if response.status_code == 200:
            print_success("模板列表获取成功")
            data = response.json()
            templates = data['data']['templates']
            pagination = data['data']['pagination']

            print_info(f"模板数量: {len(templates)}")
            print_info(f"分页信息: 页码 {pagination['page']}/{pagination['pages']}, 总计 {pagination['total']}")

            if templates:
                print_info(f"第一个模板: {templates[0].get('name')} (ID: {templates[0].get('id')})")

            return templates
        else:
            print_error(f"模板列表获取失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return []


def test_get_template(template_id):
    """测试获取单个模板"""
    print_section("4. 测试获取单个模板")

    if not template_id:
        print_error("没有可用的模板ID")
        return None

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/templates/{template_id}",
            timeout=10
        )

        if response.status_code == 200:
            print_success("模板详情获取成功")
            data = response.json()
            template = data['data']

            print_info(f"模板ID: {template.get('id')}")
            print_info(f"模板名称: {template.get('name')}")
            print_info(f"分类: {template.get('category')}")
            print_info(f"标签: {template.get('tags')}")
            print_info(f"描述: {template.get('description')}")

            # 检查flow_graph
            if template.get('flow_graph'):
                flow_graph = template['flow_graph']
                print_info(f"节点数量: {len(flow_graph.get('nodes', []))}")
                print_info(f"连接数量: {len(flow_graph.get('edges', []))}")

            return template
        else:
            print_error(f"模板详情获取失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return None


def test_update_template(template_id):
    """测试更新模板"""
    print_section("5. 测试更新模板")

    if not template_id:
        print_error("没有可用的模板ID")
        return False

    update_data = {
        "name": "测试模板 - 用户登录分析（已更新）",
        "description": "这是更新后的描述",
        "tags": ["登录", "测试", "更新"],
        "category": "用户行为分析"
    }

    try:
        response = requests.put(
            f"{API_BASE_URL}/api/templates/{template_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            print_success("模板更新成功")
            data = response.json()
            print_info(f"更新后的名称: {data['data'].get('name')}")
            return True
        else:
            print_error(f"模板更新失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return False


def test_apply_template(template_id):
    """测试应用模板"""
    print_section("6. 测试应用模板")

    if not template_id:
        print_error("没有可用的模板ID")
        return None

    apply_data = {
        "variables": {
            "event_id": 42,
            "date_field": "ds"
        }
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/templates/{template_id}/apply",
            json=apply_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            print_success("模板应用成功")
            data = response.json()
            flow_graph = data['data']

            print_info(f"返回节点数量: {len(flow_graph.get('nodes', []))}")
            print_info(f"返回连接数量: {len(flow_graph.get('edges', []))}")

            return flow_graph
        else:
            print_error(f"模板应用失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return None


def test_clone_template(template_id):
    """测试克隆模板"""
    print_section("7. 测试克隆模板")

    if not template_id:
        print_error("没有可用的模板ID")
        return None

    clone_data = {
        "new_name": "测试模板 - 克隆副本",
        "game_gid": TEST_GAME_GID
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/templates/{template_id}/clone",
            json=clone_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            print_success("模板克隆成功")
            data = response.json()
            new_template_id = data['data'].get('id')
            print_info(f"新模板ID: {new_template_id}")
            print_info(f"新模板名称: {data['data'].get('name')}")
            return new_template_id
        else:
            print_error(f"模板克隆失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return None


def test_get_categories():
    """测试获取分类列表"""
    print_section("8. 测试获取分类列表")

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/templates/categories",
            timeout=10
        )

        if response.status_code == 200:
            print_success("分类列表获取成功")
            data = response.json()
            categories = data['data']['categories']

            print_info(f"分类数量: {len(categories)}")

            if categories:
                print_info("分类列表:")
                for cat in categories[:5]:  # 只显示前5个
                    print_info(f"  - {cat.get('name')}: {cat.get('count')} 个模板")

            return categories
        else:
            print_error(f"分类列表获取失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return []

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return []


def test_delete_template(template_id):
    """测试删除模板"""
    print_section("9. 测试删除模板")

    if not template_id:
        print_error("没有可用的模板ID")
        return False

    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/templates/{template_id}",
            timeout=10
        )

        if response.status_code == 200:
            print_success("模板删除成功")
            return True
        else:
            print_error(f"模板删除失败: HTTP {response.status_code}")
            print_info(f"响应: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return False


def test_filter_and_search():
    """测试筛选和搜索功能"""
    print_section("10. 测试筛选和搜索功能")

    try:
        # 测试按游戏筛选
        print_info("测试按game_gid筛选...")
        response = requests.get(
            f"{API_BASE_URL}/api/templates",
            params={"game_gid": TEST_GAME_GID},
            timeout=10
        )
        if response.status_code == 200:
            print_success("按game_gid筛选成功")
            data = response.json()
            print_info(f"找到 {len(data['data']['templates'])} 个模板")

        # 测试按分类筛选
        print_info("测试按category筛选...")
        response = requests.get(
            f"{API_BASE_URL}/api/templates",
            params={"category": "用户行为"},
            timeout=10
        )
        if response.status_code == 200:
            print_success("按category筛选成功")
            data = response.json()
            print_info(f"找到 {len(data['data']['templates'])} 个模板")

        # 测试搜索
        print_info("测试关键词搜索...")
        response = requests.get(
            f"{API_BASE_URL}/api/templates",
            params={"search": "测试"},
            timeout=10
        )
        if response.status_code == 200:
            print_success("关键词搜索成功")
            data = response.json()
            print_info(f"找到 {len(data['data']['templates'])} 个模板")

        return True

    except requests.exceptions.RequestException as e:
        print_error(f"请求失败: {e}")
        return False


def main():
    """主测试函数"""
    print(f"\n{Colors.BOLD}Canvas Template APIs 自动化测试{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.END}\n")

    # 存储创建的模板ID，用于后续测试
    template_id = None
    cloned_template_id = None

    # 1. API健康检查
    if not test_api_health():
        print(f"\n{Colors.RED}{Colors.BOLD}API服务未运行，测试终止{Colors.END}")
        print_info("请先启动Flask服务器: python web_app.py")
        return False

    # 2. 创建模板
    template_id = test_create_template()
    if not template_id:
        print(f"\n{Colors.RED}{Colors.BOLD}模板创建失败，后续测试跳过{Colors.END}")

    # 3. 获取模板列表
    test_list_templates()

    # 4. 获取单个模板
    if template_id:
        test_get_template(template_id)

    # 5. 更新模板
    if template_id:
        test_update_template(template_id)

    # 6. 应用模板
    if template_id:
        test_apply_template(template_id)

    # 7. 克隆模板
    if template_id:
        cloned_template_id = test_clone_template(template_id)

    # 8. 获取分类列表
    test_get_categories()

    # 9. 筛选和搜索
    test_filter_and_search()

    # 10. 删除克隆的模板（清理）
    if cloned_template_id:
        print_info("清理测试数据：删除克隆的模板...")
        test_delete_template(cloned_template_id)

    # 11. 删除原始模板（清理）
    if template_id:
        print_info("清理测试数据：删除原始模板...")
        test_delete_template(template_id)

    # 总结
    print_section("测试总结")
    print_success("所有测试已完成！")
    print_info("如果所有测试都显示 ✓，说明API工作正常")
    print_info("如果有 ✗ 标记，请查看错误信息并修复问题")

    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被用户中断{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}测试过程中发生错误: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

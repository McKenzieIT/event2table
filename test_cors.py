#!/usr/bin/env python3
"""
测试 CORS 响应头
"""
import requests
from flask import Flask
from flask_cors import CORS

# 测试 OPTIONS 预检请求
def test_cors_preflight():
    """测试 CORS 预检请求"""
    url = "http://127.0.0.1:5001/api/graphql"

    # 模拟浏览器的 OPTIONS 预检请求
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization"
    }

    try:
        response = requests.options(url, headers=headers, timeout=2)

        print("=== CORS 预检请求测试 ===")
        print(f"状态码: {response.status_code}")
        print(f"\n响应头:")
        for key, value in response.headers.items():
            if key.lower().startswith('access-control'):
                print(f"  {key}: {value}")

        # 检查关键 CORS 头
        checks = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }

        print(f"\n验证结果:")
        for key, value in checks.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")

        if all(checks.values()):
            print("\n✅ CORS 配置正确！")
            return True
        else:
            print("\n⚠️ CORS 配置不完整")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Flask 服务器")
        print("请先启动后端: python3 web_app.py")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_actual_request():
    """测试实际的 POST 请求"""
    url = "http://127.0.0.1:5001/api/graphql"

    headers = {
        "Origin": "http://localhost:5173",
        "Content-Type": "application/json"
    }

    # 简单的 GraphQL 查询
    query = {
        "query": "query { games { id gid name } }"
    }

    try:
        response = requests.post(url, json=query, headers=headers, timeout=2)

        print("\n=== 实际 GraphQL 请求测试 ===")
        print(f"状态码: {response.status_code}")
        print(f"\n响应头:")
        for key, value in response.headers.items():
            if key.lower().startswith('access-control'):
                print(f"  {key}: {value}")

        if response.status_code == 200:
            print("\n✅ GraphQL 请求成功！")
            return True
        else:
            print(f"\n⚠️ GraphQL 请求失败: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到 Flask 服务器")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CORS 配置测试")
    print("=" * 60)
    print("\n请确保后端服务器正在运行:")
    print("  FLASK_ENV=development python3 web_app.py")
    print("\n按 Ctrl+C 停止测试\n")

    import time
    time.sleep(1)

    # 运行测试
    test_cors_preflight()
    test_actual_request()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

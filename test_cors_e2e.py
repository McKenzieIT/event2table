#!/usr/bin/env python3
"""
CORS 端到端测试
启动 Flask 测试服务器并验证 CORS 响应头
"""
import os
import sys
import time
import subprocess
import requests
import signal

# 设置开发模式
os.environ['FLASK_ENV'] = 'development'

def test_cors_with_server():
    """启动服务器并测试 CORS"""
    print("=" * 70)
    print("CORS 端到端测试")
    print("=" * 70)

    # 启动 Flask 服务器
    print("\n[1/4] 启动 Flask 服务器...")
    env = os.environ.copy()
    env['FLASK_ENV'] = 'development'
    env['FLASK_DEBUG'] = 'False'  # 禁用 reloader 避免子进程

    proc = subprocess.Popen(
        [sys.executable, 'web_app.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # 等待服务器启动
    print("  等待服务器启动...")
    time.sleep(5)

    # 检查服务器是否运行
    try:
        response = requests.get('http://127.0.0.1:5001/test', timeout=2)
        print(f"  ✅ 服务器已启动 (PID: {proc.pid})")
    except Exception as e:
        print(f"  ❌ 服务器启动失败: {e}")
        proc.terminate()
        return False

    # 测试 OPTIONS 预检请求
    print("\n[2/4] 测试 OPTIONS 预检请求...")
    try:
        headers = {
            'Origin': 'http://localhost:5173',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'
        }
        response = requests.options(
            'http://127.0.0.1:5001/api/graphql',
            headers=headers,
            timeout=2
        )

        print(f"  状态码: {response.status_code}")

        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }

        for key, value in cors_headers.items():
            status = "✅" if value else "❌"
            print(f"  {status} {key}: {value}")

        if not cors_headers['Access-Control-Allow-Origin']:
            print("\n❌ CORS 预检请求失败！")
            proc.terminate()
            return False

    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        proc.terminate()
        return False

    # 测试实际 GraphQL POST 请求
    print("\n[3/4] 测试 GraphQL POST 请求...")
    try:
        headers = {
            'Origin': 'http://localhost:5173',
            'Content-Type': 'application/json'
        }
        query = {
            'query': 'query { games { id gid name } }'
        }
        response = requests.post(
            'http://127.0.0.1:5001/api/graphql',
            json=query,
            headers=headers,
            timeout=5
        )

        print(f"  状态码: {response.status_code}")

        if response.status_code == 200:
            print(f"  ✅ GraphQL 请求成功")
            print(f"  响应包含 CORS 头: {response.headers.get('Access-Control-Allow-Origin', 'N/A')}")
        else:
            print(f"  ❌ GraphQL 请求失败: {response.status_code}")
            print(f"  响应: {response.text[:200]}")

    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        proc.terminate()
        return False

    # 测试其他 API 端点
    print("\n[4/4] 测试其他 API 端点...")
    try:
        response = requests.get(
            'http://127.0.0.1:5001/api/games',
            headers={'Origin': 'http://localhost:5173'},
            timeout=2
        )

        print(f"  GET /api/games: {response.status_code} ✅" if response.status_code == 200 else f"  GET /api/games: {response.status_code} ❌")
        print(f"  CORS 头: {response.headers.get('Access-Control-Allow-Origin', 'N/A')}")

    except Exception as e:
        print(f"  ❌ 请求失败: {e}")

    # 清理
    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)

    print("\n正在关闭服务器...")
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    print("✅ 服务器已关闭")
    return True

if __name__ == "__main__":
    try:
        success = test_cors_with_server()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)

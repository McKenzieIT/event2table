#!/usr/bin/env python3
"""
使用 test_client 测试 CORS
"""
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

# 添加一个简单的路由
@app.route('/api/test')
def test():
    return {'data': 'test'}

# 初始化 CORS
CORS(app, resources=r"/api/*", origins=["http://localhost:5173"])

# 测试
with app.test_client() as client:
    # OPTIONS 请求
    response = client.options('/api/test', headers={
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'GET'
    })

    print("=" * 70)
    print("Flask test_client CORS 测试")
    print("=" * 70)
    print(f"\nOPTIONS /api/test:")
    print(f"  状态码: {response.status_code}")
    print(f"\n响应头:")
    for key, value in response.headers:
        if 'access-control' in key.lower():
            print(f"  ✅ {key}: {value}")

    # POST 请求
    response = client.post('/api/test', headers={
        'Origin': 'http://localhost:5173'
    })

    print(f"\n\nPOST /api/test:")
    print(f"  状态码: {response.status_code}")
    print(f"\n响应头:")
    for key, value in response.headers:
        if 'access-control' in key.lower():
            print(f"  ✅ {key}: {value}")

    # 检查是否有 CORS 头
    has_cors = any('access-control' in key.lower()
                   for key in response.headers)
    print(f"\n{'✅ 发现 CORS 头' if has_cors else '❌ 未发现 CORS 头'}")
    print("=" * 70)

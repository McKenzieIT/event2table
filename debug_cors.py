#!/usr/bin/env python3
"""
调试 CORS 配置
"""
import os
os.environ['FLASK_ENV'] = 'development'

from web_app import app

print("=" * 70)
print("Flask 应用 CORS 调试")
print("=" * 70)

# 检查应用扩展
print("\n1. 应用扩展:")
for key, value in app.extensions.items():
    if 'cors' in key.lower():
        print(f"  ✅ {key}: {type(value).__name__}")
        if hasattr(value, 'resources'):
            print(f"     资源配置: {value.resources}")
    else:
        print(f"  - {key}: {type(value).__name__}")

# 检查所有路由
print("\n2. 所有路由:")
for rule in app.url_map.iter_rules():
    if '/api/' in rule.rule:
        print(f"  {rule.rule}: {rule.methods}")

# 测试一个简单的路由
print("\n3. 测试 CORS 响应头:")
with app.test_client() as client:
    # 测试 OPTIONS 请求
    response = client.options('/api/graphql', headers={
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'POST'
    })

    print(f"  状态码: {response.status_code}")
    print(f"  响应头:")
    for key, value in response.headers:
        if 'access-control' in key.lower():
            print(f"    {key}: {value}")

    # 检查是否有 CORS 头
    has_cors = any('access-control' in key.lower() for key in response.headers)
    if has_cors:
        print(f"\n  ✅ 发现 CORS 头")
    else:
        print(f"\n  ❌ 未发现 CORS 头")
        print(f"  所有响应头:")
        for key, value in response.headers:
            print(f"    {key}: {value}")

print("\n" + "=" * 70)

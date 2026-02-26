#!/usr/bin/env python3
"""
测试 CORS 是否被正确调用
"""
import os
import sys

# 设置开发模式
os.environ['FLASK_ENV'] = 'development'

# 打印调试信息
print("=" * 70)
print("CORS 初始化测试")
print("=" * 70)

# 检查环境变量
print(f"\n环境变量:")
print(f"  FLASK_ENV: {os.environ.get('FLASK_ENV')}")
print(f"  FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")

# 导入 Flask
from flask import Flask

# 创建测试应用
app = Flask(__name__)

# 导入 CORS
from flask_cors import CORS
print(f"\nflask-cors 版本: {CORS.__module__}")

# 尝试初始化 CORS
print(f"\n初始化 CORS...")
try:
    CORS(app, resources=r"/api/*", origins=["http://localhost:5173"])
    print("✅ CORS 初始化调用成功")
except Exception as e:
    print(f"❌ CORS 初始化失败: {e}")
    sys.exit(1)

# 检查应用扩展
print(f"\n应用扩展:")
for key in app.extensions.keys():
    print(f"  - {key}")

if 'cors' in app.extensions:
    print(f"\n✅ CORS 扩展已注册")
    print(f"  CORS 扩展: {app.extensions['cors']}")
else:
    print(f"\n❌ CORS 扩展未找到")

print("\n" + "=" * 70)

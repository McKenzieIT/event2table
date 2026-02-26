#!/usr/bin/env python3
"""
简单的 CORS 配置验证
"""
import os
import sys

# 设置开发模式
os.environ['FLASK_ENV'] = 'development'

# 导入 Flask 应用
from web_app import app, logger

def test_cors_config():
    """测试 CORS 配置是否正确加载"""
    print("=" * 60)
    print("CORS 配置验证")
    print("=" * 60)

    # 检查环境
    is_dev = os.environ.get('FLASK_ENV') == 'development' or os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"\n环境检测:")
    print(f"  FLASK_ENV: {os.environ.get('FLASK_ENV')}")
    print(f"  FLASK_DEBUG: {os.environ.get('FLASK_DEBUG')}")
    print(f"  IS_DEV: {is_dev}")

    # 检查 Flask-Cors 是否安装
    try:
        import flask_cors
        print(f"\n✅ flask-cors 已安装 (版本: {flask_cors.__version__})")
    except ImportError:
        print("\n❌ flask-cors 未安装")
        return False

    # 检查 CORS 是否在应用中配置
    # flask-cors 会在 app.extensions 中添加 'cors' 键
    if 'cors' in app.extensions:
        print("✅ CORS 已配置到 Flask 应用")
        cors_config = app.extensions['cors']
        print(f"  配置的资源数: {len(cors_config.resources)}")

        # 显示资源配置
        for resource, options in cors_config.resources.items():
            print(f"\n  资源: {resource}")
            print(f"    允许的源: {options.get('origins', 'N/A')}")
            print(f"    允许的方法: {options.get('methods', 'N/A')}")
    else:
        print("⚠️ CORS 未在应用 extensions 中找到")
        print("  这可能意味着 CORS 在测试上下文中未初始化")

    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    test_cors_config()

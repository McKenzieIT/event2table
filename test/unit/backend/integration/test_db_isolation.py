#!/usr/bin/env python3
"""测试数据库隔离机制"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 测试不同环境下的数据库路径
print("=" * 60)
print("测试数据库隔离机制")
print("=" * 60)
print()

# 测试1: 默认环境（生产）
print("1. 默认环境（生产）:")
from backend.core.config import get_db_path
db_path = get_db_path()
print(f"   数据库路径: {db_path}")
print(f"   文件名: {db_path.name}")
print()

# 测试2: 开发环境
print("2. 开发环境:")
os.environ["FLASK_ENV"] = "development"
# 重新导入以获取新的配置
import importlib
import backend.core.config
importlib.reload(backend.core.config)
from backend.core.config import get_db_path as get_db_path_dev
db_path_dev = get_db_path_dev()
print(f"   数据库路径: {db_path_dev}")
print(f"   文件名: {db_path_dev.name}")
print()

# 测试3: 测试环境
print("3. 测试环境:")
os.environ["FLASK_ENV"] = "testing"
importlib.reload(backend.core.config)
from backend.core.config import get_db_path as get_db_path_test
db_path_test = get_db_path_test()
print(f"   数据库路径: {db_path_test}")
print(f"   文件名: {db_path_test.name}")
print()

# 验证三个路径不同
print("验证:")
print(f"   生产数据库: {db_path}")
print(f"   开发数据库: {db_path_dev}")
print(f"   测试数据库: {db_path_test}")
print()

if db_path != db_path_dev and db_path != db_path_test and db_path_dev != db_path_test:
    print("✅ 数据库隔离机制正常工作！")
    print("   三个环境使用不同的数据库文件。")
else:
    print("❌ 数据库隔离机制存在问题！")
    print("   某些环境使用了相同的数据库文件。")

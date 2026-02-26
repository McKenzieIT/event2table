#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证DDD Infrastructure清理

检查：
1. infrastructure目录是否已删除
2. events_v2.py是否已删除
3. 是否有残留的import引用
4. 核心模块是否能正常导入
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_deleted_paths():
    """检查已删除的路径"""
    print("=" * 60)
    print("1. 检查已删除的路径")
    print("=" * 60)

    paths_to_check = [
        "backend/infrastructure",
        "backend/api/routes/events_v2.py",
        "backend/tests/unit/infrastructure",
        "backend/tests/integration/infrastructure",
    ]

    all_deleted = True
    for path in paths_to_check:
        full_path = project_root / path
        exists = full_path.exists()
        status = "❌ 仍存在" if exists else "✓ 已删除"
        print(f"  {status}: {path}")
        if exists:
            all_deleted = False

    print()
    return all_deleted


def check_imports():
    """检查是否有残留的infrastructure import"""
    print("=" * 60)
    print("2. 检查残留的infrastructure import")
    print("=" * 60)

    backend_dir = project_root / "backend"
    found_imports = []

    for py_file in backend_dir.rglob("*.py"):
        if "infrastructure" in str(py_file):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            if "from backend.infrastructure" in content or "import backend.infrastructure" in content:
                found_imports.append(py_file.relative_to(project_root))
        except Exception:
            pass

    if found_imports:
        print(f"  ❌ 发现 {len(found_imports)} 个文件仍引用infrastructure:")
        for file in found_imports:
            print(f"    - {file}")
        return False
    else:
        print("  ✓ 无残留的infrastructure import")

    print()
    return True


def check_core_imports():
    """检查核心模块导入"""
    print("=" * 60)
    print("3. 检查核心模块导入")
    print("=" * 60)

    modules_to_test = [
        ("API Routes", "backend.api.routes.events"),
        ("Repositories", "backend.models.repositories"),
        ("Services", "backend.services.events"),
        ("Models", "backend.models.entities"),
    ]

    all_ok = True
    for name, module_path in modules_to_test:
        try:
            __import__(module_path)
            print(f"  ✓ {name}: {module_path}")
        except Exception as e:
            print(f"  ❌ {name}: {module_path}")
            print(f"    错误: {e}")
            all_ok = False

    print()
    return all_ok


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("DDD Infrastructure 清理验证")
    print("=" * 60 + "\n")

    results = {
        "路径删除": check_deleted_paths(),
        "Import检查": check_imports(),
        "模块导入": check_core_imports(),
    }

    print("=" * 60)
    print("验证总结")
    print("=" * 60)

    for name, passed in results.items():
        status = "✓ 通过" if passed else "❌ 失败"
        print(f"  {status}: {name}")

    all_passed = all(results.values())
    print()

    if all_passed:
        print("🎉 所有验证通过！DDD Infrastructure清理成功。")
        return 0
    else:
        print("⚠️  部分验证失败，请检查上述问题。")
        return 1


if __name__ == "__main__":
    sys.exit(main())

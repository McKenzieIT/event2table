#!/usr/bin/env python3
"""
Test that init_db properly seeds default categories

This script creates a fresh test database and verifies that
categories are automatically seeded during initialization.
"""

import sys
import sqlite3
from pathlib import Path
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database import init_db
from backend.core.logging import get_logger

logger = get_logger(__name__)


def test_init_db_seeds_categories():
    """Test that init_db seeds default categories in a fresh database"""
    print("\n" + "=" * 60)
    print("TEST: init_db Seeds Default Categories")
    print("=" * 60)

    # Create a temporary test database
    temp_dir = tempfile.mkdtemp()
    test_db_path = Path(temp_dir) / "test_categories.db"

    try:
        print(f"\nCreating fresh database at: {test_db_path}")
        print("\nInitializing database with init_db()...")

        # Initialize the database (should seed categories)
        init_db(test_db_path)

        # Connect and check if categories exist
        conn = sqlite3.connect(str(test_db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM event_categories ORDER BY id")
        categories = cursor.fetchall()

        print(f"\n✅ Database initialized successfully")
        print(f"\nFound {len(categories)} categories:")

        if len(categories) < 8:
            print(f"\n❌ FAIL: Expected 8 categories, found {len(categories)}")
            return False

        for cat in categories:
            print(f"   - ID {cat['id']}: {cat['name']}")

        # Verify specific categories exist
        category_names = [cat['name'] for cat in categories]
        required_categories = [
            "登录/认证",
            "游戏进度",
            "经济/交易",
            "社交/聊天",
            "战斗/PVP",
            "系统",
            "充值/付费",
            "行为/点击"
        ]

        missing = [cat for cat in required_categories if cat not in category_names]
        if missing:
            print(f"\n❌ FAIL: Missing required categories: {missing}")
            return False

        print("\n✅ PASS: All 8 default categories seeded correctly")
        return True

    except Exception as e:
        print(f"\n❌ FAIL: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if test_db_path.exists():
            test_db_path.unlink()
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        print(f"\nCleaned up test database")


def test_init_db_skips_if_categories_exist():
    """Test that init_db doesn't re-seed if categories already exist"""
    print("\n" + "=" * 60)
    print("TEST: init_db Skips Seeding if Categories Exist")
    print("=" * 60)

    # Create a temporary test database
    temp_dir = tempfile.mkdtemp()
    test_db_path = Path(temp_dir) / "test_no_reseed.db"

    try:
        # Initialize once
        print(f"\nFirst initialization...")
        init_db(test_db_path)

        # Check category count
        conn = sqlite3.connect(str(test_db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM event_categories")
        count_after_first = cursor.fetchone()[0]
        print(f"   Categories after first init: {count_after_first}")

        # Add a custom category
        cursor.execute("INSERT INTO event_categories (name) VALUES (?)", ("Custom Category",))
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM event_categories")
        count_with_custom = cursor.fetchone()[0]
        print(f"   Categories after adding custom: {count_with_custom}")

        conn.close()

        # Initialize again (should not re-seed)
        print("\nSecond initialization (should skip seeding)...")
        init_db(test_db_path)

        # Check that custom category still exists and count hasn't changed
        conn = sqlite3.connect(str(test_db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM event_categories")
        count_after_second = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM event_categories WHERE name = ?", ("Custom Category",))
        custom_exists = cursor.fetchone() is not None

        conn.close()

        print(f"   Categories after second init: {count_after_second}")
        print(f"   Custom category exists: {custom_exists}")

        if count_after_second == count_with_custom and custom_exists:
            print("\n✅ PASS: init_db correctly skipped re-seeding")
            return True
        else:
            print("\n❌ FAIL: Categories were re-seeded or custom category was lost")
            return False

    except Exception as e:
        print(f"\n❌ FAIL: Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if test_db_path.exists():
            test_db_path.unlink()
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
        print(f"\nCleaned up test database")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("init_db Category Seeding Test Suite")
    print("=" * 60)

    results = {
        'test_init_db_seeds_categories': test_init_db_seeds_categories(),
        'test_init_db_skips_if_categories_exist': test_init_db_skips_if_categories_exist()
    }

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

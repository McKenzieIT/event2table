#!/usr/bin/env python3
"""
Test category seeding and event creation

This script verifies:
1. Categories are properly seeded
2. Events can be created with valid category_id
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.core.database.database import get_db_connection
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict, execute_write
from backend.core.logging import get_logger

logger = get_logger(__name__)


def test_categories():
    """Test that categories exist and are accessible"""
    print("\n" + "=" * 60)
    print("TEST 1: Verify Categories Exist")
    print("=" * 60)

    categories = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY id")

    if not categories:
        print("❌ FAIL: No categories found in database")
        return False

    print(f"✅ PASS: Found {len(categories)} categories:")
    for cat in categories:
        print(f"   - ID {cat['id']}: {cat['name']}")

    return True


def test_event_creation_with_category():
    """Test that events can be created with valid category_id"""
    print("\n" + "=" * 60)
    print("TEST 2: Event Creation with Valid Category")
    print("=" * 60)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get a test game or create one
        game = cursor.execute("SELECT * FROM games WHERE gid = 10000147").fetchone()

        if not game:
            # Create test game
            cursor.execute("""
                INSERT INTO games (gid, name, ods_db)
                VALUES (10000147, 'Test Game', 'test_ods')
            """)
            conn.commit()
            game = cursor.execute("SELECT * FROM games WHERE gid = 10000147").fetchone()
            print(f"   Created test game: ID {game['id']}")

        game_id = game['id']

        # Try to create an event with category_id = 1
        import time
        timestamp = int(time.time())

        test_event = {
            'game_id': game_id,
            'game_gid': 10000147,
            'event_name': f'test_category_event_{timestamp}',
            'event_name_cn': '测试分类事件',
            'category_id': 1,  # This should exist now
            'source_table': f'ieu_ods.ods_test_{timestamp}',
            'target_table': f'dwd.dwd_test_{timestamp}'
        }

        print(f"\n   Attempting to create event:")
        print(f"   - Category ID: {test_event['category_id']}")
        print(f"   - Event Name: {test_event['event_name']}")

        cursor.execute("""
            INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            test_event['game_id'],
            test_event['game_gid'],
            test_event['event_name'],
            test_event['event_name_cn'],
            test_event['category_id'],
            test_event['source_table'],
            test_event['target_table']
        ))

        conn.commit()
        event_id = cursor.lastrowid

        print(f"\n✅ PASS: Event created successfully with ID {event_id}")

        # Verify the event was created
        created_event = cursor.execute("SELECT * FROM log_events WHERE id = ?", (event_id,)).fetchone()
        category = cursor.execute("SELECT * FROM event_categories WHERE id = ?", (test_event['category_id'],)).fetchone()

        print(f"\n   Verification:")
        print(f"   - Event ID: {created_event['id']}")
        print(f"   - Event Name: {created_event['event_name']}")
        print(f"   - Category ID: {created_event['category_id']}")
        print(f"   - Category Name: {category['name']}")

        # Cleanup test event
        cursor.execute("DELETE FROM log_events WHERE id = ?", (event_id,))
        conn.commit()
        print(f"\n   Cleaned up test event")

        return True

    except Exception as e:
        print(f"\n❌ FAIL: Event creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


def test_invalid_category():
    """Test that event creation fails with invalid category_id"""
    print("\n" + "=" * 60)
    print("TEST 3: Event Creation with Invalid Category (Expected Failure)")
    print("=" * 60)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get a test game
        game = cursor.execute("SELECT * FROM games WHERE gid = 10000147").fetchone()

        if not game:
            print("   SKIP: No test game available")
            return True

        game_id = game['id']

        # Try to create an event with invalid category_id
        import time
        timestamp = int(time.time())

        test_event = {
            'game_id': game_id,
            'game_gid': 10000147,
            'event_name': f'test_invalid_category_{timestamp}',
            'event_name_cn': '测试无效分类',
            'category_id': 99999,  # Invalid category_id
            'source_table': f'ieu_ods.ods_invalid_{timestamp}',
            'target_table': f'dwd.dwd_invalid_{timestamp}'
        }

        print(f"\n   Attempting to create event with invalid category_id: {test_event['category_id']}")

        # This should fail due to foreign key constraint
        cursor.execute("""
            INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            test_event['game_id'],
            test_event['game_gid'],
            test_event['event_name'],
            test_event['event_name_cn'],
            test_event['category_id'],
            test_event['source_table'],
            test_event['target_table']
        ))

        conn.commit()

        print(f"\n❌ FAIL: Event creation should have failed with invalid category_id")
        return False

    except Exception as e:
        # Expected to fail due to foreign key constraint
        print(f"\n✅ PASS: Event creation correctly failed with error:")
        print(f"   {e}")
        return True

    finally:
        conn.close()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Category Seeding Verification Test Suite")
    print("=" * 60)

    results = {
        'test_categories': test_categories(),
        'test_event_creation': test_event_creation_with_category(),
        'test_invalid_category': test_invalid_category()
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

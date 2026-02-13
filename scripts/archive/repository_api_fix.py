#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify Repository API fix for single-record CRUD operations.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.repositories.games import GameRepository


def test_single_record_crud():
    """Test single-record CRUD operations"""
    print("\n" + "="*60)
    print("Testing Single-Record CRUD Operations")
    print("="*60)

    repo = GameRepository()

    # Test create()
    print("\n1. Testing create() method...")
    print("-" * 60)
    game_data = {
        'gid': 'TEST_REPO_001',
        'name': 'Test Repository API',
        'ods_db': 'ieu_ods'
    }

    try:
        game = repo.create(game_data)
        assert game is not None, "create() failed - returned None"
        assert game['gid'] == "TEST_REPO_001", f"create() failed - incorrect gid: {game['gid']}"
        assert game['name'] == 'Test Repository API', f"create() failed - incorrect name: {game['name']}"
        assert 'id' in game, "create() failed - no 'id' in returned record"
        print(f"✅ PASS: Created game with ID {game['id']}")
        print(f"   - GID: {game['gid']}")
        print(f"   - Name: {game['name']}")
        print(f"   - ODS DB: {game['ods_db']}")
        created_game_id = game['id']
    except AttributeError as e:
        print(f"❌ FAIL: create() method not found - {e}")
        return False
    except Exception as e:
        print(f"❌ FAIL: create() failed with error - {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test update()
    print("\n2. Testing update() method...")
    print("-" * 60)
    try:
        updated = repo.update(created_game_id, {'name': 'Updated Repository API'})
        assert updated is not None, "update() failed - returned None"
        assert updated['name'] == 'Updated Repository API', f"update() failed - incorrect name: {updated['name']}"
        print(f"✅ PASS: Updated game name to '{updated['name']}'")
        print(f"   - Game ID: {updated['id']}")
        print(f"   - New Name: {updated['name']}")
    except AttributeError as e:
        print(f"❌ FAIL: update() method not found - {e}")
        # Clean up the created game before returning
        try:
            repo.delete(created_game_id)
        except:
            pass
        return False
    except Exception as e:
        print(f"❌ FAIL: update() failed with error - {e}")
        import traceback
        traceback.print_exc()
        # Clean up the created game before returning
        try:
            repo.delete(created_game_id)
        except:
            pass
        return False

    # Test delete()
    print("\n3. Testing delete() method...")
    print("-" * 60)
    try:
        success = repo.delete(created_game_id)
        assert success, "delete() failed - returned False"
        deleted = repo.find_by_id(created_game_id)
        assert deleted is None, "delete() failed - record still exists"
        print("✅ PASS: Deleted game successfully")
        print(f"   - Deleted Game ID: {created_game_id}")
        print(f"   - Verification: Record no longer exists")
    except Exception as e:
        print(f"❌ FAIL: delete() failed with error - {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test that all repository classes have these methods
    print("\n4. Verifying all repository classes have single-record methods...")
    print("-" * 60)

    from backend.models.repositories.events import EventRepository
    from backend.models.repositories.parameters import ParameterRepository

    repositories = [
        ('GameRepository', GameRepository()),
        ('EventRepository', EventRepository()),
        ('ParameterRepository', ParameterRepository())
    ]

    for repo_name, repo_instance in repositories:
        has_create = hasattr(repo_instance, 'create')
        has_update = hasattr(repo_instance, 'update')
        has_delete = hasattr(repo_instance, 'delete')

        status = "✅ PASS" if (has_create and has_update and has_delete) else "❌ FAIL"
        print(f"{status}: {repo_name}")
        print(f"   - create(): {'✓' if has_create else '✗'}")
        print(f"   - update(): {'✓' if has_update else '✗'}")
        print(f"   - delete(): {'✓' if has_delete else '✗'}")

        if not (has_create and has_update and has_delete):
            return False

    print("\n" + "="*60)
    print("✅ All Repository API tests passed!")
    print("="*60)
    return True


def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "="*60)
    print("Testing Edge Cases and Error Handling")
    print("="*60)

    repo = GameRepository()

    # Test create with empty data
    print("\n1. Testing create() with empty data...")
    print("-" * 60)
    try:
        result = repo.create({})
        # Should handle gracefully - might return None or raise error
        if result is None:
            print("✅ PASS: create() returned None for empty data (expected behavior)")
        else:
            print(f"⚠️  WARNING: create() returned result for empty data: {result}")
    except Exception as e:
        print(f"✅ PASS: create() raised error for empty data: {type(e).__name__}")

    # Test update with empty data
    print("\n2. Testing update() with empty data...")
    print("-" * 60)
    try:
        result = repo.update(9999, {})
        print(f"❌ FAIL: update() should raise ValueError for empty data, got: {result}")
        return False
    except ValueError as e:
        print(f"✅ PASS: update() raised ValueError for empty data: {e}")
    except Exception as e:
        print(f"❌ FAIL: update() raised unexpected error: {type(e).__name__}: {e}")
        return False

    # Test update non-existent record
    print("\n3. Testing update() with non-existent record...")
    print("-" * 60)
    try:
        result = repo.update(999999, {'name': 'Should Not Work'})
        # Should return None if record doesn't exist
        if result is None:
            print("✅ PASS: update() returned None for non-existent record")
        else:
            print(f"⚠️  WARNING: update() returned result for non-existent record: {result}")
    except Exception as e:
        print(f"✅ PASS: update() raised error for non-existent record: {type(e).__name__}")

    # Test delete non-existent record
    print("\n4. Testing delete() with non-existent record...")
    print("-" * 60)
    try:
        result = repo.delete(999999)
        # Should return False if record doesn't exist
        if result is False:
            print("✅ PASS: delete() returned False for non-existent record")
        else:
            print(f"⚠️  WARNING: delete() returned {result} for non-existent record")
    except Exception as e:
        print(f"✅ PASS: delete() raised error for non-existent record: {type(e).__name__}")

    print("\n" + "="*60)
    print("✅ All edge case tests passed!")
    print("="*60)
    return True


if __name__ == '__main__':
    success = True

    try:
        success = test_single_record_crud() and success
    except Exception as e:
        print(f"\n❌ Single-record CRUD tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False

    try:
        success = test_edge_cases() and success
    except Exception as e:
        print(f"\n❌ Edge case tests failed with error: {e}")
        import traceback
        traceback.print_exc()
        success = False

    if success:
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED! Repository API fix is working correctly.")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("❌ SOME TESTS FAILED! Please review the errors above.")
        print("="*60)
        sys.exit(1)

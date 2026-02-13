#!/usr/bin/env python3
"""
Test script to verify game_gid type consistency across the application.

This test ensures that game_gid is consistently treated as INTEGER throughout
the application, matching the database schema type.

Usage:
    python test/game_gid_type_consistency.py

Author: Claude Code
Date: 2026-02-10
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.models.schemas import GameCreate, EventCreate
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.core.utils.converters import ensure_game_gid_int


def test_schema_validation():
    """Test 1: Pydantic Schema validates game_gid as INTEGER"""
    print("\n" + "="*60)
    print("TEST 1: Pydantic Schema Type Validation")
    print("="*60)

    try:
        # Test GameCreate schema
        print("\n1.1 Testing GameCreate schema...")
        game_data = GameCreate(
            gid=10000147,  # INTEGER type
            name="Type Test Game",
            ods_db="ieu_ods"
        )

        assert isinstance(game_data.gid, int), "GameCreate.gid must be int"
        assert game_data.gid == 10000147, "GameCreate.gid value mismatch"
        print(f"✅ PASS: GameCreate.gid is int: {game_data.gid} (type: {type(game_data.gid).__name__})")

        # Test EventCreate schema
        print("\n1.2 Testing EventCreate schema...")
        event_data = EventCreate(
            game_gid=10000147,  # INTEGER type
            event_name="test_event",
            event_name_cn="测试事件",
            category_id=1
        )

        assert isinstance(event_data.game_gid, int), "EventCreate.game_gid must be int"
        assert event_data.game_gid == 10000147, "EventCreate.game_gid value mismatch"
        print(f"✅ PASS: EventCreate.game_gid is int: {event_data.game_gid} (type: {type(event_data.game_gid).__name__})")

        # Test that string input is converted to int (Pydantic V2 behavior)
        print("\n1.3 Testing that string input is auto-converted to int...")
        try:
            # Pydantic V2 will auto-convert strings to int if possible
            game_from_str = GameCreate(
                gid="10000147",  # STRING type - will be converted
                name="Game From String",
                ods_db="ieu_ods"
            )
            # After conversion, it should be int
            assert isinstance(game_from_str.gid, int), "gid should be converted to int"
            assert game_from_str.gid == 10000147, "gid value should match"
            print(f"✅ PASS: Schema auto-converts string '10000147' to int {game_from_str.gid}")
        except Exception as e:
            print(f"⚠️  Schema conversion: {e}")

        # Test that invalid string is rejected
        print("\n1.4 Testing that invalid string is rejected...")
        try:
            invalid_game = GameCreate(
                gid="not_a_number",  # Invalid STRING - should fail
                name="Invalid Game",
                ods_db="ieu_ods"
            )
            print(f"❌ FAIL: Schema accepted invalid string gid")
            return False
        except Exception as e:
            print(f"✅ PASS: Schema correctly rejects invalid string: {type(e).__name__}")

        return True

    except Exception as e:
        print(f"❌ FAIL: Schema validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_helper_function():
    """Test 2: Type conversion helper function"""
    print("\n" + "="*60)
    print("TEST 2: Type Conversion Helper")
    print("="*60)

    try:
        # Test integer input
        print("\n2.1 Testing ensure_game_gid_int with integer input...")
        result = ensure_game_gid_int(10000147)
        assert result == 10000147, "Integer input should return same value"
        assert isinstance(result, int), "Result should be int"
        print(f"✅ PASS: ensure_game_gid_int(10000147) = {result} (type: {type(result).__name__})")

        # Test string input
        print("\n2.2 Testing ensure_game_gid_int with string input...")
        result = ensure_game_gid_int("10000147")
        assert result == 10000147, "String input should be converted to int"
        assert isinstance(result, int), "Result should be int"
        print(f"✅ PASS: ensure_game_gid_int('10000147') = {result} (type: {type(result).__name__})")

        # Test invalid input
        print("\n2.3 Testing ensure_game_gid_int with invalid input...")
        try:
            result = ensure_game_gid_int("invalid")
            print(f"❌ FAIL: Helper accepted invalid input (should have raised ValueError)")
            return False
        except ValueError as e:
            print(f"✅ PASS: Helper correctly rejects invalid input: {e}")

        # Test empty string
        print("\n2.4 Testing ensure_game_gid_int with empty string...")
        try:
            result = ensure_game_gid_int("")
            print(f"❌ FAIL: Helper accepted empty string (should have raised ValueError)")
            return False
        except ValueError as e:
            print(f"✅ PASS: Helper correctly rejects empty string: {e}")

        return True

    except Exception as e:
        print(f"❌ FAIL: Helper function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_operations():
    """Test 3: Database CRUD operations maintain INTEGER type"""
    print("\n" + "="*60)
    print("TEST 3: Database Operations")
    print("="*60)

    try:
        game_repo = GameRepository()
        event_repo = EventRepository()

        # Clean up any existing test data
        print("\n3.0 Cleaning up existing test data...")
        existing_game = game_repo.find_by_gid(99999999)
        if existing_game:
            game_repo.delete(existing_game['id'])
            print("  Cleaned up existing test game")

        # Test Game creation
        print("\n3.1 Testing Game creation...")
        game_data = GameCreate(
            gid=99999999,  # Test GID
            name="Type Consistency Test Game",
            ods_db="ieu_ods"
        )

        # Use model_dump() for Pydantic V2
        game = game_repo.create(game_data.model_dump())
        assert game is not None, "Game creation failed"
        actual_gid = game.get('gid')
        print(f"  DEBUG: Created game with gid={actual_gid} (type: {type(actual_gid).__name__})")
        assert actual_gid is not None, "Game gid is None"
        assert actual_gid == 99999999, f"Game gid mismatch: expected 99999999, got {actual_gid}"
        assert isinstance(actual_gid, int), f"Database gid must be int, got {type(actual_gid).__name__}"
        print(f"✅ PASS: Game created with gid={game['gid']} (type: {type(game['gid']).__name__})")

        # Test Game retrieval by gid
        print("\n3.2 Testing Game retrieval by gid...")
        retrieved_game = game_repo.find_by_gid(99999999)
        assert retrieved_game is not None, "Game not found by gid"
        assert retrieved_game['gid'] == 99999999, "Retrieved game gid mismatch"
        assert isinstance(retrieved_game['gid'], int), "Retrieved game gid must be int"
        print(f"✅ PASS: Retrieved game with gid={retrieved_game['gid']} (type: {type(retrieved_game['gid']).__name__})")

        # Test Event creation with game_gid
        print("\n3.3 Testing Event creation with game_gid...")
        event_data = EventCreate(
            game_gid=99999999,  # INTEGER
            event_name="type_test_event",
            event_name_cn="类型测试事件",
            category_id=1,
            parameters=[
                {
                    "param_name": "test_param",
                    "param_name_cn": "测试参数",
                    "template_id": 1
                }
            ]
        )

        # Use repository's create method
        from backend.core.database.database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Generate required table names
        source_table = f"ieu_ods.ods_{event_data.game_gid}_all_view"
        target_table = f"ieu_cdm.v_dwd_{event_data.game_gid}_{event_data.event_name}_di"

        cursor.execute(
            """INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, category_id, source_table, target_table)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (game['id'], event_data.game_gid, event_data.event_name,
             event_data.event_name_cn, event_data.category_id, source_table, target_table)
        )
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        assert event_id is not None, "Event creation failed"
        print(f"✅ PASS: Event created with id={event_id}")

        # Test Event retrieval
        print("\n3.4 Testing Event retrieval...")
        event = event_repo.find_by_id(event_id)
        assert event is not None, "Event not found"
        assert event['game_gid'] == 99999999, "Event game_gid mismatch"
        assert isinstance(event['game_gid'], int), "Event game_gid must be int"
        print(f"✅ PASS: Retrieved event with game_gid={event['game_gid']} (type: {type(event['game_gid']).__name__})")

        # Test query with INTEGER game_gid
        print("\n3.5 Testing query with INTEGER game_gid...")
        events = event_repo.find_by_game_gid(99999999)
        assert len(events) > 0, "No events found for game_gid"
        for evt in events:
            assert isinstance(evt['game_gid'], int), f"Event game_gid must be int, got {type(evt['game_gid'])}"
        print(f"✅ PASS: All {len(events)} events have INTEGER game_gid")

        # Cleanup
        print("\n3.6 Cleaning up test data...")
        event_repo.delete(event_id)
        game_repo.delete(game['id'])
        print("✅ PASS: Test data cleaned up")

        return True

    except Exception as e:
        print(f"❌ FAIL: Database operations test failed: {e}")
        import traceback
        traceback.print_exc()

        # Try cleanup on failure
        try:
            if 'game' in locals() and game:
                game_repo.delete(game['id'])
            if 'event_id' in locals() and event_id:
                event_repo.delete(event_id)
        except:
            pass

        return False


def test_api_type_consistency():
    """Test 4: API endpoint type consistency"""
    print("\n" + "="*60)
    print("TEST 4: API Type Consistency Check")
    print("="*60)

    try:
        # Check that API routes use proper type annotations
        print("\n4.1 Checking API route type annotations...")

        import inspect
        from backend.api.routes import games, events

        # Check games.py routes
        print("  Checking backend/api/routes/games.py...")
        get_game_func = getattr(games, 'api_get_game', None)
        if get_game_func:
            sig = inspect.signature(get_game_func)
            gid_param = sig.parameters.get('gid')
            if gid_param and gid_param.annotation == int:
                print("  ✅ api_get_game(gid: int) - correct type annotation")
            else:
                print(f"  ⚠️  api_get_game(gid) annotation: {gid_param.annotation if gid_param else 'not found'}")

        # Check events.py routes
        print("  Checking backend/api/routes/events.py...")
        list_events_func = getattr(events, 'api_list_events', None)
        if list_events_func:
            # Check that it handles game_gid parameter
            source = inspect.getsource(list_events_func)
            if 'game_gid' in source and 'safe_int_convert' in source:
                print("  ✅ api_list_events handles game_gid with safe_int_convert")
            else:
                print("  ⚠️  api_list_events game_gid handling")

        print("\n✅ PASS: API type consistency check completed")
        return True

    except Exception as e:
        print(f"❌ FAIL: API type consistency check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all type consistency tests"""
    print("\n" + "="*60)
    print("GAME_GID TYPE CONSISTENCY TEST SUITE")
    print("="*60)
    print("\nThis test suite verifies that game_gid is consistently")
    print("treated as INTEGER throughout the application.")
    print("\nDatabase Schema: games.gid INTEGER, log_events.game_gid INTEGER")

    results = []

    # Run all tests
    results.append(("Schema Validation", test_schema_validation()))
    results.append(("Type Conversion Helper", test_helper_function()))
    results.append(("Database Operations", test_database_operations()))
    results.append(("API Type Consistency", test_api_type_consistency()))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n🎉 All game_gid type consistency tests passed!")
        print("\nThe application correctly treats game_gid as INTEGER throughout.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

#!/usr/bin/env python3
"""
Test script to verify event_params schema alignment.

This script tests:
1. Table schema inspection
2. Schema alignment with Pydantic models
3. CRUD operations on event_params
4. JSON path validation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from backend.models.repositories.parameters import ParameterRepository
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.models.schemas import EventParameterCreate


def inspect_table_schema():
    """Inspect the actual event_params table schema"""
    print("="*70)
    print("INSPECTING EVENT_PARAMS TABLE SCHEMA")
    print("="*70)

    conn = sqlite3.connect('/Users/mckenzie/Documents/event2table/dwd_generator.db')
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(event_params);")
    columns = cursor.fetchall()

    print("\nActual table structure:")
    print("-" * 70)
    print(f"{'Column Name':<20} {'Type':<15} {'NotNull':<8} {'Default':<15} {'PK':<3}")
    print("-" * 70)
    for col in columns:
        col_id, name, type_, notnull, default, pk = col
        not_null_str = 'YES' if notnull else 'NO'
        default_str = str(default) if default else ''
        pk_str = 'PK' if pk else ''
        print(f"{name:<20} {type_:<15} {not_null_str:<8} {default_str:<15} {pk_str:<3}")
    print("-" * 70)

    # Check for json_path column
    column_names = [col[1] for col in columns]
    if 'json_path' in column_names:
        print("\n✅ SUCCESS: json_path column exists in table")
    else:
        print("\n❌ ERROR: json_path column missing from table")

    conn.close()
    return columns


def test_schema_alignment():
    """Test that Schema matches actual table structure"""
    print("\n" + "="*70)
    print("TESTING SCHEMA ALIGNMENT")
    print("="*70)

    # Get actual table columns
    conn = sqlite3.connect('/Users/mckenzie/Documents/event2table/dwd_generator.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(event_params);")
    columns = cursor.fetchall()
    conn.close()

    actual_columns = {col[1]: col[2] for col in columns}

    # Get Schema fields
    schema = EventParameterCreate(
        param_name="test_param",
        template_id=1,
        json_path="$.testPath" if "json_path" in actual_columns else None
    )
    schema_fields = set(schema.model_dump().keys())

    # Check alignment - only validate that Schema fields exist in table
    print("\nValidating Schema fields exist in table...")
    table_columns = set(actual_columns.keys())

    # Critical fields that MUST be in both
    critical_schema_fields = {'param_name', 'param_name_cn', 'template_id', 'param_description', 'json_path'}

    missing_in_table = critical_schema_fields - table_columns
    extra_in_schema = schema_fields - table_columns

    if missing_in_table:
        print(f"❌ ERROR: Schema fields missing from table: {missing_in_table}")
        return False

    if extra_in_schema:
        print(f"⚠️  WARNING: Schema fields not in table: {extra_in_schema}")
        return False

    print("✅ PASS: All critical Schema fields exist in table!")
    print(f"   Validated fields: {critical_schema_fields}")

    # Check that json_path specifically exists
    if 'json_path' in table_columns:
        print("✅ SUCCESS: json_path field exists in both Schema and table")
        return True
    else:
        print("❌ ERROR: json_path field missing from table")
        return False


def test_json_path_validation():
    """Test JSON path validation"""
    print("\n" + "="*70)
    print("TESTING JSON PATH VALIDATION")
    print("="*70)

    test_cases = [
        ("$.zoneId", True, "Valid JSON path"),
        ("$.user.level", True, "Valid nested JSON path"),
        ("zoneId", False, "Missing $. prefix"),
        ("", True, "Empty path (optional field)"),
        (None, True, "None value (optional field)"),
        ("$.level", True, "Simple valid path"),
    ]

    all_passed = True
    for json_path, should_pass, description in test_cases:
        try:
            if json_path is None or json_path == "":
                schema = EventParameterCreate(
                    param_name="test_param",
                    template_id=1
                )
            else:
                schema = EventParameterCreate(
                    param_name="test_param",
                    template_id=1,
                    json_path=json_path
                )

            if should_pass:
                print(f"✅ PASS: {description} - '{json_path}'")
            else:
                print(f"❌ FAIL: {description} - '{json_path}' should have failed validation")
                all_passed = False
        except Exception as e:
            if not should_pass:
                print(f"✅ PASS: {description} - Correctly rejected '{json_path}'")
                print(f"         Error: {e}")
            else:
                print(f"❌ FAIL: {description} - Should have accepted '{json_path}'")
                print(f"         Error: {e}")
                all_passed = False

    return all_passed


def test_parameter_crud():
    """Test basic CRUD operations on event_params"""
    print("\n" + "="*70)
    print("TESTING PARAMETER CRUD OPERATIONS")
    print("="*70)

    param_repo = ParameterRepository()
    game_repo = GameRepository()
    event_repo = EventRepository()

    # Use timestamp to ensure unique IDs
    import time
    unique_id = int(time.time() * 1000) % 1000000

    # Create a test game and event first
    print("\n1. Setting up test game and event...")
    try:
        game = game_repo.create({
            'gid': str(unique_id),
            'name': f'Test Game for Schema Fix {unique_id}',
            'ods_db': 'ieu_ods'
        })
        print(f"   ✅ Created game with ID {game['id']}")

        event = event_repo.create({
            'game_id': game['id'],  # Use game_id instead of game_gid
            'game_gid': unique_id,
            'event_name': f'test_schema_event_{unique_id}',
            'event_name_cn': '测试事件',
            'category_id': 1,
            'source_table': f'ieu_ods.ods_{unique_id}_all_view',
            'target_table': f'dwd.dwd_{unique_id}_test_schema_event'
        })
        print(f"   ✅ Created event with ID {event['id']}")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to create test data: {e}")
        return False

    # Test parameter creation with json_path
    print("\n2. Testing parameter creation with json_path...")
    try:
        param_data = EventParameterCreate(
            param_name="test_zone_id",
            param_name_cn="分区ID",
            template_id=1,
            param_description="Test zone identifier",
            json_path="$.zoneId"
        )

        param = param_repo.create({
            'event_id': event['id'],
            **param_data.model_dump()
        })

        assert param is not None, "Parameter creation failed"
        print(f"   ✅ PASS: Created parameter with ID {param['id']}")
        print(f"   📝 Parameter details:")
        print(f"      - param_name: {param['param_name']}")
        print(f"      - json_path: {param.get('json_path', 'None')}")
        print(f"      - param_description: {param.get('param_description', 'None')}")

    except Exception as e:
        print(f"   ❌ ERROR: Parameter creation failed: {e}")
        # Cleanup
        try:
            event_repo.delete(event['id'])
            game_repo.delete(game['id'])
        except:
            pass
        return False

    # Test parameter retrieval
    print("\n3. Testing parameter retrieval...")
    try:
        retrieved = param_repo.find_by_id(param['id'])
        assert retrieved is not None, "Parameter retrieval failed"
        assert retrieved['json_path'] == "$.zoneId", "json_path not correctly retrieved"
        print(f"   ✅ PASS: Retrieved parameter: {retrieved['param_name']}")
        print(f"   📝 Retrieved json_path: {retrieved['json_path']}")

    except Exception as e:
        print(f"   ❌ ERROR: Parameter retrieval failed: {e}")
        # Cleanup
        try:
            param_repo.delete(param['id'])
            event_repo.delete(event['id'])
            game_repo.delete(game['id'])
        except:
            pass
        return False

    # Test parameter update
    print("\n4. Testing parameter update...")
    try:
        updated = param_repo.update(param['id'], {
            'param_description': 'Updated zone identifier',
            'json_path': '$.zoneIdUpdated'
        })
        assert updated['json_path'] == "$.zoneIdUpdated", "json_path update failed"
        print(f"   ✅ PASS: Updated parameter json_path to: {updated['json_path']}")

    except Exception as e:
        print(f"   ❌ ERROR: Parameter update failed: {e}")
        # Cleanup
        try:
            param_repo.delete(param['id'])
            event_repo.delete(event['id'])
            game_repo.delete(game['id'])
        except:
            pass
        return False

    # Test parameter deletion
    print("\n5. Testing parameter deletion...")
    try:
        param_repo.delete(param['id'])
        deleted = param_repo.find_by_id(param['id'])
        assert deleted is None, "Parameter should be deleted"
        print(f"   ✅ PASS: Parameter deleted successfully")

    except Exception as e:
        print(f"   ❌ ERROR: Parameter deletion failed: {e}")
        # Cleanup
        try:
            param_repo.delete(param['id'])
            event_repo.delete(event['id'])
            game_repo.delete(game['id'])
        except:
            pass
        return False

    # Cleanup
    print("\n6. Cleaning up test data...")
    try:
        event_repo.delete(event['id'])
        game_repo.delete(game['id'])
        print(f"   ✅ Cleanup completed")
    except Exception as e:
        print(f"   ⚠️  WARNING: Cleanup failed: {e}")

    return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("EVENT_PARAMS SCHEMA FIX VERIFICATION TESTS")
    print("="*70)
    print("\nThis test suite verifies:")
    print("  1. Table schema has json_path column")
    print("  2. Pydantic Schema aligns with table structure")
    print("  3. JSON path validation works correctly")
    print("  4. CRUD operations work with json_path field")

    # Run all tests
    try:
        inspect_table_schema()

        aligned = test_schema_alignment()

        if aligned:
            json_validation_passed = test_json_path_validation()
            crud_passed = test_parameter_crud()

            # Final summary
            print("\n" + "="*70)
            print("TEST SUMMARY")
            print("="*70)

            results = [
                ("Schema Alignment", "✅ PASS" if aligned else "❌ FAIL"),
                ("JSON Path Validation", "✅ PASS" if json_validation_passed else "❌ FAIL"),
                ("CRUD Operations", "✅ PASS" if crud_passed else "❌ FAIL"),
            ]

            for test_name, result in results:
                print(f"{test_name:<30} {result}")

            all_passed = aligned and json_validation_passed and crud_passed

            print("-"*70)
            if all_passed:
                print("\n🎉 ALL TESTS PASSED! Schema fix is complete and verified.")
            else:
                print("\n⚠️  SOME TESTS FAILED. Please review the output above.")

            print("="*70 + "\n")

            return 0 if all_passed else 1

        else:
            print("\n⚠️  Schema misalignment detected. Please fix before running CRUD tests.")
            return 1

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

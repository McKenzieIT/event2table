#!/usr/bin/env python3
"""
Test script to verify HQL Generator functionality and output format.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_event_model():
    """Test Event model to check if alias field exists"""
    print("\n" + "="*80)
    print("TEST 1: Event Model - Check for 'alias' field")
    print("="*80)

    try:
        from backend.services.hql.models.event import Event

        # Check Event dataclass fields
        import dataclasses
        fields = [f.name for f in dataclasses.fields(Event)]

        print(f"\nEvent model fields: {fields}")

        if 'alias' in fields:
            print("✅ PASS: Event model has 'alias' field")
            return True
        else:
            print("❌ FAIL: Event model missing 'alias' field")
            print("   Current fields:", fields)
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_event_creation_without_alias():
    """Test creating Event without alias (should work)"""
    print("\n" + "="*80)
    print("TEST 2: Create Event WITHOUT alias")
    print("="*80)

    try:
        from backend.services.hql.models.event import Event

        event = Event(
            name="login",
            table_name="ieu_ods.ods_10000147_all_view"
        )

        print(f"\n✅ PASS: Created Event without alias")
        print(f"   Event: {event}")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_event_creation_with_alias():
    """Test creating Event with alias (will fail if alias field missing)"""
    print("\n" + "="*80)
    print("TEST 3: Create Event WITH alias")
    print("="*80)

    try:
        from backend.services.hql.models.event import Event

        event = Event(
            name="login",
            table_name="ieu_ods.ods_10000147_all_view",
            alias="e1"
        )

        print(f"\n✅ PASS: Created Event with alias")
        print(f"   Event: {event}")
        return True

    except TypeError as e:
        if "got an unexpected keyword argument 'alias'" in str(e):
            print(f"❌ FAIL: Event model missing 'alias' parameter")
            print(f"   Error: {e}")
            return False
        else:
            raise
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hql_generator_single_mode():
    """Test HQL generator in single mode"""
    print("\n" + "="*80)
    print("TEST 4: HQL Generator - Single Mode")
    print("="*80)

    try:
        from backend.services.hql.core.generator import HQLGenerator
        from backend.services.hql.models.event import Event, Field

        generator = HQLGenerator()

        event = Event(
            name="login",
            table_name="ieu_ods.ods_10000147_all_view"
        )

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId")
        ]

        hql = generator.generate(
            events=[event],
            fields=fields,
            conditions=[],
            mode="single"
        )

        print(f"\n✅ PASS: Generated HQL in single mode")
        print(f"\nGenerated HQL ({len(hql)} characters):")
        print("-"*80)
        print(hql)
        print("-"*80)

        # Check what keywords are present
        keywords_found = []
        if "CREATE TABLE" in hql.upper():
            keywords_found.append("CREATE TABLE")
        if "CREATE VIEW" in hql.upper():
            keywords_found.append("CREATE VIEW")
        if "INSERT OVERWRITE" in hql.upper():
            keywords_found.append("INSERT OVERWRITE")
        if "SELECT" in hql.upper():
            keywords_found.append("SELECT")
        if "FROM" in hql.upper():
            keywords_found.append("FROM")

        print(f"\nKeywords found: {', '.join(keywords_found)}")

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hql_generator_join_mode():
    """Test HQL generator in join mode"""
    print("\n" + "="*80)
    print("TEST 5: HQL Generator - Join Mode (requires alias)")
    print("="*80)

    try:
        from backend.services.hql.core.generator import HQLGenerator
        from backend.services.hql.models.event import Event, Field

        generator = HQLGenerator()

        # Try with alias (will fail if alias field missing)
        try:
            event_a = Event(
                name="login_a",
                table_name="ieu_ods.ods_10000147_all_view",
                alias="a"
            )
            event_b = Event(
                name="login_b",
                table_name="ieu_ods.ods_10000148_all_view",
                alias="b"
            )
        except TypeError as e:
            if "alias" in str(e):
                print(f"❌ FAIL: Cannot create Events with alias - alias field missing")
                return False
            else:
                raise

        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId")
        ]

        hql = generator.generate(
            events=[event_a, event_b],
            fields=fields,
            conditions=[],
            mode="join",
            join_config={
                "type": "INNER",
                "conditions": [
                    {
                        "left_event": "login_a",
                        "left_field": "role_id",
                        "right_event": "login_b",
                        "right_field": "role_id",
                        "operator": "="
                    }
                ],
                "use_aliases": True
            }
        )

        print(f"\n✅ PASS: Generated HQL in join mode")
        print(f"\nGenerated HQL ({len(hql)} characters):")
        print("-"*80)
        print(hql)
        print("-"*80)
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests"""
    print("\n" + "="*80)
    print("HQL GENERATOR VERIFICATION TEST SUITE")
    print("="*80)
    print(f"Project: event2table")
    print(f"Date: {__import__('datetime').datetime.now().isoformat()}")

    results = {
        "passed": [],
        "failed": []
    }

    # Test 1: Check Event model for alias field
    if test_event_model():
        results["passed"].append("Event model has alias field")
    else:
        results["failed"].append("Event model missing alias field")

    # Test 2: Create Event without alias
    if test_event_creation_without_alias():
        results["passed"].append("Create Event without alias")
    else:
        results["failed"].append("Create Event without alias")

    # Test 3: Create Event with alias
    if test_event_creation_with_alias():
        results["passed"].append("Create Event with alias")
    else:
        results["failed"].append("Create Event with alias - ISSUE CONFIRMED")

    # Test 4: HQL Generator single mode
    if test_hql_generator_single_mode():
        results["passed"].append("HQL Generator single mode")
    else:
        results["failed"].append("HQL Generator single mode")

    # Test 5: HQL Generator join mode
    if test_hql_generator_join_mode():
        results["passed"].append("HQL Generator join mode")
    else:
        results["failed"].append("HQL Generator join mode")

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total = len(results["passed"]) + len(results["failed"])
    passed = len(results["passed"])
    failed = len(results["failed"])

    print(f"\nTotal Tests: {total}")
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")

    if results["failed"]:
        print("\n" + "-"*80)
        print("FAILED TESTS:")
        print("-"*80)
        for test in results["failed"]:
            print(f"  ❌ {test}")

    # Diagnosis
    print("\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)

    if "Create Event with alias - ISSUE CONFIRMED" in results["failed"]:
        print("\n🔴 ISSUE CONFIRMED: Event model missing 'alias' field")
        print("\n   Impact:")
        print("   - Cannot create Events with table aliases")
        print("   - JOIN mode requires table aliases")
        print("   - UNION mode requires table aliases")

        print("\n   Fix Required:")
        print("   - Add 'alias: Optional[str] = None' field to Event dataclass")
        print("   - Update Event model in backend/services/hql/models/event.py")

    if "HQL Generator single mode" in results["passed"]:
        print("\n✅ HQL Generator works in single mode")
        print("   - Output format: SELECT ... FROM ... WHERE")
        print("   - NOT: CREATE VIEW or INSERT OVERWRITE")
        print("   - This is expected behavior for the core generator")

    print("\n" + "="*80)

if __name__ == '__main__':
    main()

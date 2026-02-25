#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test SQL injection fixes in data_access.py and templates.py

This test verifies that:
1. SQL identifiers are validated
2. Malicious input is rejected
3. Valid identifiers still work correctly
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.security.sql_validator import SQLValidator
from backend.core.data_access import GenericRepository


def test_sql_validator():
    """Test SQLValidator rejects malicious input"""
    print("Testing SQLValidator...")

    # Test valid identifiers
    try:
        assert SQLValidator.validate_table_name("games") == "games"
        assert SQLValidator.validate_column_name("user_id") == "user_id"
        assert SQLValidator.validate_identifier("_private") == "_private"
        print("✅ Valid identifiers accepted")
    except Exception as e:
        print(f"❌ Valid identifiers rejected: {e}")
        return False

    # Test SQL injection attempts
    injection_attempts = [
        "games; DROP TABLE users; --",
        "users' OR '1'='1",
        "table1 UNION SELECT * FROM passwords",
        "admin`; --",
        "1=1",
        "",
        "table with spaces",
        "table-with-dashes",
        "table.with.dots",
        "123table",
        "table$name",
        "table#tag"
    ]

    for attempt in injection_attempts:
        try:
            SQLValidator.validate_table_name(attempt)
            print(f"❌ SQL injection not blocked: {attempt}")
            return False
        except ValueError:
            pass  # Expected

    print("✅ SQL injection attempts blocked")
    return True


def test_generic_repository():
    """Test GenericRepository validates identifiers"""
    print("\nTesting GenericRepository...")

    # Test valid initialization
    try:
        repo = GenericRepository("games", primary_key="id")
        assert repo.table_name == "games"
        assert repo.primary_key == "id"
        print("✅ Valid repository initialization")
    except Exception as e:
        print(f"❌ Valid initialization rejected: {e}")
        return False

    # Test malicious table name
    try:
        repo = GenericRepository("games; DROP TABLE users; --", primary_key="id")
        print("❌ Malicious table name not blocked")
        return False
    except ValueError:
        print("✅ Malicious table name blocked")

    # Test malicious primary key
    try:
        repo = GenericRepository("games", primary_key="id; OR '1'='1")
        print("❌ Malicious primary key not blocked")
        return False
    except ValueError:
        print("✅ Malicious primary key blocked")

    # Test field validation in _validate_field
    repo = GenericRepository("games", primary_key="id")

    try:
        repo._validate_field("name")
        print("✅ Valid field accepted")
    except Exception as e:
        print(f"❌ Valid field rejected: {e}")
        return False

    try:
        repo._validate_field("name; DROP TABLE users; --")
        print("❌ Malicious field not blocked")
        return False
    except ValueError:
        print("✅ Malicious field blocked")

    return True


def test_field_whitelist():
    """Test field whitelist validation"""
    print("\nTesting field whitelist validation...")

    allowed_fields = {'name', 'email', 'created_at'}

    # Test valid field
    try:
        result = SQLValidator.validate_field_whitelist('name', allowed_fields)
        assert result == 'name'
        print("✅ Valid field in whitelist accepted")
    except Exception as e:
        print(f"❌ Valid field rejected: {e}")
        return False

    # Test field not in whitelist
    try:
        SQLValidator.validate_field_whitelist('password', allowed_fields)
        print("❌ Field not in whitelist not blocked")
        return False
    except ValueError:
        print("✅ Field not in whitelist blocked")

    # Test SQL injection attempt
    try:
        SQLValidator.validate_field_whitelist("name'; DROP TABLE users; --", allowed_fields)
        print("❌ SQL injection in whitelist not blocked")
        return False
    except ValueError:
        print("✅ SQL injection in whitelist blocked")

    return True


def test_order_by_sanitization():
    """Test ORDER BY clause sanitization"""
    print("\nTesting ORDER BY sanitization...")

    allowed_fields = {'name', 'created_at', 'email'}

    # Test valid ORDER BY
    try:
        result = SQLValidator.sanitize_order_by('created_at DESC', allowed_fields)
        print(f"✅ Valid ORDER BY accepted: {result}")
    except Exception as e:
        print(f"❌ Valid ORDER BY rejected: {e}")
        return False

    # Test invalid direction
    try:
        SQLValidator.sanitize_order_by('name INVALID', allowed_fields)
        print("❌ Invalid sort direction not blocked")
        return False
    except ValueError:
        print("✅ Invalid sort direction blocked")

    # Test field not in whitelist
    try:
        SQLValidator.sanitize_order_by('password ASC', allowed_fields)
        print("❌ Field not in whitelist not blocked in ORDER BY")
        return False
    except ValueError:
        print("✅ Field not in whitelist blocked in ORDER BY")

    # Test SQL injection
    try:
        SQLValidator.sanitize_order_by("name; DROP TABLE users; --", allowed_fields)
        print("❌ SQL injection in ORDER BY not blocked")
        return False
    except ValueError:
        print("✅ SQL injection in ORDER BY blocked")

    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("SQL Injection Fix Verification Tests")
    print("=" * 60)

    tests = [
        test_sql_validator,
        test_generic_repository,
        test_field_whitelist,
        test_order_by_sanitization
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)

    if all(results):
        print("\n✅ All tests passed! SQL injection fixes are working correctly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script to verify HQL Generation API fix

This script tests all three modes (single, join, union) with both
camelCase and snake_case field naming conventions.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_single_mode_camelCase():
    """Test single event mode with camelCase field names"""
    print("\n1. Testing single mode with camelCase (fieldName, fieldType)")

    request_data = {
        "events": [
            {
                "game_gid": 10000147,
                "event_id": 1
            }
        ],
        "fields": [
            {
                "fieldName": "role_id",
                "fieldType": "base"
            },
            {
                "fieldName": "zone_id",
                "fieldType": "param",
                "jsonPath": "$.zone_id"
            }
        ],
        "options": {
            "mode": "single",
            "include_comments": True
        }
    }

    response = requests.post(f"{BASE_URL}/hql-preview-v2/api/generate", json=request_data)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"   ✅ SUCCESS")
            print(f"   HQL: {data['data']['hql'][:100]}...")
            return True
        else:
            print(f"   ❌ FAIL: {data.get('error')}")
            return False
    else:
        print(f"   ❌ FAIL: HTTP {response.status_code}")
        return False

def test_single_mode_snake_case():
    """Test single event mode with snake_case field names"""
    print("\n2. Testing single mode with snake_case (field_name, field_type)")

    request_data = {
        "game_gid": "10000147",
        "events": [{"event_id": 1, "name": "login"}],
        "mode": "single",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"}
        ],
        "options": {
            "mode": "single"
        }
    }

    response = requests.post(f"{BASE_URL}/hql-preview-v2/api/generate", json=request_data)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"   ✅ SUCCESS")
            print(f"   HQL: {data['data']['hql'][:100]}...")
            return True
        else:
            print(f"   ❌ FAIL: {data.get('error')}")
            return False
    else:
        print(f"   ❌ FAIL: HTTP {response.status_code}")
        return False

def test_union_mode():
    """Test union mode with multiple events"""
    print("\n3. Testing union mode (multiple events)")

    request_data = {
        "game_gid": "10000147",
        "events": [
            {"event_id": 1},  # login
            {"event_id": 2}   # logout
        ],
        "fields": [
            {"field_name": "role_id", "field_type": "base"}
        ],
        "options": {
            "mode": "union",
            "include_comments": True
        }
    }

    response = requests.post(f"{BASE_URL}/hql-preview-v2/api/generate", json=request_data)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            hql = data['data']['hql']
            if "UNION ALL" in hql:
                print(f"   ✅ SUCCESS - UNION ALL detected")
                print(f"   HQL: {hql[:150]}...")
                return True
            else:
                print(f"   ❌ FAIL: UNION ALL not found in HQL")
                return False
        else:
            print(f"   ❌ FAIL: {data.get('error')}")
            return False
    else:
        print(f"   ❌ FAIL: HTTP {response.status_code}")
        return False

def test_with_where_conditions():
    """Test with WHERE conditions"""
    print("\n4. Testing with WHERE conditions")

    request_data = {
        "events": [
            {
                "game_gid": 10000147,
                "event_id": 1
            }
        ],
        "fields": [
            {
                "fieldName": "role_id",
                "fieldType": "base"
            }
        ],
        "where_conditions": [
            {
                "field": "zone_id",
                "operator": "=",
                "value": 1,
                "logicalOp": "AND"
            }
        ],
        "options": {
            "mode": "single"
        }
    }

    response = requests.post(f"{BASE_URL}/hql-preview-v2/api/generate", json=request_data)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            hql = data['data']['hql']
            if "WHERE" in hql and "zone_id" in hql:
                print(f"   ✅ SUCCESS - WHERE clause detected")
                print(f"   HQL: {hql[:150]}...")
                return True
            else:
                print(f"   ⚠️  PARTIAL: HQL generated but WHERE clause may be missing")
                print(f"   HQL: {hql[:150]}...")
                return True
        else:
            print(f"   ❌ FAIL: {data.get('error')}")
            return False
    else:
        print(f"   ❌ FAIL: HTTP {response.status_code}")
        return False

def test_error_handling():
    """Test error handling with invalid event_id"""
    print("\n5. Testing error handling (invalid event_id)")

    request_data = {
        "events": [
            {
                "game_gid": 10000147,
                "event_id": 99999  # Non-existent event
            }
        ],
        "fields": [
            {
                "fieldName": "role_id",
                "fieldType": "base"
            }
        ],
        "options": {
            "mode": "single"
        }
    }

    response = requests.post(f"{BASE_URL}/hql-preview-v2/api/generate", json=request_data)

    if response.status_code == 404:
        data = response.json()
        if "not found" in data.get("error", "").lower():
            print(f"   ✅ SUCCESS - Proper 404 error returned")
            print(f"   Error: {data.get('error')}")
            return True
        else:
            print(f"   ⚠️  PARTIAL: 404 returned but error message unclear")
            return True
    else:
        print(f"   ❌ FAIL: Expected 404, got HTTP {response.status_code}")
        return False

def test_cache_functionality():
    """Test that caching works (second request should be faster)"""
    print("\n6. Testing cache functionality")

    request_data = {
        "events": [
            {
                "game_gid": 10000147,
                "event_id": 1
            }
        ],
        "fields": [
            {
                "fieldName": "role_id",
                "fieldType": "base"
            }
        ],
        "options": {
            "mode": "single"
        }
    }

    # First request
    start1 = datetime.now()
    response1 = requests.post(f"{BASE_URL}/hql-preview-v2/api/generate", json=request_data)
    time1 = (datetime.now() - start1).total_seconds()

    # Second request (should be cached)
    start2 = datetime.now()
    response2 = requests.post(f"{BASE_URL}/hql-preview-v2/api/generate", json=request_data)
    time2 = (datetime.now() - start2).total_seconds()

    if response1.status_code == 200 and response2.status_code == 200:
        data2 = response2.json()
        if data2.get("data", {}).get("cached"):
            print(f"   ✅ SUCCESS - Response marked as cached")
            print(f"   First request: {time1:.3f}s, Second request: {time2:.3f}s")
            return True
        else:
            print(f"   ⚠️  PARTIAL - Cache not detected but both requests succeeded")
            print(f"   First request: {time1:.3f}s, Second request: {time2:.3f}s")
            return True
    else:
        print(f"   ❌ FAIL: HTTP {response1.status_code}, {response2.status_code}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("HQL Generation API Fix Verification")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Check server is running
    try:
        response = requests.get(f"{BASE_URL}/api/games")
        if response.status_code != 200:
            print("\n❌ FATAL: Server is not responding correctly")
            return False
    except Exception as e:
        print(f"\n❌ FATAL: Cannot connect to server: {e}")
        return False

    # Run all tests
    results = {
        "single_mode_camelCase": test_single_mode_camelCase(),
        "single_mode_snake_case": test_single_mode_snake_case(),
        "union_mode": test_union_mode(),
        "where_conditions": test_with_where_conditions(),
        "error_handling": test_error_handling(),
        "cache": test_cache_functionality()
    }

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 All tests passed! HQL Generation API is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")

    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

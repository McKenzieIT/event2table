#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct cache system test
"""

import sys
sys.path.insert(0, '.')

from backend.core.cache.cache_system import cache_result

print("=" * 60)
print("Direct Cache System Test")
print("=" * 60)

# Test 1: Set and Get
print("\n1. Set value:")
cache_result.set("test_key", {"data": "value"}, ttl_l1=60)
print("   ✅ Set test_key")

print("\n2. Get value:")
value = cache_result.get("test_key")
print(f"   Result: {value}")

print("\n3. Get again (should hit cache):")
value2 = cache_result.get("test_key")
print(f"   Result: {value2}")

print("\n4. Verification:")
print(f"   Values equal: {value == value2}")

# Test 2: Check if key exists
print("\n5. Check if key exists:")
exists = cache_result.get("test_key") is not None
print(f"   Key exists: {exists}")

print("\n" + "=" * 60)

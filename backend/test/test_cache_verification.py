#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple cache verification test
"""

import sys
sys.path.insert(0, '.')

from backend.models.repositories.parameters import ParameterRepository

# Create repo
repo = ParameterRepository()

print("=" * 60)
print("Cache Verification Test")
print("=" * 60)

# First call
print("\n1. First call (should be cache miss):")
result1 = repo.get_paginated_params(page=1, per_page=5)
print(f"   Result: {len(result1['params'])} params")
print(f"   Pagination: {result1['pagination']}")

# Second call
print("\n2. Second call (should be cache hit):")
result2 = repo.get_paginated_params(page=1, per_page=5)
print(f"   Result: {len(result2['params'])} params")
print(f"   Pagination: {result2['pagination']}")

# Verify results are identical
print("\n3. Verification:")
print(f"   Results identical: {result1 == result2}")
print(f"   Same params: {result1['params'] == result2['params']}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

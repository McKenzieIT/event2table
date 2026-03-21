#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test existing cached method
"""

import sys
import logging
sys.path.insert(0, '.')

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

from backend.models.repositories.parameters import ParameterRepository

# Create repo
repo = ParameterRepository()

print("=" * 60)
print("Test Existing Cached Method")
print("=" * 60)

# Test get_common_parameters (which uses @cached)
print("\n1. First call to get_common_parameters:")
result1 = repo.get_common_parameters()
print(f"   Result count: {len(result1)}")

print("\n2. Second call to get_common_parameters (should hit cache):")
result2 = repo.get_common_parameters()
print(f"   Result count: {len(result2)}")

print("\n3. Verification:")
print(f"   Results identical: {result1 == result2}")
print(f"   Same object: {result1 is result2}")

print("\n" + "=" * 60)

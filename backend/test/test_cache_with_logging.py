#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache test with logging enabled
"""

import sys
import logging
sys.path.insert(0, '.')

# Enable debug logging for cache
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

from unittest.mock import patch
from backend.models.repositories.parameters import ParameterRepository

# Create repo
repo = ParameterRepository()

# Mock data
mock_param_data = {
    'id': 1,
    'event_id': 100,
    'param_name': 'test_param',
    'game_gid': 90000001,
}

print("=" * 60)
print("Cache Test with Logging")
print("=" * 60)

# Patch fetch_all_as_dict
with patch('backend.models.repositories.parameters.fetch_all_as_dict') as mock_fetch:
    mock_fetch.return_value = [mock_param_data]

    print("\n1. First call:")
    result1 = repo.get_paginated_params(page=1, per_page=50)
    print(f"   Mock calls: {mock_fetch.call_count}")

    print("\n2. Second call:")
    result2 = repo.get_paginated_params(page=1, per_page=50)
    print(f"   Mock calls: {mock_fetch.call_count}")

    print(f"\n3. Total mock calls: {mock_fetch.call_count}")

print("\n" + "=" * 60)

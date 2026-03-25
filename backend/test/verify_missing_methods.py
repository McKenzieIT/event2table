#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify Missing Methods in ParameterRepository

This script checks which methods are missing and what they should do.
"""

import inspect
import sys

from backend.models.repositories.parameters import ParameterRepository


def check_method_exists(repo, method_name):
    """Check if method exists in repository"""
    return hasattr(repo, method_name)


def main():
    repo = ParameterRepository()

    print("=" * 60)
    print("ParameterRepository Method Check")
    print("=" * 60)

    # Methods that tests expect
    expected_methods = ['get_paginated_params', 'get_params_by_event_id', 'get_common_params']

    # Methods that actually exist
    existing_methods = [
        'get_common_parameters',
        'get_common_params_by_game',
        'get_common_params_with_event_count',
    ]

    print("\n📋 Expected by Tests (MISSING):")
    for method in expected_methods:
        exists = check_method_exists(repo, method)
        status = "✅" if exists else "❌"
        print(f"  {status} {method}")

    print("\n✅ Actually Existing:")
    for method in existing_methods:
        exists = check_method_exists(repo, method)
        status = "✅" if exists else "❌"
        print(f"  {status} {method}")

    print("\n" + "=" * 60)
    print("Method Signatures (for existing methods):")
    print("=" * 60)

    # Show signature of get_common_parameters
    if hasattr(repo, 'get_common_parameters'):
        sig = inspect.signature(repo.get_common_parameters)
        print(f"\nget_common_parameters{sig}")
        print(f"  → Should add alias: get_common_params()")

    print("\n" + "=" * 60)
    print("Actions Needed:")
    print("=" * 60)
    print(
        """
1. Add get_paginated_params(page, per_page)
   - Follow EventsRepository.get_paginated() pattern
   - Return paginated parameter list

2. Add get_params_by_event_id(event_id)
   - Simple WHERE event_id = ? query
   - Return list of parameters for that event

3. Add get_common_params() as alias
   - Call get_common_parameters() internally
   - Maintain backward compatibility
    """
    )


if __name__ == "__main__":
    main()

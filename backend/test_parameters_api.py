#!/usr/bin/env python3
"""Test script to debug parameters API error"""

import sys
import traceback

# Add backend to path
sys.path.insert(0, '/Users/mckenzie/Documents/event2table')

from backend.services.parameters.parameter_service import ParameterService


def test_parameters_api():
    """Test parameters API"""
    try:
        print("🔵 Testing ParameterService.get_parameters_paginated()...")
        service = ParameterService()

        result = service.get_parameters_paginated(
            game_gid=10000147, search=None, type_filter=None, page=1, page_size=50
        )

        print(f"✅ Success: {result}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_parameters_api()
    sys.exit(0 if success else 1)

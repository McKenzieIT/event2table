"""
TDD Test for FieldTypeEnum - P0-1 Fix

This test validates that FieldTypeEnum uses the correct enum values to match
the frontend TypeScript definitions.

Expected behavior:
- PARAM = "param" (NOT "params")
- NON_COMMON = "non_common" (NOT "non-common")
- BASE = "base"
- COMMON = "common"
- ALL = "all"

This test is written following TDD principles:
1. RED: Write failing test first
2. GREEN: Make minimal changes to pass
3. REFACTOR: Improve code while keeping tests passing

Author: Event2Table Development Team
Date: 2026-03-08
Priority: P0-1 (Critical)
"""

import pytest

from backend.gql_api.schema_parameter_management import FieldTypeEnum


def test_field_type_enum_has_correct_values():
    """
    Test FieldTypeEnum uses correct enum values

    This test will FAIL initially because the current implementation uses:
    - PARAMS = "params" (WRONG - should be "param")
    - NON_COMMON = "non-common" (WRONG - should be "non_common")

    After the fix, it should pass with:
    - PARAM = "param"
    - NON_COMMON = "non_common"

    This mismatch causes GraphQL 400 errors because the frontend sends
    "param" but the backend expects "params".
    """
    # Verify PARAM enum value (should be "param", not "params")
    # This will fail because the enum is currently named PARAMS with value "params"
    assert hasattr(FieldTypeEnum, 'PARAM'), "FieldTypeEnum must have PARAM attribute"

    assert (
        FieldTypeEnum.PARAM.value == "param"
    ), f"Expected FieldTypeEnum.PARAM.value to be 'param', but got '{FieldTypeEnum.PARAM.value}'"

    # Verify NON_COMMON enum value (should be "non_common", not "non-common")
    assert (
        FieldTypeEnum.NON_COMMON.value == "non_common"
    ), f"Expected FieldTypeEnum.NON_COMMON.value to be 'non_common', but got '{FieldTypeEnum.NON_COMMON.value}'"

    # Verify other enum values remain unchanged
    assert (
        FieldTypeEnum.BASE.value == "base"
    ), f"Expected FieldTypeEnum.BASE.value to be 'base', but got '{FieldTypeEnum.BASE.value}'"

    assert (
        FieldTypeEnum.COMMON.value == "common"
    ), f"Expected FieldTypeEnum.COMMON.value to be 'common', but got '{FieldTypeEnum.COMMON.value}'"

    assert (
        FieldTypeEnum.ALL.value == "all"
    ), f"Expected FieldTypeEnum.ALL.value to be 'all', but got '{FieldTypeEnum.ALL.value}'"


def test_field_type_enum_does_not_have_old_params_attribute():
    """
    Test that the old PARAMS attribute does not exist

    After the fix, we should have PARAM (not PARAMS).
    This test verifies we removed the old incorrect attribute.
    """
    # This should fail if PARAMS still exists (we want only PARAM)
    assert not hasattr(
        FieldTypeEnum, 'PARAMS'
    ), "FieldTypeEnum should NOT have PARAMS attribute (use PARAM instead)"


def test_field_type_enum_values_match_frontend_typescript():
    """
    Test that all enum values match the frontend TypeScript definitions

    Frontend TypeScript enum (frontend/src/graphql/enums.ts):
    export enum FieldType {
      ALL = "all"
      PARAM = "param"        // ← Must match
      NON_COMMON = "non_common"  // ← Must match
      COMMON = "common"
      BASE = "base"
    }

    This test ensures backend and frontend are perfectly aligned.
    """
    expected_values = {
        'ALL': 'all',
        'PARAM': 'param',  # NOT 'params'
        'NON_COMMON': 'non_common',  # NOT 'non-common'
        'COMMON': 'common',
        'BASE': 'base',
    }

    for attr_name, expected_value in expected_values.items():
        assert hasattr(FieldTypeEnum, attr_name), f"FieldTypeEnum must have {attr_name} attribute"

        actual_value = getattr(FieldTypeEnum, attr_name).value
        assert (
            actual_value == expected_value
        ), f"FieldTypeEnum.{attr_name}.value should be '{expected_value}', but got '{actual_value}'"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])

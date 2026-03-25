"""
TDD Test for JoinTypeEnum - P0-14 Fix

This test validates that JoinTypeEnum uses the correct enum values to match
the frontend TypeScript definitions.

Expected behavior:
- LEFT_JOIN = "LEFT" (for "LEFT JOIN")
- RIGHT_JOIN = "RIGHT" (for "RIGHT JOIN")
- INNER_JOIN = "INNER" (for "INNER JOIN")
- FULL_JOIN = "FULL" (for "FULL JOIN")

This test is written following TDD principles:
1. RED: Write failing test first
2. GREEN: Make minimal changes to pass
3. REFACTOR: Improve code while keeping tests passing

Author: Event2Table Development Team
Date: 2026-03-09
Priority: P0-14 (Critical)
"""

import pytest

from backend.gql_api.types.join_config_type import JoinTypeEnum


def test_join_type_enum_has_correct_attributes():
    """
    Test JoinTypeEnum has all required enum attributes

    This test verifies that the JoinTypeEnum defines all required
    join types: LEFT_JOIN, RIGHT_JOIN, INNER_JOIN, FULL_JOIN
    """
    # Verify LEFT_JOIN exists
    assert hasattr(JoinTypeEnum, 'LEFT_JOIN'), "JoinTypeEnum must have LEFT_JOIN attribute"

    # Verify RIGHT_JOIN exists
    assert hasattr(JoinTypeEnum, 'RIGHT_JOIN'), "JoinTypeEnum must have RIGHT_JOIN attribute"

    # Verify INNER_JOIN exists
    assert hasattr(JoinTypeEnum, 'INNER_JOIN'), "JoinTypeEnum must have INNER_JOIN attribute"

    # Verify FULL_JOIN exists
    assert hasattr(JoinTypeEnum, 'FULL_JOIN'), "JoinTypeEnum must have FULL_JOIN attribute"


def test_join_type_enum_has_correct_values():
    """
    Test JoinTypeEnum uses correct enum values

    This test verifies that the enum values match what's expected
    for SQL JOIN operations.

    Expected values:
    - LEFT_JOIN = "LEFT"
    - RIGHT_JOIN = "RIGHT"
    - INNER_JOIN = "INNER"
    - FULL_JOIN = "FULL"
    """
    # Verify LEFT_JOIN value
    assert (
        JoinTypeEnum.LEFT_JOIN.value == "LEFT"
    ), f"Expected JoinTypeEnum.LEFT_JOIN.value to be 'LEFT', but got '{JoinTypeEnum.LEFT_JOIN.value}'"

    # Verify RIGHT_JOIN value
    assert (
        JoinTypeEnum.RIGHT_JOIN.value == "RIGHT"
    ), f"Expected JoinTypeEnum.RIGHT_JOIN.value to be 'RIGHT', but got '{JoinTypeEnum.RIGHT_JOIN.value}'"

    # Verify INNER_JOIN value
    assert (
        JoinTypeEnum.INNER_JOIN.value == "INNER"
    ), f"Expected JoinTypeEnum.INNER_JOIN.value to be 'INNER', but got '{JoinTypeEnum.INNER_JOIN.value}'"

    # Verify FULL_JOIN value
    assert (
        JoinTypeEnum.FULL_JOIN.value == "FULL"
    ), f"Expected JoinTypeEnum.FULL_JOIN.value to be 'FULL', but got '{JoinTypeEnum.FULL_JOIN.value}'"


def test_join_type_enum_values_match_frontend_typescript():
    """
    Test that all enum values match the frontend TypeScript definitions

    Frontend TypeScript enum should be:
    export enum HqlJoinType {
      LEFT_JOIN = "LEFT",
      RIGHT_JOIN = "RIGHT",
      INNER_JOIN = "INNER",
      FULL_JOIN = "FULL"
    }

    This test ensures backend and frontend are perfectly aligned.
    """
    expected_values = {
        'LEFT_JOIN': 'LEFT',
        'RIGHT_JOIN': 'RIGHT',
        'INNER_JOIN': 'INNER',
        'FULL_JOIN': 'FULL',
    }

    for attr_name, expected_value in expected_values.items():
        assert hasattr(JoinTypeEnum, attr_name), f"JoinTypeEnum must have {attr_name} attribute"

        actual_value = getattr(JoinTypeEnum, attr_name).value
        assert (
            actual_value == expected_value
        ), f"JoinTypeEnum.{attr_name}.value should be '{expected_value}', but got '{actual_value}'"


def test_join_type_enum_is_graphene_enum():
    """
    Test that JoinTypeEnum is a proper Graphene enum

    This test verifies that JoinTypeEnum inherits from graphene.Enum
    and can be used in GraphQL schema definitions.
    """
    from graphene import Enum

    assert issubclass(JoinTypeEnum, Enum), "JoinTypeEnum must be a subclass of graphene.Enum"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])

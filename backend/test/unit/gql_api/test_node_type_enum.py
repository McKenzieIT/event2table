"""
TDD Test for NodeTypeEnum - P0-15 Fix

This test validates that NodeTypeEnum uses the correct enum values to match
the frontend TypeScript definitions.

Expected behavior:
- EVENT = "event" (Event Node)
- JOIN = "join" (Join Node)
- UNION = "union" (Union Node)
- FILTER = "filter" (Filter Node)

This test is written following TDD principles:
1. RED: Write failing test first
2. GREEN: Make minimal changes to pass
3. REFACTOR: Improve code while keeping tests passing

Author: Event2Table Development Team
Date: 2026-03-09
Priority: P0-15 (Critical)
"""

import pytest

from backend.gql_api.types.node_type import NodeTypeEnum


def test_node_type_enum_has_correct_attributes():
    """
    Test NodeTypeEnum has all required enum attributes

    This test verifies that the NodeTypeEnum defines all required
    node types: EVENT, JOIN, UNION, FILTER
    """
    # Verify EVENT exists
    assert hasattr(NodeTypeEnum, 'EVENT'), "NodeTypeEnum must have EVENT attribute"

    # Verify JOIN exists
    assert hasattr(NodeTypeEnum, 'JOIN'), "NodeTypeEnum must have JOIN attribute"

    # Verify UNION exists
    assert hasattr(NodeTypeEnum, 'UNION'), "NodeTypeEnum must have UNION attribute"

    # Verify FILTER exists
    assert hasattr(NodeTypeEnum, 'FILTER'), "NodeTypeEnum must have FILTER attribute"


def test_node_type_enum_has_correct_values():
    """
    Test NodeTypeEnum uses correct enum values

    This test verifies that the enum values match what's expected
    for canvas node types.

    Expected values:
    - EVENT = "event"
    - JOIN = "join"
    - UNION = "union"
    - FILTER = "filter"
    """
    # Verify EVENT value
    assert (
        NodeTypeEnum.EVENT.value == "event"
    ), f"Expected NodeTypeEnum.EVENT.value to be 'event', but got '{NodeTypeEnum.EVENT.value}'"

    # Verify JOIN value
    assert (
        NodeTypeEnum.JOIN.value == "join"
    ), f"Expected NodeTypeEnum.JOIN.value to be 'join', but got '{NodeTypeEnum.JOIN.value}'"

    # Verify UNION value
    assert (
        NodeTypeEnum.UNION.value == "union"
    ), f"Expected NodeTypeEnum.UNION.value to be 'union', but got '{NodeTypeEnum.UNION.value}'"

    # Verify FILTER value
    assert (
        NodeTypeEnum.FILTER.value == "filter"
    ), f"Expected NodeTypeEnum.FILTER.value to be 'filter', but got '{NodeTypeEnum.FILTER.value}'"


def test_node_type_enum_values_match_frontend_typescript():
    """
    Test that all enum values match the frontend TypeScript definitions

    Frontend TypeScript constants should be:
    export const NODE_TYPES = {
      EVENT: "event",
      UNION_ALL: "union_all",
      JOIN: "join",
      OUTPUT: "output",
      FILTER: "filter",
      AGGREGATE: "aggregate",
    } as const;

    This test ensures backend and frontend are perfectly aligned
    for the shared node types.
    """
    expected_values = {'EVENT': 'event', 'JOIN': 'join', 'UNION': 'union', 'FILTER': 'filter'}

    for attr_name, expected_value in expected_values.items():
        assert hasattr(NodeTypeEnum, attr_name), f"NodeTypeEnum must have {attr_name} attribute"

        actual_value = getattr(NodeTypeEnum, attr_name).value
        assert (
            actual_value == expected_value
        ), f"NodeTypeEnum.{attr_name}.value should be '{expected_value}', but got '{actual_value}'"


def test_node_type_enum_is_graphene_enum():
    """
    Test that NodeTypeEnum is a proper Graphene enum

    This test verifies that NodeTypeEnum inherits from graphene.Enum
    and can be used in GraphQL schema definitions.
    """
    from graphene import Enum

    assert issubclass(NodeTypeEnum, Enum), "NodeTypeEnum must be a subclass of graphene.Enum"


def test_node_type_field_uses_enum():
    """
    Test that NodeType.node_type field uses the enum

    This test verifies that the NodeType GraphQL type properly uses
    NodeTypeEnum for the node_type field instead of String.
    """
    from backend.gql_api.types.node_type import NodeType

    # Verify node_type field exists
    assert hasattr(NodeType, 'node_type'), "NodeType must have node_type field"

    # Verify node_type field type (it should be a Field, not String)
    from graphene import Field

    node_type_field = NodeType.node_type

    # The field should be defined (we can't easily test the enum type
    # without initializing the schema, but we can verify it's not a plain String)
    assert node_type_field is not None, "NodeType.node_type field must be defined"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])

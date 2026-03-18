"""
Enhanced Query Complexity Calculator

Implements field-weighted complexity calculation to accurately measure
query complexity and prevent resource exhaustion.
"""

import logging
from typing import Dict, Set

from graphql import GraphQLError

logger = logging.getLogger(__name__)


class EnhancedComplexityMiddleware:
    """
    Enhanced Query Complexity Middleware

    Calculates query complexity based on:
    - Field type (scalar vs object vs list)
    - Nesting depth (exponential multiplier)
    - List size limits

    Prevents malicious queries that would exhaust server resources.
    """

    # Complexity weights
    SCALAR_COST = 1
    OBJECT_COST = 5
    LIST_COST_MULTIPLIER = 10
    DEPTH_MULTIPLIER = 2

    # Known list fields that accept limit/first/last arguments
    LIST_FIELDS: Set[str] = {
        'games', 'events', 'parameters', 'categories',
        'templates', 'nodes', 'flows', 'joinConfigs',
        'gameStats', 'allGameStats'
    }

    def __init__(self, max_complexity: int = 1000):
        """
        Initialize middleware.

        Args:
            max_complexity: Maximum allowed query complexity
        """
        self.max_complexity = max_complexity
        logger.info(f"EnhancedComplexityMiddleware initialized with max_complexity={max_complexity}")

    def resolve(self, next, root, info, **args):
        """
        Check query complexity before resolving.

        Args:
            next: Next resolver in chain
            root: Root object
            info: GraphQL resolve info
            **args: Resolver arguments

        Returns:
            Result from next resolver

        Raises:
            GraphQLError: If complexity exceeds limit
        """
        # Calculate complexity
        complexity = self._calculate_complexity(info.operation)

        if complexity > self.max_complexity:
            logger.warning(
                f"Query complexity {complexity} exceeds maximum {self.max_complexity}"
            )
            raise GraphQLError(
                f"Query complexity {complexity} exceeds maximum allowed "
                f"complexity of {self.max_complexity}. "
                f"Please reduce query complexity by: "
                f"- Reducing number of fields "
                f"- Reducing nesting depth "
                f"- Using smaller limits on list fields"
            )

        logger.debug(f"Query complexity: {complexity}/{self.max_complexity}")
        return next(root, info, **args)

    def _calculate_complexity(self, operation, depth: int = 1) -> int:
        """
        Calculate query complexity with field weighting.

        Args:
            operation: GraphQL operation node
            depth: Current nesting depth

        Returns:
            Complexity score as integer
        """
        if not operation:
            return 0

        complexity = 0

        # Count fields in selection set
        if hasattr(operation, 'selection_set') and operation.selection_set:
            for selection in operation.selection_set.selections:
                # Calculate cost for this field
                field_cost = self._calculate_field_cost(selection, depth)

                # Recursively calculate nested fields
                nested_cost = 0
                if hasattr(selection, 'selection_set') and selection.selection_set:
                    nested_cost = self._calculate_complexity(selection, depth + 1)

                # Apply depth multiplier
                # Each level of nesting exponentially increases complexity
                depth_multiplier = self.DEPTH_MULTIPLIER ** (depth - 1)
                total_cost = (field_cost + nested_cost) * depth_multiplier

                complexity += total_cost

        return complexity

    def _calculate_field_cost(self, field, depth: int) -> int:
        """
        Calculate cost for a single field.

        Args:
            field: GraphQL field node
            depth: Current nesting depth

        Returns:
            Field cost as integer
        """
        if not hasattr(field, 'name') or not hasattr(field.name, 'value'):
            return self.SCALAR_COST

        field_name = field.name.value

        # Check if this is a list field with size argument
        list_size = self._get_list_size(field)
        if list_size > 0:
            # List fields have higher cost: size * multiplier
            return list_size * self.LIST_COST_MULTIPLIER

        # Check if this is an object field (has selection set)
        if hasattr(field, 'selection_set') and field.selection_set:
            return self.OBJECT_COST

        # Default to scalar cost
        return self.SCALAR_COST

    def _get_list_size(self, field) -> int:
        """
        Get the size limit for a list field.

        Args:
            field: GraphQL field node

        Returns:
            List size limit (0 if not a list field)
        """
        if not hasattr(field, 'name') or not hasattr(field.name, 'value'):
            return 0

        field_name = field.name.value

        # Check if this is a known list field
        if field_name not in self.LIST_FIELDS:
            return 0

        # Look for limit/first/last arguments
        if hasattr(field, 'arguments'):
            for arg in field.arguments:
                if hasattr(arg, 'name') and hasattr(arg.name, 'value'):
                    arg_name = arg.name.value
                    if arg_name in ['limit', 'first', 'last']:
                        # Get the value
                        if hasattr(arg, 'value') and hasattr(arg.value, 'value'):
                            try:
                                return int(arg.value.value)
                            except (ValueError, TypeError):
                                return 10  # Default limit

        # Return default limit for list fields
        return 10


__all__ = ['EnhancedComplexityMiddleware']

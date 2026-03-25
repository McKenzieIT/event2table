"""
Parameter Queries

Implements GraphQL query resolvers for Parameter entity.
PERF: Added caching decorators for performance optimization
"""

import logging
from typing import Any, Dict
from typing import List as TypingList

import graphene
from graphene import Boolean, Field, Int, List, String

# PERF: Import cache decorator for Parameter query optimization
from backend.core.cache.decorators import cached

logger = logging.getLogger(__name__)


class ParameterQueries:
    """Parameter-related GraphQL queries"""

    @staticmethod
    @cached(ttl=1800, key_prefix="parameter")
    def resolve_parameter(root, info, id: int):
        """
        Resolve a single parameter by ID.

        PERF: Cache decorator improves performance significantly
        """
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            parameter = fetch_one_as_dict(
                """
                SELECT
                    ep.*,
                    pt.name as template_name,
                    pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id = ?
            """,
                (id,),
            )

            if parameter:
                return ParameterType.from_dict(parameter)
            return None

        except Exception as e:
            logger.error(f"Error resolving parameter {id}: {e}", exc_info=True)
            return None

    @staticmethod
    @cached(ttl=1800, key_prefix="parameters")
    def resolve_parameters(root, info, event_id: int, active_only: bool = True):
        """
        Resolve list of parameters for an event.

        PERF: Cache decorator improves performance significantly
        Optimized with DataLoader to prevent N+1 queries when multiple events
        request their parameters simultaneously.
        """
        try:
            from backend.gql_api.dataloaders.parameter_loader_enhanced import (
                get_parameter_loader_enhanced,
            )
            from backend.gql_api.types.parameter_type import ParameterType

            # Use DataLoader to batch load parameters
            loader = get_parameter_loader_enhanced()
            params = loader.load_by_event(event_id)

            # Filter by active_only flag
            if active_only and params:
                params = [p for p in params if p.get('is_active', 0) == 1]

            if params:
                return [ParameterType.from_dict(param) for param in params]
            return []

        except Exception as e:
            logger.error(f"Error resolving parameters: {e}", exc_info=True)
            return []

    @staticmethod
    @cached(ttl=600, key_prefix="parameters_search")
    def resolve_search_parameters(root, info, query: str, event_id: int | None = None):
        """
        Search parameters by name.

        PERF: Cache decorator with shorter TTL (10 min) for search results
        """
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            search_pattern = f"%{query}%"

            if event_id:
                parameters = fetch_all_as_dict(
                    """
                    SELECT
                        ep.*,
                        pt.name as template_name,
                        pt.description
                    FROM event_params ep
                    LEFT JOIN param_templates pt ON ep.template_id = pt.id
                    WHERE ep.event_id = ?
                      AND (ep.param_name LIKE ? OR ep.param_name_cn LIKE ?)
                    ORDER BY ep.id
                    LIMIT 20
                    """,
                    (event_id, search_pattern, search_pattern),
                )
            else:
                parameters = fetch_all_as_dict(
                    """
                    SELECT
                        ep.*,
                        pt.name as template_name,
                        pt.description
                    FROM event_params ep
                    LEFT JOIN param_templates pt ON ep.template_id = pt.id
                    WHERE ep.param_name LIKE ? OR ep.param_name_cn LIKE ?
                    ORDER BY ep.id
                    LIMIT 20
                    """,
                    (search_pattern, search_pattern),
                )

            return [ParameterType.from_dict(param) for param in parameters]

        except Exception as e:
            logger.error(f"Error searching parameters: {e}", exc_info=True)
            return []

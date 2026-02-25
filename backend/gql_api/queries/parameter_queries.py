"""
Parameter Queries

Implements GraphQL query resolvers for Parameter entity.
"""

import graphene
from graphene import Field, List, Int, String, Boolean
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ParameterQueries:
    """Parameter-related GraphQL queries"""

    @staticmethod
    def resolve_parameter(root, info, id: int):
        """Resolve a single parameter by ID."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            parameter = fetch_one_as_dict("""
                SELECT
                    ep.*,
                    pt.name as template_name,
                    pt.description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.id = ?
            """, (id,))

            if parameter:
                return ParameterType.from_dict(parameter)
            return None

        except Exception as e:
            logger.error(f"Error resolving parameter {id}: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_parameters(root, info, event_id: int, active_only: bool = True):
        """Resolve list of parameters for an event."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.parameter_type import ParameterType

            if active_only:
                parameters = fetch_all_as_dict("""
                    SELECT
                        ep.*,
                        pt.name as template_name,
                        pt.description
                    FROM event_params ep
                    LEFT JOIN param_templates pt ON ep.template_id = pt.id
                    WHERE ep.event_id = ? AND ep.is_active = 1
                    ORDER BY ep.id
                """, (event_id,))
            else:
                parameters = fetch_all_as_dict("""
                    SELECT
                        ep.*,
                        pt.name as template_name,
                        pt.description
                    FROM event_params ep
                    LEFT JOIN param_templates pt ON ep.template_id = pt.id
                    WHERE ep.event_id = ?
                    ORDER BY ep.id
                """, (event_id,))

            return [ParameterType.from_dict(param) for param in parameters]

        except Exception as e:
            logger.error(f"Error resolving parameters: {e}", exc_info=True)
            return []

    @staticmethod
    def resolve_search_parameters(root, info, query: str, event_id: int = None):
        """Search parameters by name."""
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
                    (event_id, search_pattern, search_pattern)
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
                    (search_pattern, search_pattern)
                )

            return [ParameterType.from_dict(param) for param in parameters]

        except Exception as e:
            logger.error(f"Error searching parameters: {e}", exc_info=True)
            return []

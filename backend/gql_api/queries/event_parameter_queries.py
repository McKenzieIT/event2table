"""
Event Parameter Queries

Implements GraphQL query resolvers for Event Parameter extended functionality.
"""

import graphene
from graphene import Field, List, Int
import logging

logger = logging.getLogger(__name__)


class EventParameterQueries:
    """Event Parameter-related GraphQL queries"""

    @staticmethod
    def resolve_event_parameter_extended(root, info, id: int):
        """Resolve a single event parameter with extended info."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.event_parameter_type import EventParameterExtendedType

            param = fetch_one_as_dict(
                "SELECT * FROM event_params WHERE id = ?",
                (id,)
            )

            return EventParameterExtendedType.from_dict(param) if param else None

        except Exception as e:
            logger.error(f"Error resolving event parameter: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_param_history(root, info, param_id: int, limit: int = 10):
        """Resolve parameter version history."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.event_parameter_type import ParamVersionType

            versions = fetch_all_as_dict(
                """
                SELECT * FROM param_versions
                WHERE param_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (param_id, limit)
            )

            return [ParamVersionType.from_dict(v) for v in versions]

        except Exception as e:
            logger.error(f"Error resolving param history: {e}", exc_info=True)
            return []

    @staticmethod
    def resolve_param_config(root, info, param_id: int):
        """Resolve parameter configuration."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.event_parameter_type import ParamConfigType

            config = fetch_one_as_dict(
                "SELECT * FROM param_configs WHERE param_id = ?",
                (param_id,)
            )

            return ParamConfigType.from_dict(config) if config else None

        except Exception as e:
            logger.error(f"Error resolving param config: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_validation_rules(root, info, param_id: int):
        """Resolve validation rules for a parameter."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.event_parameter_type import ValidationRuleType

            rules = fetch_all_as_dict(
                """
                SELECT * FROM param_validation_rules
                WHERE param_id = ? AND is_active = 1
                ORDER BY created_at DESC
                """,
                (param_id,)
            )

            return [ValidationRuleType.from_dict(r) for r in rules]

        except Exception as e:
            logger.error(f"Error resolving validation rules: {e}", exc_info=True)
            return []

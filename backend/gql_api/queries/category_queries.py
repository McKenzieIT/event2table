"""
Category Queries

Implements GraphQL query resolvers for Category entity.
"""

import graphene
from graphene import Field, List, Int, String
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CategoryQueries:
    """Category-related GraphQL queries"""

    @staticmethod
    def resolve_category(root, info, id: int):
        """Resolve a single category by ID."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.category_type import CategoryType

            category = fetch_one_as_dict("""
                SELECT
                    ec.id,
                    ec.name,
                    ec.created_at,
                    ec.updated_at,
                    COUNT(le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON le.category_id = ec.id
                WHERE ec.id = ?
                GROUP BY ec.id, ec.name, ec.created_at, ec.updated_at
            """, (id,))

            if category:
                return CategoryType.from_dict(category)
            return None

        except Exception as e:
            logger.error(f"Error resolving category {id}: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_categories(root, info, limit: int = 50, offset: int = 0):
        """Resolve list of categories with pagination."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.category_type import CategoryType

            categories = fetch_all_as_dict("""
                SELECT
                    ec.id,
                    ec.name,
                    ec.created_at,
                    ec.updated_at,
                    COUNT(le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON le.category_id = ec.id
                GROUP BY ec.id, ec.name, ec.created_at, ec.updated_at
                ORDER BY ec.id
                LIMIT ? OFFSET ?
            """, (limit, offset))

            return [CategoryType.from_dict(cat) for cat in categories]

        except Exception as e:
            logger.error(f"Error resolving categories: {e}", exc_info=True)
            return []

    @staticmethod
    def resolve_search_categories(root, info, query: str):
        """Search categories by name."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.category_type import CategoryType

            search_pattern = f"%{query}%"
            categories = fetch_all_as_dict(
                """
                SELECT
                    ec.id,
                    ec.name,
                    ec.created_at,
                    ec.updated_at,
                    COUNT(le.id) as event_count
                FROM event_categories ec
                LEFT JOIN log_events le ON le.category_id = ec.id
                WHERE ec.name LIKE ?
                GROUP BY ec.id, ec.name, ec.created_at, ec.updated_at
                ORDER BY ec.id
                LIMIT 20
                """,
                (search_pattern,)
            )

            return [CategoryType.from_dict(cat) for cat in categories]

        except Exception as e:
            logger.error(f"Error searching categories: {e}", exc_info=True)
            return []

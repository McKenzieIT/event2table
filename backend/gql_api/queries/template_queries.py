"""
Template Queries

Implements GraphQL query resolvers for Template entity.
"""

import graphene
from graphene import Field, List, Int, String, Boolean
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class TemplateQueries:
    """Template-related GraphQL queries"""

    @staticmethod
    def resolve_template(root, info, id: int):
        """Resolve a single template by ID."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.template_type import TemplateType

            template = fetch_one_as_dict(
                "SELECT * FROM canvas_templates WHERE id = ?",
                (id,)
            )

            return TemplateType.from_dict(template) if template else None

        except Exception as e:
            logger.error(f"Error resolving template: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_templates(root, info, game_gid: int = None, category: str = None,
                          search: str = None, limit: int = 20, offset: int = 0):
        """Resolve list of templates with optional filtering."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.template_type import TemplateType

            query = "SELECT * FROM canvas_templates WHERE is_active = 1"
            params = []

            if game_gid:
                query += " AND game_gid = ?"
                params.append(game_gid)

            if category:
                query += " AND category = ?"
                params.append(category)

            if search:
                query += " AND (name LIKE ? OR description LIKE ?)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param])

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            templates = fetch_all_as_dict(query, tuple(params))

            return [TemplateType.from_dict(t) for t in templates]

        except Exception as e:
            logger.error(f"Error resolving templates: {e}", exc_info=True)
            return []

    @staticmethod
    def resolve_search_templates(root, info, query: str, game_gid: int = None):
        """Search templates by name or description."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.template_type import TemplateType

            sql = """
                SELECT * FROM canvas_templates
                WHERE is_active = 1
                AND (name LIKE ? OR description LIKE ?)
            """
            search_param = f"%{query}%"
            params = [search_param, search_param]

            if game_gid:
                sql += " AND game_gid = ?"
                params.append(game_gid)

            sql += " ORDER BY created_at DESC LIMIT 50"

            templates = fetch_all_as_dict(sql, tuple(params))

            return [TemplateType.from_dict(t) for t in templates]

        except Exception as e:
            logger.error(f"Error searching templates: {e}", exc_info=True)
            return []

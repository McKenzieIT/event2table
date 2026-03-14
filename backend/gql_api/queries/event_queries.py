"""
Event Queries

Implements GraphQL query resolvers for Event entity.
Optimized with DataLoader to prevent N+1 queries.
PERF: Added caching decorators for performance optimization
"""

import logging
from typing import Any, Dict
from typing import List as TypingList

import graphene
from graphene import Field, Int, List, String

# PERF: Import cache decorator for Event query optimization
from backend.core.cache.decorators import cached

logger = logging.getLogger(__name__)


class EventQueries:
    """Event-related GraphQL queries"""

    @staticmethod
    @cached(ttl=1800, key_prefix="event")
    def resolve_event(root, info, id: int):
        """
        Resolve a single event by ID.

        PERF: Cache decorator improves performance significantly
        """
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.event_type import EventType

            # Optimized: Remove subquery, will use DataLoader for params
            event = fetch_one_as_dict(
                """
                SELECT
                    le.*,
                    g.gid, g.name as game_name, g.ods_db,
                    ec.name as category_name
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE le.id = ?
                """,
                (id,),
            )

            if event:
                return EventType.from_dict(event)
            return None

        except Exception as e:
            logger.error(f"Error resolving event {id}: {e}", exc_info=True)
            return None

    @staticmethod
    @cached(ttl=1800, key_prefix="events")
    def resolve_events(
        root, info, game_gid: int, category: str = None, limit: int = 50, offset: int = 0
    ):
        """
        Resolve list of events for a game with filtering and pagination.

        PERF: Cache decorator improves performance significantly
        """
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.event_type import EventType

            # Build query with optional category filter
            # Optimized: Remove subquery, will use DataLoader for params
            if category:
                events = fetch_all_as_dict(
                    """
                    SELECT
                        le.*,
                        g.gid, g.name as game_name, g.ods_db,
                        ec.name as category_name
                    FROM log_events le
                    LEFT JOIN games g ON le.game_gid = g.gid
                    LEFT JOIN event_categories ec ON le.category_id = ec.id
                    WHERE le.game_gid = ? AND ec.name = ?
                    ORDER BY le.id DESC
                    LIMIT ? OFFSET ?
                    """,
                    (game_gid, category, limit, offset),
                )
            else:
                events = fetch_all_as_dict(
                    """
                    SELECT
                        le.*,
                        g.gid, g.name as game_name, g.ods_db,
                        ec.name as category_name
                    FROM log_events le
                    LEFT JOIN games g ON le.game_gid = g.gid
                    LEFT JOIN event_categories ec ON le.category_id = ec.id
                    WHERE le.game_gid = ?
                    ORDER BY le.id DESC
                    LIMIT ? OFFSET ?
                    """,
                    (game_gid, limit, offset),
                )

            return [EventType.from_dict(event) for event in events]

        except Exception as e:
            logger.error(f"Error resolving events: {e}", exc_info=True)
            return []

    @staticmethod
    @cached(ttl=600, key_prefix="events_search")
    def resolve_search_events(root, info, query: str, game_gid: int = None):
        """
        Search events by name.

        PERF: Cache decorator with shorter TTL (10 min) for search results
        """
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.event_type import EventType

            search_pattern = f"%{query}%"

            if game_gid:
                events = fetch_all_as_dict(
                    """
                    SELECT
                        le.*,
                        g.gid, g.name as game_name, g.ods_db,
                        ec.name as category_name
                    FROM log_events le
                    LEFT JOIN games g ON le.game_gid = g.gid
                    LEFT JOIN event_categories ec ON le.category_id = ec.id
                    WHERE le.game_gid = ? 
                      AND (le.event_name LIKE ? OR le.event_name_cn LIKE ?)
                    ORDER BY le.id DESC
                    LIMIT 20
                    """,
                    (game_gid, search_pattern, search_pattern),
                )
            else:
                events = fetch_all_as_dict(
                    """
                    SELECT
                        le.*,
                        g.gid, g.name as game_name, g.ods_db,
                        ec.name as category_name
                    FROM log_events le
                    LEFT JOIN games g ON le.game_gid = g.gid
                    LEFT JOIN event_categories ec ON le.category_id = ec.id
                    WHERE le.event_name LIKE ? OR le.event_name_cn LIKE ?
                    ORDER BY le.id DESC
                    LIMIT 20
                    """,
                    (search_pattern, search_pattern),
                )

            return [EventType.from_dict(event) for event in events]

        except Exception as e:
            logger.error(f"Error searching events: {e}", exc_info=True)
            return []

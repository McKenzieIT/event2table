"""
Event Queries

Implements GraphQL query resolvers for Event entity.
"""

import graphene
from graphene import Field, List, Int, String
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EventQueries:
    """Event-related GraphQL queries"""
    
    @staticmethod
    def resolve_event(root, info, id: int):
        """Resolve a single event by ID."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.event_type import EventType
            
            event = fetch_one_as_dict(
                """
                SELECT
                    le.*,
                    g.gid, g.name as game_name, g.ods_db,
                    ec.name as category_name,
                    (SELECT COUNT(*) FROM event_params ep 
                     WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE le.id = ?
                """,
                (id,)
            )
            
            if event:
                return EventType.from_dict(event)
            return None
            
        except Exception as e:
            logger.error(f"Error resolving event {id}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def resolve_events(root, info, game_gid: int, category: str = None, 
                       limit: int = 50, offset: int = 0):
        """Resolve list of events for a game with filtering and pagination."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.event_type import EventType
            
            # Build query with optional category filter
            if category:
                events = fetch_all_as_dict(
                    """
                    SELECT
                        le.*,
                        g.gid, g.name as game_name, g.ods_db,
                        ec.name as category_name,
                        (SELECT COUNT(*) FROM event_params ep 
                         WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
                    FROM log_events le
                    LEFT JOIN games g ON le.game_gid = g.gid
                    LEFT JOIN event_categories ec ON le.category_id = ec.id
                    WHERE le.game_gid = ? AND ec.name = ?
                    ORDER BY le.id DESC
                    LIMIT ? OFFSET ?
                    """,
                    (game_gid, category, limit, offset)
                )
            else:
                events = fetch_all_as_dict(
                    """
                    SELECT
                        le.*,
                        g.gid, g.name as game_name, g.ods_db,
                        ec.name as category_name,
                        (SELECT COUNT(*) FROM event_params ep 
                         WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
                    FROM log_events le
                    LEFT JOIN games g ON le.game_gid = g.gid
                    LEFT JOIN event_categories ec ON le.category_id = ec.id
                    WHERE le.game_gid = ?
                    ORDER BY le.id DESC
                    LIMIT ? OFFSET ?
                    """,
                    (game_gid, limit, offset)
                )
            
            return [EventType.from_dict(event) for event in events]
            
        except Exception as e:
            logger.error(f"Error resolving events: {e}", exc_info=True)
            return []
    
    @staticmethod
    def resolve_search_events(root, info, query: str, game_gid: int = None):
        """Search events by name."""
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
                    (game_gid, search_pattern, search_pattern)
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
                    (search_pattern, search_pattern)
                )
            
            return [EventType.from_dict(event) for event in events]
            
        except Exception as e:
            logger.error(f"Error searching events: {e}", exc_info=True)
            return []

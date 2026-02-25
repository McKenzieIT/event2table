"""
Dashboard Queries

Implements GraphQL query resolvers for Dashboard statistics.
"""

import graphene
from graphene import Field, List, Int
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DashboardQueries:
    """Dashboard-related GraphQL queries"""

    @staticmethod
    def resolve_dashboard_stats(root, info):
        """Resolve dashboard statistics."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.dashboard_type import DashboardStatsType

            # Get total counts
            stats = fetch_one_as_dict("""
                SELECT
                    (SELECT COUNT(*) FROM games) as total_games,
                    (SELECT COUNT(*) FROM log_events) as total_events,
                    (SELECT COUNT(*) FROM event_params WHERE is_active = 1) as total_parameters,
                    (SELECT COUNT(*) FROM event_categories) as total_categories
            """)

            # Get recent activity (last 7 days)
            recent = fetch_one_as_dict("""
                SELECT
                    (SELECT COUNT(*) FROM log_events 
                     WHERE created_at >= datetime('now', '-7 days')) as events_last_7_days,
                    (SELECT COUNT(*) FROM event_params 
                     WHERE created_at >= datetime('now', '-7 days')) as parameters_last_7_days
            """)

            # Merge stats
            if stats and recent:
                stats.update(recent)

            return DashboardStatsType.from_dict(stats) if stats else None

        except Exception as e:
            logger.error(f"Error resolving dashboard stats: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_game_stats(root, info, game_gid: int):
        """Resolve statistics for a specific game."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.dashboard_type import GameStatsType

            stats = fetch_one_as_dict("""
                SELECT
                    g.gid as game_gid,
                    g.name as game_name,
                    COUNT(DISTINCT le.id) as event_count,
                    COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as parameter_count,
                    COUNT(DISTINCT le.category_id) as category_count
                FROM games g
                LEFT JOIN log_events le ON le.game_gid = g.gid
                LEFT JOIN event_params ep ON ep.event_id = le.id
                WHERE g.gid = ?
                GROUP BY g.gid, g.name
            """, (game_gid,))

            return GameStatsType.from_dict(stats) if stats else None

        except Exception as e:
            logger.error(f"Error resolving game stats: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_all_game_stats(root, info, limit: int = 20):
        """Resolve statistics for all games."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.dashboard_type import GameStatsType

            stats = fetch_all_as_dict("""
                SELECT
                    g.gid as game_gid,
                    g.name as game_name,
                    COUNT(DISTINCT le.id) as event_count,
                    COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as parameter_count,
                    COUNT(DISTINCT le.category_id) as category_count
                FROM games g
                LEFT JOIN log_events le ON le.game_gid = g.gid
                LEFT JOIN event_params ep ON ep.event_id = le.id
                GROUP BY g.gid, g.name
                ORDER BY event_count DESC
                LIMIT ?
            """, (limit,))

            return [GameStatsType.from_dict(s) for s in stats]

        except Exception as e:
            logger.error(f"Error resolving all game stats: {e}", exc_info=True)
            return []

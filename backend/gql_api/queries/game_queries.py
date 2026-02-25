"""
Game Queries

Implements GraphQL query resolvers for Game entity.
"""

import graphene
from graphene import Field, List, Int, String
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GameQueries:
    """Game-related GraphQL queries"""
    
    @staticmethod
    def resolve_game(root, info, gid: int):
        """Resolve a single game by GID."""
        try:
            from backend.core.data_access import Repositories
            from backend.gql_api.types.game_type import GameType
            
            game = Repositories.GAMES.find_by_field("gid", gid)
            if game:
                return GameType.from_dict(game)
            return None
            
        except Exception as e:
            logger.error(f"Error resolving game {gid}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def resolve_games(root, info, limit: int = 10, offset: int = 0):
        """Resolve list of games with pagination."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.game_type import GameType
            
            # Use optimized query with event counts
            games = fetch_all_as_dict("""
                SELECT
                    g.id,
                    g.gid,
                    g.name,
                    g.ods_db,
                    g.icon_path,
                    g.created_at,
                    g.updated_at,
                    COUNT(DISTINCT le.id) as event_count,
                    COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as param_count
                FROM games g
                LEFT JOIN log_events le ON le.game_gid = g.gid
                LEFT JOIN event_params ep ON ep.event_id = le.id
                GROUP BY g.id, g.gid, g.name, g.ods_db, g.icon_path, g.created_at, g.updated_at
                ORDER BY g.id
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            return [GameType.from_dict(game) for game in games]
            
        except Exception as e:
            logger.error(f"Error resolving games: {e}", exc_info=True)
            return []
    
    @staticmethod
    def resolve_search_games(root, info, query: str):
        """Search games by name or GID."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.game_type import GameType
            
            search_pattern = f"%{query}%"
            games = fetch_all_as_dict(
                """
                SELECT * FROM games
                WHERE name LIKE ? OR CAST(gid AS TEXT) LIKE ?
                ORDER BY id
                LIMIT 20
                """,
                (search_pattern, search_pattern)
            )
            
            return [GameType.from_dict(game) for game in games]
            
        except Exception as e:
            logger.error(f"Error searching games: {e}", exc_info=True)
            return []

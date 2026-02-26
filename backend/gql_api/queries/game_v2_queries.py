"""
Game V2 Queries

Implements GraphQL query resolvers for Game V2 API.
"""

import graphene
from graphene import Field, List, Int, String
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GameV2Queries:
    """Game V2-related GraphQL queries"""
    
    @staticmethod
    def resolve_games_v2(root, info):
        """
        Resolve list of all games (V2 API).
        
        Returns games with enhanced V2 fields.
        """
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.game_v2_type import GameV2Type
            
            # Use optimized query with event counts
            games = fetch_all_as_dict("""
                SELECT
                    g.id,
                    g.gid,
                    g.name,
                    g.ods_db,
                    g.created_at,
                    g.updated_at,
                    COUNT(DISTINCT le.id) as event_count
                FROM games g
                LEFT JOIN log_events le ON le.game_gid = g.gid
                GROUP BY g.id, g.gid, g.name, g.ods_db, g.created_at, g.updated_at
                ORDER BY g.id
            """)
            
            # Add V2 fields (is_active, name_cn, description)
            # These fields may not exist in database yet, so we set defaults
            for game in games:
                game['is_active'] = True
                game['name_cn'] = None
                game['description'] = None
            
            return [GameV2Type.from_dict(game) for game in games]
            
        except Exception as e:
            logger.error(f"Error resolving games V2: {e}", exc_info=True)
            return []
    
    @staticmethod
    def resolve_game_v2(root, info, gid: int):
        """
        Resolve a single game by GID (V2 API).
        
        Args:
            gid: Game business GID
        """
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.game_v2_type import GameV2Type
            
            # Get game with event count
            game = fetch_one_as_dict("""
                SELECT
                    g.id,
                    g.gid,
                    g.name,
                    g.ods_db,
                    g.created_at,
                    g.updated_at,
                    COUNT(DISTINCT le.id) as event_count
                FROM games g
                LEFT JOIN log_events le ON le.game_gid = g.gid
                WHERE g.gid = ?
                GROUP BY g.id, g.gid, g.name, g.ods_db, g.created_at, g.updated_at
            """, (gid,))
            
            if game:
                # Add V2 fields
                game['is_active'] = True
                game['name_cn'] = None
                game['description'] = None
                return GameV2Type.from_dict(game)
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving game V2 {gid}: {e}", exc_info=True)
            return None

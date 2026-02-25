"""
Game DataLoader

Implements batch loading for games to prevent N+1 queries.
"""

from promise.dataloader import DataLoader
from promise import Promise
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GameLoader(DataLoader):
    """
    Game DataLoader

    Batches game loading requests to prevent N+1 queries.
    Instead of loading games one by one, it collects all gids
    and loads all games in a single query.
    """

    def batch_load_fn(self, gids: List[int]) -> Promise[List[Dict[str, Any]]]:
        """
        Batch load games by GIDs.

        Args:
            gids: List of game GIDs to load

        Returns:
            Promise resolving to list of games (one per gid, None if not found)
        """
        logger.debug(f"GameLoader: batch loading {len(gids)} games")

        try:
            # Import here to avoid circular dependencies
            from backend.core.utils import fetch_all_as_dict

            # Single query to fetch all games
            placeholders = ','.join(['?'] * len(gids))
            query = f"""
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
                WHERE g.gid IN ({placeholders})
                GROUP BY g.id, g.gid, g.name, g.ods_db, g.icon_path, g.created_at, g.updated_at
            """

            games = fetch_all_as_dict(query, tuple(gids))

            # Create a map for quick lookup
            games_by_gid: Dict[int, Dict[str, Any]] = {
                game['gid']: game for game in games
            }

            # Return games in the same order as requested gids
            result = [games_by_gid.get(gid) for gid in gids]

            logger.debug(f"GameLoader: loaded {len(games)} games for {len(gids)} requests")

            return Promise.resolve(result)

        except Exception as e:
            logger.error(f"GameLoader error: {e}", exc_info=True)
            # Return None for each request on error
            return Promise.resolve([None for _ in gids])


class GamesByFilterLoader(DataLoader):
    """
    Games by Filter DataLoader

    Caches filtered game list queries.
    """

    def batch_load_fn(self, keys: List[str]) -> Promise[List[List[Dict[str, Any]]]]:
        """
        Batch load games by filter keys.

        Args:
            keys: List of filter keys (serialized filter params)

        Returns:
            Promise resolving to list of game lists
        """
        logger.debug(f"GamesByFilterLoader: batch loading for {len(keys)} filters")

        try:
            from backend.core.utils import fetch_all_as_dict
            import json

            results = []
            for key in keys:
                # Parse filter from key
                try:
                    filter_data = json.loads(key)
                    limit = filter_data.get('limit', 10)
                    offset = filter_data.get('offset', 0)
                except:
                    limit, offset = 10, 0

                # Query games with pagination
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

                results.append(games)

            return Promise.resolve(results)

        except Exception as e:
            logger.error(f"GamesByFilterLoader error: {e}", exc_info=True)
            return Promise.resolve([[] for _ in keys])


# Global singleton instances
game_loader = GameLoader()
games_by_filter_loader = GamesByFilterLoader()

"""
Event DataLoader

Implements batch loading for events to prevent N+1 queries.
"""

from promise.dataloader import DataLoader
from promise import Promise
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EventLoader(DataLoader):
    """
    Event DataLoader
    
    Batches event loading requests to prevent N+1 queries.
    Instead of loading events one by one for each game,
    it collects all game_gids and loads all events in a single query.
    """
    
    def batch_load_fn(self, game_gids: List[int]) -> Promise[List[List[Dict[str, Any]]]]:
        """
        Batch load events for multiple games.
        
        Args:
            game_gids: List of game GIDs to load events for
            
        Returns:
            Promise resolving to list of event lists (one list per game_gid)
        """
        logger.debug(f"EventLoader: batch loading events for {len(game_gids)} games")
        
        try:
            # Import here to avoid circular dependencies
            from backend.core.utils import fetch_all_as_dict
            
            # Single query to fetch all events for all games
            placeholders = ','.join(['?'] * len(game_gids))
            query = f"""
                SELECT
                    le.*,
                    g.gid, g.name as game_name, g.ods_db,
                    ec.name as category_name,
                    (SELECT COUNT(*) FROM event_params ep 
                     WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
                FROM log_events le
                LEFT JOIN games g ON le.game_gid = g.gid
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE le.game_gid IN ({placeholders})
                ORDER BY le.id DESC
            """
            
            all_events = fetch_all_as_dict(query, tuple(game_gids))
            
            # Group events by game_gid
            events_by_game: Dict[int, List[Dict[str, Any]]] = {}
            for event in all_events:
                game_gid = event['game_gid']
                if game_gid not in events_by_game:
                    events_by_game[game_gid] = []
                events_by_game[game_gid].append(event)
            
            # Return events in the same order as requested game_gids
            result = [events_by_game.get(gid, []) for gid in game_gids]
            
            logger.debug(f"EventLoader: loaded {len(all_events)} events for {len(game_gids)} games")
            
            return Promise.resolve(result)
            
        except Exception as e:
            logger.error(f"EventLoader error: {e}", exc_info=True)
            # Return empty lists on error
            return Promise.resolve([[] for _ in game_gids])


# Global singleton instance
event_loader = EventLoader()

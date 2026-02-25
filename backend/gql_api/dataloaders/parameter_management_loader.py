"""
Parameter Management DataLoader

DataLoader for optimizing parameter management queries.
Reduces N+1 query problem by batching parameter fetches.
"""

from promise.dataloader import DataLoader
from promise import Promise
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ParameterManagementLoader(DataLoader):
    """
    DataLoader for parameter management queries.
    
    Batches parameter fetches by event IDs to reduce N+1 queries.
    """
    
    def batch_load_fn(self, event_ids: List[int]) -> Promise:
        """
        Batch load parameters by event IDs.
        
        Args:
            event_ids: List of event IDs to load parameters for
            
        Returns:
            Promise resolving to list of parameter lists
        """
        try:
            from backend.core.data_access import Repositories
            
            repo = Repositories.parameters()
            
            # Batch query: get all parameters for all events
            query = """
                SELECT ep.*, e.event_name, e.event_name_cn, e.game_gid
                FROM event_parameters ep
                JOIN events e ON ep.event_id = e.id
                WHERE ep.event_id IN ({})
                ORDER BY ep.event_id, ep.param_name
            """.format(','.join('?' * len(event_ids)))
            
            all_params = repo.fetch_all(query, event_ids)
            
            # Group by event_id
            params_by_event = {}
            for param in all_params:
                event_id = param['event_id']
                if event_id not in params_by_event:
                    params_by_event[event_id] = []
                params_by_event[event_id].append(param)
            
            # Return in same order as event_ids
            return Promise.resolve([
                params_by_event.get(event_id, [])
                for event_id in event_ids
            ])
            
        except Exception as e:
            logger.error(f"Error in ParameterManagementLoader: {e}")
            # Return empty lists on error
            return Promise.resolve([[] for _ in event_ids])


class CommonParametersLoader(DataLoader):
    """
    DataLoader for common parameters queries.
    
    Batches common parameter fetches by game GIDs.
    """
    
    def batch_load_fn(self, game_gids: List[int]) -> Promise:
        """
        Batch load common parameters by game GIDs.
        
        Args:
            game_gids: List of game GIDs to load common parameters for
            
        Returns:
            Promise resolving to list of common parameter lists
        """
        try:
            from backend.core.data_access import Repositories
            
            repo = Repositories.parameters()
            
            # Batch query: get common parameters for all games
            query = """
                SELECT 
                    ep.param_name,
                    ep.param_type,
                    ep.param_description,
                    COUNT(DISTINCT ep.event_id) as event_count,
                    GROUP_CONCAT(DISTINCT e.event_name) as event_names
                FROM event_parameters ep
                JOIN events e ON ep.event_id = e.id
                WHERE e.game_gid IN ({})
                GROUP BY ep.param_name, ep.param_type, ep.param_description
                HAVING event_count > 1
                ORDER BY event_count DESC
            """.format(','.join('?' * len(game_gids)))
            
            all_common_params = repo.fetch_all(query, game_gids)
            
            # Group by game_gid (simplified - in real implementation, need to track which game each param belongs to)
            params_by_game = {gid: all_common_params for gid in game_gids}
            
            # Return in same order as game_gids
            return Promise.resolve([
                params_by_game.get(gid, [])
                for gid in game_gids
            ])
            
        except Exception as e:
            logger.error(f"Error in CommonParametersLoader: {e}")
            # Return empty lists on error
            return Promise.resolve([[] for _ in game_gids])


# Global loader instances
_parameter_management_loader = None
_common_parameters_loader = None


def get_parameter_management_loader() -> ParameterManagementLoader:
    """Get or create parameter management loader instance"""
    global _parameter_management_loader
    if _parameter_management_loader is None:
        _parameter_management_loader = ParameterManagementLoader()
    return _parameter_management_loader


def get_common_parameters_loader() -> CommonParametersLoader:
    """Get or create common parameters loader instance"""
    global _common_parameters_loader
    if _common_parameters_loader is None:
        _common_parameters_loader = CommonParametersLoader()
    return _common_parameters_loader

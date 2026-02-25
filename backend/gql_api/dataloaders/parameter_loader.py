"""
Parameter DataLoader

Implements batch loading for event parameters to prevent N+1 queries.
"""

from promise.dataloader import DataLoader
from promise import Promise
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ParameterLoader(DataLoader):
    """
    Parameter DataLoader
    
    Batches parameter loading requests to prevent N+1 queries.
    Instead of loading parameters one by one for each event,
    it collects all event_ids and loads all parameters in a single query.
    """
    
    def batch_load_fn(self, event_ids: List[int]) -> Promise[List[List[Dict[str, Any]]]]:
        """
        Batch load parameters for multiple events.
        
        Args:
            event_ids: List of event IDs to load parameters for
            
        Returns:
            Promise resolving to list of parameter lists (one list per event_id)
        """
        logger.debug(f"ParameterLoader: batch loading parameters for {len(event_ids)} events")
        
        try:
            # Import here to avoid circular dependencies
            from backend.core.utils import fetch_all_as_dict
            
            # Single query to fetch all parameters for all events
            placeholders = ','.join(['?'] * len(event_ids))
            query = f"""
                SELECT
                    ep.id,
                    ep.event_id,
                    ep.param_name,
                    ep.param_name_cn,
                    ep.template_id,
                    pt.template_name as param_type,
                    ep.param_description,
                    ep.json_path,
                    ep.is_active,
                    ep.version,
                    ep.created_at,
                    ep.updated_at
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id IN ({placeholders}) AND ep.is_active = 1
                ORDER BY ep.id
            """
            
            all_params = fetch_all_as_dict(query, tuple(event_ids))
            
            # Group parameters by event_id
            params_by_event: Dict[int, List[Dict[str, Any]]] = {}
            for param in all_params:
                event_id = param['event_id']
                if event_id not in params_by_event:
                    params_by_event[event_id] = []
                params_by_event[event_id].append(param)
            
            # Return parameters in the same order as requested event_ids
            result = [params_by_event.get(eid, []) for eid in event_ids]
            
            logger.debug(f"ParameterLoader: loaded {len(all_params)} parameters for {len(event_ids)} events")
            
            return Promise.resolve(result)
            
        except Exception as e:
            logger.error(f"ParameterLoader error: {e}", exc_info=True)
            # Return empty lists on error
            return Promise.resolve([[] for _ in event_ids])


# Global singleton instance
parameter_loader = ParameterLoader()

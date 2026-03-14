"""
Enhanced Parameter DataLoader

Optimized batch loader for event parameters with additional convenience methods.
"""

import logging
from typing import Any, Dict, List

from promise import Promise
from promise.dataloader import DataLoader

from backend.core.database import get_db_connection
from backend.gql_api.dataloaders.optimized_loaders import CachedDataLoader

logger = logging.getLogger(__name__)


class ParameterLoaderEnhanced(DataLoader):
    """
    Enhanced Parameter DataLoader with convenience methods.

    Batches parameter fetches by event IDs to reduce N+1 queries.
    """

    def __init__(self):
        super().__init__(load_fn=self._batch_load_parameters)
        self.cache_loader = CachedDataLoader('parameters')

    def load_by_event(self, event_id: int):
        """
        Load all parameters for a single event.

        Args:
            event_id: Event ID

        Returns:
            Promise: List of parameters
        """
        return self.load(event_id)

    def load_by_events(self, event_ids: List[int]):
        """
        Load parameters for multiple events.

        Args:
            event_ids: List of event IDs

        Returns:
            Promise: List of parameter lists
        """
        return self.load_many(event_ids)

    def _batch_load_parameters(self, event_ids: List[int]) -> Promise:
        """
        Batch load parameters by event IDs.

        Args:
            event_ids: List of event IDs to load parameters for

        Returns:
            Promise resolving to list of parameter lists
        """

        def load_from_db(ids: List[int]) -> List[List[Dict]]:
            """从数据库批量加载"""
            conn = get_db_connection()
            cursor = conn.cursor()

            # 一次性查询所有事件的参数(包括模板信息)
            placeholders = ','.join('?' * len(ids))
            cursor.execute(
                f"""
                SELECT
                    ep.*,
                    pt.name as template_name,
                    pt.description as template_description
                FROM event_params ep
                LEFT JOIN param_templates pt ON ep.template_id = pt.id
                WHERE ep.event_id IN ({placeholders})
                ORDER BY ep.event_id, ep.id
            """,
                ids,
            )

            rows = cursor.fetchall()
            conn.close()

            # 按事件ID分组
            params_by_event = {eid: [] for eid in ids}
            for row in rows:
                param = dict(row)
                event_id = param['event_id']
                params_by_event[event_id].append(param)

            # 按请求顺序返回
            return [params_by_event.get(eid, []) for eid in ids]

        return self.cache_loader._batch_load_with_cache(
            event_ids, load_from_db, ttl_l1=60, ttl_l2=300
        )


# Global loader instance
_parameter_loader_enhanced = None


def get_parameter_loader_enhanced() -> ParameterLoaderEnhanced:
    """Get or create enhanced parameter loader instance"""
    global _parameter_loader_enhanced
    if _parameter_loader_enhanced is None:
        _parameter_loader_enhanced = ParameterLoaderEnhanced()
    return _parameter_loader_enhanced

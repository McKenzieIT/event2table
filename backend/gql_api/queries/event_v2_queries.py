"""
Event V2 Queries

Implements GraphQL query resolvers for Event V2 API with pagination.
"""

import graphene
from graphene import Field, List, Int, String
from typing import List as TypingList, Dict, Any
import logging
import math

logger = logging.getLogger(__name__)


class EventV2Queries:
    """Event V2-related GraphQL queries"""
    
    @staticmethod
    def resolve_events_v2(root, info, game_gid: int, page: int = 1, per_page: int = 20, category: str = None):
        """
        Resolve paginated list of events (V2 API).
        
        Args:
            game_gid: Game business GID (required)
            page: Page number (default: 1)
            per_page: Items per page (default: 20, max: 100)
            category: Filter by category (optional)
        """
        try:
            from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict
            from backend.gql_api.types.event_v2_type import PaginatedEventsV2, EventV2Type, PaginationInfo
            
            # Validate and limit per_page
            per_page = min(per_page, 100)
            offset = (page - 1) * per_page
            
            # Build query
            where_clauses = ["le.game_gid = ?"]
            params = [game_gid]
            
            if category:
                where_clauses.append("ec.name = ?")
                params.append(category)
            
            where_sql = " AND ".join(where_clauses)
            
            # Get total count
            count_query = f"""
                SELECT COUNT(DISTINCT le.id) as total
                FROM log_events le
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE {where_sql}
            """
            count_result = fetch_one_as_dict(count_query, tuple(params))
            total = count_result['total'] if count_result else 0
            
            # Calculate pagination
            total_pages = math.ceil(total / per_page) if total > 0 else 1
            
            # Get events
            events_query = f"""
                SELECT
                    le.id,
                    le.event_name,
                    le.event_name_cn,
                    le.description,
                    le.is_active,
                    le.category_id,
                    le.game_gid,
                    le.created_at,
                    le.updated_at
                FROM log_events le
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE {where_sql}
                ORDER BY le.id
                LIMIT ? OFFSET ?
            """
            params.extend([per_page, offset])
            events = fetch_all_as_dict(events_query, tuple(params))
            
            # Build pagination info
            pagination_info = {
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
            
            # Build result
            result = {
                'data': events,
                'pagination': pagination_info
            }
            
            return PaginatedEventsV2.from_dict(result)
            
        except Exception as e:
            logger.error(f"Error resolving events V2: {e}", exc_info=True)
            # Return empty paginated result on error
            return PaginatedEventsV2(
                data=[],
                pagination=PaginationInfo(
                    total=0,
                    page=page,
                    per_page=per_page,
                    total_pages=1
                )
            )

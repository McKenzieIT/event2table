"""
Event Mutations

Implements GraphQL mutation resolvers for Event entity.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class CreateEvent(graphene.Mutation):
    """Create a new event"""
    
    class Arguments:
        game_gid = Int(required=True, description="游戏GID")
        event_name = String(required=True, description="事件英文名")
        event_name_cn = String(required=True, description="事件中文名")
        category_id = Int(required=True, description="分类ID")
        include_in_common_params = Boolean(default_value=False, description="是否包含在公共参数中")
    
    ok = Boolean(description="操作是否成功")
    event = Field(lambda: __import__('backend.gql_api.types.event_type', fromlist=['EventType']).EventType, description="创建的事件")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, game_gid: int, event_name: str, event_name_cn: str, 
               category_id: int, include_in_common_params: bool = False):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.event_type import EventType
            
            # Validate game exists
            game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
            if not game:
                return CreateEvent(ok=False, errors=[f"Game {game_gid} not found"])
            
            # Generate table names
            ods_db = game['ods_db']
            source_table = f"{ods_db}.ods_{game_gid}_all_view"
            dwd_prefix = "ieu_cdm" if ods_db == "ieu_ods" else ods_db
            clean_name = event_name.replace(".", "_")
            target_table = f"{dwd_prefix}.v_dwd_{game_gid}_{clean_name}_di"
            
            # Create event
            event_id = execute_write(
                """INSERT INTO log_events 
                   (game_gid, event_name, event_name_cn, category_id, source_table, target_table, include_in_common_params)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (game_gid, event_name, event_name_cn, category_id, source_table, target_table, 
                 1 if include_in_common_params else 0),
                return_last_id=True
            )
            
            # Clear cache
            clear_cache_pattern(f"events:{game_gid}:*")
            clear_cache_pattern("dashboard_statistics")
            
            logger.info(f"Event created via GraphQL: {event_name} (ID: {event_id})")
            
            # Return created event
            event = fetch_one_as_dict(
                """
                SELECT le.*, ec.name as category_name
                FROM log_events le
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE le.id = ?
                """,
                (event_id,)
            )
            
            return CreateEvent(ok=True, event=EventType.from_dict(event) if event else None)
            
        except Exception as e:
            logger.error(f"Error creating event: {e}", exc_info=True)
            return CreateEvent(ok=False, errors=[str(e)])


class UpdateEvent(graphene.Mutation):
    """Update an existing event"""
    
    class Arguments:
        id = Int(required=True, description="事件ID")
        event_name_cn = String(description="事件中文名")
        category_id = Int(description="分类ID")
        include_in_common_params = Boolean(description="是否包含在公共参数中")
    
    ok = Boolean(description="操作是否成功")
    event = Field(lambda: __import__('backend.gql_api.types.event_type', fromlist=['EventType']).EventType, description="更新的事件")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, id: int, event_name_cn: str = None, category_id: int = None,
               include_in_common_params: bool = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            
            # Check if event exists
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (id,))
            if not event:
                return UpdateEvent(ok=False, errors=["Event not found"])
            
            # Build update query
            updates = []
            params = []
            
            if event_name_cn:
                updates.append("event_name_cn = ?")
                params.append(event_name_cn)
            
            if category_id:
                updates.append("category_id = ?")
                params.append(category_id)
            
            if include_in_common_params is not None:
                updates.append("include_in_common_params = ?")
                params.append(1 if include_in_common_params else 0)
            
            if not updates:
                return UpdateEvent(ok=False, errors=["No fields to update"])
            
            params.append(id)
            query = f"UPDATE log_events SET {', '.join(updates)} WHERE id = ?"
            
            execute_write(query, tuple(params))
            
            # Clear cache
            clear_cache_pattern(f"events:{event['game_gid']}:*")
            clear_cache_pattern("dashboard_statistics")
            
            logger.info(f"Event updated via GraphQL: ID {id}")
            
            # Return updated event
            updated_event = fetch_one_as_dict(
                """
                SELECT le.*, ec.name as category_name
                FROM log_events le
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                WHERE le.id = ?
                """,
                (id,)
            )
            
            return UpdateEvent(ok=True, event=EventType.from_dict(updated_event) if updated_event else None)
            
        except Exception as e:
            logger.error(f"Error updating event: {e}", exc_info=True)
            return UpdateEvent(ok=False, errors=[str(e)])


class DeleteEvent(graphene.Mutation):
    """Delete an event"""
    
    class Arguments:
        id = Int(required=True, description="事件ID")
    
    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")
    
    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            
            # Check if event exists
            event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (id,))
            if not event:
                return DeleteEvent(ok=False, errors=["Event not found"])
            
            game_gid = event['game_gid']
            
            # Delete associated parameters
            execute_write("DELETE FROM event_params WHERE event_id = ?", (id,))
            
            # Delete event
            execute_write("DELETE FROM log_events WHERE id = ?", (id,))
            
            # Clear cache
            clear_cache_pattern(f"events:{game_gid}:*")
            clear_cache_pattern("dashboard_statistics")
            
            logger.info(f"Event deleted via GraphQL: ID {id}")
            
            return DeleteEvent(ok=True, message="Event deleted successfully")
            
        except Exception as e:
            logger.error(f"Error deleting event: {e}", exc_info=True)
            return DeleteEvent(ok=False, errors=[str(e)])


class EventMutations:
    """Container for event mutations"""
    CreateEvent = CreateEvent
    UpdateEvent = UpdateEvent
    DeleteEvent = DeleteEvent

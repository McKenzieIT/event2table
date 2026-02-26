"""
Event V2 Mutations

Implements GraphQL mutation resolvers for Event V2 API.
"""

import graphene
from graphene import Field, Int, String, Boolean, List
import logging

logger = logging.getLogger(__name__)


class EventV2Mutations:
    """Event V2-related GraphQL mutations"""
    
    class CreateEventV2(graphene.Mutation):
        """Create a new event (V2 API)"""
        
        class Arguments:
            input = graphene.Argument(
                lambda: __import__('backend.gql_api.types.event_v2_type', fromlist=['EventV2CreateInput']).EventV2CreateInput,
                required=True,
                description="创建事件输入"
            )
        
        Output = lambda: __import__('backend.gql_api.types.event_v2_type', fromlist=['EventV2Result']).EventV2Result
        
        def mutate(self, info, input):
            """Execute the mutation"""
            try:
                from backend.core.utils import execute_insert, fetch_one_as_dict
                from backend.gql_api.types.event_v2_type import EventV2Type, EventV2Result
                from datetime import datetime
                
                # Check if game exists
                game = fetch_one_as_dict("SELECT id FROM games WHERE gid = ?", (input.game_gid,))
                if not game:
                    return EventV2Result.error_result(
                        errors=[f"Game with GID {input.game_gid} not found"],
                        message="游戏不存在"
                    )
                
                # Check if event name already exists in this game
                existing_event = fetch_one_as_dict(
                    "SELECT id FROM log_events WHERE game_gid = ? AND event_name = ?",
                    (input.game_gid, input.event_name)
                )
                if existing_event:
                    return EventV2Result.error_result(
                        errors=[f"Event '{input.event_name}' already exists in this game"],
                        message="事件已存在"
                    )
                
                # Create event
                now = datetime.utcnow().isoformat()
                event_id = execute_insert(
                    """
                    INSERT INTO log_events (event_name, event_name_cn, description, is_active, category_id, game_gid, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        input.event_name,
                        input.event_name_cn,
                        input.description,
                        input.is_active if input.is_active is not None else True,
                        input.category_id,
                        input.game_gid,
                        now,
                        now
                    )
                )
                
                # Fetch created event
                event_data = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (event_id,))
                event = EventV2Type.from_dict(event_data)
                
                logger.info(f"Event created via GraphQL V2: {input.event_name} (Game GID: {input.game_gid})")
                
                return EventV2Result.success_result(event, "事件创建成功")
            
            except Exception as e:
                logger.error(f"Error creating event: {e}", exc_info=True)
                return EventV2Result.error_result(errors=[str(e)], message="创建失败")
    
    class UpdateEventV2(graphene.Mutation):
        """Update an existing event (V2 API)"""
        
        class Arguments:
            id = Int(required=True, description="事件ID")
            input = graphene.Argument(
                lambda: __import__('backend.gql_api.types.event_v2_type', fromlist=['EventV2UpdateInput']).EventV2UpdateInput,
                required=True,
                description="更新事件输入"
            )
        
        Output = lambda: __import__('backend.gql_api.types.event_v2_type', fromlist=['EventV2Result']).EventV2Result
        
        def mutate(self, info, id: int, input):
            """Execute the mutation"""
            try:
                from backend.core.utils import execute_update, fetch_one_as_dict
                from backend.gql_api.types.event_v2_type import EventV2Type, EventV2Result
                from datetime import datetime
                
                # Check if event exists
                event = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (id,))
                if not event:
                    return EventV2Result.error_result(
                        errors=[f"Event with ID {id} not found"],
                        message="事件不存在"
                    )
                
                # Build update query
                update_fields = []
                params = []
                
                if input.event_name is not None:
                    # Check if new name conflicts with existing event
                    if input.event_name != event['event_name']:
                        existing = fetch_one_as_dict(
                            "SELECT id FROM log_events WHERE game_gid = ? AND event_name = ? AND id != ?",
                            (event['game_gid'], input.event_name, id)
                        )
                        if existing:
                            return EventV2Result.error_result(
                                errors=[f"Event '{input.event_name}' already exists in this game"],
                                message="事件名称冲突"
                            )
                    update_fields.append("event_name = ?")
                    params.append(input.event_name)
                
                if input.event_name_cn is not None:
                    update_fields.append("event_name_cn = ?")
                    params.append(input.event_name_cn)
                
                if input.description is not None:
                    update_fields.append("description = ?")
                    params.append(input.description)
                
                if input.is_active is not None:
                    update_fields.append("is_active = ?")
                    params.append(input.is_active)
                
                if input.category_id is not None:
                    update_fields.append("category_id = ?")
                    params.append(input.category_id)
                
                if not update_fields:
                    return EventV2Result.error_result(
                        errors=["No fields to update"],
                        message="无更新内容"
                    )
                
                # Add updated_at
                update_fields.append("updated_at = ?")
                params.append(datetime.utcnow().isoformat())
                
                # Add event ID
                params.append(id)
                
                # Execute update
                query = f"UPDATE log_events SET {', '.join(update_fields)} WHERE id = ?"
                execute_update(query, tuple(params))
                
                # Fetch updated event
                event_data = fetch_one_as_dict("SELECT * FROM log_events WHERE id = ?", (id,))
                event = EventV2Type.from_dict(event_data)
                
                logger.info(f"Event updated via GraphQL V2: ID {id}")
                
                return EventV2Result.success_result(event, "事件更新成功")
            
            except Exception as e:
                logger.error(f"Error updating event: {e}", exc_info=True)
                return EventV2Result.error_result(errors=[str(e)], message="更新失败")
    
    class DeleteEventV2(graphene.Mutation):
        """Delete an event (V2 API)"""
        
        class Arguments:
            id = Int(required=True, description="事件ID")
        
        Output = lambda: __import__('backend.gql_api.types.game_v2_type', fromlist=['OperationResult']).OperationResult
        
        def mutate(self, info, id: int):
            """Execute the mutation"""
            try:
                from backend.core.utils import execute_update, fetch_one_as_dict
                from backend.gql_api.types.game_v2_type import OperationResult
                
                # Check if event exists
                event = fetch_one_as_dict("SELECT id, event_name FROM log_events WHERE id = ?", (id,))
                if not event:
                    return OperationResult.error_result(
                        errors=[f"Event with ID {id} not found"],
                        message="事件不存在"
                    )
                
                # Delete event (cascade will delete parameters)
                execute_update("DELETE FROM log_events WHERE id = ?", (id,))
                
                logger.info(f"Event deleted via GraphQL V2: ID {id}, Name: {event['event_name']}")
                
                return OperationResult.success_result("事件删除成功")
            
            except Exception as e:
                logger.error(f"Error deleting event: {e}", exc_info=True)
                return OperationResult.error_result(errors=[str(e)], message="删除失败")
    
    # Expose mutations as fields
    create_event_v2 = CreateEventV2.Field()
    update_event_v2 = UpdateEventV2.Field()
    delete_event_v2 = DeleteEventV2.Field()

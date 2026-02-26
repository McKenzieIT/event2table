"""
GraphQL Schema V2 Extension

Extends the main GraphQL schema with V2 API support.
"""

import graphene
from graphene import ObjectType, Field, List, Int, String, Boolean
import logging

# Import V2 Types
from backend.gql_api.types.game_v2_type import (
    GameV2Type,
    GameV2CreateInput,
    GameV2UpdateInput,
    GameV2Result,
    BatchOperationResult,
    OperationResult
)
from backend.gql_api.types.event_v2_type import (
    EventV2Type,
    EventV2CreateInput,
    EventV2UpdateInput,
    EventV2Result,
    PaginatedEventsV2,
    PaginationInfo
)

# Import V2 Queries
from backend.gql_api.queries.game_v2_queries import GameV2Queries
from backend.gql_api.queries.event_v2_queries import EventV2Queries

# Import V2 Mutations
from backend.gql_api.mutations.game_v2_mutations import GameV2Mutations
from backend.gql_api.mutations.event_v2_mutations import EventV2Mutations

logger = logging.getLogger(__name__)


class V2Query(ObjectType):
    """
    V2 GraphQL Query Root Type
    
    Provides all V2 query operations for the API.
    """
    
    # Games V2 queries
    games_v2 = List(
        GameV2Type,
        description="获取所有游戏 (V2 API)"
    )
    
    game_v2 = Field(
        GameV2Type,
        gid=Int(required=True),
        description="根据GID获取单个游戏 (V2 API)"
    )
    
    # Events V2 queries
    events_v2 = Field(
        PaginatedEventsV2,
        game_gid=Int(required=True),
        page=Int(default_value=1),
        per_page=Int(default_value=20),
        category=String(),
        description="获取分页事件列表 (V2 API)"
    )
    
    # Resolvers
    def resolve_games_v2(self, info):
        """Resolve games V2 list"""
        return GameV2Queries.resolve_games_v2(self, info)
    
    def resolve_game_v2(self, info, gid):
        """Resolve single game V2"""
        return GameV2Queries.resolve_game_v2(self, info, gid)
    
    def resolve_events_v2(self, info, game_gid, page=1, per_page=20, category=None):
        """Resolve events V2 list with pagination"""
        return EventV2Queries.resolve_events_v2(self, info, game_gid, page, per_page, category)


class V2Mutation(ObjectType):
    """
    V2 GraphQL Mutation Root Type
    
    Provides all V2 mutation operations for the API.
    """
    
    # Games V2 mutations
    create_game_v2 = GameV2Mutations.CreateGameV2.Field()
    update_game_v2 = GameV2Mutations.UpdateGameV2.Field()
    delete_game_v2 = GameV2Mutations.DeleteGameV2.Field()
    batch_delete_games_v2 = GameV2Mutations.BatchDeleteGamesV2.Field()
    
    # Events V2 mutations
    create_event_v2 = EventV2Mutations.CreateEventV2.Field()
    update_event_v2 = EventV2Mutations.UpdateEventV2.Field()
    delete_event_v2 = EventV2Mutations.DeleteEventV2.Field()


def extend_schema_with_v2(schema):
    """
    Extend existing schema with V2 types and operations.
    
    Args:
        schema: Existing GraphQL schema
    
    Returns:
        Extended schema with V2 support
    """
    # This function can be used to dynamically extend the schema
    # For now, we'll use the separate V2Query and V2Mutation classes
    return schema


# Create V2 schema
v2_schema = graphene.Schema(query=V2Query, mutation=V2Mutation)

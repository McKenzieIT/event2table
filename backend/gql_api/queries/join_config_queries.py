"""
Join Config GraphQL Queries

Query resolvers for join configuration management.
"""

import graphene
from graphene import ObjectType, Field, List, Int, String
import logging
from typing import Optional, List as ListType

logger = logging.getLogger(__name__)


class JoinConfigQueries(ObjectType):
    """
    Join Configuration Queries
    """
    
    join_config = Field(
        'backend.gql_api.types.join_config_type.JoinConfigType',
        id=Int(required=True),
        description="Get a single join configuration by ID"
    )
    
    join_configs = List(
        'backend.gql_api.types.join_config_type.JoinConfigType',
        gameId=Int(),
        joinType=String(),
        limit=Int(default_value=50),
        offset=Int(default_value=0),
        description="Get list of join configurations with optional filtering"
    )
    
    def resolve_join_config(self, info, id):
        """Resolve single join configuration"""
        try:
            from backend.core.data_access import Repositories
            
            repo = Repositories.join_configs()
            config = repo.get_by_id(id)
            
            if not config:
                return None
            
            return config
            
        except Exception as e:
            logger.error(f"Error fetching join config {id}: {e}")
            return None
    
    def resolve_join_configs(self, info, gameId=None, joinType=None, limit=50, offset=0):
        """Resolve list of join configurations"""
        try:
            from backend.core.data_access import Repositories
            
            repo = Repositories.join_configs()
            
            # Build query
            query = "SELECT * FROM join_configs WHERE 1=1"
            params = []
            
            if gameId:
                query += " AND game_id = ?"
                params.append(gameId)
            
            if joinType:
                query += " AND join_type = ?"
                params.append(joinType)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            configs = repo.fetch_all(query, params)
            
            return configs
            
        except Exception as e:
            logger.error(f"Error fetching join configs: {e}")
            return []

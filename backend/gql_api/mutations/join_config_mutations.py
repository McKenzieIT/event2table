"""
Join Config GraphQL Mutations

Mutation resolvers for join configuration management.
"""

import graphene
from graphene import Mutation, String, Int, Boolean, Field, List, ObjectType
import logging
import json

logger = logging.getLogger(__name__)


class CreateJoinConfig(Mutation):
    """
    Create a new join configuration
    """
    class Arguments:
        gameId = Int(required=True)
        name = String(required=True)
        displayName = String()
        sourceEvents = String()
        joinCondition = String()
        outputFields = String()
        outputTable = String()
        joinType = String()
        whereConditions = String()
        fieldMappings = String()
        description = String()
    
    ok = Boolean()
    joinConfig = Field('backend.gql_api.types.join_config_type.JoinConfigType')
    errors = List(String)
    
    def mutate(self, info, gameId, name, **kwargs):
        """Create join configuration"""
        try:
            from backend.core.data_access import Repositories
            from backend.core.cache.cache_system import clear_cache_pattern
            
            repo = Repositories.join_configs()
            
            # Prepare data
            data = {
                'game_id': gameId,
                'name': name,
                'display_name': kwargs.get('displayName'),
                'source_events': kwargs.get('sourceEvents'),
                'join_condition': kwargs.get('joinCondition'),
                'output_fields': kwargs.get('outputFields'),
                'output_table': kwargs.get('outputTable'),
                'join_type': kwargs.get('joinType'),
                'where_conditions': kwargs.get('whereConditions'),
                'field_mappings': kwargs.get('fieldMappings'),
                'description': kwargs.get('description'),
            }
            
            # Insert
            config_id = repo.insert(data)
            
            # Clear cache
            clear_cache_pattern(f"join_configs:*")
            
            # Fetch created config
            config = repo.get_by_id(config_id)
            
            return CreateJoinConfig(
                ok=True,
                joinConfig=config,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error creating join config: {e}")
            return CreateJoinConfig(
                ok=False,
                joinConfig=None,
                errors=[str(e)]
            )


class UpdateJoinConfig(Mutation):
    """
    Update an existing join configuration
    """
    class Arguments:
        id = Int(required=True)
        name = String()
        displayName = String()
        sourceEvents = String()
        joinCondition = String()
        outputFields = String()
        outputTable = String()
        joinType = String()
        whereConditions = String()
        fieldMappings = String()
        description = String()
    
    ok = Boolean()
    joinConfig = Field('backend.gql_api.types.join_config_type.JoinConfigType')
    errors = List(String)
    
    def mutate(self, info, id, **kwargs):
        """Update join configuration"""
        try:
            from backend.core.data_access import Repositories
            from backend.core.cache.cache_system import clear_cache_pattern
            
            repo = Repositories.join_configs()
            
            # Prepare update data
            update_data = {}
            if kwargs.get('name'):
                update_data['name'] = kwargs['name']
            if kwargs.get('displayName'):
                update_data['display_name'] = kwargs['displayName']
            if kwargs.get('sourceEvents'):
                update_data['source_events'] = kwargs['sourceEvents']
            if kwargs.get('joinCondition'):
                update_data['join_condition'] = kwargs['joinCondition']
            if kwargs.get('outputFields'):
                update_data['output_fields'] = kwargs['outputFields']
            if kwargs.get('outputTable'):
                update_data['output_table'] = kwargs['outputTable']
            if kwargs.get('joinType'):
                update_data['join_type'] = kwargs['joinType']
            if kwargs.get('whereConditions'):
                update_data['where_conditions'] = kwargs['whereConditions']
            if kwargs.get('fieldMappings'):
                update_data['field_mappings'] = kwargs['fieldMappings']
            if kwargs.get('description'):
                update_data['description'] = kwargs['description']
            
            # Update
            repo.update(id, update_data)
            
            # Clear cache
            clear_cache_pattern(f"join_configs:*")
            
            # Fetch updated config
            config = repo.get_by_id(id)
            
            return UpdateJoinConfig(
                ok=True,
                joinConfig=config,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error updating join config {id}: {e}")
            return UpdateJoinConfig(
                ok=False,
                joinConfig=None,
                errors=[str(e)]
            )


class DeleteJoinConfig(Mutation):
    """
    Delete a join configuration
    """
    class Arguments:
        id = Int(required=True)
    
    ok = Boolean()
    message = String()
    errors = List(String)
    
    def mutate(self, info, id):
        """Delete join configuration"""
        try:
            from backend.core.data_access import Repositories
            from backend.core.cache.cache_system import clear_cache_pattern
            
            repo = Repositories.join_configs()
            
            # Delete
            repo.delete(id)
            
            # Clear cache
            clear_cache_pattern(f"join_configs:*")
            
            return DeleteJoinConfig(
                ok=True,
                message="Join configuration deleted successfully",
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error deleting join config {id}: {e}")
            return DeleteJoinConfig(
                ok=False,
                message="",
                errors=[str(e)]
            )


class JoinConfigMutations(ObjectType):
    """
    Join Configuration Mutations
    """
    create_join_config = CreateJoinConfig.Field()
    update_join_config = UpdateJoinConfig.Field()
    delete_join_config = DeleteJoinConfig.Field()

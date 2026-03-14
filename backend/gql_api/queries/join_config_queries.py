"""
Join Config GraphQL Queries

Query resolvers for join configuration management.
"""

import logging
from typing import List as ListType
from typing import Optional

import graphene
from graphene import Field, Int, List, ObjectType, String

logger = logging.getLogger(__name__)


class JoinConfigQueries(ObjectType):
    """
    Join Configuration Queries
    """

    join_config = Field(
        'backend.gql_api.types.join_config_type.JoinConfigType',
        id=Int(required=True),
        description="Get a single join configuration by ID",
    )

    join_configs = List(
        'backend.gql_api.types.join_config_type.JoinConfigType',
        game_gid=Int(),
        joinType=graphene.Argument(
            'backend.gql_api.types.join_config_type.JoinTypeEnum', required=False
        ),
        limit=Int(default_value=50),
        offset=Int(default_value=0),
        description="Get list of join configurations with optional filtering",
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

    def resolve_join_configs(self, info, game_gid=None, joinType=None, limit=50, offset=0):
        """Resolve list of join configurations"""
        try:
            from backend.core.data_access import Repositories

            repo = Repositories.join_configs()

            # Build query
            query = "SELECT * FROM join_configs WHERE 1=1"
            params = []

            if game_gid:
                query += " AND game_gid = ?"
                params.append(game_gid)

            if joinType:
                # Handle enum value - extract the value if it's an enum
                join_type_value = joinType.value if hasattr(joinType, 'value') else joinType
                query += " AND join_type = ?"
                params.append(join_type_value)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            configs = repo.fetch_all(query, params)

            return configs

        except Exception as e:
            logger.error(f"Error fetching join configs: {e}")
            return []

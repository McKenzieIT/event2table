"""
Join Config GraphQL Type

GraphQL type definitions for join configuration management.
"""

from datetime import datetime

import graphene
from graphene import Boolean, Enum, Field, Int, List, ObjectType, String


class JoinTypeEnum(Enum):
    """
    Join Type Enumeration

    Defines the supported join types for multi-event queries.
    """

    LEFT_JOIN = "LEFT"  # LEFT JOIN
    RIGHT_JOIN = "RIGHT"  # RIGHT JOIN
    INNER_JOIN = "INNER"  # INNER JOIN
    FULL_JOIN = "FULL"  # FULL JOIN

    class Meta:
        description = "Join type enumeration for multi-event queries"


class JoinConfigType(ObjectType):
    """
    Join Configuration Type

    Represents a join configuration for multi-event queries.
    """

    id = Int(required=True)
    game_gid = Int(required=True)
    name = String(required=True)
    displayName = String()
    sourceEvents = String()  # JSON string
    joinCondition = String()  # JSON string
    outputFields = String()  # JSON string
    outputTable = String()
    joinType = Field(JoinTypeEnum, description="Join type")
    whereConditions = String()  # JSON string
    fieldMappings = String()  # JSON string
    description = String()
    createdAt = String()
    updatedAt = String()

    class Meta:
        description = "Join configuration for multi-event queries"

    def resolve_createdAt(self, info):
        return (
            self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None
        )

    def resolve_updatedAt(self, info):
        return (
            self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        )


class JoinConfigInput(graphene.InputObjectType):
    """
    Input type for creating/updating join configurations
    """

    game_gid = Int(required=True)
    name = String(required=True)
    displayName = String()
    sourceEvents = String()
    joinCondition = String()
    outputFields = String()
    outputTable = String()
    joinType = graphene.Argument(JoinTypeEnum, required=False)
    whereConditions = String()
    fieldMappings = String()
    description = String()

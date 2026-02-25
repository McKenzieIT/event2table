"""
Join Config GraphQL Type

GraphQL type definitions for join configuration management.
"""

import graphene
from graphene import ObjectType, Int, String, List, Boolean, Field
from datetime import datetime


class JoinConfigType(ObjectType):
    """
    Join Configuration Type
    
    Represents a join configuration for multi-event queries.
    """
    id = Int(required=True)
    gameId = Int(required=True)
    name = String(required=True)
    displayName = String()
    sourceEvents = String()  # JSON string
    joinCondition = String()  # JSON string
    outputFields = String()  # JSON string
    outputTable = String()
    joinType = String()
    whereConditions = String()  # JSON string
    fieldMappings = String()  # JSON string
    description = String()
    createdAt = String()
    updatedAt = String()
    
    class Meta:
        description = "Join configuration for multi-event queries"
    
    def resolve_createdAt(self, info):
        return self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None
    
    def resolve_updatedAt(self, info):
        return self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None


class JoinConfigInput(graphene.InputObjectType):
    """
    Input type for creating/updating join configurations
    """
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

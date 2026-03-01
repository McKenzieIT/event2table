"""
Field Builder GraphQL Types

GraphQL type definitions for field builder configuration management.
This module provides comprehensive types for the Field Builder API migration to GraphQL.
"""

import graphene
from graphene import ObjectType, Int, String, List, Boolean, Field, InputObjectType, JSONString
from datetime import datetime


# ============================================
# Input Types
# ============================================

class ViewConfigInput(InputObjectType):
    """
    View configuration input type

    Defines the view-level settings for field builder configuration.
    """
    gameGid = Int(required=True, description="Game GID")
    dateVar = String(default_value="${bizdate}", description="Date variable for partitioning")
    outputTable = String(description="Output table name")


class BaseFieldInput(InputObjectType):
    """
    Base field input type

    Represents a base field from source events.
    """
    eventId = Int(required=True, description="Source event ID")
    eventName = String(required=True, description="Event name for alias")
    fieldName = String(required=True, description="Field name in the event")
    alias = String(description="Output field alias")
    fieldType = String(default_value="base", description="Field type: base, param, custom, fixed")


class ParamFieldInput(InputObjectType):
    """
    Parameter field input type

    Represents a parameter field with JSON path extraction.
    """
    eventId = Int(required=True, description="Source event ID")
    eventName = String(required=True, description="Event name for alias")
    paramName = String(required=True, description="Parameter name")
    jsonPath = String(required=True, description="JSON path for extraction")
    alias = String(description="Output field alias")
    fieldType = String(default_value="param", description="Field type")


class CustomFieldInput(InputObjectType):
    """
    Custom field input type

    Represents a custom HQL expression field.
    """
    name = String(required=True, description="Field name")
    expression = String(required=True, description="HQL expression")
    alias = String(description="Output field alias")
    fieldType = String(default_value="custom", description="Field type")


class FixedFieldInput(InputObjectType):
    """
    Fixed field input type

    Represents a fixed value field.
    """
    name = String(required=True, description="Field name")
    value = String(required=True, description="Fixed value")
    alias = String(description="Output field alias")
    fieldType = String(default_value="fixed", description="Field type")


class FieldMappingV2Input(InputObjectType):
    """
    Field mapping v2 input type

    Complete field mapping configuration for field builder.
    """
    viewConfig = Field(ViewConfigInput, description="View configuration")
    baseFields = List(BaseFieldInput, description="List of base fields")
    paramFields = List(ParamFieldInput, description="List of parameter fields")
    customFields = List(CustomFieldInput, description="List of custom fields")
    fixedFields = List(FixedFieldInput, description="List of fixed fields")


class FieldBuilderConfigInput(InputObjectType):
    """
    Field builder configuration input type

    Complete configuration for saving a field builder config.
    """
    config = Field(FieldMappingV2Input, required=True, description="Field mapping configuration")
    viewName = String(required=True, description="View/table name")
    displayName = String(description="Display name for the configuration")


# ============================================
# Output Types
# ============================================

class ViewConfigType(ObjectType):
    """
    View configuration output type
    """
    gameGid = Int(required=True, description="Game GID")
    dateVar = String(description="Date variable for partitioning")
    outputTable = String(description="Output table name")

    class Meta:
        description = "View configuration for field builder"


class BaseFieldType(ObjectType):
    """
    Base field output type
    """
    eventId = Int(required=True, description="Source event ID")
    eventName = String(required=True, description="Event name for alias")
    fieldName = String(required=True, description="Field name in the event")
    alias = String(description="Output field alias")
    fieldType = String(description="Field type")

    class Meta:
        description = "Base field from source events"


class ParamFieldType(ObjectType):
    """
    Parameter field output type
    """
    eventId = Int(required=True, description="Source event ID")
    eventName = String(required=True, description="Event name for alias")
    paramName = String(required=True, description="Parameter name")
    jsonPath = String(required=True, description="JSON path for extraction")
    alias = String(description="Output field alias")
    fieldType = String(description="Field type")

    class Meta:
        description = "Parameter field with JSON path extraction"


class CustomFieldType(ObjectType):
    """
    Custom field output type
    """
    name = String(required=True, description="Field name")
    expression = String(required=True, description="HQL expression")
    alias = String(description="Output field alias")
    fieldType = String(description="Field type")

    class Meta:
        description = "Custom HQL expression field"


class FixedFieldType(ObjectType):
    """
    Fixed field output type
    """
    name = String(required=True, description="Field name")
    value = String(required=True, description="Fixed value")
    alias = String(description="Output field alias")
    fieldType = String(description="Field type")

    class Meta:
        description = "Fixed value field"


class FieldMappingV2Type(ObjectType):
    """
    Field mapping v2 output type
    """
    viewConfig = Field(ViewConfigType, description="View configuration")
    baseFields = List(BaseFieldType, description="List of base fields")
    paramFields = List(ParamFieldType, description="List of parameter fields")
    customFields = List(CustomFieldType, description="List of custom fields")
    fixedFields = List(FixedFieldType, description="List of fixed fields")

    class Meta:
        description = "Complete field mapping configuration"


class FieldBuilderConfigType(ObjectType):
    """
    Field builder configuration output type

    Represents a saved field builder configuration.
    """
    id = Int(required=True, description="Configuration ID")
    config = Field(FieldMappingV2Type, description="Field mapping configuration")
    viewName = String(required=True, description="View/table name")
    displayName = String(description="Display name")
    createdAt = String(description="Creation timestamp")
    updatedAt = String(description="Last update timestamp")

    class Meta:
        description = "Field builder configuration"

    def resolve_createdAt(self, info):
        """Resolve created_at timestamp"""
        return self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None

    def resolve_updatedAt(self, info):
        """Resolve updated_at timestamp"""
        return self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None


class FieldBuilderConfigSummaryType(ObjectType):
    """
    Field builder configuration summary type

    Lightweight type for listing configurations.
    """
    id = Int(required=True, description="Configuration ID")
    name = String(description="Configuration name")
    viewName = String(required=True, description="View/table name")
    displayName = String(description="Display name")
    createdAt = String(description="Creation timestamp")

    class Meta:
        description = "Field builder configuration summary"

    def resolve_viewName(self, info):
        """Resolve view name from output_table"""
        return self.output_table if hasattr(self, 'output_table') else None

    def resolve_createdAt(self, info):
        """Resolve created_at timestamp"""
        return self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None


class HQLPreviewType(ObjectType):
    """
    HQL preview output type
    """
    hql = String(required=True, description="Generated HQL script")

    class Meta:
        description = "HQL preview result"


# ============================================
# Mutation Response Types
# ============================================

class SaveFieldBuilderConfigPayload(ObjectType):
    """
    Save field builder configuration mutation payload
    """
    ok = Boolean(required=True, description="Operation success status")
    fieldBuilderConfig = Field(FieldBuilderConfigType, description="Saved configuration")
    errors = List(String, description="List of errors")
    message = String(description="Success message")

    class Meta:
        description = "Response payload for save field builder config mutation"


class DeleteFieldBuilderConfigPayload(ObjectType):
    """
    Delete field builder configuration mutation payload
    """
    ok = Boolean(required=True, description="Operation success status")
    message = String(description="Success/error message")
    errors = List(String, description="List of errors")

    class Meta:
        description = "Response payload for delete field builder config mutation"

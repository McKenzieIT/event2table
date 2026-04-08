"""
数据库迁移模块

提供数据库版本迁移功能，支持增量升级。
"""

from .base import BaseMigration
from .runner import MigrationRunner, get_migration_registry
from .v1_to_v18 import (
    MigrationV1_AddCategoryId,
    MigrationV2_EventCategoryRelations,
    MigrationV3_IncludeInCommonParams,
    MigrationV4_IconPath,
    MigrationV5_EditTracking,
    MigrationV6_ParameterManagementRefactoring,
    MigrationV7_ParameterValidationAndBatchOperations,
    MigrationV8_ParameterDependencies,
    MigrationV9_EnhancedHQLGeneration,
    MigrationV10_ArrayParameterHierarchy,
    MigrationV11_FieldBuilderSupport,
    MigrationV12_FlowTemplates,
    MigrationV13_EventNodesAndParameterAliases,
    MigrationV14_FieldNameMappings,
    MigrationV15_EventNodeConfigs,
    MigrationV16_AsyncTasks,
    MigrationV17_CommonParamsDisplayName,
    MigrationV18_AddGameGid,
)

__all__ = [
    "BaseMigration",
    "MigrationRunner",
    "get_migration_registry",
    "MigrationV1_AddCategoryId",
    "MigrationV2_EventCategoryRelations",
    "MigrationV3_IncludeInCommonParams",
    "MigrationV4_IconPath",
    "MigrationV5_EditTracking",
    "MigrationV6_ParameterManagementRefactoring",
    "MigrationV7_ParameterValidationAndBatchOperations",
    "MigrationV8_ParameterDependencies",
    "MigrationV9_EnhancedHQLGeneration",
    "MigrationV10_ArrayParameterHierarchy",
    "MigrationV11_FieldBuilderSupport",
    "MigrationV12_FlowTemplates",
    "MigrationV13_EventNodesAndParameterAliases",
    "MigrationV14_FieldNameMappings",
    "MigrationV15_EventNodeConfigs",
    "MigrationV16_AsyncTasks",
    "MigrationV17_CommonParamsDisplayName",
    "MigrationV18_AddGameGid",
]

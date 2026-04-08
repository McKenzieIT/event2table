"""
迁移运行器
"""

import logging
import sqlite3
from typing import Optional

from backend.core.cache import cached

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

logger = logging.getLogger(__name__)


class MigrationRunner:
    """迁移运行器"""

    def __init__(self, db_path: str):
        """
        初始化迁移运行器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.registry = get_migration_registry()

    def get_current_version(self) -> int:
        """
        获取当前数据库版本

        Returns:
            当前版本号
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA user_version")
        version = cursor.fetchone()[0]
        conn.close()

        return version

    def migrate_to_version(self, target_version: int):
        """
        迁移到指定版本

        Args:
            target_version: 目标版本号
        """
        current_version = self.get_current_version()

        if current_version >= target_version:
            logger.info(f"Database is already at version {current_version}")
            return

        logger.info(f"Migrating database from version {current_version} to {target_version}...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            for version in range(current_version + 1, target_version + 1):
                if version in self.registry:
                    migration = self.registry[version]
                    logger.info(f"Applying migration v{version}...")
                    migration.upgrade(cursor, conn)

                    # Update version (PRAGMA doesn't support parameters in SQLite)
                    cursor.execute(f"PRAGMA user_version = {version}")
                    conn.commit()
                    logger.info(f"Migration v{version} completed")

        finally:
            conn.close()


@cached(ttl=1800)  # Cache for 30 minutes
def get_migration_registry() -> dict:
    """
    获取迁移注册表

    Returns:
        版本号到迁移类的映射字典
    """
    return {
        1: MigrationV1_AddCategoryId(),
        2: MigrationV2_EventCategoryRelations(),
        3: MigrationV3_IncludeInCommonParams(),
        4: MigrationV4_IconPath(),
        5: MigrationV5_EditTracking(),
        6: MigrationV6_ParameterManagementRefactoring(),
        7: MigrationV7_ParameterValidationAndBatchOperations(),
        8: MigrationV8_ParameterDependencies(),
        9: MigrationV9_EnhancedHQLGeneration(),
        10: MigrationV10_ArrayParameterHierarchy(),
        11: MigrationV11_FieldBuilderSupport(),
        12: MigrationV12_FlowTemplates(),
        13: MigrationV13_EventNodesAndParameterAliases(),
        14: MigrationV14_FieldNameMappings(),
        15: MigrationV15_EventNodeConfigs(),
        16: MigrationV16_AsyncTasks(),
        17: MigrationV17_CommonParamsDisplayName(),
        18: MigrationV18_AddGameGid(),
    }

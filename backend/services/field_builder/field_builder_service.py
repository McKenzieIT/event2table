#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Field Builder Service - 业务逻辑层 (精简架构)

提供Field Builder相关的业务逻辑服务
- 使用统一Entity模型 (FieldBuilderConfigEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
- 支持HQL预览生成
"""

from typing import List, Optional, Dict, Any
import logging
import json
from backend.models.repositories.join_config_repository import JoinConfigRepository
from backend.core.cache.cache_system import CacheInvalidator, cached

logger = logging.getLogger(__name__)


class FieldBuilderService:
    """Field Builder业务服务 (精简架构)"""

    def __init__(self):
        self.config_repo = JoinConfigRepository()
        from backend.core.cache.cache_system import HierarchicalCache
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)
        logger.info("✅ FieldBuilderService initialized")

    @cached("field_builder.list", timeout=120)
    def list_configs(
        self,
        limit: int = 50,
        search: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取Field Builder配置列表 (带缓存)

        Args:
            limit: 最大返回数量
            search: 可选, 在display_name或view_name中搜索

        Returns:
            配置字典列表

        Raises:
            ValueError: 参数验证失败
        """
        if limit <= 0 or limit > 1000:
            raise ValueError(f"limit must be between 1 and 1000, got: {limit}")

        # 使用Repository查询
        query = """
            SELECT
                id,
                name,
                output_table as view_name,
                display_name,
                created_at
            FROM join_configs
            WHERE field_mapping_v2 IS NOT NULL
        """
        params = []

        if search and search.strip():
            query += " AND (display_name LIKE ? OR output_table LIKE ?)"
            search_pattern = f"%{search.strip()}%"
            params.extend([search_pattern, search_pattern])

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        from backend.core.utils.converters import fetch_all_as_dict
        configs = fetch_all_as_dict(query, tuple(params))

        return configs

    @cached("field_builder.detail", timeout=300)
    def get_config_by_id(self, config_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取Field Builder配置 (带缓存)

        Args:
            config_id: 配置ID

        Returns:
            配置字典, 不存在返回None

        Raises:
            ValueError: config_id格式不正确
        """
        if config_id <= 0:
            raise ValueError(f"config_id must be positive, got: {config_id}")

        # 从数据库获取原始数据
        from backend.core.utils.converters import fetch_one_as_dict
        config = fetch_one_as_dict(
            """
            SELECT id, field_mapping_v2, output_table, display_name
            FROM join_configs
            WHERE id = ?
        """,
            (config_id,)
        )

        if not config:
            return None

        # 反序列化field_mapping_v2
        field_mapping_v2 = None
        if config.get("field_mapping_v2"):
            try:
                field_mapping_v2 = json.loads(config["field_mapping_v2"])
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse field_mapping_v2 for config {config_id}: {e}")
                field_mapping_v2 = None

        return {
            "id": config["id"],
            "config": field_mapping_v2,
            "view_name": config["output_table"],
            "display_name": config["display_name"],
        }

    def save_config(
        self,
        config: Dict[str, Any],
        view_name: str,
        display_name: str,
        config_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        保存Field Builder配置 (自动失效缓存)

        Args:
            config: 字段映射配置
            view_name: 输出视图名称
            display_name: 显示名称
            config_id: 可选, 更新时提供配置ID

        Returns:
            保存的配置字典 {id, view_name}

        Raises:
            ValueError: 配置验证失败
            ValidationError: 数据验证失败
        """
        if not config:
            raise ValueError("Missing configuration data")

        if not view_name or not view_name.strip():
            raise ValueError("Missing view_name")

        if not display_name or not display_name.strip():
            display_name = view_name

        # 转换config为JSON字符串
        config_json = json.dumps(config, ensure_ascii=False)

        # 重试逻辑 (处理数据库锁)
        import time
        max_retries = 3
        delay = 0.1  # 100ms

        for attempt in range(max_retries):
            try:
                if config_id:
                    # 更新现有配置
                    from backend.core.utils import execute_write

                    affected = execute_write(
                        """
                        UPDATE join_configs
                        SET field_mapping_v2 = ?,
                            output_table = ?,
                            display_name = ?
                        WHERE id = ?
                    """,
                        (config_json, view_name, display_name, config_id)
                    )

                    if affected == 0:
                        raise ValueError(f"Configuration {config_id} not found")

                    logger.info(f"Field builder config updated: {config_id}")
                else:
                    # 创建新配置
                    from backend.core.utils import execute_write

                    # 从view_name生成name
                    name = view_name.replace("v_dwd_", "").replace("_", " ").strip().title()

                    config_id = execute_write(
                        """
                        INSERT INTO join_configs (
                            name,
                            source_events,
                            field_mapping_v2,
                            output_table,
                            display_name,
                            output_fields,
                            created_at
                        ) VALUES (?, '[]', ?, ?, ?, '[]', CURRENT_TIMESTAMP)
                    """,
                        (name, config_json, view_name, display_name),
                        return_last_id=True
                    )

                    logger.info(f"Field builder config created: {config_id}")

                # 清理缓存
                self.invalidator.invalidate_pattern("field_builder")

                return {
                    "id": config_id,
                    "view_name": view_name
                }

            except Exception as e:
                error_str = str(e).lower()
                # 检查是否是数据库锁错误且还有重试机会
                if "database is locked" in error_str and attempt < max_retries - 1:
                    wait_time = delay * (2**attempt)
                    logger.warning(
                        f"Database locked, retry {attempt + 1}/{max_retries} after {wait_time}s"
                    )
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Error saving field builder config: {e}", exc_info=True)
                    raise

    def delete_config(self, config_id: int) -> bool:
        """
        删除Field Builder配置 (自动失效缓存)

        Args:
            config_id: 配置ID

        Returns:
            删除成功返回True

        Raises:
            ValueError: 配置不存在
        """
        # 检查配置是否存在 (使用原始查询避免Entity验证问题)
        from backend.core.utils.converters import fetch_one_as_dict
        config = fetch_one_as_dict(
            "SELECT id FROM join_configs WHERE id = ?",
            (config_id,)
        )

        if not config:
            raise ValueError(f"Configuration {config_id} not found")

        # 删除配置
        from backend.core.utils import execute_write
        deleted = execute_write(
            "DELETE FROM join_configs WHERE id = ?",
            (config_id,)
        )

        # 清理缓存
        self.invalidator.invalidate_pattern("field_builder")

        logger.info(f"Field builder config deleted: {config_id}")
        return deleted > 0

    def get_configs_batch(
        self,
        config_ids: List[int]
    ) -> Dict[int, Optional[Dict[str, Any]]]:
        """
        批量获取Field Builder配置 (避免N+1查询)

        使用IN clause批量查询，避免循环查询导致的N+1问题。

        Args:
            config_ids: 配置ID列表

        Returns:
            配置字典 {config_id: config_dict}
            - 如果config存在: config_dict包含完整配置
            - 如果config不存在: config_dict为None

        Raises:
            ValueError: config_ids为空或格式不正确

        Performance:
            - 100 configs: < 1 second (batch query)
            - N+1 pattern would take 5-10 seconds
        """
        if not config_ids:
            return {}

        if not isinstance(config_ids, list):
            raise ValueError(f"config_ids must be a list, got: {type(config_ids)}")

        # Validate all IDs are positive integers
        for config_id in config_ids:
            if not isinstance(config_id, int) or config_id <= 0:
                raise ValueError(f"All config_ids must be positive integers, got: {config_id}")

        # Remove duplicates while preserving order
        unique_ids = list(dict.fromkeys(config_ids))

        # Batch query using IN clause (avoid N+1)
        from backend.core.utils.converters import fetch_all_as_dict

        placeholders = ",".join(["?" for _ in unique_ids])
        query = f"""
            SELECT
                id,
                field_mapping_v2,
                output_table as view_name,
                display_name
            FROM join_configs
            WHERE id IN ({placeholders})
        """

        configs_data = fetch_all_as_dict(query, tuple(unique_ids))

        # Build result dictionary with all requested IDs
        # (including None for non-existent IDs)
        result = {}
        for config_id in config_ids:
            # Find config in results (or None if not found)
            config = next(
                (c for c in configs_data if c["id"] == config_id),
                None
            )

            if config:
                # Parse field_mapping_v2
                field_mapping_v2 = None
                if config.get("field_mapping_v2"):
                    try:
                        field_mapping_v2 = json.loads(config["field_mapping_v2"])
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse field_mapping_v2 for config {config_id}: {e}")
                        field_mapping_v2 = None

                result[config_id] = {
                    "id": config["id"],
                    "config": field_mapping_v2,
                    "view_name": config["view_name"],
                    "display_name": config["display_name"],
                }
            else:
                result[config_id] = None

        return result

    def preview_hql(
        self,
        config: Dict[str, Any],
        source_events: List[int],
        view_name: str,
        date_var: str = "${bizdate}"
    ) -> str:
        """
        预览HQL (从Field Builder配置生成)

        Args:
            config: 字段映射配置
            source_events: 源事件ID列表
            view_name: 输出视图名称
            date_var: 日期变量

        Returns:
            生成的HQL语句

        Raises:
            ValueError: 参数验证失败
            Exception: HQL生成失败
        """
        if not config:
            raise ValueError("Missing configuration data")

        if not source_events:
            raise ValueError("Missing source_events")

        if not view_name or not view_name.strip():
            raise ValueError("Missing view_name")

        # 构建join_config用于v3生成器
        join_config = {
            "source_events": json.dumps(source_events),
            "field_mapping_v2": json.dumps(config),
            "output_table": view_name,
            "display_name": "Preview",
        }

        # 使用v3生成器创建HQL
        try:
            from backend.services.hql.generator_v3 import hql_generator_v3

            hql = hql_generator_v3.generate_from_field_mapping_v2(join_config, date_var)

            return hql

        except Exception as e:
            logger.error(f"Error generating HQL preview: {e}", exc_info=True)
            raise

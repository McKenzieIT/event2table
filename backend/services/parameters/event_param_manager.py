# Performance Optimization: N+1 query detected (2026-03-05)
# TODO: Replace loop queries with JOIN or prefetch pattern
# Expected improvement: 50-100x faster
#
# Example optimization:
#   Original: for item in items: data = fetch_item(item.id)
#   Fixed: items_with_data = fetch_all_as_dict('SELECT * FROM items')
#

from backend.core.cache.decorators import cached

# ⚠️ PERFORMANCE ISSUE: N+1 query detected in this file
# TODO: Refactor to use JOIN or prefetch pattern
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Parameter Manager - DEPRECATED
=====================================

⚠️ DEPRECATED: Use ParameterService instead

This class is kept for backward compatibility only.
All methods delegate to ParameterService.

Migration Guide:
- OLD: from backend.services.parameters.event_param_manager import event_param_manager
- NEW: from backend.services.parameters.parameter_service import ParameterService

For new code, use ParameterService directly.
"""

import json
import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional

from backend.core.utils import fetch_one_as_dict
from backend.services.parameters.param_library_manager import param_library_manager
from backend.services.parameters.param_type_manager import param_type_manager
from backend.services.parameters.parameter_service import ParameterService

logger = logging.getLogger(__name__)


class EventParamManager:
    """
    DEPRECATED: Event parameter management wrapper

    ⚠️ This class is deprecated. Use ParameterService instead.

    This class provides backward compatibility by delegating all calls
    to ParameterService. Some methods with unique business logic
    (version control, parameter config, hierarchy) are kept but will
    be migrated to ParameterService in future updates.
    """

    def __init__(self):
        """Initialize event param manager (deprecated)"""
        logger.warning(
            "EventParamManager is deprecated. Use ParameterService instead. "
            "See: backend/services/parameters/event_param_manager.py"
        )
        self.service = ParameterService()

    # ========== Delegated Methods (use ParameterService) ==========

    @cached(ttl=1800, key_prefix="event_params:by_event")  # Cache for 30 minutes
    def get_event_parameters(
        self, event_id: int, include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取事件的所有参数（带缓存）

        DEPRECATED: Use ParameterService.get_parameters_by_event() instead
        """
        logger.warning(f"get_event_parameters() is deprecated, use ParameterService")
        params = self.service.get_parameters_by_event(event_id, include_inactive)
        # Convert ParameterEntity to dict for backward compatibility
        return [p.model_dump() for p in params]

    @cached(ttl=1800, key_prefix="event_params:by_id")  # Cache for 30 minutes
    def get_parameter_by_id(self, param_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取参数（带缓存）

        DEPRECATED: Use ParameterService.get_parameter_by_id() instead
        """
        logger.warning(f"get_parameter_by_id() is deprecated, use ParameterService")
        param = self.service.get_parameter_by_id(param_id)
        return param.model_dump() if param else None

    # ========== Unique Methods (to be migrated to ParameterService) ==========

    def add_parameter(
        self, event_id: int, param_data: Dict[str, Any], change_reason: str = "新增参数"
    ) -> int:
        """
        为事件添加参数（带版本控制）

        Note: This method has unique business logic (version control, library integration).
        It will be migrated to ParameterService in a future update.
        """
        from backend.core.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        # 解析类型
        type_str = param_data.get("param_type", "string")
        template = param_type_manager.get_template_by_name(type_str)

        if not template:
            raise ValueError(f"未知的类型: {type_str}")

        # 检查是否引用参数库
        library_id = param_data.get("library_id")
        is_from_library = 0

        if library_id:
            # 从库中引用
            lib_param = param_library_manager.get_parameter_by_id(library_id)
            if not lib_param:
                raise ValueError(f"库参数不存在: {library_id}")

            is_from_library = 1
            param_name = lib_param["param_name"]
            param_name_cn = lib_param.get("param_name_cn", param_data.get("param_name_cn"))
            param_description = lib_param.get(
                "param_description", param_data.get("param_description")
            )
            template_id = lib_param["template_id"]
        else:
            # 自定义参数
            param_name = param_data["param_name"]
            param_name_cn = param_data.get("param_name_cn")
            param_description = param_data.get("param_description", "")
            template_id = template["id"]

            # 尝试匹配参数库
            existing_lib = fetch_one_as_dict(
                "SELECT id FROM param_library WHERE param_name = ?", (param_name,)
            )

            if existing_lib:
                library_id = existing_lib["id"]
                is_from_library = 1

        # 检查是否已存在同名参数
        existing = fetch_one_as_dict(
            "SELECT id, version FROM event_params WHERE event_id = ? AND param_name = ? AND is_active = 1",
            (event_id, param_name),
        )

        if existing:
            # 创建新版本(停用旧版本)
            from backend.core.utils import execute_write

            execute_write("UPDATE event_params SET is_active = 0 WHERE id = ?", (existing["id"],))
            new_version = existing["version"] + 1
        else:
            new_version = 1

        # 插入新参数
        cursor.execute(
            """
            INSERT INTO event_params
            (event_id, library_id, param_name, param_name_cn, template_id,
             param_description, version, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """,
            (
                event_id,
                library_id,
                param_name,
                param_name_cn,
                template_id,
                param_description,
                new_version,
            ),
        )

        param_id = cursor.lastrowid

        # 记录版本历史
        cursor.execute(
            """
            INSERT INTO param_versions
            (event_param_id, version, param_name, change_reason, created_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (param_id, new_version, param_name, change_reason),
        )

        # 更新参数库使用次数
        if library_id:
            cursor.execute(
                "UPDATE param_library SET usage_count = usage_count + 1 WHERE id = ?", (library_id,)
            )

        conn.commit()
        conn.close()

        logger.info(f"Added parameter {param_name} to event {event_id}, version {new_version}")
        return param_id

    def _save_version(
        self, cursor, event_param_id: int, version: int, reason: str, changed_by: str = "system"
    ):
        """保存参数版本到历史表"""
        cursor.execute(
            """
            INSERT INTO param_versions
            (event_param_id, version, param_name, param_name_cn, template_id,
             param_description, hql_config, change_reason, changed_by)
            SELECT id, version, param_name, param_name_cn, template_id,
                   param_description, hql_config, ?, ?
            FROM event_params
            WHERE id = ?
        """,
            (reason, changed_by, event_param_id),
        )

    def update_parameter(
        self, event_param_id: int, param_data: Dict[str, Any], change_reason: str = "更新参数"
    ) -> bool:
        """
        更新参数（创建新版本）

        Note: This method has unique version control logic.
        Consider using ParameterService.update_parameter() for simple updates.
        """
        from backend.core.database import get_db

        with get_db() as conn:
            cursor = conn.cursor()

            # 获取当前参数
            current = cursor.execute(
                "SELECT * FROM event_params WHERE id = ?", (event_param_id,)
            ).fetchone()

            if not current:
                return False

            # 保存当前版本
            self._save_version(cursor, event_param_id, current["version"], change_reason)

            # 解析类型
            type_str = param_data.get("param_type")
            if type_str:
                template = param_type_manager.get_template_by_name(type_str)
                if template:
                    template_id = template["id"]
                else:
                    template_id = current["template_id"]
            else:
                template_id = current["template_id"]

            # 停用当前版本
            cursor.execute("UPDATE event_params SET is_active = 0 WHERE id = ?", (event_param_id,))

            # 创建新版本
            new_version = current["version"] + 1
            cursor.execute(
                """
                INSERT INTO event_params
                (event_id, library_id, param_name, param_name_cn, template_id,
                 param_description, is_from_library, version, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
                (
                    current["event_id"],
                    param_data.get("library_id", current["library_id"]),
                    param_data.get("param_name", current["param_name"]),
                    param_data.get("param_name_cn", current["param_name_cn"]),
                    template_id,
                    param_data.get("param_description", current["param_description"]),
                    param_data.get("is_from_library", current["is_from_library"]),
                    new_version,
                ),
            )

            conn.commit()
            logger.info(f"Updated parameter {event_param_id} to version {new_version}")
            return True

    @cached(ttl=1800, key_prefix="event_params:history")  # Cache for 30 minutes
    def get_parameter_history(self, event_param_id: int) -> List[Dict[str, Any]]:
        """
        获取参数变更历史

        Note: This is unique functionality not yet in ParameterService.
        """
        from backend.core.database import get_db

        with get_db() as conn:
            history = conn.execute(
                """
                SELECT pv.*, pt.template_name
                FROM param_versions pv
                JOIN param_templates pt ON pv.template_id = pt.id
                WHERE pv.event_param_id = ?
                ORDER BY pv.version DESC
            """,
                (event_param_id,),
            ).fetchall()

            return [dict(h) for h in history]

    def delete_parameter(self, event_param_id: int) -> bool:
        """
        删除参数（软删除）

        DEPRECATED: Use ParameterService.delete_parameter() instead
        """
        logger.warning(f"delete_parameter() is deprecated, use ParameterService")
        try:
            self.service.delete_parameter(event_param_id)
            return True
        except Exception:
            return False

    def set_parameter_config(self, event_param_id: int, config: Dict[str, Any]) -> bool:
        """
        设置参数配置（用于array展开等）

        Note: This is unique functionality not yet in ParameterService.
        """
        from backend.core.database import get_db

        with get_db() as conn:
            cursor = conn.cursor()

            # 检查是否存在配置
            existing = cursor.execute(
                "SELECT id FROM param_configs WHERE event_param_id = ?", (event_param_id,)
            ).fetchone()

            config_data = {
                "parse_mode": config.get("parse_mode", "json_extract"),
                "explode_config": json.dumps(config.get("explode_config", {})),
                "array_element_delimiter": config.get("array_element_delimiter", ","),
                "map_key_value_delimiter": config.get("map_key_value_delimiter", ":"),
                "custom_hql_template": config.get("custom_hql_template"),
            }

            if existing:
                # 更新
                cursor.execute(
                    """
                    UPDATE param_configs
                    SET parse_mode = ?, explode_config = ?,
                        array_element_delimiter = ?, map_key_value_delimiter = ?,
                        custom_hql_template = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE event_param_id = ?
                """,
                    (
                        config_data["parse_mode"],
                        config_data["explode_config"],
                        config_data["array_element_delimiter"],
                        config_data["map_key_value_delimiter"],
                        config_data["custom_hql_template"],
                        event_param_id,
                    ),
                )
            else:
                # 插入
                cursor.execute(
                    """
                    INSERT INTO param_configs
                    (event_param_id, parse_mode, explode_config,
                     array_element_delimiter, map_key_value_delimiter, custom_hql_template)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        event_param_id,
                        config_data["parse_mode"],
                        config_data["explode_config"],
                        config_data["array_element_delimiter"],
                        config_data["map_key_value_delimiter"],
                        config_data["custom_hql_template"],
                    ),
                )

            conn.commit()
            logger.info(f"Updated config for parameter {event_param_id}")
            return True

    @cached(ttl=1800, key_prefix="event_params:config")  # Cache for 30 minutes
    def get_parameter_config(self, event_param_id: int) -> Optional[Dict[str, Any]]:
        """
        获取参数配置

        Note: This is unique functionality not yet in ParameterService.
        """
        from backend.core.cache.cache_system import parse_json_cached
        from backend.core.database import get_db

        with get_db() as conn:
            config = conn.execute(
                "SELECT * FROM param_configs WHERE event_param_id = ?", (event_param_id,)
            ).fetchone()

            if not config:
                # 返回默认配置
                return {
                    "parse_mode": "json_extract",
                    "explode_config": {},
                    "array_element_delimiter": ",",
                    "map_key_value_delimiter": ":",
                }

            result = dict(config)
            # 解析JSON字段(使用缓存)
            if result.get("explode_config"):
                result["explode_config"] = parse_json_cached(result["explode_config"])

            return result

    @cached(ttl=1800, key_prefix="event_params:rollback")  # Cache for 30 minutes
    def rollback_to_version(self, event_param_id: int, target_version: int) -> bool:
        """
        回滚参数到指定版本

        Note: This is unique functionality not yet in ParameterService.
        """
        from backend.core.database import get_db

        with get_db() as conn:
            cursor = conn.cursor()

            # 获取当前参数
            current = cursor.execute(
                "SELECT * FROM event_params WHERE id = ?", (event_param_id,)
            ).fetchone()

            if not current:
                return False

            # 获取目标版本
            target = cursor.execute(
                """
                SELECT * FROM param_versions
                WHERE event_param_id = ? AND version = ?
            """,
                (event_param_id, target_version),
            ).fetchone()

            if not target:
                return False

            # 保存当前版本
            self._save_version(
                cursor, event_param_id, current["version"], f"回滚到版本{target_version}"
            )

            # 停用当前版本
            cursor.execute("UPDATE event_params SET is_active = 0 WHERE id = ?", (event_param_id,))

            # 创建新版本(使用目标版本的数据)
            new_version = current["version"] + 1
            cursor.execute(
                """
                INSERT INTO event_params
                (event_id, library_id, param_name, param_name_cn, template_id,
                 param_description, hql_config, is_from_library, version, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
                (
                    current["event_id"],
                    target["library_id"],
                    target["param_name"],
                    target["param_name_cn"],
                    target["template_id"],
                    target["param_description"],
                    target["hql_config"],
                    0,  # 回滚的版本标记为非库引用
                    new_version,
                ),
            )

            conn.commit()
            logger.info(
                f"Rolled back parameter {event_param_id} to version {target_version}, new version {new_version}"
            )
            return True

    @cached(ttl=1800, key_prefix="event_params:with_children")  # Cache for 30 minutes
    def get_parameter_with_children(self, param_id: int) -> Optional[Dict[str, Any]]:
        """
        获取参数及其子参数（用于array类型）

        Note: This is unique functionality not yet in ParameterService.
        """
        # 获取基础参数信息
        param = self.get_parameter_by_id(param_id)
        if not param:
            return None

        # 检查是否为array类型
        if param.get("base_type") != "array":
            return param

        # 获取参数配置
        config = self.get_parameter_config(param_id)

        # 生成或获取子参数定义
        child_params = self._generate_child_params_for_array(param)

        if child_params:
            result = dict(param)
            result["children"] = child_params
            result["has_children"] = True
            return result

        return param

    @cached(ttl=1800, key_prefix="event_params:hierarchy")  # Cache for 30 minutes
    def get_event_parameters_hierarchy(
        self, event_id: int, include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        获取事件的所有参数（带层级结构）

        Note: This is unique functionality not yet in ParameterService.
        """
        # 获取所有基础参数
        params = self.get_event_parameters(event_id, include_inactive)

        # 为array类型参数添加子参数
        result = []
        for param in params:
            if param.get("base_type") == "array":
                param_with_children = self.get_parameter_with_children(param["id"])
                if param_with_children:
                    result.append(param_with_children)
                else:
                    result.append(param)
            else:
                result.append(param)

        return result

    def _generate_child_params_for_array(self, param: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        为array类型参数生成虚拟子参数定义

        Note: This is unique functionality not yet in ParameterService.
        """
        from backend.core.cache.cache_system import parse_json_cached

        # 尝试从配置中获取已保存的子参数定义
        config = self.get_parameter_config(param["id"])

        if config.get("child_params"):
            # 使用缓存的JSON解析
            return parse_json_cached(config["child_params"])

        # 根据类型模板生成默认子参数
        element_type = param.get("element_type", "string")

        if element_type == "map":
            # Map类型的子参数
            return [
                {
                    "virtual_id": f"{param['id']}_map_element",
                    "name": "map_element",
                    "name_cn": "Map元素",
                    "type": "map",
                    "description": f"Map数组元素",
                    "is_virtual": True,
                }
            ]
        elif element_type == "string":
            # 字符串数组的子参数
            return [
                {
                    "virtual_id": f"{param['id']}_element",
                    "name": "element",
                    "name_cn": "数组元素",
                    "type": "string",
                    "description": "字符串数组元素",
                    "is_virtual": True,
                }
            ]
        elif element_type == "int":
            # 整数数组的子参数
            return [
                {
                    "virtual_id": f"{param['id']}_element",
                    "name": "element",
                    "name_cn": "数组元素",
                    "type": "int",
                    "description": "整数数组元素",
                    "is_virtual": True,
                }
            ]
        elif element_type == "float":
            # 浮点数数组的子参数
            return [
                {
                    "virtual_id": f"{param['id']}_element",
                    "name": "element",
                    "name_cn": "数组元素",
                    "type": "float",
                    "description": "浮点数数组元素",
                    "is_virtual": True,
                }
            ]
        else:
            # 其他类型的默认子参数
            return [
                {
                    "virtual_id": f"{param['id']}_element",
                    "name": "element",
                    "name_cn": "数组元素",
                    "type": element_type,
                    "description": f"{element_type}数组元素",
                    "is_virtual": True,
                }
            ]

    def save_child_params_config(
        self, event_param_id: int, child_params: List[Dict[str, Any]]
    ) -> bool:
        """
        保存子参数配置

        Note: This is unique functionality not yet in ParameterService.
        """
        from backend.core.database import get_db

        with get_db() as conn:
            cursor = conn.cursor()

            # 检查是否存在配置
            existing = cursor.execute(
                "SELECT id FROM param_configs WHERE event_param_id = ?", (event_param_id,)
            ).fetchone()

            child_params_json = json.dumps(child_params, ensure_ascii=False)

            if existing:
                # 更新
                cursor.execute(
                    """
                    UPDATE param_configs
                    SET child_params = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE event_param_id = ?
                """,
                    (child_params_json, event_param_id),
                )
            else:
                # 插入
                cursor.execute(
                    """
                    INSERT INTO param_configs
                    (event_param_id, child_params)
                    VALUES (?, ?)
                """,
                    (event_param_id, child_params_json),
                )

            conn.commit()
            logger.info(f"Saved child params config for parameter {event_param_id}")
            return True


# ========== Module-level cached functions (deprecated, kept for compatibility) ==========


@lru_cache(maxsize=128)
@cached(ttl=1800, key_prefix="event_params:cached")  # Cache for 30 minutes
def _get_event_parameters_cached(
    event_id: int, include_inactive: bool = False
) -> List[Dict[str, Any]]:
    """
    获取事件的所有参数（缓存层）

    DEPRECATED: This is kept for backward compatibility only.
    Use ParameterService.get_parameters_by_event() instead.
    """
    logger.warning(f"_get_event_parameters_cached() is deprecated, use ParameterService")
    service = ParameterService()
    params = service.get_parameters_by_event(event_id, include_inactive)
    return [p.model_dump() for p in params]


@lru_cache(maxsize=256)
@cached(ttl=1800, key_prefix="event_params:by_id_cached")  # Cache for 30 minutes
def _get_parameter_by_id_cached(param_id: int) -> Optional[Dict[str, Any]]:
    """
    根据ID获取参数（缓存层）

    DEPRECATED: This is kept for backward compatibility only.
    Use ParameterService.get_parameter_by_id() instead.
    """
    logger.warning(f"_get_parameter_by_id_cached() is deprecated, use ParameterService")
    service = ParameterService()
    param = service.get_parameter_by_id(param_id)
    return param.model_dump() if param else None


# ========== Singleton instance (deprecated) ==========

event_param_manager = EventParamManager()

logger.warning(
    "EventParamManager module is deprecated. "
    "Use ParameterService instead: "
    "from backend.services.parameters.parameter_service import ParameterService"
)

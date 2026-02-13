#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Parameter Manager
Manages parameters for specific events with version control
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import lru_cache
from backend.core.database import get_db, get_db_connection
from backend.core.logging import get_logger
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict, execute_write
from backend.services.parameters.param_type_manager import param_type_manager
from backend.services.parameters.param_library_manager import param_library_manager
from backend.core.cache.cache_system import parse_json_cached

logger = get_logger(__name__)


class EventParamManager:
    """Event parameter management with version control"""

    def __init__(self):
        """Initialize event param manager"""
        pass

    def get_event_parameters(
        self, event_id: int, include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """获取事件的所有参数（带缓存）"""
        return _get_event_parameters_cached(event_id, include_inactive)

    def get_parameter_by_id(self, param_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取参数（带缓存）"""
        return _get_parameter_by_id_cached(param_id)

    def add_parameter(
        self, event_id: int, param_data: Dict[str, Any], change_reason: str = "新增参数"
    ) -> int:
        """为事件添加参数"""
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
            # 创建新版本（停用旧版本）
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
        """更新参数（创建新版本）

        Args:
            event_param_id: 参数ID
            param_data: 更新的参数数据
            change_reason: 变更原因

        Returns:
            是否更新成功
        """
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

    def get_parameter_history(self, event_param_id: int) -> List[Dict[str, Any]]:
        """获取参数变更历史

        Args:
            event_param_id: 参数ID

        Returns:
            历史版本列表
        """
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
        """删除参数（软删除）

        Args:
            event_param_id: 参数ID

        Returns:
            是否删除成功
        """
        with get_db() as conn:
            cursor = conn.cursor()

            # 软删除：设置is_active=0
            cursor.execute("UPDATE event_params SET is_active = 0 WHERE id = ?", (event_param_id,))

            affected = cursor.rowcount
            conn.commit()

            if affected > 0:
                logger.info(f"Deleted parameter {event_param_id}")
                return True
            return False

    def set_parameter_config(self, event_param_id: int, config: Dict[str, Any]) -> bool:
        """设置参数配置（用于array展开等）

        Args:
            event_param_id: 参数ID
            config: 配置字典

        Returns:
            是否设置成功
        """
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

    def get_parameter_config(self, event_param_id: int) -> Optional[Dict[str, Any]]:
        """获取参数配置

        Args:
            event_param_id: 参数ID

        Returns:
            配置字典
        """
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
            # 解析JSON字段（使用缓存）
            if result.get("explode_config"):
                result["explode_config"] = parse_json_cached(result["explode_config"])

            return result

    def rollback_to_version(self, event_param_id: int, target_version: int) -> bool:
        """回滚参数到指定版本

        Args:
            event_param_id: 参数ID
            target_version: 目标版本号

        Returns:
            是否回滚成功
        """
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

            # 创建新版本（使用目标版本的数据）
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

    def get_parameter_with_children(self, param_id: int) -> Optional[Dict[str, Any]]:
        """获取参数及其子参数（用于array类型）

        Args:
            param_id: 参数ID

        Returns:
            包含子参数的完整参数信息，如果没有子参数则返回None
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

    def get_event_parameters_hierarchy(
        self, event_id: int, include_inactive: bool = False
    ) -> List[Dict[str, Any]]:
        """获取事件的所有参数（带层级结构）

        Args:
            event_id: 事件ID
            include_inactive: 是否包含非激活参数

        Returns:
            带层级结构的参数列表
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
        """为array类型参数生成虚拟子参数定义

        Args:
            param: 参数信息

        Returns:
            子参数列表
        """
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
        """保存子参数配置

        Args:
            event_param_id: 参数ID
            child_params: 子参数列表

        Returns:
            是否保存成功
        """
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


# Module-level cached functions (to work with singleton pattern)
@lru_cache(maxsize=128)
def _get_event_parameters_cached(
    event_id: int, include_inactive: bool = False
) -> List[Dict[str, Any]]:
    """获取事件的所有参数（缓存层）"""
    query = """
        SELECT
            ep.*,
            pt.template_name,
            pt.display_name as type_display_name,
            pt.base_type,
            pt.element_type,
            pt.nesting_level,
            pt.hql_parse_template,
            pl.param_name as library_param_name,
            pl.is_standard
        FROM event_params ep
        JOIN param_templates pt ON ep.template_id = pt.id
        LEFT JOIN param_library pl ON ep.library_id = pl.id
        WHERE ep.event_id = ?
    """

    if not include_inactive:
        query += " AND ep.is_active = 1"

    query += " ORDER BY ep.param_name"

    return fetch_all_as_dict(query, (event_id,))


@lru_cache(maxsize=256)
def _get_parameter_by_id_cached(param_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取参数（缓存层）"""
    return fetch_one_as_dict(
        """
        SELECT
            ep.*,
            pt.template_name,
            pt.display_name as type_display_name,
            pt.base_type,
            pt.element_type,
            pt.nesting_level,
            pt.hql_parse_template,
            pl.param_name as library_param_name,
            pl.is_standard
        FROM event_params ep
        JOIN param_templates pt ON ep.template_id = pt.id
        LEFT JOIN param_library pl ON ep.library_id = pl.id
        WHERE ep.id = ?
    """,
        (param_id,),
    )


# Singleton instance
event_param_manager = EventParamManager()

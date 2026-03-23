#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Version Repository (HQL版本仓储层)

提供HQL版本的数据访问操作:
- 保存HQL版本历史
- 查询版本历史
- 版本差异计算
- 版本回滚
"""

import difflib
import logging
from typing import Any, Dict, List, Optional

from backend.core.cache.decorators import cached as cached_decorator
from backend.core.data_access import GenericRepository
from backend.core.utils.converters import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    get_db_connection,
)

logger = logging.getLogger(__name__)


class HQLVersionRepository(GenericRepository):
    """
    HQL版本仓储类

    提供HQL版本表的CRUD操作和特定查询方法
    """

    def __init__(self) -> None:
        """初始化HQL版本仓储"""
        super().__init__(
            table_name="hql_versions",
            primary_key="id",
            enable_cache=True,
            cache_timeout=300,  # 5分钟缓存
        )

    @cached_decorator(ttl=300)
    def find_by_event_id(self, event_id: int) -> List[Dict[str, Any]]:
        """
        根据事件ID获取所有版本

        Args:
            event_id: 事件ID

        Returns:
            HQL版本列表，按版本号降序排列
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE event_id = ?
            ORDER BY version_number DESC
        """
        return fetch_all_as_dict(query, (event_id,))

    @cached_decorator(ttl=300)
    def find_by_event_and_version(
        self, event_id: int, version_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        根据事件ID和版本号获取特定版本

        Args:
            event_id: 事件ID
            version_number: 版本号

        Returns:
            HQL版本字典，不存在返回None
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE event_id = ? AND version_number = ?
        """
        return fetch_one_as_dict(query, (event_id, version_number))

    @cached_decorator(ttl=300)
    def get_latest_version(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件的最新版本

        Args:
            event_id: 事件ID

        Returns:
            最新版本字典，不存在返回None
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE event_id = ?
            ORDER BY version_number DESC
            LIMIT 1
        """
        return fetch_one_as_dict(query, (event_id,))

    @cached_decorator(ttl=300)
    def get_version_count(self, event_id: int) -> int:
        """
        获取事件的版本总数

        Args:
            event_id: 事件ID

        Returns:
            版本总数
        """
        query = f"""
            SELECT COUNT(*) as count FROM {self.table_name}
            WHERE event_id = ?
        """
        result = fetch_one_as_dict(query, (event_id,))
        return result["count"] if result else 0

    def save_version(
        self,
        event_id: int,
        hql_content: str,
        version_number: int,
        change_description: str,
        created_by: str,
    ) -> Optional[Dict[str, Any]]:
        """
        保存新版本

        Args:
            event_id: 事件ID
            hql_content: HQL内容
            version_number: 版本号
            change_description: 变更描述
            created_by: 创建者

        Returns:
            创建的版本字典，失败返回None
        """
        query = f"""
            INSERT INTO {self.table_name}
            (event_id, hql_content, version_number, change_description, created_by)
            VALUES (?, ?, ?, ?, ?)
        """

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                query,
                (event_id, hql_content, version_number, change_description, created_by),
            )
            conn.commit()
            version_id = cursor.lastrowid

            # 清除缓存
            self._clear_event_cache(event_id)

            # 返回创建的版本
            return self.find_by_id(version_id)
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving HQL version: {e}")
            return None
        finally:
            conn.close()

    def compare_versions(self, version_id_1: int, version_id_2: int) -> Dict[str, Any]:
        """
        比较两个版本的差异

        Args:
            version_id_1: 版本1的ID
            version_id_2: 版本2的ID

        Returns:
            差异字典，包含：
            - version_1: 版本1信息
            - version_2: 版本2信息
            - diff: 差异内容
            - additions: 新增行数
            - deletions: 删除行数
            - changes: 修改行数
        """
        version_1 = self.find_by_id(version_id_1)
        version_2 = self.find_by_id(version_id_2)

        if not version_1 or not version_2:
            return {
                "error": "One or both versions not found",
                "version_1": version_1,
                "version_2": version_2,
            }

        # 计算差异
        diff = self._calculate_diff(version_1["hql_content"], version_2["hql_content"])

        return {
            "version_1": {
                "id": version_1["id"],
                "version_number": version_1["version_number"],
                "created_at": version_1["created_at"],
                "created_by": version_1["created_by"],
            },
            "version_2": {
                "id": version_2["id"],
                "version_number": version_2["version_number"],
                "created_at": version_2["created_at"],
                "created_by": version_2["created_by"],
            },
            "diff": diff["diff_output"],
            "additions": diff["additions"],
            "deletions": diff["deletions"],
            "changes": diff["changes"],
        }

    def _calculate_diff(self, content1: str, content2: str) -> Dict[str, Any]:
        """
        计算两个HQL内容的差异

        Args:
            content1: 内容1
            content2: 内容2

        Returns:
            差异统计字典
        """
        lines1 = content1.splitlines(keepends=True)
        lines2 = content2.splitlines(keepends=True)

        # 使用difflib计算差异
        differ = difflib.Differ()
        diff_output = list(differ.compare(lines1, lines2))

        # 统计差异
        additions = 0
        deletions = 0
        changes = 0

        for line in diff_output:
            if line.startswith("+ "):
                additions += 1
            elif line.startswith("- "):
                deletions += 1
            elif line.startswith("? "):
                changes += 1

        # 格式化差异输出
        formatted_diff = "".join(diff_output)

        return {
            "diff_output": formatted_diff,
            "additions": additions,
            "deletions": deletions,
            "changes": changes,
        }

    def rollback_to_version(
        self, event_id: int, target_version_id: int, rolled_back_by: str
    ) -> Optional[Dict[str, Any]]:
        """
        回滚到指定版本

        Args:
            event_id: 事件ID
            target_version_id: 目标版本ID
            rolled_back_by: 回滚操作者

        Returns:
            新创建的版本字典，失败返回None
        """
        # 获取目标版本
        target_version = self.find_by_id(target_version_id)
        if not target_version:
            logger.error(f"Target version {target_version_id} not found")
            return None

        # 获取当前最新版本号
        latest_version = self.get_latest_version(event_id)
        if not latest_version:
            logger.error(f"No versions found for event {event_id}")
            return None

        new_version_number = latest_version["version_number"] + 1

        # 创建新版本（回滚版本）
        change_description = f"Rollback to version {target_version['version_number']}"

        return self.save_version(
            event_id=event_id,
            hql_content=target_version["hql_content"],
            version_number=new_version_number,
            change_description=change_description,
            created_by=rolled_back_by,
        )

    def _clear_event_cache(self, event_id: int):
        """清除事件相关的所有缓存"""
        try:
            from backend.core.cache.cache_system import clear_cache_pattern

            clear_cache_pattern(f"hql_versions:event_id:{event_id}:*")
        except ImportError:
            pass

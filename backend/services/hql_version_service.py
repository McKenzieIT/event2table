#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Version Service (HQL版本服务层)

提供HQL版本管理的业务逻辑:
- 保存HQL版本历史
- 对比两个版本的差异
- 获取版本历史列表
- 支持版本回滚
"""

import logging
from typing import Any, Dict, List, Optional

from backend.core.cache.cache_system import CacheInvalidator, cached
from backend.services.base_service import BaseService

from backend.models.repositories.hql_version_repository import HQLVersionRepository

logger = logging.getLogger(__name__)


class HQLVersionService(BaseService):
    """
    HQL版本服务类

    提供HQL版本管理的业务逻辑，包括版本保存、对比、历史查询和回滚
    """

    def __init__(self):
        """初始化HQL版本服务"""
        super().__init__()
        self.repository = HQLVersionRepository()

    def save_version(
        self,
        event_id: int,
        hql_content: str,
        change_description: str,
        created_by: str,
    ) -> Optional[Dict[str, Any]]:
        """
        保存HQL新版本

        Args:
            event_id: 事件ID
            hql_content: HQL内容
            change_description: 变更描述
            created_by: 创建者

        Returns:
            创建的版本字典，失败返回None

        Raises:
            ValueError: 如果HQL内容为空
        """
        if not hql_content or not hql_content.strip():
            raise ValueError("HQL content cannot be empty")

        # 获取当前最新版本号
        latest_version = self.repository.get_latest_version(event_id)
        version_number = 1

        if latest_version:
            version_number = latest_version["version_number"] + 1

        # 保存版本
        version = self.repository.save_version(
            event_id=event_id,
            hql_content=hql_content,
            version_number=version_number,
            change_description=change_description,
            created_by=created_by,
        )

        if version:
            # 清除相关缓存
            self._clear_version_cache(event_id)
            logger.info(
                f"Saved HQL version {version_number} for event {event_id} by {created_by}"
            )

        return version

    def compare_versions(
        self, version_id_1: int, version_id_2: int
    ) -> Dict[str, Any]:
        """
        比较两个版本的差异

        Args:
            version_id_1: 版本1的ID
            version_id_2: 版本2的ID

        Returns:
            差异字典，包含版本信息和差异详情

        Raises:
            ValueError: 如果版本不存在
        """
        # 验证版本存在
        version_1 = self.repository.find_by_id(version_id_1)
        version_2 = self.repository.find_by_id(version_id_2)

        if not version_1:
            raise ValueError(f"Version {version_id_1} not found")
        if not version_2:
            raise ValueError(f"Version {version_id_2} not found")

        # 计算差异
        diff_result = self.repository.compare_versions(version_id_1, version_id_2)

        logger.info(
            f"Compared versions {version_id_1} and {version_id_2}: "
            f"{diff_result['additions']} additions, "
            f"{diff_result['deletions']} deletions, "
            f"{diff_result['changes']} changes"
        )

        return diff_result

    def get_version_history(
        self, event_id: int, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取事件的版本历史

        Args:
            event_id: 事件ID
            limit: 限制返回数量

        Returns:
            版本历史列表，按版本号降序排列

        Raises:
            ValueError: 如果event_id无效
        """
        if not event_id or event_id <= 0:
            raise ValueError("Invalid event_id")

        versions = self.repository.find_by_event_id(event_id)

        if limit and len(versions) > limit:
            versions = versions[:limit]

        logger.info(f"Retrieved {len(versions)} versions for event {event_id}")

        return versions

    def get_latest_version(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件的最新版本

        Args:
            event_id: 事件ID

        Returns:
            最新版本字典，不存在返回None
        """
        return self.repository.get_latest_version(event_id)

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

        Raises:
            ValueError: 如果目标版本不存在
        """
        # 验证目标版本存在
        target_version = self.repository.find_by_id(target_version_id)
        if not target_version:
            raise ValueError(f"Target version {target_version_id} not found")

        # 验证目标版本属于指定事件
        if target_version["event_id"] != event_id:
            raise ValueError(
                f"Target version {target_version_id} does not belong to event {event_id}"
            )

        # 执行回滚
        new_version = self.repository.rollback_to_version(
            event_id=event_id,
            target_version_id=target_version_id,
            rolled_back_by=rolled_back_by,
        )

        if new_version:
            # 清除相关缓存
            self._clear_version_cache(event_id)
            logger.info(
                f"Rolled back event {event_id} to version {target_version['version_number']} "
                f"by {rolled_back_by}, created new version {new_version['version_number']}"
            )

        return new_version

    def get_version_count(self, event_id: int) -> int:
        """
        获取事件的版本总数

        Args:
            event_id: 事件ID

        Returns:
            版本总数
        """
        return self.repository.get_version_count(event_id)

    @cached(ttl=300)
    def get_version_by_number(
        self, event_id: int, version_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        根据事件ID和版本号获取版本

        Args:
            event_id: 事件ID
            version_number: 版本号

        Returns:
            版本字典，不存在返回None
        """
        return self.repository.find_by_event_and_version(event_id, version_number)

    def _clear_version_cache(self, event_id: int):
        """
        清除HQL版本相关的所有缓存

        Args:
            event_id: 事件ID
        """
        # 清除Repository层缓存
        self.repository._clear_event_cache(event_id)

        # 清除Service层缓存
        self.invalidator.invalidate_pattern(f"hql_version:event_id:{event_id}:*")

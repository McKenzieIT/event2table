#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Service - 业务逻辑层 (精简架构)

提供事件相关的业务逻辑服务
- 使用统一Entity模型 (EventEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
- 集成Bloom Filter防止缓存穿透 (2026-02-25)
"""

from typing import List, Optional, Dict, Any
import logging
import threading
import os
from backend.models.entities import EventEntity
from backend.models.repositories.events import EventRepository
from backend.models.repositories.games import GameRepository
from backend.models.repositories.event_categories import EventCategoryRepository
from backend.core.cache.cache_system import cached
from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter

logger = logging.getLogger(__name__)


class EventService:
    """事件业务服务 (精简架构 + Bloom Filter防护)"""

    def __init__(self):
        self.event_repo = EventRepository()
        self.game_repo = GameRepository()
        self.category_repo = EventCategoryRepository()
        from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)

        # Bloom Filter延迟初始化（lazy loading）
        self._bloom_filter = None
        self._bloom_filter_lock = threading.Lock()
        logger.info("✅ EventService initialized (Bloom Filter lazy)")

    @property
    def bloom_filter(self):
        """延迟加载Bloom Filter（线程安全）"""
        if self._bloom_filter is None:
            with self._bloom_filter_lock:
                if self._bloom_filter is None:
                    logger.info("Lazy initializing EventService Bloom Filter...")
                    self._bloom_filter = EnhancedBloomFilter(
                        capacity=500000,  # 50万容量（事件数量通常比游戏多）
                        error_rate=0.001,  # 0.1%误判率
                        persistence_path="data/events_bloom_filter.pkl",
                        strict_validation=self._is_test_mode()
                    )
                    logger.info("✅ EventService Bloom Filter initialized")
        return self._bloom_filter

    def _is_test_mode(self) -> bool:
        """检测是否在测试环境"""
        return (
            os.environ.get("TESTING") == "true" or
            os.environ.get("PYTEST_CURRENT_TEST") is not None
        )

    @cached("events.list", timeout=120)
    def get_events_by_game(
        self, game_gid: int, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """
        根据游戏GID获取事件列表 (带缓存)

        Args:
            game_gid: 游戏业务GID
            page: 页码（从1开始）
            per_page: 每页数量

        Returns:
            包含事件列表和分页信息的字典

        Raises:
            ValueError: 游戏不存在
        """
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game not found: gid={game_gid}")

        events = self.event_repo.find_by_game_gid(game_gid, page, per_page)
        total = self.event_repo.count_by_game_gid(game_gid)

        return {
            "events": events,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @cached("events.detail", timeout=300)
    def get_event_by_id(self, event_id: int) -> Optional[EventEntity]:
        """
        根据ID获取事件 (带Bloom Filter防护)

        使用Bloom Filter防止查询不存在的事件ID导致数据库压力

        Args:
            event_id: 事件ID

        Returns:
            EventEntity, 不存在返回None
        """
        # 检查Bloom Filter
        cache_key = f"events:{event_id}"
        if not self.bloom_filter.contains(cache_key):
            logger.debug(f"⚡ Bloom Filter: event {event_id} does not exist (fast reject)")
            return None

        # Bloom Filter说可能存在，查询数据库
        event = self.event_repo.find_by_id(event_id)

        # 如果存在，添加到Bloom Filter
        if event:
            self.bloom_filter.add(cache_key)
            logger.debug(f"✅ Bloom Filter: event {event_id} exists, added to filter")
        else:
            # 不存在（Bloom Filter误判），也添加到Filter防止重复查询
            self.bloom_filter.add(cache_key)
            logger.debug(f"⚠️ Bloom Filter: event {event_id} false positive, added to filter")

        return event

    @cached("events.with_params", timeout=300)
    def get_event_with_params(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件及其参数 (带缓存)

        Args:
            event_id: 事件ID

        Returns:
            包含事件和参数信息的字典, 不存在返回None
        """
        return self.event_repo.get_with_parameters(event_id)

    def create_event(self, event_data: EventEntity) -> EventEntity:
        """
        创建事件 (自动失效缓存 + 更新Bloom Filter)

        Args:
            event_data: 事件Entity (已通过Pydantic验证)

        Returns:
            创建的EventEntity

        Raises:
            ValueError: game不存在或事件已存在
            ValidationError: 数据验证失败
        """
        # 验证游戏存在
        game = self.game_repo.find_by_gid(event_data.game_gid)
        if not game:
            raise ValueError(f"Game not found: gid={event_data.game_gid}")

        # 验证事件名唯一性
        existing = self.event_repo.find_by_name(event_data.name, event_data.game_gid)
        if existing:
            raise ValueError(
                f"Event '{event_data.name}' already exists for game {event_data.game_gid}"
            )

        # 创建事件 (Entity已通过Pydantic验证)
        result = self.event_repo.create(event_data.model_dump())
        if result is None:
            raise ValueError("Failed to create event")

        # 失效事件列表缓存
        self.invalidator.invalidate_pattern("events.list")

        # 添加到Bloom Filter
        cache_key = f"events:{result.id}"
        self.bloom_filter.add(cache_key)

        logger.info(
            f"事件创建成功,已失效缓存并更新Bloom Filter: event_id={result.id}, game_gid={event_data.game_gid}"
        )

        return result

    def update_event(
        self, event_id: int, updates: Dict[str, Any]
    ) -> EventEntity:
        """
        更新事件 (自动失效缓存)

        Args:
            event_id: 事件ID
            updates: 更新字段字典

        Returns:
            更新后的EventEntity

        Raises:
            ValueError: 事件不存在
        """
        event = self.event_repo.find_by_id(event_id)
        if event is None:
            raise ValueError(f"Event not found: id={event_id}")

        self.event_repo.update(event_id, updates)
        result = self.event_repo.find_by_id(event_id)
        if result is None:
            raise ValueError("Failed to update event")

        # 失效事件相关缓存
        game_gid = event.game_gid
        self.invalidator.invalidate_pattern("events.list")
        self.invalidator.invalidate_pattern(f"events.detail:{event_id}")
        logger.info(f"事件更新成功,已失效缓存: event_id={event_id}")

        return result

    def delete_event(self, event_id: int) -> None:
        """
        删除事件 (自动失效缓存)

        Args:
            event_id: 事件ID

        Raises:
            ValueError: 事件不存在
        """
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event not found: id={event_id}")

        game_gid = event.game_gid
        self.event_repo.delete(event_id)

        # 失效事件相关缓存
        self.invalidator.invalidate_pattern("events.list")
        self.invalidator.invalidate_pattern(f"events.detail:{event_id}")
        logger.info(
            f"事件删除成功,已失效缓存: event_id={event_id}, game_gid={game_gid}"
        )

    @cached("events.search", timeout=120)
    def search_events(
        self, keyword: str, game_gid: Optional[int] = None
    ) -> List[EventEntity]:
        """
        搜索事件 (带缓存)

        Args:
            keyword: 搜索关键词
            game_gid: 可选的游戏GID过滤

        Returns:
            匹配的EventEntity列表
        """
        return self.event_repo.search_events(keyword, game_gid)

    @cached("events.recent", timeout=60)
    def get_recent_events(
        self, game_gid: Optional[int] = None, limit: int = 10
    ) -> List[EventEntity]:
        """
        获取最近的事件 (带缓存 - 短TTL用于实时数据)

        Args:
            game_gid: 可选的游戏GID过滤
            limit: 返回数量限制

        Returns:
            最近的EventEntity列表
        """
        return self.event_repo.get_recent_events(game_gid, limit)

    @cached("events.statistics", timeout=300)
    def get_event_statistics(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件统计 (带缓存)

        Args:
            event_id: 事件ID

        Returns:
            事件统计信息字典, 不存在返回None
        """
        return self.event_repo.get_event_statistics(event_id)

    def get_bloom_filter_stats(self) -> Dict[str, Any]:
        """
        获取Bloom Filter统计信息

        Returns:
            Bloom Filter统计字典
        """
        return self.bloom_filter.get_stats()

    def rebuild_bloom_filter(self) -> Dict[str, Any]:
        """
        重建Bloom Filter (从数据库)

        Returns:
            重建统计信息
        """
        logger.info("🔄 Rebuilding Events Bloom Filter from database...")

        # 获取所有现有事件
        events = self.event_repo.find_all()

        # 清空并重建Bloom Filter
        self.bloom_filter.clear()
        for event in events:
            cache_key = f"events:{event.id}"
            self.bloom_filter.add(cache_key)

        stats = self.bloom_filter.get_stats()
        logger.info(f"✅ Events Bloom Filter rebuilt: {stats['total_items']} items")

        return stats

    @cached("events.list.paginated", timeout=120)
    def get_events_paginated(
        self,
        game_gid: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取分页事件列表（支持搜索和游戏过滤）

        Args:
            game_gid: 可选的游戏GID过滤
            page: 页码（从1开始）
            per_page: 每页数量
            search: 搜索关键词

        Returns:
            包含事件列表和分页信息的字典
        """
        # 使用Repository方法（修复架构违规）
        return self.event_repo.get_paginated(
            game_gid=game_gid,
            page=page,
            per_page=per_page,
            search=search
        )

    @cached("events.detail.with_game", timeout=300)
    def get_event_detail_with_game(self, event_id: int, game_gid: int) -> Optional[Dict[str, Any]]:
        """
        获取事件详情（包含游戏信息）

        Args:
            event_id: 事件ID
            game_gid: 游戏GID

        Returns:
            事件详情字典，不存在返回None
        """
        # 使用Repository方法（修复架构违规）
        return self.event_repo.find_detail_with_game(event_id, game_gid)

    @cached("event_params.list", timeout=300)
    def get_event_parameters(self, event_id: int) -> List[Dict[str, Any]]:
        """
        获取事件参数列表

        Args:
            event_id: 事件ID

        Returns:
            参数列表
        """
        # 使用Repository方法（修复架构违规）
        return self.event_repo.get_event_parameters(event_id)

    def create_event_with_parameters(
        self,
        event_data: EventEntity,
        parameters: List[Dict[str, Any]]
    ) -> EventEntity:
        """
        创建事件及其参数

        Args:
            event_data: 事件Entity
            parameters: 参数列表

        Returns:
            创建的EventEntity

        Raises:
            ValueError: 游戏不存在或事件已存在
        """
        # 验证游戏存在
        game: Optional[Any] = self.game_repo.find_by_gid(event_data.game_gid)
        if not game:
            raise ValueError(f"Game not found: gid={event_data.game_gid}")

        # 验证事件名唯一性
        existing = self.event_repo.find_by_name(event_data.name, event_data.game_gid)
        if existing:
            raise ValueError(
                f"Event '{event_data.name}' already exists for game {event_data.game_gid}"
            )

        # 使用Repository方法创建事件和参数（修复架构违规）
        event_dict = event_data.model_dump()
        event_dict['ods_db'] = game.ods_db  # 添加ods_db字段用于生成表名

        # Ensure game.id is available
        game_id: int = game.id if hasattr(game, 'id') and game.id is not None else 0

        result: Optional[EventEntity] = self.event_repo.create_with_parameters(
            event_data=event_dict,
            game_id=game_id,
            parameters=parameters
        )

        if result is None:
            raise ValueError("Failed to create event with parameters")

        # 失效缓存
        self.invalidator.invalidate_pattern("events.list")
        self.invalidator.invalidate_pattern("dashboard_statistics")

        # 添加到Bloom Filter
        cache_key = f"events:{result.id}"
        self.bloom_filter.add(cache_key)

        logger.info(
            f"事件创建成功: event_id={result.id}, game_gid={event_data.game_gid}, "
            f"parameters_count={len(parameters)}"
        )

        return result

    @cached("event_categories.default", timeout=1800)
    def get_or_create_default_category(self) -> int:
        """
        获取或创建"未分类"类别（带缓存）

        Returns:
            类别ID

        Note:
            使用EventCategoryRepository（ERS架构合规）
        """
        category_id = self.category_repo.get_or_create_default()
        logger.info(f"获取或创建默认类别'未分类': category_id={category_id}")
        return category_id

    @cached("event_categories.exists", timeout=1800)
    def validate_category_exists(self, category_id: int) -> bool:
        """
        验证类别是否存在（带缓存）

        Args:
            category_id: 类别ID

        Returns:
            是否存在

        Note:
            使用EventCategoryRepository（ERS架构合规）
        """
        return self.category_repo.exists_by_id(category_id)

    def update_event_with_invalidation(
        self,
        event_id: int,
        event_name: str,
        event_name_cn: str,
        category_id: Optional[int] = None,
        include_in_common_params: int = 1
    ) -> Optional[EventEntity]:
        """
        更新事件并失效缓存

        Args:
            event_id: 事件ID
            event_name: 事件名
            event_name_cn: 事件中文名
            category_id: 类别ID
            include_in_common_params: 是否包含在公共参数中

        Returns:
            更新后的EventEntity，不存在返回None

        Raises:
            ValueError: 事件不存在
        """
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event not found: id={event_id}")

        # 使用Repository更新方法（修复架构违规）
        updates = {
            "event_name": event_name,
            "event_name_cn": event_name_cn,
            "category_id": category_id,
            "include_in_common_params": include_in_common_params
        }

        self.event_repo.update(event_id, updates)

        # 失效缓存
        self.invalidator.invalidate_pattern("events.list")
        self.invalidator.invalidate_pattern(f"events.detail:{event_id}")

        logger.info(f"事件更新成功: event_id={event_id}, event_name={event_name}")

        return self.event_repo.find_by_id(event_id)

    def batch_delete_events(self, event_ids: List[int]) -> int:
        """
        批量删除事件

        Args:
            event_ids: 事件ID列表

        Returns:
            删除的事件数量
        """
        # 使用Repository的批量删除方法（修复架构违规）
        deleted_count = self.event_repo.delete_batch(event_ids)

        # 失效缓存
        self.invalidator.invalidate_pattern("events.list")
        logger.info(f"批量删除事件成功: count={deleted_count}")

        return deleted_count

    def batch_update_events(
        self,
        event_ids: List[int],
        updates: Dict[str, Any]
    ) -> int:
        """
        批量更新事件

        Args:
            event_ids: 事件ID列表
            updates: 更新字段字典

        Returns:
            更新的事件数量
        """
        # 使用Repository的批量更新方法（修复架构违规）
        updated_count = self.event_repo.update_batch(event_ids, updates)

        # 失效缓存
        self.invalidator.invalidate_pattern("events.list")
        logger.info(f"批量更新事件成功: count={updated_count}")

        return updated_count

    @cached("events.count", timeout=120)
    def get_events_count(
        self,
        game_gid: Optional[int] = None,
        search: Optional[str] = None
    ) -> int:
        """
        获取事件数量（带缓存）

        Args:
            game_gid: 可选的游戏GID过滤
            search: 可选的搜索关键词

        Returns:
            事件数量
        """
        # 使用Repository方法（修复架构违规）
        return self.event_repo.count_by_filters(game_gid, search)

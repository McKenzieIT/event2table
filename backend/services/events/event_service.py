#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event Service - Business logic layer (simplified architecture).

This service provides business logic for event management:
- Uses unified Entity model (EventEntity)
- Removes DDD abstractions to simplify business logic
- Integrates cache protection and invalidation mechanisms
- Integrates Bloom Filter to prevent cache penetration (2026-02-25)
"""

import logging
import os
import threading
from typing import Any, Dict, List, Optional

from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter
from backend.core.cache.cache_system import cached
from backend.core.cache.decorators import cache_invalidate  # ⚡ PERF: Phase 1.3
from backend.models.entities import EventEntity
from backend.models.repositories.event_categories import EventCategoryRepository
from backend.models.repositories.events import EventRepository
from backend.models.repositories.games import GameRepository

logger = logging.getLogger(__name__)


class EventService:
    """Event business service with Bloom Filter protection.

    This service handles event management operations including CRUD,
    caching, and Bloom Filter integration for cache penetration prevention.
    """

    def __init__(self) -> None:
        """Initialize the EventService with required repositories and cache."""
        from backend.core.cache.cache_system import CacheInvalidator, HierarchicalCache

        self.event_repo = EventRepository()
        self.game_repo = GameRepository()
        self.category_repo = EventCategoryRepository()
        self.cache: HierarchicalCache = HierarchicalCache()
        self.invalidator: CacheInvalidator = CacheInvalidator(self.cache)

        # Bloom Filter延迟初始化(lazy loading)
        self._bloom_filter: Optional[EnhancedBloomFilter] = None
        self._bloom_filter_lock = threading.Lock()
        logger.info("✅ EventService initialized (Bloom Filter lazy)")

    @property
    def bloom_filter(self) -> EnhancedBloomFilter:
        """Lazy-loaded Bloom Filter instance (thread-safe).

        Returns:
            EnhancedBloomFilter: The Bloom Filter instance for event ID validation.

        Raises:
            AssertionError: If bloom_filter is None (should never happen after initialization).
        """
        if self._bloom_filter is None:
            with self._bloom_filter_lock:
                if self._bloom_filter is None:
                    logger.info("Lazy initializing EventService Bloom Filter...")
                    self._bloom_filter = EnhancedBloomFilter(
                        capacity=500000,  # 50万容量（事件数量通常比游戏多）
                        error_rate=0.001,  # 0.1%误判率
                        persistence_path="data/events_bloom_filter.pkl",
                        strict_validation=self._is_test_mode(),
                    )
                    logger.info("✅ EventService Bloom Filter initialized")
        # Assert non-None for type checker (property always returns non-None after initialization)
        assert (
            self._bloom_filter is not None
        ), "Bloom Filter should be initialized after property access"
        return self._bloom_filter

    def _is_test_mode(self) -> bool:
        """Check if the code is running in test mode.

        Returns:
            bool: True if in test mode, False otherwise.
        """
        return (
            os.environ.get("TESTING") == "true" or os.environ.get("PYTEST_CURRENT_TEST") is not None
        )

    @cached("events.list", timeout=120)
    def get_events_by_game(
        self, game_gid: int, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """Get paginated event list by game GID with caching.

        Args:
            game_gid: Game business GID.
            page: Page number starting from 1.
            per_page: Number of events per page.

        Returns:
            A dictionary containing:
                - events: List of EventEntity objects
                - total: Total number of events
                - page: Current page number
                - per_page: Events per page
                - total_pages: Total number of pages

        Raises:
            ValueError: If the game does not exist.

        Example:
            >>> service = EventService()
            >>> result = service.get_events_by_game(10000147, page=1, per_page=20)
            >>> print(f"Total events: {result['total']}")
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
        """Get event by ID with Bloom Filter protection.

        Uses Bloom Filter to prevent database pressure from querying non-existent
        event IDs.

        Args:
            event_id: Event ID.

        Returns:
            EventEntity if found, None otherwise.

        Example:
            >>> service = EventService()
            >>> event = service.get_event_by_id(1)
            >>> if event:
            ...     print(f"Event: {event.event_name}")
        """
        # 检查Bloom Filter
        cache_key = f"events:{event_id}"
        if not self.bloom_filter.contains(cache_key):
            logger.debug(f"⚡ Bloom Filter: event {event_id} does not exist (fast reject)")
            return None

        # Bloom Filter说可能存在, 查询数据库
        event = self.event_repo.find_by_id(event_id)

        # 如果存在, 添加到Bloom Filter
        if event:
            self.bloom_filter.add(cache_key)
            logger.debug(f"✅ Bloom Filter: event {event_id} exists, added to filter")
        else:
            # 不存在(Bloom Filter误判), 也添加到Filter防止重复查询
            self.bloom_filter.add(cache_key)
            logger.debug(f"⚠️ Bloom Filter: event {event_id} false positive, added to filter")

        return event

    @cached("events.with_params", timeout=300)
    def get_event_with_params(self, event_id: int) -> Optional[Dict[str, Any]]:
        """Get event with its parameters with caching.

        Args:
            event_id: Event ID.

        Returns:
            Dictionary containing event and parameter information,
            or None if not found.

        Example:
            >>> service = EventService()
            >>> event_data = service.get_event_with_params(1)
            >>> if event_data:
            ...     print(f"Event: {event_data['event']}")
            ...     print(f"Params: {event_data['parameters']}")
        """
        return self.event_repo.get_with_parameters(event_id)

    @cache_invalidate  # ⚡ PERF: Phase 1.3 - Auto-invalidate dashboard_statistics
    def create_event(self, event_data: EventEntity) -> EventEntity:
        """Create a new event with cache invalidation and Bloom Filter update.

        Args:
            event_data: Event Entity (validated by Pydantic).

        Returns:
            The created EventEntity.

        Raises:
            ValueError: If game does not exist or event name already exists.
            ValidationError: If data validation fails.

        Example:
            >>> service = EventService()
            >>> event = EventEntity(
            ...     game_gid=10000147,
            ...     name="login",
            ...     event_name_cn="登录"
            ... )
            >>> created = service.create_event(event)
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

    @cache_invalidate  # ⚡ PERF: Phase 1.3 - Auto-invalidate dashboard_statistics
    def update_event(self, event_id: int, updates: Dict[str, Any]) -> EventEntity:
        """Update event with automatic cache invalidation.

        Args:
            event_id: Event ID.
            updates: Dictionary of fields to update.

        Returns:
            The updated EventEntity.

        Raises:
            ValueError: If event does not exist.

        Example:
            >>> service = EventService()
            >>> updated = service.update_event(1, {"event_name_cn": "登录V2"})
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

    @cache_invalidate  # ⚡ PERF: Phase 1.3 - Auto-invalidate dashboard_statistics
    def delete_event(self, event_id: int) -> None:
        """Delete event with automatic cache invalidation.

        Args:
            event_id: Event ID.

        Raises:
            ValueError: If event does not exist.

        Example:
            >>> service = EventService()
            >>> service.delete_event(1)
        """
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event not found: id={event_id}")

        game_gid = event.game_gid
        self.event_repo.delete(event_id)

        # 失效事件相关缓存
        self.invalidator.invalidate_pattern("events.list")
        self.invalidator.invalidate_pattern(f"events.detail:{event_id}")
        logger.info(f"事件删除成功,已失效缓存: event_id={event_id}, game_gid={game_gid}")

    @cached("events.search", timeout=120)
    def search_events(self, keyword: str, game_gid: Optional[int] = None) -> List[EventEntity]:
        """Search events by keyword with caching.

        Args:
            keyword: Search keyword.
            game_gid: Optional game GID filter.

        Returns:
            List of matching EventEntity objects.

        Example:
            >>> service = EventService()
            >>> results = service.search_events("login", game_gid=10000147)
        """
        return self.event_repo.search_events(keyword, game_gid)

    @cached("events.recent", timeout=60)
    def get_recent_events(
        self, game_gid: Optional[int] = None, limit: int = 10
    ) -> List[EventEntity]:
        """Get recent events with caching (short TTL for real-time data).

        Args:
            game_gid: Optional game GID filter.
            limit: Maximum number of events to return.

        Returns:
            List of recent EventEntity objects.

        Example:
            >>> service = EventService()
            >>> recent = service.get_recent_events(game_gid=10000147, limit=5)
        """
        return self.event_repo.get_recent_events(game_gid, limit)

    @cached("events.statistics", timeout=600)  # ⚡ TTL优化: 300秒→600秒 (10分钟)
    def get_event_statistics(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Get event statistics with caching.

        ⚡ TTL设置理由: 事件统计数据变化较慢
        - 事件统计（参数数量, 使用频率等）相对稳定
        - 10分钟TTL减少数据库查询, 提升性能
        - 缓存失效会在事件/参数变更时自动清理

        Args:
            event_id: Event ID.

        Returns:
            Dictionary of event statistics, or None if not found.

        Example:
            >>> service = EventService()
            >>> stats = service.get_event_statistics(1)
        """
        return self.event_repo.get_event_statistics(event_id)

    def get_bloom_filter_stats(self) -> Dict[str, Any]:
        """Get Bloom Filter statistics.

        Returns:
            Dictionary containing Bloom Filter statistics including:
                - total_items: Number of items in the filter
                - size: Filter size in bytes
                - capacity: Filter capacity
                - error_rate: Current error rate

        Example:
            >>> service = EventService()
            >>> stats = service.get_bloom_filter_stats()
            >>> print(f"Items: {stats['total_items']}")
        """
        return self.bloom_filter.get_stats()

    def rebuild_bloom_filter(self) -> Dict[str, Any]:
        """Rebuild Bloom Filter from database.

        This method clears and rebuilds the Bloom Filter by loading all
        existing events from the database.

        Returns:
            Dictionary containing rebuild statistics.

        Example:
            >>> service = EventService()
            >>> stats = service.rebuild_bloom_filter()
            >>> print(f"Rebuilt {stats['total_items']} items")
        """
        logger.info("🔄 Rebuilding Events Bloom Filter from database...")

        # 获取所有现有事件
        events = self.event_repo.find_all()

        # 清空并重建Bloom Filter
        self.bloom_filter.clear()
        for event in events:
            cache_key = f"events:{event.id}"
            self.bloom_filter.add(cache_key)

        stats: Dict[str, Any] = self.bloom_filter.get_stats()
        logger.info(f"✅ Events Bloom Filter rebuilt: {stats['total_items']} items")

        return stats

    @cached("events.list.paginated", timeout=120)
    def get_events_paginated(
        self,
        game_gid: Optional[int] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
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
        # 使用Repository方法(修复架构违规)
        return self.event_repo.get_paginated(
            game_gid=game_gid, page=page, per_page=per_page, search=search
        )

    @cached("events.detail.with_game", timeout=300)
    def get_event_detail_with_game(self, event_id: int, game_gid: int) -> Optional[Dict[str, Any]]:
        """
        获取事件详情（包含游戏信息）

        Args:
            event_id: 事件ID
            game_gid: 游戏GID

        Returns:
            事件详情字典, 不存在返回None
        """
        # 使用Repository方法(修复架构违规)
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
        # 使用Repository方法(修复架构违规)
        return self.event_repo.get_event_parameters(event_id)

    def create_event_with_parameters(
        self, event_data: EventEntity, parameters: List[Dict[str, Any]]
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

        # 使用Repository方法创建事件和参数(修复架构违规)
        event_dict = event_data.model_dump()
        event_dict['ods_db'] = game.ods_db  # 添加ods_db字段用于生成表名

        # Ensure game.id is available
        game_id: int = game.id if hasattr(game, 'id') and game.id is not None else 0

        result: Optional[EventEntity] = self.event_repo.create_with_parameters(
            event_data=event_dict, game_id=game_id, parameters=parameters
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
        include_in_common_params: int = 1,
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
            更新后的EventEntity, 不存在返回None

        Raises:
            ValueError: 事件不存在
        """
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event not found: id={event_id}")

        # 使用Repository更新方法(修复架构违规)
        updates = {
            "event_name": event_name,
            "event_name_cn": event_name_cn,
            "category_id": category_id,
            "include_in_common_params": include_in_common_params,
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
        # 使用Repository的批量删除方法(修复架构违规)
        deleted_count = self.event_repo.delete_batch(event_ids)

        # 失效缓存
        self.invalidator.invalidate_pattern("events.list")
        logger.info(f"批量删除事件成功: count={deleted_count}")

        return deleted_count

    def batch_update_events(self, event_ids: List[int], updates: Dict[str, Any]) -> int:
        """
        批量更新事件

        Args:
            event_ids: 事件ID列表
            updates: 更新字段字典

        Returns:
            更新的事件数量
        """
        # 使用Repository的批量更新方法(修复架构违规)
        updated_count = self.event_repo.update_batch(event_ids, updates)

        # 失效缓存
        self.invalidator.invalidate_pattern("events.list")
        logger.info(f"批量更新事件成功: count={updated_count}")

        return updated_count

    @cached("events.count", timeout=120)
    def get_events_count(self, game_gid: Optional[int] = None, search: Optional[str] = None) -> int:
        """
        获取事件数量（带缓存）

        Args:
            game_gid: 可选的游戏GID过滤
            search: 可选的搜索关键词

        Returns:
            事件数量
        """
        # 使用Repository方法(修复架构违规)
        return self.event_repo.count_by_filters(game_gid, search)

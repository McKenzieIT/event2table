#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Service - 业务逻辑层 (精简架构)

提供事件相关的业务逻辑服务
- 使用统一Entity模型 (EventEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
"""

from typing import List, Optional, Dict, Any
import logging
from backend.models.entities import EventEntity
from backend.models.repositories.events import EventRepository
from backend.models.repositories.games import GameRepository
from backend.core.cache.cache_system import CacheInvalidator, cached

logger = logging.getLogger(__name__)


class EventService:
    """事件业务服务 (精简架构)"""

    def __init__(self):
        self.event_repo = EventRepository()
        self.game_repo = GameRepository()
        from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)

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
        根据ID获取事件 (带缓存)

        Args:
            event_id: 事件ID

        Returns:
            EventEntity, 不存在返回None
        """
        return self.event_repo.find_by_id(event_id)

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
        创建事件 (自动失效缓存)

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
        logger.info(
            f"事件创建成功,已失效缓存: event_id={result.id}, game_gid={event_data.game_gid}"
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

    def search_events(
        self, keyword: str, game_gid: Optional[int] = None
    ) -> List[EventEntity]:
        """
        搜索事件

        Args:
            keyword: 搜索关键词
            game_gid: 可选的游戏GID过滤

        Returns:
            匹配的EventEntity列表
        """
        return self.event_repo.search_events(keyword, game_gid)

    def get_recent_events(
        self, game_gid: Optional[int] = None, limit: int = 10
    ) -> List[EventEntity]:
        """
        获取最近的事件

        Args:
            game_gid: 可选的游戏GID过滤
            limit: 返回数量限制

        Returns:
            最近的EventEntity列表
        """
        return self.event_repo.get_recent_events(game_gid, limit)

    def get_event_statistics(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件统计

        Args:
            event_id: 事件ID

        Returns:
            事件统计信息字典, 不存在返回None
        """
        return self.event_repo.get_event_statistics(event_id)

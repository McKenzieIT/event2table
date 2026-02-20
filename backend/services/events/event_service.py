#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event Service - 业务逻辑层

提供事件相关的业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from backend.models.repositories.events import EventRepository
from backend.models.repositories.games import GameRepository


class EventService:
    """事件业务服务"""

    def __init__(self):
        self.event_repo = EventRepository()
        self.game_repo = GameRepository()

    def get_events_by_game(
        self, game_gid: int, page: int = 1, per_page: int = 20
    ) -> Dict[str, Any]:
        """根据游戏GID获取事件列表

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

    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取事件

        Args:
            event_id: 事件ID

        Returns:
            事件信息，不存在返回None
        """
        return self.event_repo.find_by_id(event_id)

    def get_event_with_params(self, event_id: int) -> Optional[Dict[str, Any]]:
        """获取事件及其参数

        Args:
            event_id: 事件ID

        Returns:
            包含事件和参数信息的字典，不存在返回None
        """
        return self.event_repo.get_with_parameters(event_id)

    def create_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建事件

        Args:
            event_data: 事件数据，包含game_gid、event_name等字段

        Returns:
            创建的事件信息

        Raises:
            ValueError: game_gid或event_name无效，或事件已存在
        """
        game_gid = event_data.get("game_gid")
        if not game_gid:
            raise ValueError("game_gid is required")

        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game not found: gid={game_gid}")

        event_name = event_data.get("event_name")
        if not event_name:
            raise ValueError("event_name is required")

        existing = self.event_repo.find_by_name(event_name, game_gid)
        if existing:
            raise ValueError(f"Event '{event_name}' already exists for game {game_gid}")

        created = self.event_repo.create(event_data)
        if created is None:
            raise ValueError("Failed to create event")

        event_id: int = created["id"]
        result = self.event_repo.find_by_id(event_id)
        if result is None:
            raise ValueError("Failed to create event")
        return result

    def update_event(self, event_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新事件

        Args:
            event_id: 事件ID
            updates: 更新字段

        Returns:
            更新后的事件信息

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
        return result

    def delete_event(self, event_id: int) -> bool:
        """删除事件

        Args:
            event_id: 事件ID

        Returns:
            删除成功返回True

        Raises:
            ValueError: 事件不存在
        """
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event not found: id={event_id}")

        self.event_repo.delete(event_id)
        return True

    def search_events(
        self, keyword: str, game_gid: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """搜索事件

        Args:
            keyword: 搜索关键词
            game_gid: 可选的游戏GID过滤

        Returns:
            匹配的事件列表
        """
        return self.event_repo.search_events(keyword, game_gid)

    def get_recent_events(
        self, game_gid: Optional[int] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取最近的事件

        Args:
            game_gid: 可选的游戏GID过滤
            limit: 返回数量限制

        Returns:
            最近的事件列表
        """
        return self.event_repo.get_recent_events(game_gid, limit)

    def get_event_statistics(self, event_id: int) -> Optional[Dict[str, Any]]:
        """获取事件统计

        Args:
            event_id: 事件ID

        Returns:
            事件统计信息，不存在返回None
        """
        return self.event_repo.get_event_statistics(event_id)

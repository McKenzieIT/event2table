#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Service - 业务逻辑层

提供游戏相关的业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from backend.core.utils.converters import fetch_one_as_dict, fetch_all_as_dict
from backend.models.repositories.games import GameRepository


class GameService:
    """游戏业务服务"""

    def __init__(self):
        self.game_repo = GameRepository()

    def get_all_games(self, include_stats: bool = False) -> List[Dict[str, Any]]:
        """获取所有游戏

        Args:
            include_stats: 是否包含统计信息（事件数量、流程数量）

        Returns:
            游戏列表，包含基本信息和可选的统计信息

        Raises:
            DatabaseError: 数据库查询失败
        """
        games = self.game_repo.find_all()

        if include_stats:
            for game in games:
                game["event_count"] = self._get_event_count(game["gid"])
                game["flow_count"] = self._get_flow_count(game["gid"])

        return games

    def get_game_by_gid(self, game_gid: int) -> Optional[Dict[str, Any]]:
        """根据GID获取游戏

        Args:
            game_gid: 游戏业务GID

        Returns:
            游戏信息，不存在返回None
        """
        return self.game_repo.find_by_gid(game_gid)

    def create_game(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建游戏

        Args:
            game_data: 游戏数据，包含gid、name、ods_db等字段

        Returns:
            创建的游戏信息

        Raises:
            ValueError: gid已存在或无效
        """
        gid_value = game_data.get("gid")
        if gid_value is None:
            raise ValueError("gid is required")

        existing = self.game_repo.find_by_gid(gid_value)
        if existing:
            raise ValueError(f"Game gid {gid_value} already exists")

        created = self.game_repo.create(game_data)
        if created is None:
            raise ValueError("Failed to create game")

        game_id: int = created["id"]
        result = self.game_repo.find_by_id(game_id)
        if result is None:
            raise ValueError("Failed to create game")
        return result

    def update_game(self, game_gid: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新游戏

        Args:
            game_gid: 游戏业务GID
            updates: 更新字段

        Returns:
            更新后的游戏信息

        Raises:
            ValueError: 游戏不存在
        """
        game = self.game_repo.find_by_gid(game_gid)
        if game is None:
            raise ValueError(f"Game not found: gid={game_gid}")

        self.game_repo.update(game_gid, updates)
        result = self.game_repo.find_by_gid(game_gid)
        if result is None:
            raise ValueError("Failed to update game")
        return result

    def delete_game(self, game_gid: int) -> bool:
        """删除游戏

        Args:
            game_gid: 游戏业务GID

        Returns:
            删除成功返回True

        Raises:
            ValueError: 游戏不存在或有关联数据
        """
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game not found: gid={game_gid}")

        event_count = self._get_event_count(game_gid)
        if event_count > 0:
            raise ValueError(f"Cannot delete game with {event_count} events")

        self.game_repo.delete(game_gid)
        return True

    def get_games_with_stats(self) -> List[Dict[str, Any]]:
        """获取所有游戏及其统计信息

        Returns:
            游戏列表，包含事件数量和流程数量统计
        """
        return self.game_repo.get_all_with_stats()

    def search_games(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索游戏

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的游戏列表
        """
        return self.game_repo.search_by_name(f"%{keyword}%")

    def _get_event_count(self, game_gid: int) -> int:
        """获取游戏事件数量

        Args:
            game_gid: 游戏业务GID

        Returns:
            事件数量
        """
        result = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?", (game_gid,)
        )
        return result["count"] if result else 0

    def _get_flow_count(self, game_gid: int) -> int:
        """获取游戏流程数量

        Args:
            game_gid: 游戏业务GID

        Returns:
            流程数量
        """
        result = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM flow_templates WHERE game_gid = ?",
            (game_gid,),
        )
        return result["count"] if result else 0

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Service - 业务逻辑层 (精简架构)

提供游戏相关的业务逻辑服务
- 使用统一Entity模型 (GameEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
"""

from typing import List, Optional
import logging
from backend.models.entities import GameEntity
from backend.models.repositories.games import GameRepository
from backend.core.cache.cache_system import CacheInvalidator, cached
from backend.core.utils.business_helpers import validate_game_gid

logger = logging.getLogger(__name__)


class GameService:
    """游戏业务服务 (精简架构)"""

    def __init__(self):
        self.game_repo = GameRepository()
        from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)

    @cached("games.list", timeout=120)
    def get_all_games(self, include_stats: bool = False) -> List[GameEntity]:
        """
        获取所有游戏 (带缓存)

        Args:
            include_stats: 是否包含统计信息 (事件数量、流程数量)

        Returns:
            游戏Entity列表

        Raises:
            DatabaseError: 数据库查询失败
        """
        games = self.game_repo.find_all()

        if include_stats:
            for game in games:
                # 添加统计信息 (不持久化到数据库)
                game.event_count = self._get_event_count(game.gid)

        return games

    @cached("games.detail", timeout=300)
    def get_game_by_gid(self, game_gid: int) -> Optional[GameEntity]:
        """
        根据GID获取游戏 (带缓存)

        Args:
            game_gid: 游戏业务GID

        Returns:
            GameEntity, 不存在返回None

        Raises:
            ValueError: game_gid格式不正确
        """
        validate_game_gid(game_gid)
        return self.game_repo.find_by_gid(game_gid)

    def create_game(self, game_data: GameEntity) -> GameEntity:
        """
        创建游戏 (自动失效缓存)

        Args:
            game_data: 游戏Entity (已通过Pydantic验证)

        Returns:
            创建的GameEntity

        Raises:
            ValueError: gid已存在
            ValidationError: 数据验证失败
        """
        # 验证gid唯一性
        existing = self.game_repo.find_by_gid(game_data.gid)
        if existing:
            raise ValueError(f"Game GID {game_data.gid} already exists")

        # 创建游戏 (Entity已通过Pydantic验证)
        result = self.game_repo.create(game_data.model_dump())
        if result is None:
            raise ValueError("Failed to create game")

        # 失效游戏列表缓存
        self.invalidator.invalidate_pattern("games.list")
        logger.info(f"游戏创建成功,已失效缓存: gid={game_data.gid}")

        return result

    def update_game(self, game_gid: int, updates: dict) -> GameEntity:
        """
        更新游戏 (自动失效缓存)

        Args:
            game_gid: 游戏业务GID
            updates: 更新字段字典

        Returns:
            更新后的GameEntity

        Raises:
            ValueError: game不存在
        """
        validate_game_gid(game_gid)

        # 验证游戏存在
        existing = self.game_repo.find_by_gid(game_gid)
        if not existing:
            raise ValueError(f"Game GID {game_gid} not found")

        # 更新游戏
        self.game_repo.update(game_gid, updates)

        # 失效缓存
        self.invalidator.invalidate_pattern("games.list")
        self.invalidator.invalidate_pattern(f"games.detail:{game_gid}")
        logger.info(f"游戏更新成功,已失效缓存: gid={game_gid}")

        return self.get_game_by_gid(game_gid)

    def delete_game(self, game_gid: int) -> None:
        """
        删除游戏 (自动失效缓存)

        Args:
            game_gid: 游戏业务GID

        Raises:
            ValueError: game不存在或有关联数据
        """
        validate_game_gid(game_gid)

        # 验证游戏存在
        existing = self.game_repo.find_by_gid(game_gid)
        if not existing:
            raise ValueError(f"Game GID {game_gid} not found")

        # 删除游戏
        self.game_repo.delete(game_gid)

        # 失效缓存
        self.invalidator.invalidate_pattern("games.list")
        self.invalidator.invalidate_pattern(f"games.detail:{game_gid}")
        logger.info(f"游戏删除成功,已失效缓存: gid={game_gid}")

    def get_by_id(self, game_id: int) -> Optional[GameEntity]:
        """
        根据数据库ID获取游戏

        Args:
            game_id: 数据库自增ID

        Returns:
            GameEntity, 不存在返回None
        """
        return self.game_repo.find_by_id(game_id)

    def batch_delete_games(self, game_gids: List[int]) -> int:
        """
        批量删除游戏 (自动失效缓存)

        Args:
            game_gids: 游戏GID列表

        Returns:
            删除的游戏数量

        Raises:
            ValueError: game_gid包含无效值
        """
        if not game_gids:
            return 0

        # 验证所有gid
        for gid in game_gids:
            validate_game_gid(gid)

        # 批量删除
        deleted_count = self.game_repo.batch_delete(game_gids)

        # 失效缓存
        if deleted_count > 0:
            self.invalidator.invalidate_pattern("games.list")
            for gid in game_gids:
                self.invalidator.invalidate_pattern(f"games.detail:{gid}")
            logger.info(f"批量删除游戏成功,已失效缓存: count={deleted_count}")

        return deleted_count

    # ========== 私有辅助方法 ==========

    def _get_event_count(self, game_gid: int) -> int:
        """获取游戏的事件数量"""
        from backend.core.utils.converters import fetch_one_as_dict

        count = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
            (game_gid,),
        )
        return count["count"] if count else 0

    def _get_flow_count(self, game_gid: int) -> int:
        """获取游戏的流程数量"""
        from backend.core.utils.converters import fetch_one_as_dict

        count = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM canvas_flows WHERE game_gid = ?",
            (game_gid,),
        )
        return count["count"] if count else 0

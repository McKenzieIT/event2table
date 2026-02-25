#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Service - 业务逻辑层 (精简架构)

提供游戏相关的业务逻辑服务
- 使用统一Entity模型 (GameEntity)
- 移除DDD抽象,简化业务逻辑
- 集成缓存防护和失效机制
- 集成Bloom Filter防止缓存穿透 (2026-02-25)
"""

from typing import List, Optional
import logging
from backend.models.entities import GameEntity
from backend.models.repositories.games import GameRepository
from backend.core.cache.cache_system import CacheInvalidator, cached
from backend.core.cache.bloom_filter_enhanced import EnhancedBloomFilter
from backend.core.utils.business_helpers import validate_game_gid

logger = logging.getLogger(__name__)


class GameService:
    """游戏业务服务 (精简架构 + Bloom Filter防护)"""

    def __init__(self):
        self.game_repo = GameRepository()
        from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)

        # 初始化Bloom Filter防止缓存穿透
        self.bloom_filter = EnhancedBloomFilter(
            capacity=100000,  # 10万容量
            error_rate=0.001,  # 0.1%误判率
            persistence_path="data/games_bloom_filter.pkl"
        )
        logger.info("✅ GameService initialized with Bloom Filter protection")

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
        根据GID获取游戏 (带Bloom Filter防护)

        使用Bloom Filter防止查询不存在的game_gid导致数据库压力:
        1. 先检查Bloom Filter
        2. Bloom Filter说不存在 → 直接返回None (避免查询数据库)
        3. Bloom Filter说可能存在 → 查询缓存/数据库
        4. 数据存在 → 添加到Bloom Filter

        Args:
            game_gid: 游戏业务GID

        Returns:
            GameEntity, 不存在返回None

        Raises:
            ValueError: game_gid格式不正确
        """
        validate_game_gid(game_gid)

        # 步骤1: 检查Bloom Filter
        cache_key = f"games:{game_gid}"
        if not self.bloom_filter.contains(cache_key):
            logger.debug(f"⚡ Bloom Filter: game {game_gid} does not exist (fast reject)")
            return None

        # 步骤2: Bloom Filter说可能存在，查询数据库
        game = self.game_repo.find_by_gid(game_gid)

        # 步骤3: 如果存在，添加到Bloom Filter
        if game:
            self.bloom_filter.add(cache_key)
            logger.debug(f"✅ Bloom Filter: game {game_gid} exists, added to filter")
        else:
            # 不存在（Bloom Filter误判），也添加到Filter防止重复查询
            self.bloom_filter.add(cache_key)
            logger.debug(f"⚠️ Bloom Filter: game {game_gid} false positive, added to filter")

        return game

    def create_game(self, game_data: GameEntity) -> GameEntity:
        """
        创建游戏 (自动失效缓存 + 更新Bloom Filter)

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

        # 添加到Bloom Filter
        cache_key = f"games:{game_data.gid}"
        self.bloom_filter.add(cache_key)

        logger.info(f"游戏创建成功,已失效缓存并更新Bloom Filter: gid={game_data.gid}")

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
        删除游戏 (自动失效缓存 + 从Bloom Filter移除)

        注意: Bloom Filter不支持删除操作，重建是唯一方式
        因此我们标记需要重建，而不是立即删除

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

        # Bloom Filter不支持删除，标记需要重建
        # 下次查询时会自动从数据库重建
        logger.info(f"游戏删除成功,已失效缓存: gid={game_gid} (Bloom Filter将在下次重建时更新)")

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

    def get_bloom_filter_stats(self) -> dict:
        """
        获取Bloom Filter统计信息

        Returns:
            Bloom Filter统计字典
        """
        return self.bloom_filter.get_stats()

    def rebuild_bloom_filter(self) -> dict:
        """
        重建Bloom Filter (从Redis缓存或数据库)

        用于删除游戏后同步Bloom Filter状态

        Returns:
            重建统计信息
        """
        logger.info("🔄 Rebuilding Bloom Filter from database...")

        # 获取所有现有游戏
        games = self.game_repo.find_all()

        # 清空并重建Bloom Filter
        self.bloom_filter.clear()
        for game in games:
            cache_key = f"games:{game.gid}"
            self.bloom_filter.add(cache_key)

        stats = self.bloom_filter.get_stats()
        logger.info(f"✅ Bloom Filter rebuilt: {stats['total_items']} items")

        return stats

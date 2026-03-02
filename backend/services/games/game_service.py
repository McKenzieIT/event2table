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
import threading
import os
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

        # Bloom Filter延迟初始化（lazy loading）
        self._bloom_filter = None
        self._bloom_filter_lock = threading.Lock()
        logger.info("✅ GameService initialized (Bloom Filter lazy)")

    @property
    def bloom_filter(self):
        """延迟加载Bloom Filter（线程安全）"""
        if self._bloom_filter is None:
            with self._bloom_filter_lock:
                if self._bloom_filter is None:
                    logger.info("Lazy initializing GameService Bloom Filter...")
                    self._bloom_filter = EnhancedBloomFilter(
                        capacity=100000,  # 10万容量
                        error_rate=0.001,  # 0.1%误判率
                        persistence_path="data/games_bloom_filter.pkl",
                        strict_validation=self._is_test_mode()
                    )
                    logger.info("✅ GameService Bloom Filter initialized")
        return self._bloom_filter

    def _is_test_mode(self) -> bool:
        """检测是否在测试环境"""
        return (
            os.environ.get("TESTING") == "true" or
            os.environ.get("PYTEST_CURRENT_TEST") is not None
        )

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
        根据GID获取游戏

        Args:
            game_gid: 游戏业务GID

        Returns:
            GameEntity, 不存在返回None

        Raises:
            ValueError: game_gid格式不正确
        """
        validate_game_gid(game_gid)

        # 查询数据库
        game = self.game_repo.find_by_gid(game_gid)

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

    @cached("games.detailed_stats", timeout=300)
    def get_games_with_detailed_stats(self) -> List[dict]:
        """
        获取所有游戏及其详细统计信息（带缓存）

        使用LEFT JOIN获取统计信息，避免N+1查询问题

        Returns:
            游戏字典列表（包含详细统计）
        """
        from backend.core.utils.converters import fetch_all_as_dict

        games = fetch_all_as_dict("""
            SELECT
                g.id,
                g.gid,
                g.name,
                g.ods_db,
                g.icon_path,
                g.created_at,
                g.updated_at,
                COUNT(DISTINCT le.id) as event_count,
                COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as param_count,
                COUNT(DISTINCT enc.id) as event_node_count,
                COUNT(DISTINCT CASE WHEN ft.is_active = 1 THEN ft.id END) as flow_template_count
            FROM games g
            LEFT JOIN log_events le ON le.game_gid = g.gid
            LEFT JOIN event_params ep ON ep.event_id = le.id
            LEFT JOIN event_node_configs enc ON enc.game_gid = CAST(g.gid AS INTEGER)
            LEFT JOIN flow_templates ft ON ft.game_gid = g.gid
            GROUP BY g.id, g.gid, g.name, g.ods_db, g.icon_path, g.created_at, g.updated_at
            ORDER BY g.id
        """)

        return games

    @cached("games.deletion_impact", timeout=60)
    def check_deletion_impact(self, game_gid: int) -> dict:
        """
        检查删除游戏的影响范围 (带缓存 - 短TTL用于实时数据)

        Args:
            game_gid: 游戏业务GID

        Returns:
            影响统计字典
        """
        from backend.core.utils.converters import fetch_one_as_dict

        impact = {
            "game_gid": game_gid,
            "has_associated_data": False,
            "event_count": 0,
            "param_count": 0,
            "node_config_count": 0,
        }

        # 检查事件数量
        event_count = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM log_events WHERE game_gid = ?",
            (game_gid,)
        )
        impact["event_count"] = event_count["count"] if event_count else 0

        # 检查参数数量（通过事件关联）
        param_count = fetch_one_as_dict(
            """
            SELECT COUNT(*) as count
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE le.game_gid = ?
        """,
            (game_gid,)
        )
        impact["param_count"] = param_count["count"] if param_count else 0

        # 检查Canvas节点配置
        node_count = fetch_one_as_dict(
            "SELECT COUNT(*) as count FROM event_node_configs WHERE game_gid = ?",
            (game_gid,)
        )
        impact["node_config_count"] = node_count["count"] if node_count else 0

        # 判断是否有关联数据
        impact["has_associated_data"] = any([
            impact["event_count"] > 0,
            impact["param_count"] > 0,
            impact["node_config_count"] > 0,
        ])

        logger.debug(
            f"Deletion impact for game_gid={game_gid}: "
            f"events={impact['event_count']}, "
            f"params={impact['param_count']}, "
            f"nodes={impact['node_config_count']}"
        )

        return impact

    def cascade_delete_game(self, game_gid: int, force: bool = False) -> dict:
        """
        级联删除游戏及其所有关联数据

        Args:
            game_gid: 游戏业务GID
            force: 是否强制删除（跳过关联数据检查）

        Returns:
            删除结果字典

        Raises:
            ValueError: 游戏不存在或未确认删除有关联数据的游戏
        """
        validate_game_gid(game_gid)

        # 验证游戏存在
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game GID {game_gid} not found")

        # 检查删除影响
        impact = self.check_deletion_impact(game_gid)

        # 如果有关联数据且未强制删除，返回影响统计
        if not force and impact["has_associated_data"]:
            raise ValueError(
                f"Game has {impact['event_count']} events, "
                f"{impact['param_count']} parameters, "
                f"{impact['node_config_count']} node configs. "
                f"Set force=True to delete."
            )

        # 执行级联删除
        from backend.core.database import get_db_connection

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                cursor.execute("BEGIN IMMEDIATE")  # 立即锁，防止并发修改

                # 验证游戏仍然存在（防止已被其他请求删除）
                cursor.execute("SELECT id FROM games WHERE gid = ?", (game_gid,))
                game_exists = cursor.fetchone()

                if not game_exists:
                    conn.rollback()
                    raise ValueError(f"Game GID {game_gid} not found (may have been deleted)")

                # 1. 删除事件参数（通过事件ID）
                cursor.execute(
                    """
                    DELETE FROM event_params
                    WHERE event_id IN (
                        SELECT id FROM log_events WHERE game_gid = ?
                    )
                """,
                    (game_gid,),
                )

                # 2. 删除事件记录
                cursor.execute("DELETE FROM log_events WHERE game_gid = ?", (game_gid,))

                # 3. 删除Canvas节点配置
                cursor.execute(
                    "DELETE FROM event_node_configs WHERE game_gid = ?",
                    (game_gid,)
                )

                # 4. 删除游戏记录
                cursor.execute("DELETE FROM games WHERE gid = ?", (game_gid,))

                conn.commit()

                logger.info(
                    f"Cascade deleted game {game.name} (GID: {game_gid}): "
                    f"{impact['event_count']} events, "
                    f"{impact['param_count']} params, "
                    f"{impact['node_config_count']} node configs"
                )

                # 失效缓存
                self.invalidator.invalidate_pattern("games.list")
                self.invalidator.invalidate_pattern(f"games.detail:{game_gid}")
                self.invalidator.invalidate_pattern("dashboard_statistics")

                return {
                    "success": True,
                    "deleted_event_count": impact["event_count"],
                    "deleted_param_count": impact["param_count"],
                    "deleted_node_config_count": impact["node_config_count"],
                }

            except Exception as e:
                conn.rollback()
                raise e

            finally:
                conn.close()

        except Exception as e:
            logger.error(f"Error cascade deleting game: {e}")
            raise

    def batch_update_games(self, game_gids: List[int], updates: dict) -> int:
        """
        批量更新游戏

        Args:
            game_gids: 游戏GID列表
            updates: 更新字段字典

        Returns:
            更新的游戏数量

        Raises:
            ValueError: 更新字段无效
        """
        if not game_gids:
            return 0

        if not updates:
            raise ValueError("No update fields provided")

        # 验证所有gid
        for gid in game_gids:
            validate_game_gid(gid)

        # 批量更新
        updated_count = self.game_repo.batch_update_by_gid(game_gids, updates)

        # 失效缓存
        if updated_count > 0:
            self.invalidator.invalidate_pattern("games.list")
            for gid in game_gids:
                self.invalidator.invalidate_pattern(f"games.detail:{gid}")
            logger.info(f"批量更新游戏成功,已失效缓存: count={updated_count}")

        return updated_count

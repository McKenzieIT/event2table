#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存预热系统
===========
应用启动时和定时自动预热热点数据，确保缓存命中率高

版本: 1.0.0
日期: 2026-01-20
"""

from backend.core.cache.cache_hierarchical import hierarchical_cache
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict
import logging
import threading
import time

logger = logging.getLogger(__name__)


class CacheWarmer:
    """缓存预热管理器

    功能:
    - 应用启动时预热热点数据
    - 定时自动预热（默认每小时）
    - 支持选择性预热（游戏、事件、参数模板）
    """

    def __init__(self):
        self.warmed_games = 0
        self.warmed_events = 0
        self.warmed_templates = 0
        self._warming_thread = None
        self._stop_event = threading.Event()

    def warmup_games(self):
        """预热游戏列表（所有游戏）"""
        logger.info("🔥 预热游戏列表...")
        try:
            games = fetch_all_as_dict("SELECT * FROM games ORDER BY id")
            for game in games:
                hierarchical_cache.set("games.detail", game, id=game["id"])

            self.warmed_games = len(games)
            logger.info(f"✅ 预热游戏列表完成: {len(games)}个游戏")

        except Exception as e:
            logger.error(f"❌ 预热游戏列表失败: {e}")

    def warmup_games_list(self):
        """预热游戏列表API（带统计信息）"""
        logger.info("🔥 预热游戏列表API（带统计信息）...")
        try:
            from backend.core.config.config import CacheConfig

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

            # Cache with 1 hour TTL (static data)
            hierarchical_cache.set(
                "games.list", games, ttl=CacheConfig.CACHE_TIMEOUT_STATIC
            )

            logger.info(f"✅ 预热游戏列表API完成: {len(games)}个游戏")

        except Exception as e:
            logger.error(f"❌ 预热游戏列表API失败: {e}")

    def warmup_hot_events(self, limit=100):
        """
        预热热门事件（Top N）

        Args:
            limit: 预热事件数量，默认100
        """
        logger.info(f"🔥 预热热门事件(Top {limit})...")
        try:
            events = fetch_all_as_dict(
                "SELECT * FROM log_events ORDER BY id LIMIT ?", (limit,)
            )
            for event in events:
                hierarchical_cache.set("events.detail", event, id=event["id"])

            self.warmed_events = len(events)
            logger.info(f"✅ 预热热门事件完成: {len(events)}个事件")

        except Exception as e:
            logger.error(f"❌ 预热热门事件失败: {e}")

    def warmup_param_templates(self):
        """预热参数模板（系统模板）"""
        logger.info("🔥 预热参数模板...")
        try:
            templates = fetch_all_as_dict(
                "SELECT * FROM param_templates WHERE is_system = 1"
            )
            for template in templates:
                hierarchical_cache.set(
                    "param_templates.detail", template, id=template["id"]
                )

            self.warmed_templates = len(templates)
            logger.info(f"✅ 预热参数模板完成: {len(templates)}个模板")

        except Exception as e:
            logger.error(f"❌ 预热参数模板失败: {e}")

    def warmup_categories(self):
        """预热分类列表"""
        logger.info("🔥 预热分类列表...")
        try:
            categories = fetch_all_as_dict("SELECT * FROM event_categories ORDER BY id")
            hierarchical_cache.set("categories.list", categories)

            logger.info(f"✅ 预热分类列表完成: {len(categories)}个分类")

        except Exception as e:
            # Table might not exist - log warning but continue
            if "no such table" in str(e):
                logger.warning(f"⚠️ categories表不存在，跳过分类预热")
            else:
                logger.error(f"❌ 预热分类列表失败: {e}")

    def warmup_game_events(self, game_gid: int, limit=50):
        """
        预热特定游戏的事件列表

        Args:
            game_gid: 游戏业务GID
            limit: 预热事件数量，默认50
        """
        logger.info(f"🔥 预热游戏{game_gid}的事件列表...")
        try:
            events = fetch_all_as_dict(
                """SELECT * FROM log_events
                   WHERE game_gid = ?
                   ORDER BY id
                   LIMIT ?""",
                (game_gid, limit),
            )

            for event in events:
                hierarchical_cache.set("events.detail", event, id=event["id"])

            logger.info(f"✅ 预热游戏{game_gid}事件完成: {len(events)}个事件")

        except Exception as e:
            logger.error(f"❌ 预热游戏{game_gid}事件失败: {e}")

    def warmup_on_startup(self, warm_all_events=False):
        """
        应用启动时预热

        Args:
            warm_all_events: 是否预热所有事件（默认仅Top 100）
        """
        logger.info("=" * 60)
        logger.info("开始缓存预热...")
        logger.info("=" * 60)

        try:
            # 预热游戏列表（带统计信息 - 优先预热，这是最常用的API）
            self.warmup_games_list()

            # 预热游戏详情
            self.warmup_games()

            # 预热事件
            if warm_all_events:
                logger.info("预热所有事件...")
                events = fetch_all_as_dict("SELECT * FROM log_events ORDER BY id")
                for event in events:
                    hierarchical_cache.set("events.detail", event, id=event["id"])
                logger.info(f"✅ 预热所有事件完成: {len(events)}个事件")
            else:
                # 仅预热热门事件
                self.warmup_hot_events(limit=100)

            # 预热参数模板
            self.warmup_param_templates()

            # 预热分类（如果表存在）
            self.warmup_categories()

            logger.info("=" * 60)
            logger.info("✅ 缓存预热完成")
            logger.info(f"  - 游戏: {self.warmed_games}个")
            logger.info(f"  - 事件: {self.warmed_events}个")
            logger.info(f"  - 模板: {self.warmed_templates}个")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"❌ 缓存预热失败: {e}")
            import traceback

            traceback.print_exc()

    def start_periodic_warmup(self, interval_hours=1):
        """
        启动定时预热（使用后台线程）

        Args:
            interval_hours: 预热间隔（小时），默认1小时
        """
        if self._warming_thread is not None and self._warming_thread.is_alive():
            logger.warning("⚠️ 定时预热已在运行中")
            return

        self._stop_event.clear()

        def warming_worker():
            """后台预热线程"""
            interval_seconds = interval_hours * 3600
            logger.info(f"✅ 定时预热启动: 每{interval_hours}小时")

            while not self._stop_event.is_set():
                # 等待指定间隔或停止信号
                self._stop_event.wait(interval_seconds)

                # 如果收到停止信号，退出循环
                if self._stop_event.is_set():
                    break

                # 执行预热
                try:
                    self.warmup_on_startup(warm_all_events=False)
                except Exception as e:
                    logger.error(f"❌ 定时预热失败: {e}")

            logger.info("⏹️ 定时预热已停止")

        # 启动后台线程
        self._warming_thread = threading.Thread(
            target=warming_worker, name="CacheWarmer", daemon=True
        )
        self._warming_thread.start()

    def stop_periodic_warmup(self):
        """停止定时预热"""
        if self._warming_thread is None or not self._warming_thread.is_alive():
            logger.warning("⚠️ 定时预热未在运行")
            return

        # 发送停止信号
        self._stop_event.set()

        # 等待线程结束（最多等待5秒）
        self._warming_thread.join(timeout=5)

        if self._warming_thread.is_alive():
            logger.warning("⚠️ 定时预热线程未能及时停止")
        else:
            logger.info("⏹️ 定时预热已停止")

    def get_warmup_stats(self) -> dict:
        """
        获取预热统计信息

        Returns:
            统计信息字典
        """
        return {
            "warmed_games": self.warmed_games,
            "warmed_events": self.warmed_events,
            "warmed_templates": self.warmed_templates,
            "total": self.warmed_games + self.warmed_events + self.warmed_templates,
        }

    def reset_stats(self):
        """重置预热统计"""
        self.warmed_games = 0
        self.warmed_events = 0
        self.warmed_templates = 0
        logger.info("📊 预热统计已重置")


# 全局预热器实例
cache_warmer = CacheWarmer()


logger.info("✅ 缓存预热系统已加载 (1.0.0)")

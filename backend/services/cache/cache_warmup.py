# ⚠️ PERFORMANCE ISSUE: N+1 query detected in this file
# TODO: Refactor to use JOIN or prefetch pattern
# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存预热服务
============

在应用启动时预热常用数据，消除冷启动延迟

功能:
- 预热热门游戏
- 预热常用事件
- 预热参数配置

作者: Event2Table Development Team
版本: 1.0.0
日期: 2026-02-25
"""

import logging
from typing import Dict, Any
from backend.core.cache.cache_system import get_cache
from backend.core.utils.converters import fetch_all_as_dict

logger = logging.getLogger(__name__)


class CacheWarmer:
    """缓存预热器"""

    def __init__(self, cache=None):
        self.cache = cache if cache is not None else get_cache()
        self.stats = {
            "games_warmed": 0,
            "events_warmed": 0,
            "params_warmed": 0,
            "total_keys": 0
        }

    def warmup_popular_games(self, limit: int = 100) -> int:
        """
        预热热门游戏

        Args:
            limit: 预热的游戏数量

        Returns:
            预热的游戏数量
        """
        logger.info(f"🔥 Warming up top {limit} popular games...")

        games = fetch_all_as_dict(
            'SELECT id, gid, name, ods_db FROM games ORDER BY gid LIMIT ?',
            (limit,)
        )

        for game in games:
            cache_key = f"games:{game['gid']}"
            self.cache.set(cache_key, game, ttl=3600)
            self.stats["games_warmed"] += 1

        logger.info(f"✅ Warmed up {len(games)} games")
        return len(games)

    def warmup_recent_events(self, limit: int = 100) -> int:
        """
        预热最近的事件

        Args:
            limit: 预热的事件数量

        Returns:
            预热的事件数量
        """
        logger.info(f"🔥 Warming up {limit} recent events...")

        events = fetch_all_as_dict(
            'SELECT id, event_name, game_gid, created_at FROM log_events ORDER BY created_at DESC LIMIT ?',
            (limit,)
        )

        for event in events:
            cache_key = f"events:{event['id']}"
            self.cache.set(cache_key, event, ttl=1800)
            self.stats["events_warmed"] += 1

        logger.info(f"✅ Warmed up {len(events)} events")
        return len(events)

    def warmup_common_params(self, game_gid: int = None) -> int:
        """
        预热常用参数

        Args:
            game_gid: 可选的游戏GID，不指定则预热所有游戏的参数

        Returns:
            预热的参数数量
        """
        logger.info("🔥 Warming up common parameters...")

        if game_gid:
            params = fetch_all_as_dict(
                '''SELECT ep.* FROM event_params ep
                   INNER JOIN log_events le ON ep.event_id = le.id
                   WHERE le.game_gid = ? AND ep.is_common = 1
                   LIMIT 50''',
                (game_gid,)
            )
        else:
            params = fetch_all_as_dict(
                'SELECT id, param_name, event_id, game_gid, is_common FROM event_params WHERE is_common = 1 LIMIT 100'
            )

        for param in params:
            cache_key = f"params:{param['id']}"
            self.cache.set(cache_key, param, ttl=3600)
            self.stats["params_warmed"] += 1

        logger.info(f"✅ Warmed up {len(params)} parameters")
        return len(params)

    def warmup_all(self, games_limit: int = 100, events_limit: int = 100) -> Dict[str, Any]:
        """
        执行完整预热

        Args:
            games_limit: 预热的游戏数量
            events_limit: 预热的事件数量

        Returns:
            预热统计信息
        """
        logger.info("🚀 Starting cache warmup...")

        # 预热游戏
        self.warmup_popular_games(games_limit)

        # 预热事件
        self.warmup_recent_events(events_limit)

        # 预热参数
        self.warmup_common_params()

        # 获取总缓存键数
        try:
            import redis
            redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)
            self.stats["total_keys"] = redis_client.dbsize()
        except Exception as e:
            logger.warning(f"Failed to get total keys: {e}")

        logger.info(f"✅ Cache warmup completed: {self.stats}")

        return self.stats


def warmup_cache_on_startup():
    """
    应用启动时自动预热缓存

    在web_app.py中调用此函数
    """
    warmer = CacheWarmer()
    stats = warmer.warmup_all(games_limit=100, events_limit=100)

    logger.info(f"🎉 Cache warmup completed:")
    logger.info(f"  - Games: {stats['games_warmed']}")
    logger.info(f"  - Events: {stats['events_warmed']}")
    logger.info(f"  - Params: {stats['params_warmed']}")
    logger.info(f"  - Total keys: {stats['total_keys']}")

    return stats


if __name__ == "__main__":
    # 测试预热
    logging.basicConfig(level=logging.INFO)
    stats = warmup_cache_on_startup()
    print(f"\n📊 Warmup Statistics:")
    print(f"  Games: {stats['games_warmed']}")
    print(f"  Events: {stats['events_warmed']}")
    print(f"  Params: {stats['params_warmed']}")
    print(f"  Total keys: {stats['total_keys']}")

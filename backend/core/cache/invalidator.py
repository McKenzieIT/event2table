#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存失效器模块
==============

提供统一的缓存失效策略管理

版本: 1.0.0
日期: 2026-02-20

功能:
- 精确失效：删除特定缓存键
- 模式失效：使用通配符删除匹配的键
- 关联失效：失效游戏/事件相关的所有缓存
- 批量失效：使用Redis Pipeline优化批量删除
"""

from typing import Optional, Set, List, Tuple, Dict
import logging

from backend.core.cache.cache_system import (
    hierarchical_cache,
    CacheKeyBuilder,
    get_redis_client
)
from backend.core.cache.validators import CacheKeyValidator
from backend.core.cache.filters import SensitiveDataFilter

logger = logging.getLogger(__name__)

# Add sensitive data filter to prevent information leakage
logger.addFilter(SensitiveDataFilter())


class CacheInvalidatorEnhanced:
    """
    增强的缓存失效器
    
    提供多种失效策略:
    1. 精确失效 - 删除特定缓存键
    2. 模式失效 - 使用通配符删除匹配的键
    3. 关联失效 - 失效游戏/事件相关的所有缓存
    4. 批量失效 - 使用Redis Pipeline优化批量删除
    """
    
    def __init__(self):
        """初始化缓存失效器"""
        self.cache = hierarchical_cache
        logger.info("✅ 缓存失效器初始化完成")
    
    # ========================================================================
    # 精确失效
    # ========================================================================
    
    def invalidate_key(self, pattern: str, **kwargs) -> bool:
        """
        精确失效单个缓存键
        
        Args:
            pattern: 缓存模式
            **kwargs: 缓存键参数
        
        Returns:
            是否成功删除
        """
        try:
            self.cache.delete(pattern, **kwargs)
            logger.debug(f"缓存失效: {pattern} {kwargs}")
            return True
        except Exception as e:
            logger.error(f"缓存失效失败: {e}")
            return False
    
    # ========================================================================
    # 模式失效
    # ========================================================================
    
    def invalidate_pattern(self, pattern: str, **kwargs) -> int:
        """
        模式失效（L1和L2）
        
        Args:
            pattern: 缓存模式
            **kwargs: 要匹配的参数
        
        Returns:
            失效的键数量
        """
        try:
            # 失效L1缓存
            l1_count = self.cache.invalidate_pattern(pattern, **kwargs)
            
            # 失效L2缓存（Redis）
            l2_count = self._invalidate_redis_pattern(pattern, **kwargs)
            
            total_count = l1_count + l2_count
            logger.info(f"模式失效: {pattern} {kwargs} (L1={l1_count}, L2={l2_count})")
            return total_count
        
        except Exception as e:
            logger.error(f"模式失效失败: {e}")
            return 0
    
    def scan_keys(self, pattern: str = '*', count: int = 100) -> list:
        """
        使用SCAN命令扫描键（非阻塞）

        ⚡ 性能优化: 替代KEYS命令，避免Redis阻塞

        Args:
            pattern: 键模式（默认 '*'）
            count: 每次扫描返回的键数量（默认100）

        Returns:
            匹配的键列表
        """
        redis_client = get_redis_client()
        if redis_client is None:
            return []
        
        keys = []
        cursor = '0'
        
        try:
            while cursor != 0:
                # SCAN返回 (cursor, [keys])
                cursor, batch_keys = redis_client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=count
                )
                keys.extend(batch_keys)
                
                # 避免无限循环（最多10,000个键）
                if len(keys) > 10000:
                    logger.warning(f"SCAN超过10,000个键，停止扫描: {pattern}")
                    break
            
            return keys
        
        except Exception as e:
            logger.error(f"SCAN命令失败: {e}")
            return []

    def _invalidate_redis_pattern(self, pattern: str, **kwargs) -> int:
        """
        失效Redis中匹配模式的键
        
        Args:
            pattern: 缓存模式
            **kwargs: 要匹配的参数
        
        Returns:
            失效的键数量
        """
        redis_client = get_redis_client()
        if redis_client is None:
            return 0
        
        try:
            # 构建通配符模式
            wildcard = CacheKeyBuilder.build_pattern(pattern, **kwargs)

            # 验证通配符模式的安全性
            if not CacheKeyValidator.validate_pattern_for_wildcard(wildcard):
                logger.error(f"不安全的通配符模式: {wildcard}")
                return 0

            # ⚡ 使用SCAN替代KEYS（非阻塞）
            keys = self.scan_keys(wildcard)
            
            if keys:
                # 批量删除
                redis_client.delete(*keys)
                logger.debug(f"Redis模式失效: {len(keys)}个键")
                return len(keys)
            
            return 0
        
        except Exception as e:
            logger.error(f"Redis模式失效失败: {e}")
            return 0
    
    # ========================================================================
    # 关联失效
    # ========================================================================
    
    def invalidate_game_related(self, game_gid: int) -> Set[str]:
        """
        失效游戏相关的所有缓存
        
        包括:
        - 游戏详情
        - 游戏列表
        - 游戏的事件列表
        - 游戏的参数列表
        - 游戏的分类列表
        - 游戏的HQL历史
        
        Args:
            game_gid: 游戏业务GID
        
        Returns:
            失效的缓存键集合
        """
        invalidated_keys = set()
        
        try:
            # 1. 游戏详情
            if self.invalidate_key('games.detail', gid=game_gid):
                invalidated_keys.add(f"games.detail:gid:{game_gid}")
            
            # 2. 游戏列表
            if self.invalidate_key('games.list'):
                invalidated_keys.add("games.list")
            
            # 3. 游戏的事件列表（所有变体）
            # ✅ Fix: Use game_gid parameter consistently
            event_count = self.invalidate_pattern('events.list', game_gid=game_gid)
            invalidated_keys.add(f"events.list:game_gid:{game_gid}:*")
            
            # 4. 游戏的参数列表
            if self.invalidate_key('params.list', game_gid=game_gid):
                invalidated_keys.add(f"params.list:game_gid:{game_gid}")
            
            # 5. 游戏的分类列表
            if self.invalidate_key('categories.list', game_gid=game_gid):
                invalidated_keys.add(f"categories.list:game_gid:{game_gid}")
            
            # 6. 游戏的HQL历史
            hql_count = self.invalidate_pattern('hql.history', game_gid=game_gid)
            invalidated_keys.add(f"hql.history:game_gid:{game_gid}:*")
            
            # 7. 游戏的节点配置
            if self.invalidate_key('nodes.config', game_gid=game_gid):
                invalidated_keys.add(f"nodes.config:game_gid:{game_gid}")
            
            # 8. 游戏的流程模板
            if self.invalidate_key('flows.templates', game_gid=game_gid):
                invalidated_keys.add(f"flows.templates:game_gid:{game_gid}")
            
            logger.info(f"游戏关联失效: game_gid={game_gid}, {len(invalidated_keys)}个键")
            
        except Exception as e:
            logger.error(f"游戏关联失效失败: {e}")
        
        return invalidated_keys
    
    def invalidate_event_related(self, event_id: int, game_gid: int) -> Set[str]:
        """
        失效事件相关的所有缓存
        
        包括:
        - 事件详情
        - 事件的参数列表
        - 所属游戏的事件列表
        - 所属游戏的参数列表
        
        Args:
            event_id: 事件ID
            game_gid: 游戏业务GID
        
        Returns:
            失效的缓存键集合
        """
        invalidated_keys = set()
        
        try:
            # 1. 事件详情
            if self.invalidate_key('events.detail', id=event_id):
                invalidated_keys.add(f"events.detail:id:{event_id}")
            
            # 2. 事件的参数列表
            param_count = self.invalidate_pattern('params.list', event_id=event_id)
            invalidated_keys.add(f"params.list:event_id:{event_id}:*")
            
            # 3. 所属游戏的事件列表
            # ✅ Fix: Use game_gid parameter consistently
            event_count = self.invalidate_pattern('events.list', game_gid=game_gid)
            invalidated_keys.add(f"events.list:game_gid:{game_gid}:*")
            
            # 4. 所属游戏的参数列表
            if self.invalidate_key('params.list', game_gid=game_gid):
                invalidated_keys.add(f"params.list:game_gid:{game_gid}")
            
            # 5. 所属游戏的详情（更新事件计数）
            if self.invalidate_key('games.detail', gid=game_gid):
                invalidated_keys.add(f"games.detail:gid:{game_gid}")
            
            # 6. 游戏列表（更新事件计数）
            if self.invalidate_key('games.list'):
                invalidated_keys.add("games.list")
            
            logger.info(f"事件关联失效: event_id={event_id}, game_gid={game_gid}, {len(invalidated_keys)}个键")
            
        except Exception as e:
            logger.error(f"事件关联失效失败: {e}")
        
        return invalidated_keys
    
    def invalidate_parameter_related(self, param_id: int, event_id: int, game_gid: int) -> Set[str]:
        """
        失效参数相关的所有缓存
        
        包括:
        - 参数详情
        - 所属事件的参数列表
        - 所属游戏的参数列表
        - 所属游戏的事件列表
        
        Args:
            param_id: 参数ID
            event_id: 事件ID
            game_gid: 游戏业务GID
        
        Returns:
            失效的缓存键集合
        """
        invalidated_keys = set()
        
        try:
            # 1. 参数详情
            if self.invalidate_key('params.detail', id=param_id):
                invalidated_keys.add(f"params.detail:id:{param_id}")
            
            # 2. 所属事件的参数列表
            if self.invalidate_key('params.list', event_id=event_id):
                invalidated_keys.add(f"params.list:event_id:{event_id}")
            
            # 3. 所属游戏的参数列表
            if self.invalidate_key('params.list', game_gid=game_gid):
                invalidated_keys.add(f"params.list:game_gid:{game_gid}")
            
            # 4. 所属游戏的事件列表（更新参数计数）
            # ✅ Fix: Use game_gid parameter consistently
            event_count = self.invalidate_pattern('events.list', game_gid=game_gid)
            invalidated_keys.add(f"events.list:game_gid:{game_gid}:*")
            
            # 5. 所属游戏的详情（更新参数计数）
            if self.invalidate_key('games.detail', gid=game_gid):
                invalidated_keys.add(f"games.detail:gid:{game_gid}")
            
            # 6. 游戏列表（更新参数计数）
            if self.invalidate_key('games.list'):
                invalidated_keys.add("games.list")
            
            logger.info(f"参数关联失效: param_id={param_id}, event_id={event_id}, game_gid={game_gid}, {len(invalidated_keys)}个键")
            
        except Exception as e:
            logger.error(f"参数关联失效失败: {e}")
        
        return invalidated_keys
    
    def invalidate_category_related(self, category_id: int, game_gid: Optional[int] = None) -> Set[str]:
        """失效分类相关的所有缓存"""
        invalidated_keys = set()
        try:
            if self.invalidate_key('categories.detail', id=category_id):
                invalidated_keys.add(f"categories.detail:id:{category_id}")
            if self.invalidate_key('categories.list'):
                invalidated_keys.add("categories.list")
            if game_gid:
                # ✅ Fix: Use game_gid parameter consistently
                self.invalidate_pattern('events.list', game_gid=game_gid)
            logger.info(f"分类关联失效: category_id={category_id}, {len(invalidated_keys)}个键")
        except Exception as e:
            logger.error(f"分类关联失效失败: {e}")
        return invalidated_keys
    
    def invalidate_template_related(self, template_id: int, game_gid: Optional[int] = None) -> Set[str]:
        """失效模板相关的所有缓存"""
        invalidated_keys = set()
        try:
            if self.invalidate_key('templates.detail', id=template_id):
                invalidated_keys.add(f"templates.detail:id:{template_id}")
            if self.invalidate_key('templates.list'):
                invalidated_keys.add("templates.list")
            logger.info(f"模板关联失效: template_id={template_id}, {len(invalidated_keys)}个键")
        except Exception as e:
            logger.error(f"模板关联失效失败: {e}")
        return invalidated_keys
    
    def invalidate_node_related(self, node_id: int, game_gid: int) -> Set[str]:
        """失效节点相关的所有缓存"""
        invalidated_keys = set()
        try:
            if self.invalidate_key('nodes.detail', id=node_id):
                invalidated_keys.add(f"nodes.detail:id:{node_id}")
            if self.invalidate_key('nodes.list'):
                invalidated_keys.add("nodes.list")
            if self.invalidate_key('nodes.config', game_gid=game_gid):
                invalidated_keys.add(f"nodes.config:game_gid:{game_gid}")
            logger.info(f"节点关联失效: node_id={node_id}, {len(invalidated_keys)}个键")
        except Exception as e:
            logger.error(f"节点关联失效失败: {e}")
        return invalidated_keys
    
    def invalidate_flow_related(self, flow_id: int, game_gid: int) -> Set[str]:
        """失效流程相关的所有缓存"""
        invalidated_keys = set()
        try:
            if self.invalidate_key('flows.detail', id=flow_id):
                invalidated_keys.add(f"flows.detail:id:{flow_id}")
            if self.invalidate_key('flows.list'):
                invalidated_keys.add("flows.list")
            if self.invalidate_key('flows.templates', game_gid=game_gid):
                invalidated_keys.add(f"flows.templates:game_gid:{game_gid}")
            logger.info(f"流程关联失效: flow_id={flow_id}, {len(invalidated_keys)}个键")
        except Exception as e:
            logger.error(f"流程关联失效失败: {e}")
        return invalidated_keys
    
    def invalidate_join_config_related(self, config_id: int, game_gid: int) -> Set[str]:
        """失效连接配置相关的所有缓存"""
        invalidated_keys = set()
        try:
            if self.invalidate_key('join_configs.detail', id=config_id):
                invalidated_keys.add(f"join_configs.detail:id:{config_id}")
            if self.invalidate_key('join_configs.list'):
                invalidated_keys.add("join_configs.list")
            logger.info(f"连接配置关联失效: config_id={config_id}, {len(invalidated_keys)}个键")
        except Exception as e:
            logger.error(f"连接配置关联失效失败: {e}")
        return invalidated_keys
    
    # ========================================================================
    # 批量失效
    # ========================================================================
    
    def invalidate_batch(self, patterns: List[Tuple[str, Dict]]) -> int:
        """
        批量失效多个缓存键（使用Pipeline优化）
        
        Args:
            patterns: [(pattern, kwargs), ...] 列表
        
        Returns:
            失效的总键数
        """
        total_count = 0
        
        try:
            redis_client = get_redis_client()
            
            if redis_client:
                # 使用Redis Pipeline批量删除
                pipe = redis_client.pipeline()
                
                for pattern, kwargs in patterns:
                    # 使用CacheKeyValidator构建安全的缓存键
                    key = CacheKeyValidator.build_key(pattern, **kwargs)
                    pipe.delete(key)
                    
                    # 同时删除L1
                    with self.cache._lock:
                        if key in self.cache.l1_cache:
                            del self.cache.l1_cache[key]
                            del self.cache.l1_timestamps[key]
                            total_count += 1
                
                pipe.execute()
                logger.info(f"批量失效: {len(patterns)}个键")
            
            else:
                # 降级到逐个删除
                for pattern, kwargs in patterns:
                    if self.invalidate_key(pattern, **kwargs):
                        total_count += 1
        
        except Exception as e:
            logger.error(f"批量失效失败: {e}")
        
        return total_count
    
    # ========================================================================
    # 清空缓存
    # ========================================================================
    
    def clear_all(self) -> Tuple[int, int]:
        """
        清空所有缓存（L1和L2）
        
        Returns:
            (L1清空数量, L2清空数量)
        """
        try:
            # 清空L1
            l1_before = len(self.cache.l1_cache)
            self.cache.clear_l1()
            l1_count = l1_before
            
            # 清空L2
            l2_count = 0
            redis_client = get_redis_client()
            if redis_client:
                try:
                    pattern = f"{CacheKeyBuilder.PREFIX}*"
                    # ⚡ 使用SCAN替代KEYS
                    keys = self.scan_keys(pattern)
                    if keys:
                        redis_client.delete(*keys)
                        l2_count = len(keys)
                except Exception as e:
                    logger.warning(f"清空L2缓存失败: {e}")
            
            logger.info(f"清空所有缓存: L1={l1_count}, L2={l2_count}")
            return (l1_count, l2_count)
        
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return (0, 0)


# 全局缓存失效器实例
cache_invalidator_enhanced = CacheInvalidatorEnhanced()


logger.info("✅ 缓存失效器模块已加载 (1.0.0)")

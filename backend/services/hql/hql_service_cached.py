"""
HQL服务缓存增强版

为HQLService添加多级缓存支持,提升性能
"""

from typing import List, Dict, Any, Optional
import json
import hashlib
from backend.services.hql.hql_facade import HQLFacade
from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator
import logging

logger = logging.getLogger(__name__)


class HQLServiceCached:
    """
    HQL服务缓存增强版
    
    特点:
    - 使用多级缓存存储HQL生成结果
    - 自动缓存失效
    - 支持模板缓存
    - 支持历史记录缓存
    """
    
    def __init__(self):
        self.facade = HQLFacade()
        self.cache = HierarchicalCache()
        self.invalidator = CacheInvalidator(self.cache)
    
    def generate_hql(
        self,
        events: List[Dict[str, Any]],
        fields: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        mode: str = "single",
        use_cache: bool = True
    ) -> str:
        """
        生成HQL(带缓存)
        
        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            mode: 生成模式
            use_cache: 是否使用缓存
            
        Returns:
            str: 生成的HQL语句
        """
        # 构建缓存键
        cache_key = self._build_cache_key(events, fields, conditions, mode)
        
        if use_cache:
            # 尝试从缓存获取
            cached_hql = self.cache.get(cache_key)
            if cached_hql:
                logger.debug(f"HQL缓存命中: {cache_key}")
                return cached_hql
        
        # 生成HQL
        hql = self.facade.generate_hql(events, fields, conditions, mode)
        
        if use_cache:
            # 写入缓存
            self.cache.set(cache_key, hql, ttl_l2=3600)  # 1小时缓存
            logger.debug(f"HQL已缓存: {cache_key}")
        
        return hql
    
    def validate_hql(self, hql: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        验证HQL(带缓存)
        
        Args:
            hql: HQL语句
            use_cache: 是否使用缓存
            
        Returns:
            Dict: 验证结果
        """
        # 构建缓存键
        cache_key = f"hql:validation:{hashlib.md5(hql.encode()).hexdigest()}"
        
        if use_cache:
            # 尝试从缓存获取
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"验证结果缓存命中: {cache_key}")
                return cached_result
        
        # 验证HQL
        result = self.facade.validate_hql(hql)
        
        if use_cache:
            # 写入缓存
            self.cache.set(cache_key, result, ttl_l2=1800)  # 30分钟缓存
            logger.debug(f"验证结果已缓存: {cache_key}")
        
        return result
    
    def preview_hql(
        self,
        events: List[Dict[str, Any]],
        fields: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        mode: str = "single",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        预览HQL(带缓存)
        
        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            mode: 生成模式
            use_cache: 是否使用缓存
            
        Returns:
            Dict: 包含HQL和验证结果的字典
        """
        # 构建缓存键
        cache_key = self._build_cache_key(events, fields, conditions, mode, prefix="preview")
        
        if use_cache:
            # 尝试从缓存获取
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"预览结果缓存命中: {cache_key}")
                return cached_result
        
        # 预览HQL
        result = self.facade.preview_hql(events, fields, conditions, mode)
        
        if use_cache:
            # 写入缓存
            self.cache.set(cache_key, result, ttl_l2=1800)  # 30分钟缓存
            logger.debug(f"预览结果已缓存: {cache_key}")
        
        return result
    
    def analyze_performance(self, hql: str, use_cache: bool = True):
        """
        分析HQL性能(带缓存)
        
        Args:
            hql: HQL语句
            use_cache: 是否使用缓存
            
        Returns:
            PerformanceReport: 性能报告
        """
        # 构建缓存键
        cache_key = f"hql:performance:{hashlib.md5(hql.encode()).hexdigest()}"
        
        if use_cache:
            # 尝试从缓存获取
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"性能分析缓存命中: {cache_key}")
                return cached_result
        
        # 分析性能
        result = self.facade.analyze_performance(hql)
        
        if use_cache:
            # 写入缓存
            # 将PerformanceReport转换为字典存储
            result_dict = {
                'score': result.score,
                'issues': [
                    {
                        'type': issue.type.value,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    }
                    for issue in result.issues
                ],
                'metrics': {
                    'has_partition_filter': result.metrics.has_partition_filter,
                    'has_select_star': result.metrics.has_select_star,
                    'join_count': result.metrics.join_count,
                    'complexity': result.metrics.complexity
                }
            }
            self.cache.set(cache_key, result_dict, ttl_l2=1800)
            logger.debug(f"性能分析已缓存: {cache_key}")
        
        return result
    
    def invalidate_cache(self, event_ids: List[int] = None, game_gid: int = None):
        """
        失效HQL相关缓存
        
        Args:
            event_ids: 事件ID列表
            game_gid: 游戏GID
        """
        if game_gid:
            # 失效该游戏的所有HQL缓存
            self.invalidator.invalidate_by_game(game_gid)
            logger.info(f"已失效游戏 {game_gid} 的HQL缓存")
        
        if event_ids:
            # 失效特定事件的HQL缓存
            for event_id in event_ids:
                self.invalidator.invalidate_by_event(event_id)
            logger.info(f"已失效事件 {event_ids} 的HQL缓存")
    
    def _build_cache_key(
        self,
        events: List[Dict[str, Any]],
        fields: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]],
        mode: str,
        prefix: str = "generate"
    ) -> str:
        """
        构建缓存键
        
        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            mode: 生成模式
            prefix: 缓存键前缀
            
        Returns:
            str: 缓存键
        """
        # 将参数序列化为JSON并排序
        params = {
            'events': sorted(events, key=lambda x: x.get('name', '')),
            'fields': sorted(fields, key=lambda x: x.get('name', '')),
            'conditions': sorted(conditions, key=lambda x: x.get('field', '')),
            'mode': mode
        }
        
        params_json = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_json.encode()).hexdigest()[:12]
        
        return f"hql:{prefix}:{mode}:{params_hash}"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            Dict: 缓存统计
        """
        return self.cache.get_stats()

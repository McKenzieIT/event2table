"""
缓存装饰器工具

提供便捷的缓存装饰器,简化Service层缓存集成
"""

from functools import wraps
from typing import Callable, Any, Optional
import logging
from backend.core.cache.cache_system import HierarchicalCache, CacheInvalidator

logger = logging.getLogger(__name__)


# 全局缓存实例
_cache = HierarchicalCache()
_invalidator = CacheInvalidator(_cache)


def cached_service(
    key_template: str,
    ttl_l1: int = 60,
    ttl_l2: int = 300,
    key_params: Optional[list] = None
):
    """
    Service层缓存装饰器
    
    Args:
        key_template: 缓存键模板,支持参数占位符
            例如: "game:{gid}", "events:{game_gid}:list"
        ttl_l1: L1缓存过期时间(秒)
        ttl_l2: L2缓存过期时间(秒)
        key_params: 用于构建缓存键的参数名列表
            例如: ['gid'], ['game_gid', 'category']
    
    Returns:
        装饰器函数
    
    Example:
        @cached_service("game:{gid}", ttl_l1=60, ttl_l2=300, key_params=['gid'])
        def get_game(self, gid: int):
            return self.game_repo.find_by_gid(gid)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存键
            cache_key = _build_cache_key(key_template, key_params, args, kwargs, func)
            
            # 尝试从缓存获取
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value
            
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 写入缓存
            if result is not None:
                _cache.set(cache_key, result, ttl_l1=ttl_l1, ttl_l2=ttl_l2)
                logger.debug(f"已缓存: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_pattern: str, key_params: Optional[list] = None):
    """
    缓存失效装饰器
    
    Args:
        key_pattern: 缓存键模式,支持通配符
            例如: "game:{gid}", "events:{game_gid}:*"
        key_params: 用于构建缓存键的参数名列表
    
    Returns:
        装饰器函数
    
    Example:
        @invalidate_cache("game:{gid}", key_params=['gid'])
        @invalidate_cache("games:list")
        def update_game(self, gid: int, data: dict):
            return self.game_repo.update(gid, data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 失效缓存
            cache_key = _build_cache_key(key_pattern, key_params, args, kwargs, func)
            
            # 如果包含通配符,使用模式失效
            if '*' in cache_key:
                _invalidator.invalidate_pattern(cache_key)
                logger.info(f"已失效缓存模式: {cache_key}")
            else:
                _cache.delete(cache_key)
                logger.info(f"已失效缓存: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


def _build_cache_key(
    template: str,
    key_params: Optional[list],
    args: tuple,
    kwargs: dict,
    func: Callable
) -> str:
    """
    构建缓存键
    
    Args:
        template: 缓存键模板
        key_params: 参数名列表
        args: 位置参数
        kwargs: 关键字参数
        func: 原函数
    
    Returns:
        构建好的缓存键
    """
    if key_params is None:
        # 如果没有指定参数,使用模板原样
        return template
    
    # 获取函数参数名
    import inspect
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # 构建缓存键
    cache_key = template
    for param_name in key_params:
        if param_name in bound_args.arguments:
            value = bound_args.arguments[param_name]
            cache_key = cache_key.replace(f"{{{param_name}}}", str(value))
    
    return cache_key


class CacheableService:
    """
    可缓存服务基类
    
    提供缓存相关的通用方法
    """
    
    def __init__(self):
        self._cache = _cache
        self._invalidator = _invalidator
    
    def _get_cached(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        return self._cache.get(key)
    
    def _set_cached(self, key: str, value: Any, ttl_l1: int = 60, ttl_l2: int = 300):
        """设置缓存值"""
        self._cache.set(key, value, ttl_l1=ttl_l1, ttl_l2=ttl_l2)
    
    def _delete_cached(self, key: str):
        """删除缓存值"""
        self._cache.delete(key)
    
    def _invalidate_pattern(self, pattern: str):
        """失效匹配的缓存"""
        self._invalidator.invalidate_pattern(pattern)
    
    def _get_or_set(
        self,
        key: str,
        func: Callable,
        ttl_l1: int = 60,
        ttl_l2: int = 300
    ) -> Any:
        """获取或设置缓存"""
        cached_value = self._get_cached(key)
        if cached_value is not None:
            return cached_value
        
        result = func()
        if result is not None:
            self._set_cached(key, result, ttl_l1, ttl_l2)
        
        return result

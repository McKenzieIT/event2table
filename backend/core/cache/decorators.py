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


def cached(ttl: int = 300, key_prefix: str = None):
    """
    简化的缓存装饰器 (为Worker 4性能优化添加)

    Args:
        ttl: 缓存过期时间(秒), 默认300秒(5分钟)
        key_prefix: 缓存键前缀(可选)

    Returns:
        装饰器函数

    Example:
        @cached(ttl=1800)  # 缓存30分钟
        def get_something(id: int):
            return fetch_one_as_dict('SELECT * FROM table WHERE id = ?', (id,))
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 构建缓存键
            if key_prefix:
                cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"
            else:
                cache_key = f"{func.__name__}:{args}:{kwargs}"

            # 尝试从缓存获取
            cached_value = _cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"缓存命中: {cache_key}")
                return cached_value

            # 执行原函数
            result = func(*args, **kwargs)

            # 写入缓存
            if result is not None:
                _cache.set(cache_key, result, ttl_l1=ttl)
                logger.debug(f"已缓存: {cache_key}")

            return result

        return wrapper
    return decorator


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


def cache_invalidate(func: Callable) -> Callable:
    """
    ⚡ PERF: 自动缓存失效装饰器 (Phase 1.1 - Critical Fix)

    自动失效与函数相关的所有缓存键,无需手动指定键模式。

    工作原理:
    1. 执行被装饰的函数(CREATE/UPDATE/DELETE操作)
    2. 根据函数名自动推断需要失效的缓存键
    3. 自动调用缓存失效逻辑

    Args:
        func: 需要自动失效缓存的函数

    Returns:
        包装后的函数

    Example:
        @cache_invalidate
        def create_event(self, event_data: dict):
            # 创建事件后自动失效以下缓存:
            # - dashboard_statistics
            # - events:{game_gid}
            return self.event_repo.create(event_data)

    Supported Cache Keys (自动推断):
        - create_* → 失效 {resource}_list, dashboard_statistics
        - update_* → 失效 {resource}:{id}, {resource}_list, dashboard_statistics
        - delete_* → 失效 {resource}:{id}, {resource}_list, dashboard_statistics
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 执行原函数
        result = func(*args, **kwargs)

        # 根据函数名推断需要失效的缓存键
        func_name = func.__name__

        # 自动失效dashboard_statistics (所有数据变更都影响)
        try:
            _cache.delete("dashboard_statistics")
            logger.info(f"✅ 已失效缓存: dashboard_statistics (由 {func_name} 触发)")
        except Exception as e:
            logger.warning(f"⚠️ 失效dashboard_statistics失败: {e}")

        # 根据函数类型推断其他缓存键
        if func_name.startswith('create_'):
            resource = func_name.replace('create_', '')
            # 失效资源列表缓存
            list_key = f"{resource}s"
            try:
                _cache.delete(list_key)
                logger.info(f"✅ 已失效缓存: {list_key}")
            except Exception as e:
                logger.warning(f"⚠️ 失效{list_key}失败: {e}")

        elif func_name.startswith('update_') or func_name.startswith('delete_'):
            resource = func_name.replace('update_', '').replace('delete_', '')

            # 尝试从参数中获取ID
            resource_id = None
            if args:
                # 假设第一个参数是ID (对于update/delete通常如此)
                resource_id = args[0] if len(args) > 0 else None

            # 失效具体资源缓存
            if resource_id:
                resource_key = f"{resource}:{resource_id}"
                try:
                    _cache.delete(resource_key)
                    logger.info(f"✅ 已失效缓存: {resource_key}")
                except Exception as e:
                    logger.warning(f"⚠️ 失效{resource_key}失败: {e}")

            # 失效资源列表缓存
            list_key = f"{resource}s"
            try:
                _cache.delete(list_key)
                logger.info(f"✅ 已失效缓存: {list_key}")
            except Exception as e:
                logger.warning(f"⚠️ 失效{list_key}失败: {e}")

        return result

    return wrapper


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

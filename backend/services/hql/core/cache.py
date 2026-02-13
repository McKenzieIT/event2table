"""
HQL生成缓存模块

提供LRU缓存支持，提升重复请求的性能
"""

import json
from functools import lru_cache
from typing import List, Dict, Any, Optional


def compute_hash(obj: Any) -> str:
    """
    计算对象的哈希值 - 使用SHA-256安全算法

    Args:
        obj: 任意可序列化对象

    Returns:
        str: SHA-256哈希值（64位十六进制字符串）

    Example:
        >>> hash_value = compute_hash({'key': 'value'})
        >>> print(len(hash_value))  # 64 (SHA-256输出长度)
    """
    from backend.core.crypto import SecureHasher

    # 序列化为JSON字符串（确保顺序一致）
    serialized = json.dumps(obj, sort_keys=True)
    # 使用SHA-256替代MD5
    return SecureHasher.hash_string(serialized)


class HQLCacheManager:
    """
    HQL生成缓存管理器

    使用LRU缓存存储常见的HQL生成结果
    """

    def __init__(self, maxsize: int = 256):
        """
        初始化缓存管理器

        Args:
            maxsize: 最大缓存条目数
        """
        self.maxsize = maxsize
        self._cache = {}
        self._hits = 0
        self._misses = 0

    def get_cache_key(
        self, events: List[Dict], fields: List[Dict], conditions: List[Dict], options: Dict
    ) -> str:
        """
        计算缓存键

        Args:
            events: 事件列表
            fields: 字段列表
            conditions: 条件列表
            options: 选项字典

        Returns:
            str: 缓存键
        """
        # 创建哈希输入
        hash_input = {
            "events": sorted(events, key=lambda x: x.get("game_gid", 0)),
            "fields": sorted(fields, key=lambda x: x.get("fieldName", "")),
            "conditions": sorted(conditions, key=lambda x: x.get("field", "")),
            "options": options,
        }

        return compute_hash(hash_input)

    def get(self, cache_key: str) -> Optional[str]:
        """
        获取缓存

        Args:
            cache_key: 缓存键

        Returns:
            Optional[str]: 缓存的HQL，如果不存在则返回None
        """
        if cache_key in self._cache:
            self._hits += 1
            return self._cache[cache_key]["hql"]

        self._misses += 1
        return None

    def set(self, cache_key: str, hql: str) -> None:
        """
        设置缓存

        Args:
            cache_key: 缓存键
            hql: HQL语句
        """
        # 如果缓存已满，删除最旧的条目
        if len(self._cache) >= self.maxsize:
            # 删除第一个条目（最旧的）
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        self._cache[cache_key] = {"hql": hql}

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 统计信息
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "maxsize": self.maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
        }

    def get_keys(self) -> List[str]:
        """获取所有缓存键"""
        return list(self._cache.keys())


# 全局缓存实例
_global_cache = HQLCacheManager(maxsize=256)


def get_global_cache() -> HQLCacheManager:
    """获取全局缓存实例"""
    return _global_cache


def clear_global_cache() -> None:
    """清空全局缓存"""
    _global_cache.clear()

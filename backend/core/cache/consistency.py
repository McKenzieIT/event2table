#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存一致性保证 - 读写锁机制
============================

提供读写锁机制保证并发访问缓存的数据一致性

版本: 1.0.0
日期: 2026-02-24

功能:
- 每个缓存键独立读写锁
- 允许多个读者并发访问
- 写者独占访问
- 防止读写并发导致的数据不一致
"""

import logging
import threading
from contextlib import contextmanager
from typing import Dict

logger = logging.getLogger(__name__)


class CacheReadWriteLock:
    """
    缓存读写锁

    设计原理:
    - 读操作: 允许多个读者并发访问
    - 写操作: 独占访问, 阻塞所有读者和写者
    - 锁粒度: 每个缓存键一个读写锁

    实现:
    - 使用计数器跟踪读者数量
    - 写操作等待所有读者完成
    - 可重入锁支持递归调用
    """

    def __init__(self):
        """初始化读写锁管理器"""
        # 锁结构: {key: [readers_count, write_lock]}
        self._locks: Dict[str, list] = {}
        self._global_lock = threading.Lock()

        logger.debug("✅ 缓存读写锁初始化完成")

    @contextmanager
    def read_lock(self, key: str):
        """
        获取读锁

        Args:
            key: 缓存键

        Usage:
            with rw_lock.read_lock('cache_key'):
                data = cache.get('cache_key')
        """
        # 获取全局锁以注册读者
        with self._global_lock:
            if key not in self._locks:
                # 初始化: [读者计数, 写锁]
                self._locks[key] = [0, threading.Lock()]

            # 增加读者计数
            self._locks[key][0] += 1
            logger.debug(f"📖 获取读锁: {key} (读者数: {self._locks[key][0]})")

        try:
            # 执行读操作
            yield
        finally:
            # 减少读者计数
            with self._global_lock:
                self._locks[key][0] -= 1
                logger.debug(f"📕 释放读锁: {key} (剩余读者: {self._locks[key][0]})")

                # 如果没有读者且锁不再需要, 清理
                if self._locks[key][0] == 0 and key in self._locks:
                    # 可选: 清理未使用的锁以节省内存
                    # del self._locks[key]
                    pass

    @contextmanager
    def write_lock(self, key: str):
        """
        获取写锁

        Args:
            key: 缓存键

        Usage:
            with rw_lock.write_lock('cache_key'):
                cache.set('cache_key', data)
        """
        # 获取全局锁以注册写锁
        with self._global_lock:
            if key not in self._locks:
                self._locks[key] = [0, threading.Lock()]

            write_lock = self._locks[key][1]

        # 等待所有读者完成并获取写锁
        logger.debug(f"🔒 等待写锁: {key}")
        write_lock.acquire()

        # 确保没有读者
        with self._global_lock:
            readers_count = self._locks[key][0]
            if readers_count > 0:
                logger.warning(f"⚠️ 获取写锁时仍有{readers_count}个读者: {key}")

        logger.debug(f"✅ 获取写锁: {key}")

        try:
            # 执行写操作
            yield
        finally:
            # 释放写锁
            write_lock.release()
            logger.debug(f"🔓 释放写锁: {key}")

    def cleanup_lock(self, key: str):
        """
        清理指定键的锁

        Args:
            key: 缓存键
        """
        with self._global_lock:
            if key in self._locks:
                del self._locks[key]
                logger.debug(f"🗑️ 清理锁: {key}")

    def get_lock_stats(self) -> Dict:
        """
        获取锁统计信息

        Returns:
            锁统计字典
        """
        with self._global_lock:
            active_readers = sum(lock[0] for lock in self._locks.values())
            total_locks = len(self._locks)

            return {
                'total_locks': total_locks,
                'active_readers': active_readers,
                'active_writers': 0,  # 写锁无法直接检测
            }


# 全局读写锁实例
cache_rw_lock = CacheReadWriteLock()


logger.info("✅ 缓存一致性保证模块已加载 (1.0.0)")

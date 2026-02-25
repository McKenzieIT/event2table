#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis Connection Manager - 防止连接泄露
====================================

提供Redis连接池管理和自动连接释放功能。

安全特性:
- 连接池管理（限制最大连接数）
- 上下文管理器（自动释放连接）
- 连接健康检查
- 连接泄露监控
- 线程安全

使用示例:
    >>> from backend.core.cache.redis_connection_manager import redis_connection_manager
    >>>
    >>> # 使用上下文管理器（推荐）
    >>> with redis_connection_manager.get_connection() as redis_conn:
    >>>     redis_conn.set('key', 'value')
    >>>
    >>> # 手动获取和释放
    >>> redis_conn = redis_connection_manager.get_connection()
    >>> try:
    >>>     redis_conn.set('key', 'value')
    >>> finally:
    >>>     redis_conn.close()

Author: Event2Table Development Team
Version: 1.0.0
Date: 2026-02-24
"""

import redis
import logging
import threading
import time
import contextlib
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class RedisConnectionManager:
    """
    Redis连接管理器

    特性:
    - 连接池管理（限制最大连接数）
    - 上下文管理器（自动释放连接）
    - 连接健康检查
    - 连接泄露监控
    - 线程安全
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        max_connections: int = 50,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        retry_on_timeout: bool = True,
        health_check_interval: int = 30
    ):
        """
        初始化Redis连接管理器

        Args:
            host: Redis主机地址
            port: Redis端口
            db: Redis数据库编号
            password: Redis密码
            max_connections: 最大连接数
            socket_timeout: Socket超时（秒）
            socket_connect_timeout: 连接超时（秒）
            retry_on_timeout: 超时是否重试
            health_check_interval: 健康检查间隔（秒）
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.retry_on_timeout = retry_on_timeout
        self.health_check_interval = health_check_interval

        # 连接池（延迟初始化）
        self._pool: Optional[redis.ConnectionPool] = None
        self._pool_lock = threading.Lock()

        # 连接泄露监控
        self._active_connections: Dict[int, float] = {}  # {id: timestamp}
        self._connection_lock = threading.Lock()

        # 健康检查
        self._last_health_check = 0
        self._health_check_failed = False

        logger.info(
            f"RedisConnectionManager initialized: "
            f"host={host}, port={port}, db={db}, max_connections={max_connections}"
        )

    def _get_pool(self) -> redis.ConnectionPool:
        """
        获取或创建连接池（延迟初始化）

        Returns:
            Redis连接池
        """
        if self._pool is None:
            with self._pool_lock:
                if self._pool is None:
                    logger.info("Creating Redis connection pool...")
                    self._pool = redis.ConnectionPool(
                        host=self.host,
                        port=self.port,
                        db=self.db,
                        password=self.password,
                        max_connections=self.max_connections,
                        socket_timeout=self.socket_timeout,
                        socket_connect_timeout=self.socket_connect_timeout,
                        retry_on_timeout=self.retry_on_timeout,
                        decode_responses=False  # 返回bytes，手动解码
                    )
                    logger.info(f"✅ Redis connection pool created: {self._pool}")

        return self._pool

    @contextlib.contextmanager
    def get_connection(self):
        """
        获取Redis连接（上下文管理器）

        使用with语句确保连接自动释放：

        >>> with redis_connection_manager.get_connection() as conn:
        >>>     conn.set('key', 'value')
        >>> # 连接自动释放

        Yields:
            Redis连接对象
        """
        conn = None
        connection_id = None

        try:
            # 获取连接
            conn = redis.Redis(connection_pool=self._get_pool())
            connection_id = id(conn)

            # 记录活跃连接
            with self._connection_lock:
                self._active_connections[connection_id] = time.time()

            # 执行健康检查（如果需要）
            self._check_health_if_needed(conn)

            logger.debug(f"Redis connection acquired: {connection_id}")
            yield conn

        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            # 如果是连接错误，标记健康检查失败
            if "Connection" in str(e) or "Timeout" in str(e):
                self._health_check_failed = True
            raise

        finally:
            # 连接自动返回连接池
            if conn is not None:
                # 移除活跃连接记录
                with self._connection_lock:
                    if connection_id in self._active_connections:
                        del self._active_connections[connection_id]

                logger.debug(f"Redis connection released: {connection_id}")
                # 显式关闭（返回连接池）
                try:
                    # 注意：不要调用conn.close()，这会关闭整个连接池
                    # Redis连接由连接池管理，自动返回池中
                    pass
                except Exception as e:
                    logger.warning(f"Error releasing Redis connection: {e}")

    def get_client(self) -> redis.Redis:
        """
        获取Redis客户端（不推荐使用）

        警告：此方法不使用上下文管理器，需要手动管理连接。
        推荐使用get_connection()上下文管理器。

        Returns:
            Redis客户端
        """
        logger.warning(
            "Using get_client() is not recommended. "
            "Use get_connection() context manager instead."
        )
        return redis.Redis(connection_pool=self._get_pool())

    def _check_health_if_needed(self, conn: redis.Redis) -> None:
        """
        如果需要，执行健康检查

        Args:
            conn: Redis连接
        """
        now = time.time()

        # 如果距离上次检查超过间隔时间
        if now - self._last_health_check > self.health_check_interval:
            try:
                conn.ping()
                self._last_health_check = int(now)
                self._health_check_failed = False
                logger.debug("Redis health check passed")
            except Exception as e:
                self._health_check_failed = True
                logger.error(f"Redis health check failed: {e}")

    def check_connection_leaks(self) -> Dict[str, Any]:
        """
        检查连接泄露

        Returns:
            泄露报告字典
        """
        with self._connection_lock:
            active_count = len(self._active_connections)

        # 计算连接存活时间
        stale_connections = []
        now = time.time()
        stale_threshold = 300  # 5分钟

        with self._connection_lock:
            for conn_id, timestamp in self._active_connections.items():
                age = now - timestamp
                if age > stale_threshold:
                    stale_connections.append({
                        'id': conn_id,
                        'age_seconds': age
                    })

        report = {
            'active_connections': active_count,
            'stale_connections': len(stale_connections),
            'max_connections': self.max_connections,
            'usage_percent': (active_count / self.max_connections * 100) if self.max_connections > 0 else 0,
            'stale_details': stale_connections[:10]  # 最多显示10个
        }

        stale_conn_count = int(report.get('stale_connections', 0))
        if stale_conn_count > 0:
            logger.warning(
                f"⚠️ Potential connection leaks detected: "
                f"{stale_conn_count} stale connections"
            )

        return report

    def get_stats(self) -> Dict[str, Any]:
        """
        获取连接统计信息

        Returns:
            统计信息字典
        """
        pool = self._get_pool()

        # 获取连接池统计
        try:
            pool_stats = {
                'created_connections': getattr(pool, 'created_connections', 0),
                'available_connections': getattr(pool, '_available_connections', 0),
                'in_use_connections': getattr(pool, '_in_use_connections', 0),
            }
        except Exception as e:
            logger.warning(f"Failed to get pool stats: {e}")
            pool_stats = {}

        # 获取泄露报告
        leak_report = self.check_connection_leaks()

        return {
            'host': self.host,
            'port': self.port,
            'db': self.db,
            'max_connections': self.max_connections,
            'health_check_failed': self._health_check_failed,
            'pool_stats': pool_stats,
            'leak_report': leak_report
        }

    def close(self):
        """
        关闭连接池

        注意：此方法会关闭所有连接，谨慎使用。
        """
        with self._pool_lock:
            if self._pool is not None:
                logger.info("Closing Redis connection pool...")
                self._pool.disconnect()
                self._pool = None
                logger.info("✅ Redis connection pool closed")

    def reset_connection_leak_monitor(self):
        """重置连接泄露监控"""
        with self._connection_lock:
            self._active_connections.clear()
        logger.info("Redis connection leak monitor reset")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False

    def __repr__(self) -> str:
        """字符串表示"""
        stats = self.get_stats()
        return (
            f"RedisConnectionManager("
            f"host={self.host}, "
            f"port={self.port}, "
            f"db={self.db}, "
            f"active={stats['leak_report']['active_connections']}, "
            f"max={self.max_connections})"
        )


# 全局Redis连接管理器实例
_global_redis_manager: Optional[RedisConnectionManager] = None
_redis_manager_lock = threading.Lock()


def get_redis_connection_manager(
    host: str = 'localhost',
    port: int = 6379,
    db: int = 0,
    password: Optional[str] = None,
    max_connections: int = 50
) -> RedisConnectionManager:
    """
    获取或创建全局Redis连接管理器实例

    Args:
        host: Redis主机地址
        port: Redis端口
        db: Redis数据库编号
        password: Redis密码
        max_connections: 最大连接数

    Returns:
        RedisConnectionManager实例
    """
    global _global_redis_manager

    with _redis_manager_lock:
        if _global_redis_manager is None:
            logger.info("Creating global RedisConnectionManager instance")
            _global_redis_manager = RedisConnectionManager(
                host=host,
                port=port,
                db=db,
                password=password,
                max_connections=max_connections
            )

        return _global_redis_manager


def shutdown_redis_connection_manager():
    """关闭全局Redis连接管理器"""
    global _global_redis_manager

    with _redis_manager_lock:
        if _global_redis_manager is not None:
            _global_redis_manager.close()
            _global_redis_manager = None
            logger.info("Global Redis connection manager shutdown")


logger.info("✅ RedisConnectionManager模块已加载 (1.0.0)")

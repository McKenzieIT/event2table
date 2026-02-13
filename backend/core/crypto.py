"""
加密和哈希工具函数模块

提供安全的哈希算法，避免使用弱加密算法（如MD5）。

作者: Claude Code
版本: 1.0.0
创建日期: 2026-02-09

使用示例:
    >>> from backend.core.crypto import SecureHasher, compute_hash
    >>> # 哈希字符串
    >>> hash_value = SecureHasher.hash_string('hello')
    >>>
    >>> # 哈希对象
    >>> data = {'name': 'Alice', 'age': 30}
    >>> hash_value = SecureHasher.hash_object(data)
    >>>
    >>> # 便捷函数
    >>> hash_value = compute_hash('hello')
"""

import hashlib
import json
from typing import Any, Union


class SecureHasher:
    """
    安全哈希计算器

    提供统一的哈希计算接口，使用强加密算法（SHA-256等）。

    支持的算法:
    - sha256: 默认，安全且性能好
    - sha512: 更安全，但性能稍差
    - blake2b: 现代哈希算法，性能优秀
    - blake2s: blake2b的轻量级版本
    """

    # 默认哈希算法（SHA-256）
    DEFAULT_ALGORITHM = "sha256"

    # 支持的哈希算法
    SUPPORTED_ALGORITHMS = {
        "sha256": hashlib.sha256,
        "sha512": hashlib.sha512,
        "blake2b": hashlib.blake2b,
        "blake2s": hashlib.blake2s,
    }

    @classmethod
    def hash_string(cls, data: str, algorithm: str = DEFAULT_ALGORITHM) -> str:
        """
        计算字符串的安全哈希值

        Args:
            data: 输入字符串
            algorithm: 哈希算法（sha256, sha512, blake2b, blake2s）

        Returns:
            十六进制哈希值

        Example:
            >>> hash_value = SecureHasher.hash_string('hello')
            >>> print(hash_value)
            '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
        """
        hasher = cls._get_hasher(algorithm)
        return hasher(data.encode()).hexdigest()

    @classmethod
    def hash_object(
        cls, obj: Any, algorithm: str = DEFAULT_ALGORITHM, sort_keys: bool = True
    ) -> str:
        """
        计算Python对象的安全哈希值

        对象会先序列化为JSON字符串，再计算哈希值。

        Args:
            obj: Python对象（dict, list, tuple等）
            algorithm: 哈希算法
            sort_keys: 是否对字典键排序（确保哈希值一致）

        Returns:
            十六进制哈希值

        Example:
            >>> data = {'name': 'Alice', 'age': 30}
            >>> hash_value = SecureHasher.hash_object(data)
            >>> print(len(hash_value))  # 64 (SHA-256输出长度)
        """
        # 序列化为JSON（确保顺序一致）
        serialized = json.dumps(obj, sort_keys=sort_keys, default=str)

        # 计算哈希
        return cls.hash_string(serialized, algorithm)

    @classmethod
    def hash_file(
        cls, file_path: str, algorithm: str = DEFAULT_ALGORITHM, chunk_size: int = 8192
    ) -> str:
        """
        计算文件的安全哈希值（支持大文件）

        Args:
            file_path: 文件路径
            algorithm: 哈希算法
            chunk_size: 读取块大小（字节）

        Returns:
            十六进制哈希值

        Example:
            >>> file_hash = SecureHasher.hash_file('/path/to/file.txt')
            >>> print(len(file_hash))  # 64 (SHA-256输出长度)
        """
        hasher = cls._get_hasher(algorithm)()

        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)

        return hasher.hexdigest()

    @classmethod
    def _get_hasher(cls, algorithm: str):
        """
        获取哈希函数

        Args:
            algorithm: 算法名称

        Returns:
            哈希构造函数

        Raises:
            ValueError: 不支持的算法
        """
        algorithm_lower = algorithm.lower()

        if algorithm_lower in cls.SUPPORTED_ALGORITHMS:
            return cls.SUPPORTED_ALGORITHMS[algorithm_lower]

        raise ValueError(
            f"Unsupported algorithm: {algorithm}. "
            f"Supported: {', '.join(cls.SUPPORTED_ALGORITHMS.keys())}"
        )


# 便捷函数（向后兼容）
def compute_hash(data: Any, algorithm: str = "sha256") -> str:
    """
    计算数据的安全哈希值（便捷函数）

    Args:
        data: 输入数据（字符串或可JSON序列化的对象）
        algorithm: 哈希算法

    Returns:
        十六进制哈希值

    Example:
        >>> # 字符串
        >>> compute_hash('hello')
        >>>
        >>> # 对象
        >>> compute_hash({'key': 'value'})
    """
    if isinstance(data, str):
        return SecureHasher.hash_string(data, algorithm)
    else:
        return SecureHasher.hash_object(data, algorithm)


def compute_cache_key(obj: Any, algorithm: str = "sha256") -> str:
    """
    计算缓存键的安全哈希值（专用函数）

    用于缓存系统，确保相同对象产生相同的哈希值。

    Args:
        obj: 要计算哈希的对象
        algorithm: 哈希算法

    Returns:
        十六进制哈希值

    Example:
        >>> cache_key = compute_cache_key({'event': 'login', 'fields': ['x', 'y']})
        >>> # 使用cache_key作为Redis/Memcached键
    """
    return SecureHasher.hash_object(obj, algorithm=algorithm)


# 导出列表
__all__ = [
    "SecureHasher",
    "compute_hash",
    "compute_cache_key",
]

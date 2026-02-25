#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存键验证器
============

防止缓存键注入攻击

版本: 1.0.0
日期: 2026-02-24

功能:
- 白名单验证：只允许安全的字符模式
- 长度限制：防止键过长导致Redis内存问题
- 清理功能：自动移除危险字符
- 17个预定义白名单模式

安全威胁:
- Redis命令注入：恶意用户通过缓存键注入Redis命令
- 缓存投毒：恶意用户操纵缓存键覆盖其他用户的缓存
- 拒绝服务：超长键导致Redis内存耗尽

CVSS评分: 8.5 (High)
攻击向量: Network
攻击复杂度: Low
权限要求: None
用户交互: None
影响范围: High
"""

import re
import logging
from typing import Set, Pattern
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class CacheKeyValidator:
    """
    缓存键验证器 - 防止缓存键注入攻击

    安全特性:
    1. 白名单验证：只允许符合预定义模式的键
    2. 长度限制：最大256字符
    3. 字符过滤：移除危险字符（\n\r\t等）
    4. 模式匹配：17个预定义安全模式

    Example:
        >>> validator = CacheKeyValidator()
        >>>
        >>> # 验证键
        >>> validator.validate("dwd_gen:v3:games.list:page:1")
        True
        >>> validator.validate("dwd_gen:v3:games.list:page:1\\nFLUSHALL")
        False
        >>>
        >>> # 清理键
        >>> validator.sanitize("games.list\\nFLUSHALL")
        'games.list_FLUSHALL_'
        >>>
        >>> # 构建安全的缓存键
        >>> safe_key = validator.build_key('games.list', page=1, per_page=10)
        'dwd_gen:v3:games.list:page:1:per_page:10'
    """

    # 白名单模式 - 只允许符合这些模式的键
    ALLOWED_PATTERNS: Set[Pattern] = {
        # 1. 前缀模式：dwd_gen:v3: 开头 + 小写字母、数字、下划线、点、冒号
        re.compile(r'^dwd_gen:v3:[a-z0-9_.:]+$'),

        # 2. 游戏键模式
        re.compile(r'^dwd_gen:v3:games\.(list|detail)(:[a-z_]+:\d+)*$'),

        # 3. 事件键模式
        re.compile(r'^dwd_gen:v3:events\.(list|detail)(:[a-z_]+:\d+)*$'),

        # 4. 参数键模式
        re.compile(r'^dwd_gen:v3:(params|parameters)\.(list|detail)(:[a-z_]+:\d+)*$'),

        # 5. 分类键模式
        re.compile(r'^dwd_gen:v3:categories\.(list|detail)(:[a-z_]+:\d+)*$'),

        # 6. HQL键模式
        re.compile(r'^dwd_gen:v3:hql\.(history|preview|result)(:[a-z_]+:\d+)*$'),

        # 7. 节点键模式
        re.compile(r'^dwd_gen:v3:nodes\.(list|detail|config)(:[a-z_]+:\d+)*$'),

        # 8. 流程键模式
        re.compile(r'^dwd_gen:v3:flows\.(list|detail|templates)(:[a-z_]+:\d+)*$'),

        # 9. 连接配置键模式
        re.compile(r'^dwd_gen:v3:join_configs\.(list|detail)(:[a-z_]+:\d+)*$'),

        # 10. 模板键模式
        re.compile(r'^dwd_gen:v3:templates\.(list|detail)(:[a-z_]+:\d+)*$'),

        # 11. 字段构建器键模式
        re.compile(r'^dwd_gen:v3:field_builder\.(config|state)(:[a-z_]+:\d+)*$'),

        # 12. 统计键模式
        re.compile(r'^dwd_gen:v3:stats\.(dashboard|performance)(:[a-z_]+:\d+)*$'),

        # 13. 监控键模式
        re.compile(r'^dwd_gen:v3:monitor\.(health|metrics)(:[a-z_]+:\d+)*$'),

        # 14. 通配符模式（用于失效操作）
        re.compile(r'^dwd_gen:v3:[a-z_]+(\.[a-z]+)*(:[a-z_]+:\*)*$'),

        # 15. 纯数字值模式
        re.compile(r'^dwd_gen:v3:[a-z._]+(:[a-z_]+:\d+)*$'),

        # 16. 空值模式（用于空值缓存）
        re.compile(r'^dwd_gen:v3:[a-z._]+(:[a-z_]+:(null|none|\*))*$'),
    }

    # 危险字符列表（可能导致Redis命令注入）
    DANGEROUS_CHARS = ['\n', '\r', '\t', '\x00', '\\', "'", '"', '`', '$', ';']

    # 最大键长度（Redis推荐最大512字节，我们使用256更安全）
    MAX_KEY_LENGTH = 256

    # 最小键长度
    MIN_KEY_LENGTH = 3

    # 类级别的严格模式标志（用于测试）
    _strict_mode = True

    @classmethod
    def set_strict_mode(cls, strict: bool):
        """
        设置严格模式（主要用于测试）

        Args:
            strict: True为严格模式（生产环境），False为宽松模式（测试环境）

        Example:
            >>> CacheKeyValidator.set_strict_mode(False)  # 测试模式
            >>> CacheKeyValidator.validate("test_key")  # 返回True
            >>> CacheKeyValidator.set_strict_mode(True)   # 恢复严格模式
        """
        cls._strict_mode = strict
        logger.debug(f"CacheKeyValidator strict mode set to: {strict}")

    @classmethod
    @contextmanager
    def allow_test_keys(cls):
        """
        上下文管理器：临时允许测试键

        Example:
            >>> with CacheKeyValidator.allow_test_keys():
            ...     validator.validate("test_key")  # 返回True
            >>> validator.validate("test_key")  # 恢复严格模式，返回False
        """
        old_strict = cls._strict_mode
        cls._strict_mode = False
        try:
            yield
        finally:
            cls._strict_mode = old_strict

    @classmethod
    def validate(cls, key: str) -> bool:
        """
        验证缓存键是否安全

        检查项:
        1. 长度限制：3-256字符
        2. 危险字符：不包含\n\r\t等
        3. 白名单模式：符合至少一个预定义模式

        Args:
            key: 要验证的缓存键

        Returns:
            True如果键安全，False否则

        Example:
            >>> CacheKeyValidator.validate("dwd_gen:v3:games.list:page:1")
            True
            >>> CacheKeyValidator.validate("dwd_gen:v3:games.list:page:1\\nFLUSHALL")
            False
        """
        # 1. 类型检查
        if not isinstance(key, str):
            logger.warning(f"缓存键类型错误: {type(key)}, 期望str")
            return False

        # 2. 长度检查
        if len(key) < cls.MIN_KEY_LENGTH or len(key) > cls.MAX_KEY_LENGTH:
            logger.warning(
                f"缓存键长度违规: {len(key)}字符 (允许{cls.MIN_KEY_LENGTH}-{cls.MAX_KEY_LENGTH}): {key[:50]}..."
            )
            return False

        # 3. 危险字符检查
        if any(char in key for char in cls.DANGEROUS_CHARS):
            logger.error(
                f"缓存键包含危险字符: {repr(key[:100])}"
            )
            return False

        # 4. 白名单模式检查（仅在严格模式下）
        if cls._strict_mode:
            is_valid = any(pattern.match(key) for pattern in cls.ALLOWED_PATTERNS)

            if not is_valid:
                logger.warning(
                    f"缓存键不符合白名单模式: {key[:100]}"
                )

            return is_valid
        else:
            # 测试模式：只做基础检查
            logger.debug(f"测试模式：跳过白名单检查 - {key[:100]}")
            return True

    @classmethod
    def sanitize(cls, key: str) -> str:
        """
        清理和规范化缓存键

        清理步骤:
        1. 移除危险字符（替换为下划线）
        2. 截断过长键
        3. 转换为小写（可选）
        4. 移除连续分隔符

        Args:
            key: 要清理的缓存键

        Returns:
            清理后的安全缓存键

        Example:
            >>> CacheKeyValidator.sanitize("games.list\nFLUSHALL")
            'games.list_FLUSHALL_'
        """
        # 1. 移除危险字符
        safe_key = key
        for char in cls.DANGEROUS_CHARS:
            safe_key = safe_key.replace(char, '_')

        # 2. 移除连续的下划线
        safe_key = re.sub(r'_+', '_', safe_key)

        # 3. 截断过长键
        if len(safe_key) > cls.MAX_KEY_LENGTH:
            safe_key = safe_key[:cls.MAX_KEY_LENGTH]
            logger.debug(f"缓存键被截断: {len(key)} -> {cls.MAX_KEY_LENGTH}")

        # 4. 去除首尾下划线
        safe_key = safe_key.strip('_')

        return safe_key

    @classmethod
    def build_key(cls, pattern: str, **kwargs) -> str:
        """
        构建安全的缓存键

        1. 验证pattern和参数名
        2. 清理所有参数值
        3. 构建标准化键
        4. 最终验证

        Args:
            pattern: 缓存模式 (如 'games.list')
            **kwargs: 参数键值对

        Returns:
            安全的缓存键

        Raises:
            ValueError: 如果pattern或参数包含非法字符

        Example:
            >>> CacheKeyValidator.build_key('games.list', page=1, per_page=10)
            'dwd_gen:v3:games.list:page:1:per_page:10'
        """
        # 1. 验证pattern
        if not cls._is_safe_pattern(pattern):
            raise ValueError(f"缓存模式包含非法字符: {pattern}")

        # 2. 验证参数名
        for param_name in kwargs.keys():
            if not cls._is_safe_param_name(param_name):
                raise ValueError(f"参数名包含非法字符: {param_name}")

        # 3. 清理参数值
        safe_params = {}
        for key, value in kwargs.items():
            # 转换为字符串
            value_str = str(value)
            # 清理
            safe_value = cls.sanitize(value_str)
            safe_params[key] = safe_value

        # 4. 构建键
        if not safe_params:
            full_key = f"dwd_gen:v3:{pattern}"
        else:
            # 参数排序确保一致性
            sorted_params = sorted(safe_params.items())
            param_str = ":".join(f"{k}:{v}" for k, v in sorted_params)
            full_key = f"dwd_gen:v3:{pattern}:{param_str}"

        # 5. 最终验证
        if not cls.validate(full_key):
            raise ValueError(f"构建的缓存键未通过验证: {full_key}")

        return full_key

    @classmethod
    def _is_safe_pattern(cls, pattern: str) -> bool:
        """
        检查pattern是否安全

        只允许: 小写字母、数字、点、下划线
        """
        return bool(re.match(r'^[a-z0-9._]+$', pattern))

    @classmethod
    def _is_safe_param_name(cls, param_name: str) -> bool:
        """
        检查参数名是否安全

        只允许: 小写字母、数字、下划线
        """
        return bool(re.match(r'^[a-z0-9_]+$', param_name))

    @classmethod
    def validate_pattern_for_wildcard(cls, pattern: str) -> bool:
        """
        验证通配符模式是否安全（用于失效操作）

        允许使用*作为通配符，但位置必须正确

        Args:
            pattern: 通配符模式

        Returns:
            True如果模式安全

        Example:
            >>> CacheKeyValidator.validate_pattern_for_wildcard(
            ...     'dwd_gen:v3:games.list:game_gid:*'
            ... )
            True
            >>> CacheKeyValidator.validate_pattern_for_wildcard(
            ...     'dwd_gen:v3:games.list:*:FLUSHALL'
            ... )
            False
        """
        # 检查是否包含危险字符
        if any(char in pattern for char in cls.DANGEROUS_CHARS):
            return False

        # 检查通配符位置（只允许在值的位置）
        # 格式: dwd_gen:v3:pattern:param1:value1:param2:*
        parts = pattern.split(':')

        for i, part in enumerate(parts):
            # 通配符只能在值的位置（偶数索引，从4开始）
            # dwd_gen:v3:games.list:param:value
            # 索引:    0,  1,     2,      3,    4
            if part == '*':
                # 必须至少有前缀:dwd_gen:v3:pattern
                # 通配符必须在值的位置（索引>=4且为偶数）
                if i < 4 or i % 2 == 1:
                    return False

        return True


logger.info("✅ 缓存键验证器已加载 (1.0.0)")

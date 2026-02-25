#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感数据过滤器
==============

自动过滤日志中的敏感信息（密码、令牌、密钥等）

核心功能:
- 过滤敏感字段（password, token, key等）
- 检测和过滤敏感模式（Bearer token, API keys等）
- 保留正常日志内容
- 支持自定义敏感字段列表

版本: 1.0.0
日期: 2026-02-24
CVSS: 8.2 (High)
"""

import logging
import re
from typing import Optional, Set, Pattern


class SensitiveDataFilter(logging.Filter):
    """
    敏感数据过滤器 - 自动过滤日志中的敏感信息

    功能:
    1. 过滤敏感字段（password, token, key等）
    2. 检测和过滤敏感模式（Bearer token, API keys等）
    3. 保留正常日志内容
    4. 支持自定义敏感字段列表

    Example:
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> logger.addFilter(SensitiveDataFilter())
        >>> logger.info("User logged in with password=secret123")
        # Output: User logged in with password=[REDACTED]
    """

    # 敏感字段列表
    SENSITIVE_FIELDS: Set[str] = {
        'password', 'passwd', 'pwd',
        'token', 'access_token', 'refresh_token', 'auth_token',
        'key', 'api_key', 'secret_key', 'private_key', 'public_key',
        'session', 'session_id',
        'auth', 'authorization', 'authenticate',
        'credential', 'credentials',
        'secret', 'passcode',
        'jwt', 'bearer'
    }

    # 敏感值模式（正则表达式）
    SENSITIVE_PATTERNS: Set[Pattern] = {
        # Bearer tokens
        re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE),
        # Basic auth
        re.compile(r'Basic\s+[A-Za-z0-9+/=]+', re.IGNORECASE),
        # JWT tokens (3 parts separated by dots)
        re.compile(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'),
        # API keys (32+ chars, alphanumeric)
        re.compile(r'[A-Za-z0-9]{32,}', re.IGNORECASE),
        # UUID-like patterns
        re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE),
    }

    def __init__(self, custom_fields: Optional[Set[str]] = None, custom_patterns: Optional[Set[Pattern]] = None):
        """
        初始化敏感数据过滤器

        Args:
            custom_fields: 自定义敏感字段集合（可选）
            custom_patterns: 自定义敏感模式集合（可选）
        """
        super().__init__()

        # 合并自定义敏感字段（统一转为小写存储）
        self.sensitive_fields = self.SENSITIVE_FIELDS.copy()
        if custom_fields:
            # 将自定义字段转为小写
            self.sensitive_fields.update(f.lower() for f in custom_fields)

        # 合并自定义敏感模式
        self.sensitive_patterns = list(self.SENSITIVE_PATTERNS)
        if custom_patterns:
            self.sensitive_patterns.extend(custom_patterns)

    def filter(self, record: logging.LogRecord) -> bool:
        """
        过滤日志记录中的敏感信息

        Args:
            record: 日志记录对象

        Returns:
            True（始终允许日志记录通过）
        """
        # 清理日志消息
        if hasattr(record, 'msg'):
            record.msg = self._sanitize(str(record.msg))

        # 清理日志参数
        if hasattr(record, 'args') and record.args is not None:
            record.args = tuple(
                self._sanitize(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args  # type: ignore[union-attr]
            )

        return True

    def _sanitize(self, text: str) -> str:
        """
        清理敏感信息

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        # 1. 先过滤敏感模式（如Bearer token, Basic auth等）
        # 这些模式应该在整个文本上匹配，不受字段名限制
        for pattern in self.sensitive_patterns:
            text = pattern.sub('[REDACTED]', text)

        # 2. 过滤敏感字段（多次迭代以处理所有匹配）
        max_iterations = 3  # 防止无限循环
        for _ in range(max_iterations):
            original_text = text
            for field in self.sensitive_fields:
                # 匹配多种格式:
                # password=secret
                # password:secret
                # "password":"secret"
                # password="secret"
                # 'password' => 'secret'
                # 使用format()方法避免f-string转义问题
                escaped_field = re.escape(field)

                # 分别匹配不同的格式，使用回调函数保留原始字段名的大小写
                # 格式1: field=value (使用S+匹配非空白字符，但不包括&和,等分隔符)
                # 使用负向后瞻和负向前瞻确保匹配完整的字段名，而不是子串
                pattern1_str = r'(?<![a-zA-Z0-9_])' + escaped_field + r'(?![a-zA-Z0-9_])\s*=\s*[^\s&,}]+'
                pattern1 = re.compile(pattern1_str, re.IGNORECASE)

                def replace_with_case_preserver(match):
                    """保留原始字段名的大小写"""
                    matched_text = match.group(0)
                    # 提取原始字段名（在=或:之前的部分）
                    parts = re.split(r'[\s:=]+', matched_text, maxsplit=1)
                    original_field_name = parts[0]
                    return original_field_name + '=[REDACTED]'

                text = pattern1.sub(replace_with_case_preserver, text)

                # 格式2: field:value
                pattern2_str = r'(?<![a-zA-Z0-9_])' + escaped_field + r'(?![a-zA-Z0-9_])\s*:\s*[^\s&,}]+'
                pattern2 = re.compile(pattern2_str, re.IGNORECASE)
                text = pattern2.sub(replace_with_case_preserver, text)

                # 格式3: "field":"value" 或 'field':'value' (JSON格式)
                # 这个模式需要特殊处理以保留引号
                # 使用负向后瞻确保不匹配子串
                pattern3_str = r'(?<![a-zA-Z0-9_])(["\']?)' + escaped_field + r'\1(?![a-zA-Z0-9_])\s*:\s*["\']([^"\']+)["\']'
                pattern3 = re.compile(pattern3_str, re.IGNORECASE)

                def replace_json_with_case(match):
                    """保留JSON格式中的字段名大小写和引号"""
                    quote1 = match.group(1) or '"'  # 第一个引号（如果没有则使用双引号）
                    # 提取原始字段名
                    full_match = match.group(0)
                    field_part = full_match.split(':')[0]
                    # 返回带引号的字段名和[REDACTED]
                    return f'{field_part}:[REDACTED]'

                text = pattern3.sub(replace_json_with_case, text)

            # 如果文本没有变化，提前退出
            if text == original_text:
                break

        return text

    def add_sensitive_field(self, field: str):
        """
        添加自定义敏感字段

        Args:
            field: 字段名称
        """
        self.sensitive_fields.add(field.lower())

    def add_sensitive_pattern(self, pattern: Pattern):
        """
        添加自定义敏感模式

        Args:
            pattern: 正则表达式模式
        """
        self.sensitive_patterns.append(pattern)

    def remove_sensitive_field(self, field: str):
        """
        移除敏感字段

        Args:
            field: 字段名称
        """
        self.sensitive_fields.discard(field.lower())


# 全局过滤器实例（单例）
_global_filter: Optional[SensitiveDataFilter] = None


def get_sensitive_data_filter() -> SensitiveDataFilter:
    """
    获取全局敏感数据过滤器实例

    Returns:
        SensitiveDataFilter实例
    """
    global _global_filter
    if _global_filter is None:
        _global_filter = SensitiveDataFilter()
    return _global_filter


def setup_logging_filter():
    """
    在根logger上设置敏感数据过滤器

    所有子logger都会自动应用此过滤器
    """
    root_logger = logging.getLogger()
    filter_instance = get_sensitive_data_filter()

    # 避免重复添加
    if not any(isinstance(f, SensitiveDataFilter) for f in root_logger.filters):
        root_logger.addFilter(filter_instance)
        logging.info("✅ 敏感数据过滤器已启用")


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )

    # 添加过滤器
    setup_logging_filter()

    # 测试用例
    logger = logging.getLogger(__name__)

    # 测试1: 密码过滤
    logger.info("User login: password=secret123")

    # 测试2: Token过滤
    logger.info("Auth: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

    # 测试3: API key过滤
    logger.info("API request: api_key=sk-1234567890abcdef1234567890abcdef")

    # 测试4: 正常日志（应该保留）
    logger.info("User logged in successfully")

    # 测试5: JSON格式
    logger.info('{"username":"john","password":"secret123"}')

    # 测试6: 混合格式
    logger.info("Request: token=abc123, user_id=456, status=active")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敏感数据过滤器单元测试
======================

测试敏感数据过滤器的功能：
- 敏感字段过滤
- 敏感模式检测
- 正常日志保留
- 自定义字段支持

版本: 1.0.0
日期: 2026-02-24
CVSS: 8.2 (High)
"""

import logging
import pytest
import re
from io import StringIO
from backend.core.cache.filters import SensitiveDataFilter


class TestSensitiveDataFilter:
    """敏感数据过滤器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.filter = SensitiveDataFilter()

    def test_password_filtering(self):
        """测试密码字段过滤"""
        # 测试等号格式
        assert self.filter._sanitize("password=secret123") == "password=[REDACTED]"

        # 测试冒号格式
        assert self.filter._sanitize("password:secret123") == "password=[REDACTED]"

        # 测试JSON格式
        assert self.filter._sanitize('"password":"secret123"') == '"password":[REDACTED]'

    def test_token_filtering(self):
        """测试令牌字段过滤"""
        assert self.filter._sanitize("token=abc123") == "token=[REDACTED]"
        assert self.filter._sanitize("access_token=xyz789") == "access_token=[REDACTED]"
        assert self.filter._sanitize("auth_token=token123") == "auth_token=[REDACTED]"

    def test_api_key_filtering(self):
        """测试API密钥字段过滤"""
        assert self.filter._sanitize("api_key=key123") == "api_key=[REDACTED]"
        assert self.filter._sanitize("secret_key=secret123") == "secret_key=[REDACTED]"
        assert self.filter._sanitize("private_key=key456") == "private_key=[REDACTED]"

    def test_bearer_token_pattern(self):
        """测试Bearer令牌模式过滤"""
        # 测试标准Bearer token
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = self.filter._sanitize(text)
        assert "[REDACTED]" in result
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result

    def test_basic_auth_pattern(self):
        """测试Basic认证模式过滤"""
        text = "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ="
        result = self.filter._sanitize(text)
        assert "[REDACTED]" in result
        assert "dXNlcm5hbWU6cGFzc3dvcmQ=" not in result

    def test_jwt_token_pattern(self):
        """测试JWT令牌模式过滤"""
        text = "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        result = self.filter._sanitize(text)
        assert "[REDACTED]" in result
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result

    def test_long_alphanumeric_pattern(self):
        """测试长字母数字模式过滤（可能的API密钥）"""
        text = "api_key=sk-1234567890abcdef1234567890abcdef"
        result = self.filter._sanitize(text)
        assert "[REDACTED]" in result
        # 字段名保留，值被过滤
        assert "api_key=" in result
        assert "sk-1234567890abcdef1234567890abcdef" not in result

    def test_normal_log_preservation(self):
        """测试正常日志内容保留"""
        # 测试普通日志（不应被过滤）
        text = "User logged in successfully"
        result = self.filter._sanitize(text)
        assert result == text

        # 测试包含数字但不敏感的日志
        text = "Request processed in 123ms"
        result = self.filter._sanitize(text)
        assert result == text

    def test_multiple_sensitive_fields(self):
        """测试多个敏感字段过滤"""
        text = "password=secret123&token=abc456&api_key=key789"
        result = self.filter._sanitize(text)
        assert result == "password=[REDACTED]&token=[REDACTED]&api_key=[REDACTED]"

    def test_case_insensitive_field_matching(self):
        """测试字段名称大小写不敏感匹配"""
        assert self.filter._sanitize("Password=secret123") == "Password=[REDACTED]"
        assert self.filter._sanitize("PASSWORD=secret123") == "PASSWORD=[REDACTED]"
        assert self.filter._sanitize("Api_Key=abc123") == "Api_Key=[REDACTED]"

    def test_custom_field_addition(self):
        """测试自定义敏感字段添加"""
        # 添加自定义字段
        self.filter.add_sensitive_field("custom_secret")

        # 测试自定义字段过滤
        text = "custom_secret=mysecret"
        result = self.filter._sanitize(text)
        assert result == "custom_secret=[REDACTED]"

    def test_custom_field_removal(self):
        """测试自定义敏感字段移除"""
        # 添加自定义字段
        self.filter.add_sensitive_field("temp_secret")

        # 确认过滤有效
        assert self.filter._sanitize("temp_secret=secret") == "temp_secret=[REDACTED]"

        # 移除自定义字段
        self.filter.remove_sensitive_field("temp_secret")

        # 确认不再过滤
        text = "temp_secret=secret"
        result = self.filter._sanitize(text)
        assert result == text

    def test_custom_pattern_addition(self):
        """测试自定义敏感模式添加"""
        # 添加自定义模式（匹配特定格式）
        custom_pattern = re.compile(r'CUSTOM\d{10}')
        self.filter.add_sensitive_pattern(custom_pattern)

        # 测试自定义模式过滤
        text = "code=CUSTOM1234567890"
        result = self.filter._sanitize(text)
        assert "[REDACTED]" in result

    def test_logging_filter_integration(self):
        """测试日志过滤器集成"""
        # 创建logger
        logger = logging.getLogger("test_logger")
        logger.setLevel(logging.INFO)

        # 添加过滤器
        logger.addFilter(self.filter)

        # 创建字符串handler捕获日志
        string_stream = StringIO()
        handler = logging.StreamHandler(string_stream)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        # 记录敏感信息
        logger.info("User login: password=secret123")

        # 检查日志输出
        log_output = string_stream.getvalue()
        assert "password=[REDACTED]" in log_output
        assert "secret123" not in log_output

        # 清理
        logger.removeHandler(handler)

    def test_complex_json_filtering(self):
        """测试复杂JSON格式过滤"""
        # 测试嵌套JSON
        text = '{"user":"john","password":"secret123","token":"abc456"}'
        result = self.filter._sanitize(text)
        assert "password=[REDACTED]" in result
        assert "token=[REDACTED]" in result
        assert '"user":"john"' in result  # 正常字段保留

    def test_url_parameter_filtering(self):
        """测试URL参数过滤"""
        # 测试URL中的敏感参数
        text = "https://api.example.com/login?password=secret123&token=abc456"
        result = self.filter._sanitize(text)
        assert "password=[REDACTED]" in result
        assert "token=[REDACTED]" in result
        assert "https://api.example.com/login?" in result  # URL保留

    def test_uuid_pattern_filtering(self):
        """测试UUID模式过滤"""
        # 测试UUID格式过滤
        text = "session_id=550e8400-e29b-41d4-a716-446655440000"
        result = self.filter._sanitize(text)
        assert "[REDACTED]" in result

    def test_multiple_log_records(self):
        """测试多个日志记录过滤"""
        logger = logging.getLogger("test_multi_logger")
        logger.setLevel(logging.INFO)

        # 添加过滤器
        logger.addFilter(self.filter)

        # 创建字符串handler
        string_stream = StringIO()
        handler = logging.StreamHandler(string_stream)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        # 记录多条日志
        logger.info("password=secret1")
        logger.info("token=abc123")
        logger.info("normal message")

        # 检查输出
        log_output = string_stream.getvalue()
        assert "password=[REDACTED]" in log_output
        assert "token=[REDACTED]" in log_output
        assert "normal message" in log_output
        assert "secret1" not in log_output
        assert "abc123" not in log_output

        # 清理
        logger.removeHandler(handler)


class TestSensitiveDataFilterEdgeCases:
    """敏感数据过滤器边界测试"""

    def setup_method(self):
        """测试前准备"""
        self.filter = SensitiveDataFilter()

    def test_empty_string(self):
        """测试空字符串"""
        assert self.filter._sanitize("") == ""

    def test_no_sensitive_data(self):
        """测试无敏感数据"""
        text = "Just a normal log message without any secrets"
        assert self.filter._sanitize(text) == text

    def test_partial_match(self):
        """测试部分匹配"""
        # 应该只过滤完整的敏感字段
        text = "password123 is not a match"
        result = self.filter._sanitize(text)
        # "password123" 不等于 "password"，所以不应该被过滤
        assert "password123" in result

    def test_special_characters(self):
        """测试特殊字符"""
        text = "password=p@ssw0rd!#$%"
        result = self.filter._sanitize(text)
        assert result == "password=[REDACTED]"

    def test_unicode_characters(self):
        """测试Unicode字符"""
        text = "password=密码123"
        result = self.filter._sanitize(text)
        assert result == "password=[REDACTED]"

    def test_very_long_string(self):
        """测试超长字符串"""
        long_value = "a" * 1000
        text = f"password={long_value}"
        result = self.filter._sanitize(text)
        assert result == "password=[REDACTED]"
        assert long_value not in result


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])

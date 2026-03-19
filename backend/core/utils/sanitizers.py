"""
SQL标识符清理工具

用于清理不符合SQL命名规范的标识符，使其安全可用。
"""

import re
from typing import Optional


class IdentifierSanitizer:
    """SQL标识符清理工具

    用于清理不符合SQL命名规范的标识符，使其安全可用。

    清理规则：
    1. 点号、连字符、空格替换为下划线
    2. 移除非字母数字下划线字符
    3. 确保不以数字开头（添加前缀_）
    4. 确保不为空（返回_safe_identifier）

    Examples:
        >>> IdentifierSanitizer.sanitize("my-field")
        'my_field'

        >>> IdentifierSanitizer.sanitize("my.field")
        'my_field'

        >>> IdentifierSanitizer.sanitize("123field")
        '_123field'

        >>> IdentifierSanitizer.sanitize("field@#$")
        'field'

        >>> IdentifierSanitizer.sanitize_and_escape("my-field")
        '`my_field`'
    """

    # 需要替换为下划线的字符
    REPLACE_CHARS = {'.': '_', '-': '_', ' ': '_'}

    # 允许的字符模式：字母、数字、下划线
    VALID_PATTERN = re.compile(r'[a-zA-Z0-9_]+')

    # 以数字开头的模式
    STARTS_WITH_DIGIT = re.compile(r'^[0-9]')

    @staticmethod
    def sanitize(identifier: str) -> str:
        """清理标识符中的特殊字符

        清理步骤：
        1. 替换点号、连字符、空格为下划线
        2. 移除所有非字母数字下划线字符
        3. 如果以数字开头，添加前缀下划线
        4. 如果为空，返回默认标识符

        Args:
            identifier: 原始标识符（如：my-field, my.field, 123field）

        Returns:
            清理后的标识符（如：my_field, my_field, _123field）

        Raises:
            ValueError: 如果identifier不是字符串或为None

        Examples:
            >>> IdentifierSanitizer.sanitize("my-field")
            'my_field'

            >>> IdentifierSanitizer.sanitize("my.field.name")
            'my_field_name'

            >>> IdentifierSanitizer.sanitize("123field")
            '_123field'

            >>> IdentifierSanitizer.sanitize("")
            '_safe_identifier'

            >>> IdentifierSanitizer.sanitize("field@#$")
            'field'
        """
        # 验证输入
        if identifier is None:
            raise ValueError("Identifier cannot be None")

        if not isinstance(identifier, str):
            raise ValueError(f"Identifier must be a string, got {type(identifier).__name__}")

        # Step 1: 替换特殊字符为下划线
        result = identifier
        for char, replacement in IdentifierSanitizer.REPLACE_CHARS.items():
            result = result.replace(char, replacement)

        # Step 2: 移除所有非字母数字下划线字符
        # 保留所有有效字符，忽略无效字符
        valid_chars = []
        for char in result:
            if IdentifierSanitizer.VALID_PATTERN.match(char):
                valid_chars.append(char)

        result = ''.join(valid_chars)

        # Step 3: 确保不以数字开头（添加前缀_）
        if IdentifierSanitizer.STARTS_WITH_DIGIT.match(result):
            result = '_' + result

        # Step 4: 确保不为空
        if not result:
            result = '_safe_identifier'

        return result

    @staticmethod
    def sanitize_and_escape(identifier: str) -> str:
        """清理并转义标识符

        对清理后的标识符添加反引号转义，确保SQL安全。

        Args:
            identifier: 原始标识符

        Returns:
            转义后的安全SQL标识符（带反引号）

        Raises:
            ValueError: 如果identifier不是字符串或为None

        Examples:
            >>> IdentifierSanitizer.sanitize_and_escape("my-field")
            '`my_field`'

            >>> IdentifierSanitizer.sanitize_and_escape("my.field")
            '`my_field`'

            >>> IdentifierSanitizer.sanitize_and_escape("123field")
            '`_123field`'
        """
        sanitized = IdentifierSanitizer.sanitize(identifier)
        return f'`{sanitized}`'

    @staticmethod
    def sanitize_list(identifiers: list[str]) -> list[str]:
        """批量清理标识符列表

        Args:
            identifiers: 标识符列表

        Returns:
            清理后的标识符列表

        Examples:
            >>> IdentifierSanitizer.sanitize_list(["field-1", "field.2", "field 3"])
            ['field_1', 'field_2', 'field_3']
        """
        return [IdentifierSanitizer.sanitize(id) for id in identifiers]

    @staticmethod
    def is_safe(identifier: str) -> bool:
        """检查标识符是否已经是安全的SQL标识符

        安全标识符定义：
        - 只包含字母、数字、下划线
        - 不以数字开头
        - 不为空

        Args:
            identifier: 要检查的标识符

        Returns:
            True如果标识符已经安全，False否则

        Examples:
            >>> IdentifierSanitizer.is_safe("my_field")
            True

            >>> IdentifierSanitizer.is_safe("my-field")
            False

            >>> IdentifierSanitizer.is_safe("123field")
            False
        """
        # 检查是否为空
        if not identifier:
            return False

        # 检查是否只包含有效字符
        if not IdentifierSanitizer.VALID_PATTERN.fullmatch(identifier):
            return False

        # 检查是否以数字开头
        if IdentifierSanitizer.STARTS_WITH_DIGIT.match(identifier):
            return False

        return True


# 便捷函数，保持向后兼容
def sanitize_identifier(identifier: str) -> str:
    """便捷函数：清理SQL标识符

    这是IdentifierSanitizer.sanitize()的便捷包装函数。

    Args:
        identifier: 原始标识符

    Returns:
        清理后的标识符

    Examples:
        >>> sanitize_identifier("my-field")
        'my_field'
    """
    return IdentifierSanitizer.sanitize(identifier)


# ============================================================================
# HTML and User Input Sanitization Functions
# ============================================================================

import re

# Sanitization patterns
XSS_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE)
XSS_EVENT_PATTERN = re.compile(r"on\w+\s*=", re.IGNORECASE)  # onclick=, onload=, etc.
XSS_JS_PATTERN = re.compile(r"javascript:", re.IGNORECASE)  # javascript:伪协议
XSS_DATA_PATTERN = re.compile(r"data:text/html", re.IGNORECASE)  # data:伪协议
XSS_IFRAME_PATTERN = re.compile(r"<iframe[^>]*>.*?</iframe>", re.IGNORECASE)
XSS_OBJECT_PATTERN = re.compile(r"<object[^>]*>.*?</object>", re.IGNORECASE)
XSS_EMBED_PATTERN = re.compile(r"<embed[^>]*>", re.IGNORECASE)
XSS_LINK_PATTERN = re.compile(r"<link[^>]*>", re.IGNORECASE)
XSS_META_PATTERN = re.compile(r"<meta[^>]*>", re.IGNORECASE)
XSS_STYLE_PATTERN = re.compile(r"<style[^>]*>.*?</style>", re.IGNORECASE)
XSS_FORM_PATTERN = re.compile(r"<form[^>]*>.*?</form>", re.IGNORECASE)
XSS_INPUT_PATTERN = re.compile(r"<input[^>]*>", re.IGNORECASE)


def sanitize_html(text: str) -> str:
    """
    Enhanced HTML sanitization to prevent XSS attacks

    Removes dangerous HTML tags, JavaScript event handlers, and
    escapes HTML special characters to prevent XSS attacks.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text with dangerous HTML removed
    """
    if not text:
        return ""

    # Remove dangerous HTML tags
    text = XSS_PATTERN.sub("", text)  # <script> tags
    text = XSS_IFRAME_PATTERN.sub("", text)  # <iframe> tags
    text = XSS_OBJECT_PATTERN.sub("", text)  # <object> tags
    text = XSS_EMBED_PATTERN.sub("", text)  # <embed> tags
    text = XSS_LINK_PATTERN.sub("", text)  # <link> tags
    text = XSS_META_PATTERN.sub("", text)  # <meta> tags
    text = XSS_STYLE_PATTERN.sub("", text)  # <style> tags
    text = XSS_FORM_PATTERN.sub("", text)  # <form> tags
    text = XSS_INPUT_PATTERN.sub("", text)  # <input> tags

    # Remove JavaScript event handlers (onclick, onload, etc.)
    text = XSS_EVENT_PATTERN.sub("", text)

    # Remove javascript: and data: pseudo-protocols
    text = XSS_JS_PATTERN.sub("", text)
    text = XSS_DATA_PATTERN.sub("", text)

    # Escape HTML special characters (do this last to catch any remaining)
    html_escape_table = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "`": "&#96;",  # Backtick (ES6 template literals)
        "=": "&#61;",  # Equals sign (can be used in attributes)
    }
    return "".join(html_escape_table.get(c, c) for c in text)


def escape_output(text: str) -> str:
    """
    Escape text for safe output in HTML templates

    Note: Jinja2 auto-escapes by default, but this is for manual output
    or when bypassing auto-escaping.

    Args:
        text: Text to escape

    Returns:
        HTML-escaped text
    """
    if not text:
        return ""

    # Use comprehensive HTML escaping
    return sanitize_html(text)


def sanitize_user_input(text: str, allow_html: bool = False) -> str:
    """
    Sanitize user input for safe storage and display

    Args:
        text: Text to sanitize
        allow_html: Whether to allow HTML (currently not supported, always sanitized)

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    text = text.strip()

    # Always sanitize HTML for security
    text = sanitize_html(text)

    # Limit length
    if len(text) > 10000:
        text = text[:10000]

    return text


__all__ = [
    'IdentifierSanitizer',
    'sanitize_identifier',
    'sanitize_html',
    'sanitize_user_input',
    'escape_output',
]
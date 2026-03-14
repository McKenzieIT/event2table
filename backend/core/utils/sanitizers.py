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

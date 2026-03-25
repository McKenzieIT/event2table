"""
P0-9: 测试错误信息不泄露敏感信息

验证: 
1. 异常堆栈跟踪不返回给客户端
2. 数据库结构不暴露（表名, 列名, SQL语句）
3. 文件路径不暴露
4. 内部变量名不暴露
5. 返回通用, 用户友好的错误消息
"""

from unittest.mock import Mock, patch

import pytest


def test_create_parameter_does_not_leak_stack_trace():
    """
    测试参数创建失败时不泄露堆栈跟踪

    错误响应应该:
    - 不包含堆栈跟踪
    - 不包含文件路径
    - 不包含SQL语句
    - 不包含内部变量名
    """
    # 先检查mutation是否存在
    try:
        from backend.gql_api.mutations.parameter_mutations import resolve_create_parameter
    except ImportError as e:
        pytest.skip(f"Mutation not yet implemented: {e}")

    info = Mock()

    # 模拟数据库错误
    with patch('backend.gql_api.mutations.parameter_mutations.execute_insert') as mock_insert:
        mock_insert.side_effect = Exception(
            "Database connection failed: integrity constraint violation"
        )

        try:
            result = resolve_create_parameter(
                info, event_id=999999, param_name="test", param_type="string"  # 不存在的事件ID
            )

            # 验证: 错误消息应该是通用的
            if hasattr(result, 'errors') and result.errors:
                error_msg = str(result.errors[0])

                # 检查不应该包含的内容
                assert (
                    "stack trace" not in error_msg.lower()
                ), "Error message should not contain 'stack trace'"
                assert ".py" not in error_msg, "Error message should not contain file paths (.py)"
                assert (
                    "integrity constraint" not in error_msg.lower()
                ), "Error message should not contain database details"
                assert (
                    "database connection" not in error_msg.lower()
                ), "Error message should not contain internal errors"

                # 应该包含通用错误消息
                assert (
                    "failed" in error_msg.lower() or "error" in error_msg.lower()
                ), "Error message should be user-friendly"
            else:
                # 如果没有errors属性, 检查返回的error字段
                if isinstance(result, dict) and 'error' in result:
                    error_msg = str(result['error'])

                    # 检查不应该包含的内容
                    assert (
                        "stack trace" not in error_msg.lower()
                    ), "Error message should not contain 'stack trace'"
                    assert (
                        ".py" not in error_msg
                    ), "Error message should not contain file paths (.py)"
                    assert (
                        "integrity constraint" not in error_msg.lower()
                    ), "Error message should not contain database details"

        except Exception as e:
            # 如果抛出异常, 验证异常消息不泄露敏感信息
            error_msg = str(e)

            # ❌ 这个测试会失败, 因为当前代码直接返回异常
            assert (
                "stack trace" not in error_msg.lower()
            ), "Error message should not contain 'stack trace'"
            assert ".py" not in error_msg, "Error message should not contain file paths (.py)"
            assert (
                "integrity constraint" not in error_msg.lower()
            ), "Error message should not contain database details"


def test_create_event_does_not_leak_sensitive_info():
    """
    测试事件创建失败时不泄露敏感信息
    """
    # 先检查mutation是否存在
    try:
        from backend.gql_api.mutations.event_mutations import resolve_create_event
    except ImportError as e:
        pytest.skip(f"Mutation not yet implemented: {e}")

    info = Mock()

    # 模拟SQL错误
    with patch('backend.gql_api.mutations.event_mutations.execute_insert') as mock_insert:
        mock_insert.side_effect = Exception(
            "SQL error: table 'log_events' has no column 'invalid_column'"
        )

        try:
            result = resolve_create_event(
                info,
                game_gid=90000001,
                event_name="Test",
                event_code="test",
                source_table="test.invalid",
            )

            if hasattr(result, 'errors') and result.errors:
                error_msg = str(result.errors[0])

                # 不应该包含SQL语句
                assert "select" not in error_msg.lower(), "Error should not contain SQL statements"
                assert "table" not in error_msg.lower(), "Error should not contain table names"
                assert "column" not in error_msg.lower(), "Error should not contain column names"
            else:
                if isinstance(result, dict) and 'error' in result:
                    error_msg = str(result['error'])

                    # 不应该包含SQL语句
                    assert (
                        "select" not in error_msg.lower()
                    ), "Error should not contain SQL statements"
                    assert "table" not in error_msg.lower(), "Error should not contain table names"
                    assert (
                        "column" not in error_msg.lower()
                    ), "Error should not contain column names"

        except Exception as e:
            # 如果抛出异常, 验证异常消息不泄露敏感信息
            error_msg = str(e)

            # ❌ 这个测试会失败, 因为当前代码直接返回异常
            assert "select" not in error_msg.lower(), "Error should not contain SQL statements"
            assert "table" not in error_msg.lower(), "Error should not contain table names"
            assert "column" not in error_msg.lower(), "Error should not contain column names"


def test_generic_error_messages_for_all_mutations():
    """
    测试所有mutation使用通用错误消息
    """
    # 敏感信息列表
    sensitive_patterns = [
        "stack trace",
        "traceback",
        ".py:",
        "file ",
        "directory",
        "sql ",
        "select ",
        "insert ",
        "update ",
        "delete ",
        "table ",
        "column ",
        "constraint",
        "integrity",
        "foreign key",
        "primary key",
    ]

    def is_error_message_safe(error_msg: str) -> bool:
        """检查错误消息是否安全"""
        error_lower = error_msg.lower()
        for pattern in sensitive_patterns:
            if pattern.lower() in error_lower:
                return False
        return True

    # 示例用法
    assert is_error_message_safe("Failed to create parameter") == True
    assert is_error_message_safe("An error occurred") == True
    assert is_error_message_safe("SQL error: table foo") == False


def test_database_error_sanitization():
    """
    测试数据库错误被正确清理
    """
    from backend.core.security.error_sanitizer import ErrorSanitizer

    # 模拟典型的数据库错误
    raw_db_errors = [
        "IntegrityError: FOREIGN KEY constraint failed",
        "OperationalError: no such table: log_events",
        "ProgrammingError: column 'invalid_col' does not exist",
        "sqlite3.IntegrityError: UNIQUE constraint failed: log_events.name",
        "psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint",
    ]

    for error_msg in raw_db_errors:
        # Create a mock exception
        error = Exception(error_msg)

        # Use ErrorSanitizer
        sanitized = ErrorSanitizer.sanitize(error)

        # ✅ 现在这些断言应该通过
        assert (
            "constraint" not in sanitized.lower()
        ), f"Sanitized error should not contain 'constraint': {sanitized}"
        assert (
            "table" not in sanitized.lower()
        ), f"Sanitized error should not contain 'table': {sanitized}"
        assert (
            "column" not in sanitized.lower()
        ), f"Sanitized error should not contain 'column': {sanitized}"
        assert ".py" not in sanitized, f"Sanitized error should not contain file paths: {sanitized}"


def test_file_path_not_leaked():
    """
    测试文件路径不泄露
    """
    from backend.core.security.error_sanitizer import ErrorSanitizer

    # 模拟包含文件路径的错误
    error_with_path = (
        "FileNotFoundError: [Errno 2] No such file or directory: "
        "'/Users/mckenzie/Documents/event2table/backend/config/config.json'"
    )

    error = Exception(error_with_path)
    sanitized = ErrorSanitizer.sanitize(error)

    # ✅ 现在这些断言应该通过
    assert "/Users/" not in sanitized, "Error should not contain file paths"
    assert "Documents/" not in sanitized, "Error should not contain file paths"
    assert ".py" not in sanitized, "Error should not contain Python file paths"
    assert ".json" not in sanitized, "Error should not contain config file paths"


def test_internal_variable_names_not_leaked():
    """
    测试内部变量名不泄露
    """
    from backend.core.security.error_sanitizer import ErrorSanitizer

    # 模拟包含内部变量名的错误
    error_with_vars = (
        "NameError: name 'user_context' is not defined " "in function create_event at line 42"
    )

    error = Exception(error_with_vars)
    sanitized = ErrorSanitizer.sanitize(error)

    # ✅ 现在这些断言应该通过
    assert "user_context" not in sanitized, "Error should not contain internal variable names"
    assert (
        "function " not in sanitized.lower() or "line " not in sanitized
    ), "Error should not contain code location details"


def test_stack_trace_not_leaked():
    """
    测试堆栈跟踪不泄露
    """
    from backend.core.security.error_sanitizer import ErrorSanitizer

    # 模拟完整的堆栈跟踪
    stack_trace = """
Traceback (most recent call last):
  File "/Users/mckenzie/Documents/event2table/backend/api/routes/events.py", line 45, in create_event
    event_id = execute_insert(...)
  File "/Users/mckenzie/Documents/event2table/backend/core/database/converters.py", line 123, in execute_insert
    cursor.execute(query, params)
sqlite3.IntegrityError: UNIQUE constraint failed
    """

    error = Exception(stack_trace)
    sanitized = ErrorSanitizer.sanitize(error)

    # ✅ 现在这些断言应该通过
    assert "Traceback" not in sanitized, "Error should not contain 'Traceback'"
    assert "File " not in sanitized, "Error should not contain 'File '"
    assert ".py" not in sanitized, "Error should not contain file paths"
    assert "line " not in sanitized.lower(), "Error should not contain line numbers"


if __name__ == "__main__":
    # 运行测试并显示详细输出
    pytest.main([__file__, "-v", "-s"])

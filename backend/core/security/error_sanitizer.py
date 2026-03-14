"""
Error Message Sanitizer

Sanitizes error messages to prevent information leakage.
Provides user-friendly error messages while logging detailed errors internally.

Security: P0-9 - Error Message Leak Prevention
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class ErrorSanitizer:
    """
    Error message sanitizer for preventing information leakage.

    Removes sensitive information from exceptions before returning to clients:
    - File paths and directory structures
    - Stack traces and traceback information
    - Database internals (table names, column names, constraints)
    - SQL statements
    - Internal variable names and code locations
    """

    # Patterns that indicate sensitive information
    SENSITIVE_PATTERNS = [
        r'Traceback',  # Stack trace headers
        r'File\s+',  # File paths in tracebacks
        r'\.py:',  # Python file references
        r'\.pyc',  # Python bytecode files
        r'line\s+\d+',  # Line numbers
        r'sqlite3\.',  # SQLite driver info
        r'psycopg2\.',  # PostgreSQL driver info
        r'pymysql\.',  # MySQL driver info
        r'constraint',  # Database constraints
        r'integrity',  # Integrity violations
        r'foreign key',  # Foreign key errors
        r'primary key',  # Primary key errors
        r'unique constraint',  # Unique violations
        r'not null',  # NOT NULL violations
        r'/[a-zA-Z0-9_\-\.]+/',  # Unix-style paths
        r'[A-Z]:\\[a-zA-Z0-9_\-\.\\]+',  # Windows-style paths
        r'\[Errno\s+\d+\]',  # Error numbers
        r'SELECT\s+',  # SQL SELECT statements
        r'INSERT\s+',  # SQL INSERT statements
        r'UPDATE\s+',  # SQL UPDATE statements
        r'DELETE\s+',  # SQL DELETE statements
        r'CREATE\s+',  # SQL CREATE statements
        r'DROP\s+',  # SQL DROP statements
        r'\btable\b',  # Table references (word boundaries)
        r'\bcolumn\b',  # Column references (word boundaries)
        r'\bdatabase\b',  # Database references (word boundaries)
        r'\bschema\b',  # Schema references (word boundaries)
        r'function\s+\w+\s+',  # Function references
        r'at\s+0x[0-9a-f]+',  # Memory addresses
    ]

    @classmethod
    def sanitize(cls, error: Exception) -> str:
        """
        Sanitize an exception message by removing sensitive information.

        Args:
            error: The exception to sanitize

        Returns:
            A safe, user-friendly error message

        Examples:
            >>> try:
            ...     raise Exception("SQL error: table 'users' has no column 'foo'")
            ... except Exception as e:
            ...     ErrorSanitizer.sanitize(e)
            'An error occurred. Please try again or contact support.'
        """
        if not error:
            return "An unknown error occurred"

        error_msg = str(error)

        # Remove sensitive information
        for pattern in cls.SENSITIVE_PATTERNS:
            error_msg = re.sub(pattern, '[REDACTED]', error_msg, flags=re.IGNORECASE)

        # Check if message is too short after sanitization or contains redactions
        if len(error_msg) < 20 or '[REDACTED]' in error_msg:
            return "An error occurred. Please try again or contact support."

        return error_msg

    @classmethod
    def sanitize_with_context(
        cls, error: Exception, context: str, include_original: bool = False
    ) -> str:
        """
        Sanitize an exception with user-friendly context.

        This is the preferred method for mutations as it provides
        context while preventing information leakage.

        Args:
            error: The exception that occurred
            context: What operation was being performed (e.g., "create event")
            include_original: Whether to include original error (DEPRECATED, always False)

        Returns:
            A user-friendly error message with context

        Examples:
            >>> try:
            ...     raise Exception("SQL error: table 'users' does not exist")
            ... except Exception as e:
            ...     ErrorSanitizer.sanitize_with_context(e, "create event")
            'Failed to create event. Please try again or contact support.'
        """
        # Always log the full error for debugging
        logger.error(f"Error in {context}: {error}", exc_info=True)

        # Return generic user-friendly message
        return f"Failed to {context}. Please try again or contact support."

    @classmethod
    def is_safe(cls, message: str) -> bool:
        """
        Check if a message is safe to show to users.

        Args:
            message: The message to check

        Returns:
            True if message contains no sensitive information

        Examples:
            >>> ErrorSanitizer.is_safe("Failed to create event")
            True
            >>> ErrorSanitizer.is_safe("SQL error: table 'users' does not exist")
            False
        """
        if not message:
            return False

        message_lower = message.lower()

        # Check against sensitive patterns
        for pattern in cls.SENSITIVE_PATTERNS:
            if re.search(pattern, message, re.IGNORECASE):
                return False

        return True

    @classmethod
    def validate_error_message(cls, error_msg: str) -> str:
        """
        Validate and sanitize an error message string.

        Use this when you have an error message string instead of an Exception.

        Args:
            error_msg: The error message to validate

        Returns:
            A safe error message (sanitized if needed)

        Examples:
            >>> ErrorSanitizer.validate_error_message("SQL error: table foo")
            'An error occurred. Please try again or contact support.'
        """
        if not error_msg:
            return "An unknown error occurred"

        # Check if message is safe
        if cls.is_safe(error_msg):
            return error_msg

        # If not safe, return generic message
        return "An error occurred. Please try again or contact support."

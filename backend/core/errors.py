"""
Unified Error Handling Module

All application-specific exception classes and JSON response helpers.
This is the single source of truth for error types in the project.
"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple


class DWDGeneratorError(Exception):
    """Base exception for DWD Generator application"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(DWDGeneratorError):
    """Exception raised for validation errors"""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(message, status_code=400)


class DatabaseError(DWDGeneratorError):
    """Exception raised for database-related errors"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class HQLGenerationError(Exception):
    """
    Base exception class for HQL generation errors.

    All HQL-related exceptions should inherit from this class to allow
    for easy exception handling and error categorization.

    Attributes:
        message (str): Error message
        node_id (str, optional): ID of the node causing the error
        node_type (str, optional): Type of the node
    """

    def __init__(self, message, node_id=None, node_type=None, **kwargs):
        """
        Initialize HQLGenerationError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node causing the error
            node_type (str, optional): Type of the node
            **kwargs: Additional context information
        """
        self.message = message
        self.node_id = node_id
        self.node_type = node_type
        self.context = kwargs

        # Build full error message
        full_message = message
        if node_id:
            full_message += f" (node_id: {node_id})"
        if node_type:
            full_message += f" (node_type: {node_type})"

        super().__init__(full_message)


class EmptyFieldListError(HQLGenerationError):
    """
    Exception raised when a node's fieldList is empty.

    This occurs when a process/event node has no fields configured,
    which is required for UNION ALL and JOIN operations.

    Example:
        >>> raise EmptyFieldListError(
        ...     "节点的 fieldList 为空",
        ...     node_id="node_123",
        ...     node_type="process",
        ...     event_id=1
        ... )
    """

    def __init__(self, message, node_id=None, node_type=None, event_id=None, **kwargs):
        """
        Initialize EmptyFieldListError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node with empty fieldList
            node_type (str, optional): Type of the node
            event_id (int, optional): Event ID if applicable
            **kwargs: Additional context information
        """
        self.event_id = event_id
        super().__init__(message, node_id, node_type, event_id=event_id, **kwargs)


class MissingJoinKeyError(HQLGenerationError):
    """
    Exception raised when a JOIN condition references a field
    that doesn't exist in the node's fieldList.

    This occurs when the JOIN conditions specify a field (e.g., role_id)
    that is not present in one of the joined tables' field configurations.

    Example:
        >>> raise MissingJoinKeyError(
        ...     "JOIN条件字段 'role_id' 在节点的 fieldList 中不存在",
        ...     node_id="node_123",
        ...     missing_key="role_id",
        ...     available_fields=["ds", "level"]
        ... )
    """

    def __init__(
        self,
        message,
        node_id=None,
        node_type=None,
        missing_key=None,
        available_fields=None,
        **kwargs,
    ):
        """
        Initialize MissingJoinKeyError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node with missing field
            node_type (str, optional): Type of the node
            missing_key (str, optional): The missing field name
            available_fields (list, optional): List of available fields
            **kwargs: Additional context information
        """
        self.missing_key = missing_key
        self.available_fields = available_fields or []
        super().__init__(
            message,
            node_id,
            node_type,
            missing_key=missing_key,
            available_fields=available_fields,
            **kwargs,
        )


class InvalidNodeTypeError(HQLGenerationError):
    """
    Exception raised when a node has an invalid type for the operation.

    This occurs when a node that should be 'process' type is actually
    'union_all', 'join', 'output', or another type.

    Example:
        >>> raise InvalidNodeTypeError(
        ...     "左表节点类型必须是process",
        ...     node_id="node_123",
        ...     actual_type="union_all",
        ...     expected_type="process"
        ... )
    """

    def __init__(self, message, node_id=None, actual_type=None, expected_type=None, **kwargs):
        """
        Initialize InvalidNodeTypeError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the node with invalid type
            actual_type (str, optional): The actual node type
            expected_type (str, optional): The expected node type
            **kwargs: Additional context information
        """
        self.actual_type = actual_type
        self.expected_type = expected_type
        super().__init__(
            message, node_id, node_type=actual_type, expected_type=expected_type, **kwargs
        )


class MissingJoinConfigError(HQLGenerationError):
    """
    Exception raised when a JOIN node is missing required joinConfig.

    This occurs when a JOIN node doesn't have the necessary configuration
    to perform the join operation.

    Example:
        >>> raise MissingJoinConfigError(
        ...     "JOIN节点缺少joinConfig配置",
        ...     node_id="node_join_1"
        ... )
    """

    def __init__(self, message, node_id=None, **kwargs):
        """
        Initialize MissingJoinConfigError.

        Args:
            message (str): Error message
            node_id (str, optional): ID of the JOIN node
            **kwargs: Additional context information
        """
        super().__init__(message, node_id, node_type="join", **kwargs)


class NotFoundError(DWDGeneratorError):
    """Exception raised when a resource is not found"""

    def __init__(self, resource_type: str, resource_id: Any = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"
        else:
            message = f"{resource_type} not found"
        super().__init__(message, status_code=404)


class DuplicateError(DWDGeneratorError):
    """Exception raised when attempting to create a duplicate resource"""

    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        message = f"{resource_type} '{identifier}' already exists"
        super().__init__(message, status_code=409)


class FileProcessingError(DWDGeneratorError):
    """Exception raised for file processing errors"""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class ConfigurationError(DWDGeneratorError):
    """Exception raised for configuration errors"""

    def __init__(self, message: str):
        super().__init__(message, status_code=500)


__all__ = [
    'DWDGeneratorError',
    'ValidationError',
    'DatabaseError',
    'HQLGenerationError',
    'NotFoundError',
    'DuplicateError',
    'FileProcessingError',
    'ConfigurationError',
    'EmptyFieldListError',
    'MissingJoinKeyError',
    'InvalidNodeTypeError',
    'MissingJoinConfigError',
]

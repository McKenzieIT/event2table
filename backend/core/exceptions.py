#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom Exceptions Module
Defines application-specific exception classes
"""


class DWDGeneratorError(Exception):
    """Base exception for DWD Generator application"""

    pass


class DatabaseError(DWDGeneratorError):
    """Exception raised for database-related errors"""

    pass


class ValidationError(DWDGeneratorError):
    """Exception raised for validation errors"""

    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class NotFoundError(DWDGeneratorError):
    """Exception raised when a resource is not found"""

    def __init__(self, resource_type: str, resource_id: any = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"
        else:
            message = f"{resource_type} not found"
        super().__init__(message)


class DuplicateError(DWDGeneratorError):
    """Exception raised when attempting to create a duplicate resource"""

    def __init__(self, resource_type: str, identifier: str):
        self.resource_type = resource_type
        self.identifier = identifier
        message = f"{resource_type} '{identifier}' already exists"
        super().__init__(message)


class FileProcessingError(DWDGeneratorError):
    """Exception raised for file processing errors"""

    pass


class HQLGenerationError(DWDGeneratorError):
    """Exception raised for HQL generation errors"""

    pass


class ConfigurationError(DWDGeneratorError):
    """Exception raised for configuration errors"""

    pass

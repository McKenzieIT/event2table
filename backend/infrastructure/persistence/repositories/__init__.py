#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Layer Factory Module

Provides factory functions for creating repository instances.
This follows the Factory pattern to centralize repository instantiation.
"""

from backend.infrastructure.persistence.repositories.parameter_repository_impl import ParameterRepositoryImpl
from backend.infrastructure.persistence.repositories.common_parameter_repository_impl import CommonParameterRepositoryImpl


def get_parameter_repository():
    """
    Factory function for ParameterRepository

    Returns:
        ParameterRepositoryImpl instance

    Example:
        >>> from backend.infrastructure.persistence.repositories import get_parameter_repository
        >>> repo = get_parameter_repository()
        >>> params = repo.find_by_game(90000001)
    """
    return ParameterRepositoryImpl()


def get_common_parameter_repository():
    """
    Factory function for CommonParameterRepository

    Returns:
        CommonParameterRepositoryImpl instance

    Example:
        >>> from backend.infrastructure.persistence.repositories import get_common_parameter_repository
        >>> repo = get_common_parameter_repository()
        >>> common_params = repo.find_by_game(90000001)
    """
    return CommonParameterRepositoryImpl()


__all__ = [
    'get_parameter_repository',
    'get_common_parameter_repository',
    'ParameterRepositoryImpl',
    'CommonParameterRepositoryImpl'
]

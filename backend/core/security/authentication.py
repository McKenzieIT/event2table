#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GraphQL Authentication and Authorization Decorators

Provides decorators for enforcing authentication and authorization
in GraphQL mutation resolvers.

Usage:
    from backend.core.security.authentication import authenticated, require_permission

    class CreateEvent(graphene.Mutation):
        @authenticated
        @require_permission('event:write')
        def mutate(self, info, ...):
            # mutation logic
"""

import logging
import os
from functools import wraps

logger = logging.getLogger(__name__)


def is_development_mode() -> bool:
    """
    Check if the application is running in development mode.

    Returns:
        True if FLASK_ENV is 'development' or not set (defaults to development)
        False if FLASK_ENV is 'production' or any other value
    """
    flask_env = os.environ.get('FLASK_ENV', 'development')
    return flask_env.lower() == 'development'


def is_production_mode() -> bool:
    """
    Check if the application is running in production mode.

    Returns:
        True if FLASK_ENV is 'production'
        False otherwise
    """
    flask_env = os.environ.get('FLASK_ENV', 'development')
    return flask_env.lower() == 'production'


def authenticated(func):
    """
    Authentication decorator - verifies user is logged in

    This decorator checks that the GraphQL context contains a valid user.
    If no user is present, it raises an Exception with an authentication error message.

    Args:
        func: The mutate method to wrap

    Returns:
        Wrapped function that checks authentication before execution

    Example:
        @authenticated
        def mutate(self, info, ...):
            # Only executes if info.context.user exists
    """

    @wraps(func)
    def wrapper(root, info, *args, **kwargs):
        # Check if context exists
        if not hasattr(info, 'context'):
            logger.warning("Authentication failed: No context in GraphQL info")
            raise Exception("Authentication required: No context found")

        # Check if user exists in context
        if info.context.user is None:
            logger.warning("Authentication failed: No user in context")
            raise Exception("Authentication required: Please log in")

        # User is authenticated, proceed with mutation
        return func(root, info, *args, **kwargs)

    return wrapper


def require_permission(permission: str):
    """
    Authorization decorator - verifies user has specific permission

    This decorator checks that the authenticated user has the required permission.
    Permissions are stored as a list in user.permissions.

    Args:
        permission: The permission string required (e.g., 'event:write')

    Returns:
        Decorator function that wraps the mutate method

    Example:
        @require_permission('event:write')
        def mutate(self, info, ...):
            # Only executes if user has 'event:write' permission
    """

    def decorator(func):
        @wraps(func)
        def wrapper(root, info, *args, **kwargs):
            # First check authentication
            if not hasattr(info, 'context') or info.context.user is None:
                logger.warning("Authorization failed: No authenticated user")
                raise Exception("Authentication required: Please log in")

            user = info.context.user

            # Check if user has permissions attribute
            if not hasattr(user, 'permissions'):
                logger.warning(f"Authorization failed: User {user} has no permissions attribute")
                raise Exception(f"Authorization failed: Permission '{permission}' required")

            # Check if user has the required permission
            if permission not in user.permissions:
                logger.warning(
                    f"Authorization failed: User {user} missing permission '{permission}'. "
                    f"User permissions: {user.permissions}"
                )
                raise Exception(f"Authorization failed: Missing '{permission}' permission")

            # User is authorized, proceed with mutation
            return func(root, info, *args, **kwargs)

        return wrapper

    return decorator


def check_auth_context(info):
    """
    Helper function to manually check authentication context

    Use this inside mutation bodies when you need more control than decorators provide.

    Args:
        info: GraphQL info object

    Raises:
        Exception: If user is not authenticated

    Example:
        def mutate(self, info, ...):
            check_auth_context(info)  # Will raise if not authenticated
            # Continue with mutation logic
    """
    if not hasattr(info, 'context'):
        raise Exception("Authentication required: No context found")

    if info.context.user is None:
        raise Exception("Authentication required: Please log in")


def check_user_permission(info, permission: str):
    """
    Helper function to manually check user permission

    Use this inside mutation bodies for more complex authorization logic.

    Args:
        info: GraphQL info object
        permission: Permission string to check

    Raises:
        Exception: If user is not authenticated or lacks permission

    Example:
        def mutate(self, info, ...):
            check_auth_context(info)
            check_user_permission(info, 'event:write')
            # Continue with mutation logic
    """
    # First check authentication
    check_auth_context(info)

    user = info.context.user

    # Check if user has permissions attribute
    if not hasattr(user, 'permissions'):
        raise Exception(f"Authorization failed: Permission '{permission}' required")

    # Check if user has the required permission
    if permission not in user.permissions:
        raise Exception(f"Authorization failed: Missing '{permission}' permission")

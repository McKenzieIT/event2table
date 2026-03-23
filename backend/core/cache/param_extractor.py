#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache Parameter Extractor

Intelligently extracts function parameters for building cache keys:
1. Skips self parameter (Repository instance)
2. Converts unhashable parameters to hashable format
"""

import inspect
import json
import logging
from typing import Callable, Tuple, Dict, Any

logger = logging.getLogger(__name__)


def _extract_cache_params(func: Callable, args: tuple, kwargs: dict) -> Tuple[tuple, dict]:
    """
    Intelligently extract cache parameters

    Processing rules:
    1. Detect if first parameter is self (Repository instance)
    2. If self, skip it; if not, keep it
    3. Convert unhashable parameters to hashable format

    Args:
        func: The decorated function
        args: Positional arguments tuple
        kwargs: Keyword arguments dictionary

    Returns:
        (cleaned_args, cleaned_kwargs) tuple

    Example:
        >>> class Repo:
        ...     def method(self, page=1):
        ...         return page
        >>> repo = Repo()
        >>> _extract_cache_params(repo.method, (repo,), {'page': 1})
        ((), {'page': 1})  # self is skipped
    """
    # Get function signature to check if this is a bound method
    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    # 1. Handle self parameter
    # For bound methods (repo.method), Python already removes 'self' from signature
    # But the instance is still in args[0], so we need to skip it
    # We detect this by checking if the function is a method and has args
    if hasattr(func, '__self__'):
        # This is a bound method, skip the first arg (the instance)
        cleaned_args = args[1:] if len(args) > 1 else ()
        logger.debug(
            f"Skip bound method instance: original args={len(args)}, cleaned={len(cleaned_args)}"
        )
    elif params and params[0].name == 'self':
        # This is an unbound method, skip the first arg (self)
        cleaned_args = args[1:] if len(args) > 1 else ()
        logger.debug(f"Skip self parameter: original args={len(args)}, cleaned={len(cleaned_args)}")
    else:
        # This is a regular function, keep all args
        cleaned_args = args

    # 2. Handle unhashable kwargs
    cleaned_kwargs = {}
    for k, v in kwargs.items():
        try:
            # Try hash detection
            hash(v)
            cleaned_kwargs[k] = v
        except TypeError:
            # Unhashable (like dict, list), convert to JSON string
            if isinstance(v, dict):
                cleaned_kwargs[k] = json.dumps(v, sort_keys=True)
                logger.debug(f"dict parameter serialized: {k} -> {cleaned_kwargs[k][:50]}...")
            elif isinstance(v, list):
                cleaned_kwargs[k] = json.dumps(v)
                logger.debug(f"list parameter serialized: {k} -> {cleaned_kwargs[k][:50]}...")
            else:
                # Custom object, use string representation
                cleaned_kwargs[k] = str(v)
                logger.debug(f"object parameter serialized: {k} -> {type(v).__name__}")

    return cleaned_args, cleaned_kwargs

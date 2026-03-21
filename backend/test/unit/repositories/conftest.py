#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration for repository tests

Provides cache cleanup fixture to ensure test isolation.
"""

import pytest
from backend.core.cache.decorators import _cache


@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    """
    Clear cache before each test to ensure test isolation.

    This is critical for cache tests to prevent state pollution
    between tests. Without this, tests can pass individually but
    fail when run together.
    """
    # Clear the global cache instance used by decorators
    _cache.l1_cache.clear()
    _cache.l1_timestamps.clear()

    yield

    # Clear again after test
    _cache.l1_cache.clear()
    _cache.l1_timestamps.clear()

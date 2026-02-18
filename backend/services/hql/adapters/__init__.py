"""
HQL Adapters Module

This module provides adapter and transformer functions for converting between
different API versions and data formats.

Available adapters:
- v2_to_v1_transformer: Transform V2 HQL responses to V1 format
- v1_to_v2_transformer: Transform V1 requests to V2 format
- project_adapter: Adapt project-specific data formats
"""

from .v2_to_v1_transformer import (
    TransformationError,
    extract_hql,
    transform_batch_responses,
    transform_debug_info,
    transform_hql_response,
    transform_performance_data,
    validate_v2_response,
    v2_to_v1,
)

__all__ = [
    "TransformationError",
    "extract_hql",
    "transform_batch_responses",
    "transform_debug_info",
    "transform_hql_response",
    "transform_performance_data",
    "validate_v2_response",
    "v2_to_v1",
]

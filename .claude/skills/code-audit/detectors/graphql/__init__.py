# GraphQL Detector Package
"""
GraphQL ecosystem detectors for Event2Table codebase.

This package contains detectors for:
- GraphQL type synchronization (frontend enums vs backend schema)
- Pydantic model completeness (Service layer field access)
"""

from .graphql_type_sync_check import GraphQLTypeSyncDetector
from .pydantic_completeness_check import PydanticCompletenessDetector

__all__ = [
    'GraphQLTypeSyncDetector',
    'PydanticCompletenessDetector',
]

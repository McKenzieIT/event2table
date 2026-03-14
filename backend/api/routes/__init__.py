"""
API Routes Package

This package contains modularized API route definitions.
Each module is responsible for a specific domain:

- events: Event management
- parameters: Parameter management
- categories: Category management
- templates: Template management
- nodes: Canvas node management
- flows: Flow management
- hql_generation: HQL generation and validation
- hql_preview_v2: ✅ ACTIVE HQL Preview V2 API (used by frontend, NOT deprecated)
- field_builder: Field builder configurations
- join_configs: Join configuration management
- health: Health check endpoint for E2E testing and monitoring
"""

# Import all route modules to register their routes with the blueprint
from . import cache  # Cache management endpoints
from . import graphql  # GraphQL API
from . import health  # Health check endpoint (2026-03-01)
from . import legacy_api  # Legacy/compatibility API endpoints
from . import monitoring  # Monitoring endpoints
from . import v1_adapter  # V1-to-V2 adapter endpoints (2026-02-17)
from . import (
    categories,
    event_parameters,
    events,
    field_builder,
    flows,
    games,
    hql_generation,
    hql_preview_v2,
    join_configs,
    parameters,
)

__all__ = [
    "cache",
    "games",
    "parameters",
    "events",
    "categories",
    "event_parameters",
    "flows",
    "graphql",
    "hql_generation",
    "hql_preview_v2",
    "field_builder",
    "health",
    "join_configs",
    "legacy_api",
    "monitoring",
    "v1_adapter",
]

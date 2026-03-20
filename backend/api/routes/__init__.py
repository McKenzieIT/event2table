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
- bulk_operations: Bulk operations for events, games, and parameters (migrated 2026-03-19)
- cache_monitor: Cache monitoring and statistics (migrated 2026-03-19)
- canvas: Canvas pages and API (migrated 2026-03-19)
- event_node_builder: Event node builder API (migrated 2026-03-19)
- common_params: Common parameters management (migrated 2026-03-19)
- parameter_aliases: Parameter aliases management (migrated 2026-03-19)
"""

# Import all route modules to register their routes with the blueprint
from . import cache  # Cache management endpoints
from . import graphql  # GraphQL API
from . import health  # Health check endpoint (2026-03-01)
from . import monitoring  # Monitoring endpoints
from . import v1_adapter  # V1-to-V2 adapter endpoints (2026-02-17)
from . import (
    bulk_operations,  # Migrated from services/bulk_operations (2026-03-19)
    cache_monitor,  # Migrated from services/cache_monitor (2026-03-19)
    canvas,  # Migrated from services/canvas (2026-03-19)
    categories,
    common_params,  # Migrated from services/parameters (2026-03-19)
    event_node_builder,  # Migrated from services/event_node_builder (2026-03-19)
    event_parameters,
    events,
    field_builder,
    flows,
    games,
    hql_generation,
    hql_preview,  # ✅ ACTIVE HQL Preview V2 API (renamed from hql_preview_v2)
    join_configs,
    parameter_aliases,  # Migrated from services/parameters (2026-03-19)
    parameters,
)

__all__ = [
    "bulk_operations",
    "cache",
    "cache_monitor",
    "canvas",
    "categories",
    "common_params",
    "event_node_builder",
    "event_parameters",
    "events",
    "field_builder",
    "flows",
    "games",
    "graphql",
    "hql_generation",
    "hql_preview",  # ✅ ACTIVE HQL Preview V2 API (renamed from hql_preview_v2)
    "health",
    "join_configs",
    "monitoring",
    "parameter_aliases",
    "parameters",
    "v1_adapter",
]

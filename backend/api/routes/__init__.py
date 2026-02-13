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
- hql_preview_v2: New HQL preview V2 API (2026-02-06)
- field_builder: Field builder configurations
- join_configs: Join configuration management
"""

# Import all route modules to register their routes with the blueprint
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
    legacy_api,  # Legacy/compatibility API endpoints
    nodes,
    parameters,
    templates,
)

__all__ = [
    "games",
    "parameters",
    "events",
    "categories",
    "event_parameters",
    "templates",
    "nodes",
    "flows",
    "hql_generation",
    "hql_preview_v2",
    "field_builder",
    "join_configs",
    "legacy_api",
]

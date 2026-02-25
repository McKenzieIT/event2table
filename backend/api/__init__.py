"""
DWD Generator API Module

This module provides a modular structure for the API routes,
splitting the monolithic api.py into smaller, maintainable modules.

Blueprint Structure:
- games: Game management endpoints
- events: Event management endpoints
- parameters: Parameter management endpoints
- categories: Category management endpoints
- templates: Template management endpoints
- nodes: Canvas node management endpoints
- flows: Flow management endpoints
- hql_generation: HQL generation endpoints
- field_builder: Field builder endpoints
- join_configs: Join configuration endpoints
- batch_operations: Batch operation endpoints
- analytics: Analytics and recommendation endpoints
"""

from flask import Blueprint

# Create the main API blueprint
api_bp = Blueprint("api", __name__)

# Import all route modules to register their routes
# These imports must come after creating the blueprint to avoid circular imports
from .routes import (
      graphql,  # GraphQL API
    categories,
    dashboard,
    event_parameters,
    events,
    field_builder,
    flows,
    games,
    hql_generation,
    join_configs,
    nodes,
    parameters,  # 添加 parameters 模块
    templates,
)

# TODO: Add more modules as they are created

__all__ = ["api_bp"]

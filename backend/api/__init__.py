"""
DWD Generator API Module

This module provides a modular structure for the API routes,
splitting the monolithic api.py into smaller, maintainable modules.

Blueprint Structure:
- graphql: GraphQL API (primary API)
- games: Game management endpoints
- events: Event management endpoints
- parameters: Parameter management endpoints
- categories: Category management endpoints
- flows: Flow management endpoints
- hql_generation: HQL generation endpoints
- field_builder: Field builder endpoints
- join_configs: Join configuration endpoints
- batch_operations: Batch operation endpoints
- cache: Cache management endpoints

Archived Modules (moved to archive/backend/api/routes/):
- dashboard: Replaced by GraphQL (dashboardStats query) - 2026-03-01
- templates: Replaced by GraphQL (templates query) - 2026-03-01
- nodes: Replaced by GraphQL (nodes query) - 2026-03-01
"""

from flask import Blueprint

# Create the main API blueprint
api_bp = Blueprint("api", __name__)

# Import all route modules to register their routes
# These imports must come after creating the blueprint to avoid circular imports
from .routes import cache  # Cache management endpoints
from .routes import graphql  # GraphQL API
from .routes import health  # Health check endpoint
from .routes import parameters  # 添加 parameters 模块
from .routes import (
    categories,
    event_parameters,
    events,
    field_builder,
    flows,
    games,
    hql_generation,
    join_configs,
)

# TODO: Add more modules as they are created

__all__ = ["api_bp"]

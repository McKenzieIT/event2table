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
# noqa: F401 - These imports register routes via side effects
from .routes import cache  # Cache management endpoints
from .routes import categories  # noqa: F401
from .routes import event_parameters  # noqa: F401
from .routes import events  # noqa: F401
from .routes import field_builder  # noqa: F401
from .routes import flows  # noqa: F401
from .routes import games  # noqa: F401
from .routes import graphql  # GraphQL API
from .routes import health  # Health check endpoint
from .routes import hql_generation  # noqa: F401
from .routes import join_configs  # noqa: F401
from .routes import parameters  # 添加 parameters 模块

# TODO: Add more modules as they are created

__all__ = ["api_bp"]

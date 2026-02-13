"""
Bulk Operations Service Module

This module provides bulk operation endpoints for managing games, events, and parameters
in batch. These endpoints improve efficiency when performing operations on multiple items.

Available endpoints:
- POST /bulk-delete-events - Delete multiple events at once
- POST /bulk-update-category - Update category for multiple events
- POST /bulk-toggle-common-params - Toggle common params inclusion for events
- POST /bulk-export-events - Export multiple events configuration
- POST /bulk-validate-parameters - Validate parameters for multiple events
"""

from flask import Blueprint

# Create the bulk operations blueprint
bulk_bp = Blueprint('bulk_operations', __name__)

# Import routes to register them with the blueprint
from . import bulk_routes

__all__ = ['bulk_bp']

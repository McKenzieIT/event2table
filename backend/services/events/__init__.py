"""
Events Service Module

Provides event management endpoints and blueprints.
"""

from .events import events_bp

# event_nodes_bp removed 2026-03-01 (replaced by GraphQL + event_node_builder_bp)
# See: archive/backend/services/events/event_nodes.py

__all__ = ["events_bp"]

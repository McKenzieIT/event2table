"""
Node and Flow Queries

Implements GraphQL query resolvers for Node and Flow entities.
"""

import graphene
from graphene import Field, List, Int, String
from typing import List as TypingList, Dict, Any
import logging

logger = logging.getLogger(__name__)


class NodeQueries:
    """Node-related GraphQL queries"""

    @staticmethod
    def resolve_node(root, info, id: int):
        """Resolve a single node by ID."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.node_type import NodeType

            node = fetch_one_as_dict(
                "SELECT * FROM canvas_nodes WHERE id = ?",
                (id,)
            )

            return NodeType.from_dict(node) if node else None

        except Exception as e:
            logger.error(f"Error resolving node: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_nodes(root, info, game_gid: int = None, node_type: str = None,
                      limit: int = 50, offset: int = 0):
        """Resolve list of nodes with optional filtering."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.node_type import NodeType

            query = "SELECT * FROM canvas_nodes WHERE is_active = 1"
            params = []

            if game_gid:
                query += " AND game_gid = ?"
                params.append(game_gid)

            if node_type:
                query += " AND node_type = ?"
                params.append(node_type)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            nodes = fetch_all_as_dict(query, tuple(params))

            return [NodeType.from_dict(n) for n in nodes]

        except Exception as e:
            logger.error(f"Error resolving nodes: {e}", exc_info=True)
            return []


class FlowQueries:
    """Flow-related GraphQL queries"""

    @staticmethod
    def resolve_flow(root, info, id: int):
        """Resolve a single flow by ID."""
        try:
            from backend.core.utils import fetch_one_as_dict
            from backend.gql_api.types.node_type import FlowType

            flow = fetch_one_as_dict(
                "SELECT * FROM canvas_flows WHERE id = ?",
                (id,)
            )

            return FlowType.from_dict(flow) if flow else None

        except Exception as e:
            logger.error(f"Error resolving flow: {e}", exc_info=True)
            return None

    @staticmethod
    def resolve_flows(root, info, game_gid: int = None, flow_type: str = None,
                      limit: int = 50, offset: int = 0):
        """Resolve list of flows with optional filtering."""
        try:
            from backend.core.utils import fetch_all_as_dict
            from backend.gql_api.types.node_type import FlowType

            query = "SELECT * FROM canvas_flows WHERE is_active = 1"
            params = []

            if game_gid:
                query += " AND game_gid = ?"
                params.append(game_gid)

            if flow_type:
                query += " AND flow_type = ?"
                params.append(flow_type)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            flows = fetch_all_as_dict(query, tuple(params))

            return [FlowType.from_dict(f) for f in flows]

        except Exception as e:
            logger.error(f"Error resolving flows: {e}", exc_info=True)
            return []

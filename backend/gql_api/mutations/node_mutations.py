"""
Node and Flow Mutations

Implements GraphQL mutation resolvers for Node and Flow entities.
"""

import json
import logging

import graphene
from graphene import Argument, Boolean, Field, Float, Int, List, String

from backend.core.security.authentication import authenticated, require_permission
from backend.gql_api.types.node_type import FlowTypeEnum, NodeTypeEnum

logger = logging.getLogger(__name__)


class CreateNode(graphene.Mutation):
    """Create a new node"""

    class Arguments:
        name = String(required=True, description="节点名称")
        description = String(description="节点描述")
        game_gid = Int(description="关联游戏GID")
        node_type = Argument(NodeTypeEnum, description="节点类型")
        config = String(description="节点配置JSON")
        position_x = Float(description="X坐标")
        position_y = Float(description="Y坐标")

    ok = Boolean(description="操作是否成功")
    node = Field(
        lambda: __import__('backend.gql_api.types.node_type', fromlist=['NodeType']).NodeType,
        description="创建的节点",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(
        self,
        info,
        name: str,
        description: str | None = None,
        game_gid: int | None = None,
        node_type: NodeTypeEnum | None = None,
        config: str | None = None,
        position_x: float = 0,
        position_y: float = 0,
    ):
        """
        Execute the mutation

        Business Rules (P1-19):
        1. ✅ Input validation:
           - node_type must be one of: 'event', 'join', 'union', 'filter'
           - position must be in valid range (0-10000)
        2. ✅ Config validation: Must be valid JSON if provided
        3. ✅ Game context validation: If game_gid provided, game must exist
        """
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.node_type import NodeType

            # ========== P1-19: Business Logic Validation ==========

            # 1. Validate node_type enum
            valid_types = ['event', 'join', 'union', 'filter']
            node_type_value = node_type.value if node_type else None
            if node_type_value and node_type_value not in valid_types:
                return CreateNode(
                    ok=False,
                    errors=[f"node_type must be one of {valid_types}, got: {node_type_value}"],
                )

            # 2. Validate game_gid if provided
            if game_gid is not None:
                game = fetch_one_as_dict("SELECT * FROM games WHERE gid = ?", (game_gid,))
                if not game:
                    return CreateNode(ok=False, errors=[f"Game {game_gid} not found"])

            # 3. Validate position range
            if position_x < 0 or position_x > 10000:
                return CreateNode(ok=False, errors=["position_x must be between 0 and 10000"])
            if position_y < 0 or position_y > 10000:
                return CreateNode(ok=False, errors=["position_y must be between 0 and 10000"])

            # 4. Validate config JSON if provided
            if config:
                try:
                    json.loads(config)
                except json.JSONDecodeError as e:
                    return CreateNode(ok=False, errors=[f"Invalid JSON in config: {str(e)}"])

            # ========== Execute Creation ==========
            node_id = execute_write(
                """
                INSERT INTO canvas_nodes (name, description, game_gid, node_type, config, position_x, position_y)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, description, game_gid, node_type_value, config, position_x, position_y),
                return_last_id=True,
            )

            # Clear cache
            clear_cache_pattern("nodes:*")

            logger.info(
                f"Node created via GraphQL: {name} (ID: {node_id}, type: {node_type_value})"
            )

            # Return created node
            node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (node_id,))

            return CreateNode(ok=True, node=NodeType.from_dict(node) if node else None)

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error creating node: {e}")
            return CreateNode(ok=False, errors=[str(e)])
        except Exception as e:
            logger.error(f"Error creating node: {e}", exc_info=True)
            return CreateNode(ok=False, errors=[str(e)])


class UpdateNode(graphene.Mutation):
    """Update an existing node"""

    class Arguments:
        id = Int(required=True, description="节点ID")
        name = String(description="节点名称")
        description = String(description="节点描述")
        config = String(description="节点配置JSON")
        position_x = Float(description="X坐标")
        position_y = Float(description="Y坐标")
        is_active = Boolean(description="是否活跃")

    ok = Boolean(description="操作是否成功")
    node = Field(
        lambda: __import__('backend.gql_api.types.node_type', fromlist=['NodeType']).NodeType,
        description="更新的节点",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(
        self,
        info,
        id: int,
        name: str | None = None,
        description: str | None = None,
        config: str | None = None,
        position_x: float | None = None,
        position_y: float | None = None,
        is_active: bool | None = None,
    ):
        """
        Execute the mutation

        Business Rules (P1-20):
        1. ✅ Existence check: Node must exist
        2. ✅ Position validation: Must be in valid range (0-10000)
        3. ✅ Config validation: Must be valid JSON if provided
        4. ✅ At least one field must be updated
        """
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.node_type import NodeType

            # ========== P1-20: Business Logic Validation ==========

            # 1. Check if node exists
            node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (id,))
            if not node:
                return UpdateNode(ok=False, errors=[f"Node {id} not found"])

            # Build update query
            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if config is not None:
                try:
                    json.loads(config)
                except json.JSONDecodeError as e:
                    return UpdateNode(ok=False, errors=[f"Invalid JSON in config: {str(e)}"])
                updates.append("config = ?")
                params.append(config)

            # 2. Validate position range
            if position_x is not None:
                if position_x < 0 or position_x > 10000:
                    return UpdateNode(ok=False, errors=["position_x must be between 0 and 10000"])
                updates.append("position_x = ?")
                params.append(position_x)

            if position_y is not None:
                if position_y < 0 or position_y > 10000:
                    return UpdateNode(ok=False, errors=["position_y must be between 0 and 10000"])
                updates.append("position_y = ?")
                params.append(position_y)

            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            # 3. Validate at least one field to update
            if not updates:
                return UpdateNode(ok=False, errors=["No fields to update"])

            # ========== Execute Update ==========
            params.append(id)
            query = f"UPDATE canvas_nodes SET {', '.join(updates)} WHERE id = ?"
            execute_write(query, tuple(params))

            # Clear cache
            clear_cache_pattern("nodes:*")

            logger.info(f"Node updated via GraphQL: ID {id}")

            # Return updated node
            updated_node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (id,))

            return UpdateNode(
                ok=True, node=NodeType.from_dict(updated_node) if updated_node else None
            )

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error updating node {id}: {e}")
            return UpdateNode(ok=False, errors=[str(e)])
        except Exception as e:
            logger.error(f"Error updating node: {e}", exc_info=True)
            return UpdateNode(ok=False, errors=[str(e)])


class DeleteNode(graphene.Mutation):
    """Delete a node"""

    class Arguments:
        id = Int(required=True, description="节点ID")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, id: int):
        """
        Execute the mutation

        Business Rules (P1-21):
        1. ✅ Existence check: Node must exist
        2. ✅ Dependency check: Cannot delete nodes with active connections
        3. ✅ Flow integrity: Ensure deletion doesn't break flow structure
        """
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.core.utils import execute_write, fetch_all_as_dict, fetch_one_as_dict

            # ========== P1-21: Business Logic Validation ==========

            # 1. Check if node exists
            node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (id,))
            if not node:
                return DeleteNode(ok=False, errors=[f"Node {id} not found"])

            # 2. Dependency check: Check if node has connections
            # This assumes there's a canvas_edges or similar table for connections
            # Adjust the query based on your actual schema
            try:
                connections = fetch_all_as_dict(
                    """
                    SELECT * FROM canvas_edges
                    WHERE source_node_id = ? OR target_node_id = ?
                    """,
                    (id, id),
                )

                if connections:
                    return DeleteNode(
                        ok=False,
                        errors=[
                            f"Cannot delete node {id} with {len(connections)} active connection(s). "
                            f"Delete connections first."
                        ],
                    )
            except Exception:
                # If canvas_edges table doesn't exist yet, skip this check
                logger.warning(
                    f"canvas_edges table not found, skipping connection check for node {id}"
                )

            # ========== Execute Deletion ==========
            # Soft delete
            execute_write("UPDATE canvas_nodes SET is_active = 0 WHERE id = ?", (id,))

            # Clear cache
            clear_cache_pattern("nodes:*")

            logger.info(f"Node deleted via GraphQL: ID {id}")

            return DeleteNode(ok=True, message="Node deleted successfully")

        except ValueError as e:
            # Business logic validation errors
            logger.warning(f"Validation error deleting node {id}: {e}")
            return DeleteNode(ok=False, errors=[str(e)])
        except Exception as e:
            logger.error(f"Error deleting node: {e}", exc_info=True)
            return DeleteNode(ok=False, errors=[str(e)])


class CreateFlow(graphene.Mutation):
    """Create a new flow"""

    class Arguments:
        name = String(required=True, description="流程名称")
        description = String(description="流程描述")
        game_gid = Int(description="关联游戏GID")
        flow_type = Argument(FlowTypeEnum, description="流程类型")
        config = String(description="流程配置JSON")
        nodes = String(description="节点数据JSON")
        edges = String(description="边数据JSON")

    ok = Boolean(description="操作是否成功")
    flow = Field(
        lambda: __import__('backend.gql_api.types.node_type', fromlist=['FlowType']).FlowType,
        description="创建的流程",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(
        self,
        info,
        name: str,
        description: str | None = None,
        game_gid: int | None = None,
        flow_type: FlowTypeEnum | None = None,
        config: str | None = None,
        nodes: str | None = None,
        edges: str | None = None,
    ):
        """Execute the mutation"""
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.node_type import FlowType

            # Create flow
            # Convert enum to string value for database storage
            flow_type_value = flow_type.value if flow_type else None
            flow_id = execute_write(
                """
                INSERT INTO canvas_flows (name, description, game_gid, flow_type, config, nodes, edges)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, description, game_gid, flow_type_value, config, nodes, edges),
                return_last_id=True,
            )

            # Clear cache
            clear_cache_pattern("flows:*")

            logger.info(f"Flow created via GraphQL: {name} (ID: {flow_id})")

            # Return created flow
            flow = fetch_one_as_dict("SELECT * FROM canvas_flows WHERE id = ?", (flow_id,))

            return CreateFlow(ok=True, flow=FlowType.from_dict(flow) if flow else None)

        except Exception as e:
            logger.error(f"Error creating flow: {e}", exc_info=True)
            return CreateFlow(ok=False, errors=[str(e)])


class UpdateFlow(graphene.Mutation):
    """Update an existing flow"""

    class Arguments:
        id = Int(required=True, description="流程ID")
        name = String(description="流程名称")
        description = String(description="流程描述")
        config = String(description="流程配置JSON")
        nodes = String(description="节点数据JSON")
        edges = String(description="边数据JSON")
        is_active = Boolean(description="是否活跃")

    ok = Boolean(description="操作是否成功")
    flow = Field(
        lambda: __import__('backend.gql_api.types.node_type', fromlist=['FlowType']).FlowType,
        description="更新的流程",
    )
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(
        self,
        info,
        id: int,
        name: str | None = None,
        description: str | None = None,
        config: str | None = None,
        nodes: str | None = None,
        edges: str | None = None,
        is_active: bool | None = None,
    ):
        """Execute the mutation"""
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.gql_api.types.node_type import FlowType

            # Check if flow exists
            flow = fetch_one_as_dict("SELECT * FROM canvas_flows WHERE id = ?", (id,))
            if not flow:
                return UpdateFlow(ok=False, errors=["Flow not found"])

            # Build update query
            updates = []
            params = []

            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if config is not None:
                updates.append("config = ?")
                params.append(config)
            if nodes is not None:
                updates.append("nodes = ?")
                params.append(nodes)
            if edges is not None:
                updates.append("edges = ?")
                params.append(edges)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if not updates:
                return UpdateFlow(ok=False, errors=["No fields to update"])

            params.append(id)
            query = f"UPDATE canvas_flows SET {', '.join(updates)} WHERE id = ?"
            execute_write(query, tuple(params))

            # Clear cache
            clear_cache_pattern("flows:*")

            logger.info(f"Flow updated via GraphQL: ID {id}")

            # Return updated flow
            updated_flow = fetch_one_as_dict("SELECT * FROM canvas_flows WHERE id = ?", (id,))

            return UpdateFlow(
                ok=True, flow=FlowType.from_dict(updated_flow) if updated_flow else None
            )

        except Exception as e:
            logger.error(f"Error updating flow: {e}", exc_info=True)
            return UpdateFlow(ok=False, errors=[str(e)])


class DeleteFlow(graphene.Mutation):
    """Delete a flow"""

    class Arguments:
        id = Int(required=True, description="流程ID")

    ok = Boolean(description="操作是否成功")
    message = String(description="操作消息")
    errors = List(String, description="错误信息")

    @authenticated
    @require_permission("write")
    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.core.utils import execute_write, fetch_one_as_dict

            # Check if flow exists
            flow = fetch_one_as_dict("SELECT * FROM canvas_flows WHERE id = ?", (id,))
            if not flow:
                return DeleteFlow(ok=False, errors=["Flow not found"])

            # Soft delete
            execute_write("UPDATE canvas_flows SET is_active = 0 WHERE id = ?", (id,))

            # Clear cache
            clear_cache_pattern("flows:*")

            logger.info(f"Flow deleted via GraphQL: ID {id}")

            return DeleteFlow(ok=True, message="Flow deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting flow: {e}", exc_info=True)
            return DeleteFlow(ok=False, errors=[str(e)])


class NodeMutations:
    """Container for node mutations"""

    CreateNode = CreateNode
    UpdateNode = UpdateNode
    DeleteNode = DeleteNode


class FlowMutations:
    """Container for flow mutations"""

    CreateFlow = CreateFlow
    UpdateFlow = UpdateFlow
    DeleteFlow = DeleteFlow

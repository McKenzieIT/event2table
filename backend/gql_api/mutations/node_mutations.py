"""
Node and Flow Mutations

Implements GraphQL mutation resolvers for Node and Flow entities.
"""

import graphene
from graphene import Field, Int, String, Boolean, List, Float
import logging
import json

logger = logging.getLogger(__name__)


class CreateNode(graphene.Mutation):
    """Create a new node"""

    class Arguments:
        name = String(required=True, description="节点名称")
        description = String(description="节点描述")
        game_gid = Int(description="关联游戏GID")
        node_type = String(description="节点类型")
        config = String(description="节点配置JSON")
        position_x = Float(description="X坐标")
        position_y = Float(description="Y坐标")

    ok = Boolean(description="操作是否成功")
    node = Field(lambda: __import__('backend.gql_api.types.node_type', fromlist=['NodeType']).NodeType, description="创建的节点")
    errors = List(String, description="错误信息")

    def mutate(self, info, name: str, description: str = None, game_gid: int = None,
               node_type: str = None, config: str = None, position_x: float = 0, position_y: float = 0):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.node_type import NodeType

            # Validate config JSON if provided
            if config:
                try:
                    json.loads(config)
                except json.JSONDecodeError:
                    return CreateNode(ok=False, errors=["Invalid JSON in config"])

            # Create node
            node_id = execute_write(
                """
                INSERT INTO canvas_nodes (name, description, game_gid, node_type, config, position_x, position_y)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, description, game_gid, node_type, config, position_x, position_y),
                return_last_id=True
            )

            # Clear cache
            clear_cache_pattern("nodes:*")

            logger.info(f"Node created via GraphQL: {name} (ID: {node_id})")

            # Return created node
            node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (node_id,))

            return CreateNode(ok=True, node=NodeType.from_dict(node) if node else None)

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
    node = Field(lambda: __import__('backend.gql_api.types.node_type', fromlist=['NodeType']).NodeType, description="更新的节点")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, name: str = None, description: str = None,
               config: str = None, position_x: float = None, position_y: float = None,
               is_active: bool = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.node_type import NodeType

            # Check if node exists
            node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (id,))
            if not node:
                return UpdateNode(ok=False, errors=["Node not found"])

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
                except json.JSONDecodeError:
                    return UpdateNode(ok=False, errors=["Invalid JSON in config"])
                updates.append("config = ?")
                params.append(config)
            if position_x is not None:
                updates.append("position_x = ?")
                params.append(position_x)
            if position_y is not None:
                updates.append("position_y = ?")
                params.append(position_y)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(1 if is_active else 0)

            if not updates:
                return UpdateNode(ok=False, errors=["No fields to update"])

            params.append(id)
            query = f"UPDATE canvas_nodes SET {', '.join(updates)} WHERE id = ?"
            execute_write(query, tuple(params))

            # Clear cache
            clear_cache_pattern("nodes:*")

            logger.info(f"Node updated via GraphQL: ID {id}")

            # Return updated node
            updated_node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (id,))

            return UpdateNode(ok=True, node=NodeType.from_dict(updated_node) if updated_node else None)

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

    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern

            # Check if node exists
            node = fetch_one_as_dict("SELECT * FROM canvas_nodes WHERE id = ?", (id,))
            if not node:
                return DeleteNode(ok=False, errors=["Node not found"])

            # Soft delete
            execute_write("UPDATE canvas_nodes SET is_active = 0 WHERE id = ?", (id,))

            # Clear cache
            clear_cache_pattern("nodes:*")

            logger.info(f"Node deleted via GraphQL: ID {id}")

            return DeleteNode(ok=True, message="Node deleted successfully")

        except Exception as e:
            logger.error(f"Error deleting node: {e}", exc_info=True)
            return DeleteNode(ok=False, errors=[str(e)])


class CreateFlow(graphene.Mutation):
    """Create a new flow"""

    class Arguments:
        name = String(required=True, description="流程名称")
        description = String(description="流程描述")
        game_gid = Int(description="关联游戏GID")
        flow_type = String(description="流程类型")
        config = String(description="流程配置JSON")
        nodes = String(description="节点数据JSON")
        edges = String(description="边数据JSON")

    ok = Boolean(description="操作是否成功")
    flow = Field(lambda: __import__('backend.gql_api.types.node_type', fromlist=['FlowType']).FlowType, description="创建的流程")
    errors = List(String, description="错误信息")

    def mutate(self, info, name: str, description: str = None, game_gid: int = None,
               flow_type: str = None, config: str = None, nodes: str = None, edges: str = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
            from backend.gql_api.types.node_type import FlowType

            # Create flow
            flow_id = execute_write(
                """
                INSERT INTO canvas_flows (name, description, game_gid, flow_type, config, nodes, edges)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (name, description, game_gid, flow_type, config, nodes, edges),
                return_last_id=True
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
    flow = Field(lambda: __import__('backend.gql_api.types.node_type', fromlist=['FlowType']).FlowType, description="更新的流程")
    errors = List(String, description="错误信息")

    def mutate(self, info, id: int, name: str = None, description: str = None,
               config: str = None, nodes: str = None, edges: str = None, is_active: bool = None):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern
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

            return UpdateFlow(ok=True, flow=FlowType.from_dict(updated_flow) if updated_flow else None)

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

    def mutate(self, info, id: int):
        """Execute the mutation"""
        try:
            from backend.core.utils import execute_write, fetch_one_as_dict
            from backend.core.cache.cache_system import clear_cache_pattern

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

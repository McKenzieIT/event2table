#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Canvas Service - Canvas业务逻辑层

提供Canvas/Flow相关的业务逻辑:
- Flow模板管理 (CRUD)
- EventNode管理 (CRUD)
- Flow图验证和生成
- HQL导出
- 缓存集成

遵循Entity架构:
- 使用Entity模型 (FlowEntity, EventNodeEntity)
- 使用Repository层 (FlowRepository, EventNodeRepository)
- 缓存装饰器集成 (@cached_service, @invalidate_cache)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.core.logging import get_logger
from backend.core.cache.decorators import cached_service, invalidate_cache
from backend.models.entities import FlowEntity, EventNodeEntity
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.repositories.event_node_repository import EventNodeRepository
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.services.canvas.node_canvas_flows import (
    validate_flow_graph,
    prepare_flow_for_generation,
    build_dependency_graph,
    detect_cycles,
    topological_sort
)

logger = get_logger(__name__)


class CanvasService:
    """
    Canvas业务服务类

    职责:
    1. Flow模板管理 (CRUD + 验证)
    2. EventNode管理 (CRUD)
    3. Flow图验证 (循环检测、拓扑排序)
    4. HQL生成准备
    5. 缓存管理 (读写分离)

    架构:
    - 继承Entity架构 (Service → Repository → Entity)
    - 缓存装饰器 (读操作缓存, 写操作失效)
    - 类型安全 (Entity模型)
    """

    def __init__(self):
        """初始化Canvas服务"""
        self.flow_repo = FlowRepository()
        self.event_node_repo = EventNodeRepository()
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()

    # ========================================================================
    # Flow Template Operations (Flow模板管理)
    # ========================================================================

    @cached_service(
        key_template="flow:{id}",
        ttl_l1=120,
        ttl_l2=600,
        key_params=['id']
    )
    def get_flow(self, flow_id: int) -> Optional[FlowEntity]:
        """
        获取Flow模板

        Args:
            flow_id: Flow ID

        Returns:
            FlowEntity, 不存在返回None

        Example:
            >>> service = CanvasService()
            >>> flow = service.get_flow(1)
            >>> print(flow.flow_name) if flow else None
        """
        return self.flow_repo.find_by_id(flow_id)

    @cached_service(
        key_template="flows:game:{game_gid}",
        ttl_l1=120,
        ttl_l2=600,
        key_params=['game_gid']
    )
    def get_flows_by_game(self, game_gid: int) -> List[FlowEntity]:
        """
        获取指定游戏的所有Flow模板

        Args:
            game_gid: 游戏GID

        Returns:
            FlowEntity列表

        Example:
            >>> service = CanvasService()
            >>> flows = service.get_flows_by_game(10000147)
            >>> print(f"Found {len(flows)} flows")
        """
        return self.flow_repo.find_by_game_gid(game_gid)

    @cached_service(
        key_template="flows:all",
        ttl_l1=60,
        ttl_l2=300
    )
    def get_all_flows(self) -> List[FlowEntity]:
        """
        获取所有激活的Flow模板

        Returns:
            FlowEntity列表
        """
        return self.flow_repo.find_all_active()

    @invalidate_cache("flows:game:{game_gid}", key_params=['game_gid'])
    @invalidate_cache("flows:all")
    def create_flow(
        self,
        game_gid: int,
        flow_name: str,
        flow_graph: Dict[str, Any],
        variables: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> FlowEntity:
        """
        创建Flow模板

        Args:
            game_gid: 游戏GID
            flow_name: Flow名称
            flow_graph: Flow图结构 (nodes, connections)
            variables: Flow变量
            description: 描述
            created_by: 创建者

        Returns:
            创建的FlowEntity

        Raises:
            ValueError: 游戏不存在或Flow图验证失败

        Example:
            >>> service = CanvasService()
            >>> flow = service.create_flow(
            ...     game_gid=10000147,
            ...     flow_name="Login Flow",
            ...     flow_graph={"nodes": [], "connections": []},
            ...     description="用户登录流程"
            ... )
            >>> print(flow.id)
        """
        # 验证游戏存在
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game not found: game_gid={game_gid}")

        # 验证Flow图结构
        validation = validate_flow_graph(flow_graph)
        if not validation['valid']:
            raise ValueError(f"Invalid flow graph: {'; '.join(validation['errors'])}")

        # 创建Flow
        flow = FlowEntity(
            game_gid=game_gid,
            flow_name=flow_name,
            flow_graph=flow_graph,
            variables=variables or {},
            description=description,
            created_by=created_by,
            is_active=True,
            version=1
        )

        flow_id = self.flow_repo.create(flow)
        logger.info(f"Created flow: id={flow_id}, name={flow_name}, game_gid={game_gid}")

        # 返回完整Flow
        return self.flow_repo.find_by_id(flow_id)

    @invalidate_cache("flow:{flow_id}", key_params=['flow_id'])
    @invalidate_cache("flows:game:{game_gid}", key_params=['game_gid'])
    @invalidate_cache("flows:all")
    def update_flow(
        self,
        flow_id: int,
        flow_name: Optional[str] = None,
        flow_graph: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        更新Flow模板

        Args:
            flow_id: Flow ID
            flow_name: Flow名称 (可选)
            flow_graph: Flow图结构 (可选)
            variables: Flow变量 (可选)
            description: 描述 (可选)
            is_active: 是否激活 (可选)

        Returns:
            是否更新成功

        Raises:
            ValueError: Flow不存在或Flow图验证失败

        Example:
            >>> service = CanvasService()
            >>> success = service.update_flow(
            ...     flow_id=1,
            ...     flow_name="Updated Flow Name",
            ...     description="Updated description"
            ... )
        """
        # 获取现有Flow
        existing_flow = self.flow_repo.find_by_id(flow_id)
        if not existing_flow:
            raise ValueError(f"Flow not found: id={flow_id}")

        # 验证Flow图结构 (如果提供)
        if flow_graph:
            validation = validate_flow_graph(flow_graph)
            if not validation['valid']:
                raise ValueError(f"Invalid flow graph: {'; '.join(validation['errors'])}")

        # 更新字段
        update_data = FlowEntity(
            flow_name=flow_name or existing_flow.flow_name,
            flow_graph=flow_graph or existing_flow.flow_graph,
            variables=variables or existing_flow.variables,
            description=description or existing_flow.description,
            is_active=is_active if is_active is not None else existing_flow.is_active
        )

        success = self.flow_repo.update(flow_id, update_data)
        if success:
            logger.info(f"Updated flow: id={flow_id}")

        return success

    @invalidate_cache("flow:{flow_id}", key_params=['flow_id'])
    @invalidate_cache("flows:game:{game_gid}", key_params=['game_gid'])
    @invalidate_cache("flows:all")
    def delete_flow(self, flow_id: int, game_gid: int) -> bool:
        """
        删除Flow模板 (软删除)

        Args:
            flow_id: Flow ID
            game_gid: 游戏GID (用于缓存失效)

        Returns:
            是否删除成功

        Example:
            >>> service = CanvasService()
            >>> success = service.delete_flow(flow_id=1, game_gid=10000147)
        """
        success = self.flow_repo.delete(flow_id)
        if success:
            logger.info(f"Deleted flow: id={flow_id}")

        return success

    def count_flows_by_game(self, game_gid: int) -> int:
        """
        统计指定游戏的Flow数量

        Args:
            game_gid: 游戏GID

        Returns:
            Flow数量
        """
        return self.flow_repo.count_by_game_gid(game_gid)

    # ========================================================================
    # Event Node Operations (EventNode管理)
    # ========================================================================

    @cached_service(
        key_template="event_node:{id}",
        ttl_l1=120,
        ttl_l2=600,
        key_params=['id']
    )
    def get_event_node(self, node_id: int) -> Optional[EventNodeEntity]:
        """
        获取EventNode

        Args:
            node_id: 节点ID

        Returns:
            EventNodeEntity, 不存在返回None
        """
        return self.event_node_repo.find_by_id(node_id)

    @cached_service(
        key_template="event_nodes:game:{game_gid}",
        ttl_l1=120,
        ttl_l2=600,
        key_params=['game_gid']
    )
    def get_event_nodes_by_game(self, game_gid: int) -> List[EventNodeEntity]:
        """
        获取指定游戏的所有EventNode

        Args:
            game_gid: 游戏GID

        Returns:
            EventNodeEntity列表
        """
        return self.event_node_repo.find_by_game_gid(game_gid)

    @cached_service(
        key_template="event_nodes:event:{event_id}",
        ttl_l1=120,
        ttl_l2=600,
        key_params=['event_id']
    )
    def get_event_nodes_by_event(self, event_id: int) -> List[EventNodeEntity]:
        """
        获取指定事件的所有EventNode

        Args:
            event_id: 事件ID

        Returns:
            EventNodeEntity列表
        """
        return self.event_node_repo.find_by_event_id(event_id)

    @invalidate_cache("event_nodes:game:{game_gid}", key_params=['game_gid'])
    @invalidate_cache("event_nodes:event:{event_id}", key_params=['event_id'])
    def create_event_node(
        self,
        game_gid: int,
        name: str,
        event_id: int,
        config_json: Dict[str, Any]
    ) -> EventNodeEntity:
        """
        创建EventNode

        Args:
            game_gid: 游戏GID
            name: 节点名称
            event_id: 事件ID
            config_json: 节点配置 (fields, mode, where等)

        Returns:
            创建的EventNodeEntity

        Raises:
            ValueError: 游戏或事件不存在

        Example:
            >>> service = CanvasService()
            >>> node = service.create_event_node(
            ...     game_gid=10000147,
            ...     name="Login Node",
            ...     event_id=1,
            ...     config_json={"fields": ["role_id"], "mode": "single"}
            ... )
            >>> print(node.id)
        """
        # 验证游戏存在
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game not found: game_gid={game_gid}")

        # 验证事件存在
        event = self.event_repo.find_by_id(event_id)
        if not event:
            raise ValueError(f"Event not found: id={event_id}")

        # 创建EventNode
        node = EventNodeEntity(
            game_gid=game_gid,
            name=name,
            event_id=event_id,
            config_json=config_json,
            is_active=True
        )

        node_id = self.event_node_repo.create(node)
        logger.info(f"Created event node: id={node_id}, name={name}, game_gid={game_gid}")

        # 返回完整Node
        return self.event_node_repo.find_by_id(node_id)

    @invalidate_cache("event_node:{node_id}", key_params=['node_id'])
    @invalidate_cache("event_nodes:game:{game_gid}", key_params=['game_gid'])
    @invalidate_cache("event_nodes:event:{event_id}", key_params=['event_id'])
    def update_event_node(
        self,
        node_id: int,
        game_gid: int,
        event_id: int,
        name: Optional[str] = None,
        config_json: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        更新EventNode

        Args:
            node_id: 节点ID
            game_gid: 游戏GID (用于缓存失效)
            event_id: 事件ID (用于缓存失效)
            name: 节点名称 (可选)
            config_json: 节点配置 (可选)
            is_active: 是否激活 (可选)

        Returns:
            是否更新成功

        Raises:
            ValueError: EventNode不存在
        """
        # 获取现有Node
        existing_node = self.event_node_repo.find_by_id(node_id)
        if not existing_node:
            raise ValueError(f"EventNode not found: id={node_id}")

        # 更新字段
        update_data = EventNodeEntity(
            name=name or existing_node.name,
            event_id=event_id,
            config_json=config_json or existing_node.config_json,
            is_active=is_active if is_active is not None else existing_node.is_active
        )

        success = self.event_node_repo.update(node_id, update_data)
        if success:
            logger.info(f"Updated event node: id={node_id}")

        return success

    @invalidate_cache("event_node:{node_id}", key_params=['node_id'])
    @invalidate_cache("event_nodes:game:{game_gid}", key_params=['game_gid'])
    @invalidate_cache("event_nodes:event:{event_id}", key_params=['event_id'])
    def delete_event_node(self, node_id: int, game_gid: int, event_id: int) -> bool:
        """
        删除EventNode (软删除)

        Args:
            node_id: 节点ID
            game_gid: 游戏GID (用于缓存失效)
            event_id: 事件ID (用于缓存失效)

        Returns:
            是否删除成功
        """
        success = self.event_node_repo.delete(node_id)
        if success:
            logger.info(f"Deleted event node: id={node_id}")

        return success

    def count_event_nodes_by_game(self, game_gid: int) -> int:
        """
        统计指定游戏的EventNode数量

        Args:
            game_gid: 游戏GID

        Returns:
            EventNode数量
        """
        return self.event_node_repo.count_by_game_gid(game_gid)

    # ========================================================================
    # Flow Validation and Generation (Flow验证和生成)
    # ========================================================================

    def validate_flow(self, flow_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证Flow图结构

        验证项:
        1. 节点存在性
        2. 输出节点存在性
        3. 循环依赖检测
        4. 拓扑排序

        Args:
            flow_graph: Flow图结构
                {
                    "nodes": [...],
                    "connections": [...]
                }

        Returns:
            验证结果
            {
                "valid": bool,
                "execution_order": list or None,
                "errors": list or None
            }

        Example:
            >>> service = CanvasService()
            >>> result = service.validate_flow({
            ...     "nodes": [{"id": "n1", "type": "output"}],
            ...     "connections": []
            ... })
            >>> print(result["valid"])
        """
        return validate_flow_graph(flow_graph)

    def prepare_flow_for_generation(self, flow_graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备Flow用于HQL生成

        Args:
            flow_graph: Flow图结构

        Returns:
            准备结果
            {
                "success": bool,
                "execution_order": list,
                "node_count": int,
                "connection_count": int,
                "error": str or None
            }

        Example:
            >>> service = CanvasService()
            >>> result = service.prepare_flow_for_generation({
            ...     "nodes": [{"id": "n1", "type": "output"}],
            ...     "connections": []
            ... })
            >>> print(result["success"])
        """
        return prepare_flow_for_generation(flow_graph)

    def build_flow_dependency_graph(
        self,
        nodes: List[Dict[str, Any]],
        connections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        构建Flow依赖图

        Args:
            nodes: 节点列表
            connections: 连接列表

        Returns:
            依赖图 {node_id: {dependencies: [], dependents: [], node: {}}}

        Example:
            >>> service = CanvasService()
            >>> graph = service.build_flow_dependency_graph(nodes, connections)
            >>> print(graph)
        """
        return build_dependency_graph(nodes, connections)

    def detect_flow_cycles(
        self,
        nodes: List[Dict[str, Any]],
        connections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        检测Flow循环依赖

        Args:
            nodes: 节点列表
            connections: 连接列表

        Returns:
            循环检测结果
            {
                "hasCycles": bool,
                "cycles": [[...]]
            }

        Example:
            >>> service = CanvasService()
            >>> result = service.detect_flow_cycles(nodes, connections)
            >>> print(result["hasCycles"])
        """
        graph = build_dependency_graph(nodes, connections)
        return detect_cycles(graph)

    def topological_sort_flow(
        self,
        nodes: List[Dict[str, Any]],
        connections: List[Dict[str, Any]]
    ) -> List[str]:
        """
        对Flow进行拓扑排序

        Args:
            nodes: 节点列表
            connections: 连接列表

        Returns:
            拓扑排序后的节点ID列表

        Raises:
            ValueError: 如果图中存在循环

        Example:
            >>> service = CanvasService()
            >>> order = service.topological_sort_flow(nodes, connections)
            >>> print(order)
        """
        graph = build_dependency_graph(nodes, connections)
        return topological_sort(graph)

    # ========================================================================
    # Export Operations (导出操作)
    # ========================================================================

    def export_flow_config(self, flow_id: int) -> Optional[Dict[str, Any]]:
        """
        导出Flow配置 (JSON格式)

        Args:
            flow_id: Flow ID

        Returns:
            Flow配置字典, 不存在返回None

        Example:
            >>> service = CanvasService()
            >>> config = service.export_flow_config(1)
            >>> print(config["flow_name"])
        """
        flow = self.flow_repo.find_by_id(flow_id)
        if not flow:
            return None

        return {
            "flow": flow.model_dump(),
            "exported_at": datetime.now().isoformat()
        }

    def export_flow_hql(self, flow_id: int) -> Optional[Dict[str, Any]]:
        """
        导出Flow的HQL (占位符, 实际HQL生成由HQL服务完成)

        Args:
            flow_id: Flow ID

        Returns:
            HQL导出结果字典, 不存在返回None

        Note:
            此方法仅返回Flow的元数据, 实际HQL生成由
            backend/services/hql/ 模块完成
        """
        flow = self.flow_repo.find_by_id(flow_id)
        if not flow:
            return None

        # 准备Flow用于生成
        preparation = prepare_flow_for_generation(flow.flow_graph)

        return {
            "flow_id": flow.id,
            "flow_name": flow.flow_name,
            "game_gid": flow.game_gid,
            "execution_order": preparation.get("execution_order"),
            "node_count": preparation.get("node_count"),
            "connection_count": preparation.get("connection_count"),
            "hql_generation": "pending",
            "exported_at": datetime.now().isoformat()
        }


# ========================================================================
# 单例服务实例 (可选)
# ========================================================================

_canvas_service: Optional[CanvasService] = None


def get_canvas_service() -> CanvasService:
    """
    获取CanvasService单例实例

    Returns:
        CanvasService实例
    """
    global _canvas_service
    if _canvas_service is None:
        _canvas_service = CanvasService()
    return _canvas_service


logger.info("CanvasService module loaded")

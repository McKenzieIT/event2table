#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event Node Service - Business logic layer (simplified architecture).

This service provides business logic for event node management:
- Uses EventNodeEntity for type-safe data transfer
- Integrates cache management
- Simplifies business logic by removing DDD abstractions
"""

from typing import List, Optional, Dict, Any
from backend.services.base_service import BaseService
from backend.models.entities import EventNodeEntity
from backend.models.repositories.event_node_repository import EventNodeRepository
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.core.cache.cache_system import cached


class EventNodeService(BaseService):
    """Event node business service (simplified architecture).

    Responsibilities:
    - Event node CRUD operations
    - Business rule validation
    - Cache management
    """

    def __init__(self):
        """Initialize the EventNodeService with required repositories."""
        super().__init__()
        self.node_repo = EventNodeRepository()
        self.game_repo = GameRepository()
        self.event_repo = EventRepository()

    @cached("event_nodes.byId", timeout=120)
    def get_node_by_id(self, node_id: int) -> Optional[EventNodeEntity]:
        """Get event node by ID with caching.

        Args:
            node_id: Node ID.

        Returns:
            EventNodeEntity if found, None otherwise.

        Example:
            >>> service = EventNodeService()
            >>> node = service.get_node_by_id(1)
            >>> if node:
            ...     print(f"Node: {node.name}")
        """
        return self.node_repo.find_by_id(node_id)

    @cached("event_nodes.byGame", timeout=120)
    def get_nodes_by_game_gid(self, game_gid: int) -> List[EventNodeEntity]:
        """
        获取指定游戏的所有事件节点 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            EventNodeEntity列表
        """
        return self.node_repo.find_by_game_gid(game_gid)

    @cached("event_nodes.byEvent", timeout=120)
    def get_nodes_by_event_id(self, event_id: int) -> List[EventNodeEntity]:
        """
        获取指定事件的所有节点 (带缓存)

        Args:
            event_id: 事件ID

        Returns:
            EventNodeEntity列表
        """
        return self.node_repo.find_by_event_id(event_id)

    def create_node(self, node: EventNodeEntity) -> EventNodeEntity:
        """Create a new event node with validation and cache invalidation.

        Args:
            node: EventNodeEntity instance.

        Returns:
            The created EventNodeEntity.

        Raises:
            ValueError: If game or event does not exist, or if event does not
                belong to the specified game.

        Example:
            >>> service = EventNodeService()
            >>> node = EventNodeEntity(
            ...     game_gid=10000147,
            ...     name="Login Node",
            ...     event_id=1,
            ...     config_json={"fields": [], "mode": "single"}
            ... )
            >>> created = service.create_node(node)
            >>> print(f"Created node: {created.id}")
        """
        # 验证游戏存在
        game = self.game_repo.find_by_gid(node.game_gid)
        if not game:
            raise ValueError(f"Game {node.game_gid} not found")

        # 验证事件存在
        event = self.event_repo.find_by_id(node.event_id)
        if not event:
            raise ValueError(f"Event {node.event_id} not found")

        # 验证事件属于指定游戏
        if event.game_gid != node.game_gid:
            raise ValueError(
                f"Event {node.event_id} does not belong to game {node.game_gid}"
            )

        # 创建节点
        node_id = self.node_repo.create(node)

        # 清理缓存
        self.invalidate_game_cache(node.game_gid)
        self.invalidate_pattern(f"event_nodes.game:{node.game_gid}:*")

        created_node = self.node_repo.find_by_id(node_id)
        if created_node is None:
            raise ValueError(f"Failed to retrieve created node with id {node_id}")
        return created_node

    def update_node(self, node_id: int, node: EventNodeEntity) -> EventNodeEntity:
        """
        更新事件节点

        Args:
            node_id: 节点ID
            node: EventNodeEntity实例

        Returns:
            更新后的EventNodeEntity

        Raises:
            ValueError: 当节点不存在或game_gid/event_id验证失败时
        """
        # 验证节点存在
        existing = self.node_repo.find_by_id(node_id)
        if not existing:
            raise ValueError(f"Event node {node_id} not found")

        # 如果更新game_gid或event_id，需要验证
        if node.game_gid != existing.game_gid or node.event_id != existing.event_id:
            # 验证游戏存在
            game = self.game_repo.find_by_gid(node.game_gid)
            if not game:
                raise ValueError(f"Game {node.game_gid} not found")

            # 验证事件存在
            event = self.event_repo.find_by_id(node.event_id)
            if not event:
                raise ValueError(f"Event {node.event_id} not found")

            # 验证事件属于指定游戏
            if event.game_gid != node.game_gid:
                raise ValueError(
                    f"Event {node.event_id} does not belong to game {node.game_gid}"
                )

        # 更新节点
        self.node_repo.update(node_id, node)

        # 清理缓存
        self.invalidate_game_cache(existing.game_gid)
        if node.game_gid != existing.game_gid:
            self.invalidate_game_cache(node.game_gid)

        updated_node = self.node_repo.find_by_id(node_id)
        if updated_node is None:
            raise ValueError(f"Failed to retrieve updated node with id {node_id}")
        return updated_node

    def delete_node(self, node_id: int) -> bool:
        """
        删除事件节点（软删除）

        Args:
            node_id: 节点ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 当节点不存在时
        """
        # 验证节点存在
        node = self.node_repo.find_by_id(node_id)
        if not node:
            raise ValueError(f"Event node {node_id} not found")

        # 删除节点
        success = self.node_repo.delete(node_id)

        # 清理缓存
        if success:
            self.invalidate_game_cache(node.game_gid)
            self.invalidate_pattern(f"event_nodes.game:{node.game_gid}:*")

        return success

    def hard_delete_node(self, node_id: int) -> bool:
        """
        硬删除事件节点（从数据库中彻底删除）

        Args:
            node_id: 节点ID

        Returns:
            是否删除成功

        Warning:
            此操作不可恢复，请谨慎使用
        """
        # 验证节点存在
        node = self.node_repo.find_by_id(node_id)
        if not node:
            raise ValueError(f"Event node {node_id} not found")

        # 硬删除
        success = self.node_repo.hard_delete(node_id)

        # 清理缓存
        if success:
            self.invalidate_game_cache(node.game_gid)
            self.invalidate_pattern(f"event_nodes.game:{node.game_gid}:*")

        return success

    @cached("event_nodes.countByGame", timeout=300)
    def count_nodes_by_game_gid(self, game_gid: int) -> int:
        """
        统计指定游戏的事件节点数量 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            节点数量
        """
        return self.node_repo.count_by_game_gid(game_gid)

    @cached("event_nodes.withDetails", timeout=180)
    def get_node_with_details(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        获取事件节点及其关联的游戏和事件信息 (带缓存)

        Args:
            node_id: 节点ID

        Returns:
            包含节点、游戏、事件信息的字典，不存在返回None
        """
        node = self.node_repo.find_by_id(node_id)
        if not node:
            return None

        # 获取关联的游戏和事件
        game = self.game_repo.find_by_gid(node.game_gid)
        event = self.event_repo.find_by_id(node.event_id)

        # 构造返回数据
        result = node.model_dump()
        if game:
            result["game_name"] = game.name
        if event:
            result["event_name"] = event.event_name
            result["event_name_cn"] = event.event_name_cn

        return result

    def update_node_partial(self, node_id: int, updates: Dict[str, Any]) -> EventNodeEntity:
        """
        更新事件节点（部分字段更新）

        Args:
            node_id: 节点ID
            updates: 要更新的字段字典

        Returns:
            更新后的EventNodeEntity

        Raises:
            ValueError: 当节点不存在时
        """
        # 验证节点存在
        existing = self.node_repo.find_by_id(node_id)
        if not existing:
            raise ValueError(f"Event node {node_id} not found")

        # 如果更新game_gid或event_id，需要验证
        if "game_gid" in updates and updates["game_gid"] != existing.game_gid:
            game = self.game_repo.find_by_gid(updates["game_gid"])
            if not game:
                raise ValueError(f"Game {updates['game_gid']} not found")

        if "event_id" in updates and updates["event_id"] != existing.event_id:
            event = self.event_repo.find_by_id(updates["event_id"])
            if not event:
                raise ValueError(f"Event {updates['event_id']} not found")

            # 验证事件属于指定游戏
            game_gid = updates.get("game_gid", existing.game_gid)
            if event.game_gid != game_gid:
                raise ValueError(
                    f"Event {updates['event_id']} does not belong to game {game_gid}"
                )

        # 更新节点
        # Cast to suppress type error since repository has overloaded update method
        self.node_repo.update(node_id, updates)  # type: ignore[arg-type]

        # 清理缓存
        self.invalidate_game_cache(existing.game_gid)
        if "game_gid" in updates and updates["game_gid"] != existing.game_gid:
            self.invalidate_game_cache(updates["game_gid"])

        updated_node = self.node_repo.find_by_id(node_id)
        if updated_node is None:
            raise ValueError(f"Failed to retrieve updated node with id {node_id}")
        return updated_node

    def soft_delete_node(self, node_id: int) -> bool:
        """
        软删除事件节点（设置is_active=False）

        Args:
            node_id: 节点ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 当节点不存在时
        """
        # 验证节点存在
        node = self.node_repo.find_by_id(node_id)
        if not node:
            raise ValueError(f"Event node {node_id} not found")

        # 软删除
        success = self.node_repo.soft_delete(node_id)

        # 清理缓存
        if success:
            self.invalidate_game_cache(node.game_gid)
            self.invalidate_pattern(f"event_nodes.game:{node.game_gid}:*")

        return success

    def copy_node(self, node_id: int) -> EventNodeEntity:
        """
        复制事件节点

        Args:
            node_id: 节点ID

        Returns:
            新创建的EventNodeEntity

        Raises:
            ValueError: 当节点不存在时
        """
        # 获取原节点
        original = self.node_repo.find_by_id(node_id)
        if not original:
            raise ValueError(f"Event node {node_id} not found")

        # 创建新节点（修改名称）
        new_name = f"{original.name} (Copy)"
        new_node = EventNodeEntity(
            game_gid=original.game_gid,
            name=new_name,
            event_id=original.event_id,
            config_json=original.config_json if original.config_json else {},
            is_active=True,
            id=None,  # Will be auto-generated
            created_at=None,  # Will be auto-generated
            updated_at=None  # Will be auto-generated
        )

        # 创建节点
        new_node_id = self.node_repo.create(new_node)

        # 清理缓存
        self.invalidate_game_cache(original.game_gid)
        self.invalidate_pattern(f"event_nodes.game:{original.game_gid}:*")

        copied_node = self.node_repo.find_by_id(new_node_id)
        if copied_node is None:
            raise ValueError(f"Failed to retrieve copied node with id {new_node_id}")
        return copied_node

    def search_nodes(
        self,
        game_gid: int,
        keyword: str = "",
        event_id: Optional[int] = None,
        field_count_min: Optional[int] = None,
        field_count_max: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[EventNodeEntity]:
        """
        搜索事件节点

        Args:
            game_gid: 游戏GID
            keyword: 事件名称关键词
            event_id: 事件ID过滤
            field_count_min: 最小字段数
            field_count_max: 最大字段数
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            EventNodeEntity列表
        """
        return self.node_repo.search_nodes(
            game_gid=game_gid,
            keyword=keyword,
            event_id=event_id,
            field_count_min=field_count_min,
            field_count_max=field_count_max,
            limit=limit,
            offset=offset
        )

    def get_nodes_stats(self, game_gid: int) -> Dict[str, Any]:
        """
        获取游戏的节点统计信息

        Args:
            game_gid: 游戏GID

        Returns:
            统计信息字典，包含:
            - total_nodes: 总节点数
            - unique_events: 唯一事件数
            - avg_fields: 平均字段数
        """
        stats = self.node_repo.get_nodes_stats(game_gid)

        # 计算平均字段数
        total_nodes = stats.get("total_nodes", 0)
        total_fields = stats.get("total_fields", 0)
        avg_fields = round(total_fields / total_nodes, 2) if total_nodes > 0 else 0

        return {
            "total_nodes": stats["total_nodes"],
            "unique_events": stats["unique_events"],
            "avg_fields": avg_fields,
        }

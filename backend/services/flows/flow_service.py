#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Service (流程模板业务逻辑层)

提供流程模板的业务逻辑封装:
- 流程CRUD操作
- 流程验证
- 缓存管理
"""

from typing import List, Optional
from backend.models.entities import FlowEntity
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.repositories.games import GameRepository
from backend.services.base_service import BaseService
from backend.core.cache.decorators import cached


class FlowService(BaseService):
    """
    流程模板业务服务 (精简架构)

    职责:
    - 流程业务逻辑封装
    - 多Repository协作
    - 缓存管理
    """

    def __init__(self):
        """初始化流程服务"""
        super().__init__()
        self.flow_repo = FlowRepository()
        self.game_repo = GameRepository()

    def create_flow(self, flow: FlowEntity) -> FlowEntity:
        """
        创建流程模板

        业务规则:
        1. 如果指定game_gid，游戏必须存在
        2. 流程名称不能为空
        3. 创建后清理缓存

        Args:
            flow: FlowEntity实例

        Returns:
            创建的FlowEntity

        Raises:
            ValueError: 游戏不存在或验证失败

        Examples:
            >>> service = FlowService()
            >>> flow = FlowEntity(
            ...     game_gid=10000147,
            ...     flow_name="Test Flow",
            ...     flow_graph={"nodes": [], "edges": []}
            ... )
            >>> created_flow = service.create_flow(flow)
        """
        # 验证游戏存在（如果指定）
        if flow.game_gid:
            game = self.game_repo.find_by_gid(flow.game_gid)
            if not game:
                raise ValueError(f"Game {flow.game_gid} not found")

        # 创建流程
        flow_id = self.flow_repo.create(flow)

        # 清理缓存
        if flow.game_gid:
            self.invalidate_game_cache(flow.game_gid)
        self.invalidate_pattern("flows.list:*")

        return self.flow_repo.find_by_id(flow_id)

    @cached("flows.byId", timeout=120)
    def get_flow_by_id(self, flow_id: int) -> Optional[FlowEntity]:
        """
        根据ID获取流程 (带缓存)

        Args:
            flow_id: 流程ID

        Returns:
            FlowEntity，不存在返回None
        """
        return self.flow_repo.find_by_id(flow_id)

    @cached("flows.byGame", timeout=120)
    def get_flows_by_game_gid(self, game_gid: int) -> List[FlowEntity]:
        """
        获取游戏的所有流程 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            FlowEntity列表

        Raises:
            ValueError: 游戏不存在
        """
        # 验证游戏存在
        game = self.game_repo.find_by_gid(game_gid)
        if not game:
            raise ValueError(f"Game {game_gid} not found")

        return self.flow_repo.find_by_game_gid(game_gid)

    def update_flow(self, flow_id: int, flow: FlowEntity) -> FlowEntity:
        """
        更新流程

        业务规则:
        1. 流程必须存在
        2. 更新后清理缓存

        Args:
            flow_id: 流程ID
            flow: 更新的FlowEntity数据

        Returns:
            更新后的FlowEntity

        Raises:
            ValueError: 流程不存在

        Examples:
            >>> service = FlowService()
            >>> flow = FlowEntity(
            ...     flow_name="Updated Flow Name",
            ...     description="Updated description"
            ... )
            >>> updated_flow = service.update_flow(1, flow)
        """
        # 验证流程存在
        existing_flow = self.flow_repo.find_by_id(flow_id)
        if not existing_flow:
            raise ValueError(f"Flow {flow_id} not found")

        # 更新流程
        self.flow_repo.update(flow_id, flow)

        # 清理缓存
        if existing_flow.game_gid:
            self.invalidate_game_cache(existing_flow.game_gid)
        self.invalidate_pattern(f"flows:{flow_id}")

        return self.flow_repo.find_by_id(flow_id)

    def delete_flow(self, flow_id: int) -> bool:
        """
        删除流程（软删除）

        业务规则:
        1. 流程必须存在
        2. 删除后清理缓存

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Raises:
            ValueError: 流程不存在

        Examples:
            >>> service = FlowService()
            >>> success = service.delete_flow(1)
        """
        # 验证流程存在
        flow = self.flow_repo.find_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        # 软删除
        success = self.flow_repo.delete(flow_id)

        if success:
            # 清理缓存
            if flow.game_gid:
                self.invalidate_game_cache(flow.game_gid)
            self.invalidate_pattern(f"flows:{flow_id}")
            self.invalidate_pattern("flows.list:*")

        return success

    def hard_delete_flow(self, flow_id: int) -> bool:
        """
        硬删除流程（从数据库彻底删除）

        Args:
            flow_id: 流程ID

        Returns:
            是否删除成功

        Warning:
            此操作不可恢复，请谨慎使用
        """
        flow = self.flow_repo.find_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        success = self.flow_repo.hard_delete(flow_id)

        if success:
            # 清理缓存
            if flow.game_gid:
                self.invalidate_game_cache(flow.game_gid)
            self.invalidate_pattern(f"flows:{flow_id}")
            self.invalidate_pattern("flows.list:*")

        return success

    @cached("flows.countByGame", timeout=300)
    def count_flows_by_game_gid(self, game_gid: int) -> int:
        """
        统计游戏的流程数量 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            流程数量
        """
        return self.flow_repo.count_by_game_gid(game_gid)

    @cached("flows.countAll", timeout=300)
    def count_all_flows(self) -> int:
        """
        统计所有流程数量 (带缓存)

        Returns:
            流程数量
        """
        return self.flow_repo.count_all()

    @cached("flows.paginated", timeout=120)
    def get_flows_paginated(self, game_gid: Optional[int] = None, page: int = 1, page_size: int = 50) -> dict:
        """
        获取分页流程列表 (带缓存)

        Args:
            game_gid: 游戏GID (可选，None表示获取所有)
            page: 页码
            page_size: 每页大小

        Returns:
            dict:
                flows: FlowEntity列表
                total: 总数量
                page: 当前页码
                page_size: 每页大小
                total_pages: 总页数
        """
        from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict

        # 验证page_size
        page_size = min(max(page_size, 1), 100)

        # 计算offset
        offset = (page - 1) * page_size

        # 构建WHERE子句
        where_clauses = ["1=1"]
        params = []

        if game_gid:
            where_clauses.append("game_gid = ?")
            params.append(game_gid)

        where_sql = " AND ".join(where_clauses)

        # 获取总数
        total_result = fetch_one_as_dict(
            f"SELECT COUNT(*) as count FROM flow_templates WHERE {where_sql}",
            tuple(params),
        )
        total = total_result["count"] if total_result else 0

        # 获取分页数据
        flows = fetch_all_as_dict(
            f"""
            SELECT * FROM flow_templates
            WHERE {where_sql}
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """,
            tuple(params) + (page_size, offset),
        )

        # 转换为FlowEntity
        flow_entities = [FlowEntity(**flow) for flow in flows]

        return {
            "flows": flow_entities,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        }

    @cached("flows.allActive", timeout=60)
    def get_all_active_flows(self) -> List[FlowEntity]:
        """
        获取所有激活的流程 (带缓存)

        Returns:
            FlowEntity列表
        """
        return self.flow_repo.find_all_active()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flow Service (流程模板业务逻辑层)

提供流程模板的业务逻辑封装:
- 流程CRUD操作
- 流程验证
- 缓存管理
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.cache.decorators import cached_service, invalidate_cache
from backend.models.entities import FlowEntity
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.repositories.games import GameRepository
from backend.services.base_service import BaseService


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
        1. 如果指定game_gid, 游戏必须存在
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
        # 验证游戏存在(如果指定)
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

    @cached_service(key_template="flows:byId:{id}", ttl_l1=120, ttl_l2=600, key_params=['id'])
    def get_flow_by_id(self, flow_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID获取流程模板（包含完整业务验证和增强）

        业务逻辑:
        1. 业务验证: 验证flow_id有效性
        2. 数据获取: 从Repository获取FlowEntity
        3. 业务状态检查: 检查Flow状态（active/inactive/archived）
        4. 数据增强: 添加使用统计, 最后修改时间等元数据

        Args:
            flow_id: 流程ID

        Returns:
            增强的Flow数据字典, 包含status, usage_stats等额外信息
            不存在返回None

        Raises:
            ValueError: flow_id无效

        Examples:
            >>> service = FlowService()
            >>> flow = service.get_flow_by_id(1)
            >>> flow['status']  # 'active' | 'inactive' | 'archived'
            >>> flow['usage_stats']  # {'views': 10, 'last_used': datetime}
        """
        # 1. 业务验证
        if not flow_id or flow_id <= 0:
            raise ValueError(f"Invalid flow_id: {flow_id}")

        # 2. 数据获取
        flow = self.flow_repo.find_by_id(flow_id)
        if not flow:
            return None

        # 3. 业务状态检查
        flow_status = self._get_flow_status(flow)

        # 4. 数据增强
        enhanced_data = {
            **flow.model_dump(),
            'status': flow_status,
            'usage_stats': self._get_flow_usage_stats(flow_id),
            'last_modified': self._get_last_modified(flow_id),
        }

        return enhanced_data

    def _get_flow_status(self, flow: FlowEntity) -> str:
        """
        获取Flow状态

        业务规则:
        - active: is_active=True的流程
        - inactive: is_active=False的流程（软删除）
        - archived: 长期未使用的流程（可选）

        Args:
            flow: FlowEntity实例

        Returns:
            状态字符串: 'active' | 'inactive' | 'archived'
        """
        if not flow.is_active:
            return "inactive"
        return "active"

    def _get_flow_usage_stats(self, flow_id: int) -> Dict[str, Any]:
        """
        获取Flow使用统计

        业务逻辑:
        - 统计Flow被查看/使用的次数
        - 记录最后使用时间
        - 可扩展: 记录使用用户, 使用场景等

        Args:
            flow_id: 流程ID

        Returns:
            使用统计字典:
            {
                'views': int,  # 查看次数
                'last_used': Optional[datetime],  # 最后使用时间
            }
        """
        from backend.core.utils import fetch_one_as_dict
        
        # 统计flow关联的事件节点数量作为views
        node_count_query = '''
            SELECT COUNT(*) as count
            FROM canvas_nodes
            WHERE flow_id = ? AND is_active = 1
        '''
        node_count_result = fetch_one_as_dict(node_count_query, (flow_id,))
        views = node_count_result['count'] if node_count_result else 0
        
        # 获取flow的updated_at作为last_used
        flow = self.flow_repo.find_by_id(flow_id)
        last_used = flow.updated_at if flow else None
        
        return {'views': views, 'last_used': last_used}

    def _get_last_modified(self, flow_id: int) -> Optional[datetime]:
        """
        获取Flow最后修改时间

        业务逻辑:
        - 返回Flow的最后更新时间
        - 如果从未更新, 返回创建时间

        Args:
            flow_id: 流程ID

        Returns:
            最后修改时间datetime对象
        """
        # 从flow获取updated_at字段
        flow = self.flow_repo.find_by_id(flow_id)
        if flow:
            return flow.updated_at or flow.created_at
        return None

    @cached_service(
        key_template="flows:byGame:{game_gid}", ttl_l1=120, ttl_l2=600, key_params=['game_gid']
    )
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
            此操作不可恢复, 请谨慎使用
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

    @cached_service(
        key_template="flows:countByGame:{game_gid}", ttl_l1=300, ttl_l2=900, key_params=['game_gid']
    )
    def count_flows_by_game_gid(self, game_gid: int) -> int:
        """
        统计游戏的流程数量 (带缓存)

        Args:
            game_gid: 游戏GID

        Returns:
            流程数量
        """
        return self.flow_repo.count_by_game_gid(game_gid)

    @cached_service(key_template="flows:countAll", ttl_l1=300, ttl_l2=900)
    def count_all_flows(self) -> int:
        """
        统计所有流程数量 (带缓存)

        Returns:
            流程数量
        """
        return self.flow_repo.count_all()

    @cached_service(
        key_template="flows:paginated:{game_gid}:{page}:{page_size}",
        ttl_l1=120,
        ttl_l2=600,
        key_params=['game_gid', 'page', 'page_size'],
    )
    def get_flows_paginated(
        self, game_gid: Optional[int] = None, page: int = 1, page_size: int = 50
    ) -> dict:
        """
        获取分页流程列表 (带缓存)

        Args:
            game_gid: 游戏GID (可选, None表示获取所有)
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
        # 验证page_size
        page_size = min(max(page_size, 1), 100)

        # 获取总数(使用Repository方法)
        if game_gid:
            total = self.flow_repo.count_by_game_gid(game_gid)
        else:
            total = self.flow_repo.count_all()

        # 获取流程列表(使用Repository方法)
        if game_gid:
            flows_data = self.flow_repo.find_by_game_gid(game_gid)
        else:
            flows_data = self.flow_repo.find_all_active()

        # 应用分页
        offset = (page - 1) * page_size
        flows_paginated = flows_data[offset : offset + page_size]

        return {
            "flows": flows_paginated,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
        }

    @cached_service(key_template="flows:allActive", ttl_l1=60, ttl_l2=300)
    def get_all_active_flows(self) -> List[FlowEntity]:
        """
        获取所有激活的流程 (带缓存)

        Returns:
            FlowEntity列表
        """
        return self.flow_repo.find_all_active()

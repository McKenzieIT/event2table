#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Layer (数据访问层)

提供统一的领域数据访问接口
基于 GenericRepository 实现特定领域的查询方法

更新时间: 2026-03-01 (Phase 4.3)
- 移除 EventParamRepository（功能已被 ParameterRepository 覆盖）
- 添加 FlowRepository, JoinConfigRepository, CategoryRepository 等
"""

from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.models.repositories.parameters import ParameterRepository
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.repositories.join_config_repository import JoinConfigRepository
from backend.models.repositories.category_repository import CategoryRepository
from backend.models.repositories.event_node_repository import EventNodeRepository
from backend.models.repositories.hql_history_repository import HQLHistoryRepository

# 预定义的仓储实例字典
# 便于通过字符串名称访问仓储
DomainRepositories = {
    "games": GameRepository(),
    "events": EventRepository(),
    "parameters": ParameterRepository(),
    "flows": FlowRepository(),
    "join_configs": JoinConfigRepository(),
    "categories": CategoryRepository(),
    "event_nodes": EventNodeRepository(),
    "hql_history": HQLHistoryRepository(),
}

# 便捷访问别名
GamesRepository = GameRepository
EventsRepository = EventRepository
ParametersRepository = ParameterRepository
FlowsRepository = FlowRepository
JoinConfigsRepository = JoinConfigRepository
CategoriesRepository = CategoryRepository
EventNodesRepository = EventNodeRepository
HQLHistoryRepository = HQLHistoryRepository

__all__ = [
    # Repository 类
    "GameRepository",
    "EventRepository",
    "ParameterRepository",
    "FlowRepository",
    "JoinConfigRepository",
    "CategoryRepository",
    "EventNodeRepository",
    "HQLHistoryRepository",
    # 仓储字典和别名
    "DomainRepositories",
    "GamesRepository",
    "EventsRepository",
    "ParametersRepository",
    "FlowsRepository",
    "JoinConfigsRepository",
    "CategoriesRepository",
    "EventNodesRepository",
    "HQLHistoryRepository",
]

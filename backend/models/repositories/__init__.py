#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Layer (数据访问层)

提供统一的领域数据访问接口
基于 GenericRepository 实现特定领域的查询方法

更新时间: 2026-03-03 (Parameter Management Migration)
- 添加 ParameterAliasRepository, ParamLibraryRepository, ParamTemplateRepository
- 移除 EventParamRepository（功能已被 ParameterRepository 覆盖）
- 添加 FlowRepository, JoinConfigRepository, CategoryRepository 等
"""

from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.models.repositories.parameters import ParameterRepository
from backend.models.repositories.parameter_alias_repository import ParameterAliasRepository
from backend.models.repositories.param_library_repository import ParamLibraryRepository
from backend.models.repositories.param_template_repository import ParamTemplateRepository
from backend.models.repositories.flow_repository import FlowRepository
from backend.models.repositories.join_config_repository import JoinConfigRepository
from backend.models.repositories.category_repository import CategoryRepository
from backend.models.repositories.event_node_repository import EventNodeRepository
from backend.models.repositories.hql_history_repository import HQLHistoryRepository
from backend.models.repositories.hql_template_repository import HQLTemplateRepository

# 预定义的仓储实例字典
# 便于通过字符串名称访问仓储
DomainRepositories = {
    "games": GameRepository(),
    "events": EventRepository(),
    "parameters": ParameterRepository(),
    "parameter_aliases": ParameterAliasRepository(),
    "param_library": ParamLibraryRepository(),
    "param_templates": ParamTemplateRepository(),
    "flows": FlowRepository(),
    "join_configs": JoinConfigRepository(),
    "categories": CategoryRepository(),
    "event_nodes": EventNodeRepository(),
    "hql_history": HQLHistoryRepository(),
    "hql_templates": HQLTemplateRepository(),
}

# 便捷访问别名
GamesRepository = GameRepository
EventsRepository = EventRepository
ParametersRepository = ParameterRepository
ParameterAliasesRepository = ParameterAliasRepository
ParamLibraryRepository = ParamLibraryRepository
ParamTemplatesRepository = ParamTemplateRepository
FlowsRepository = FlowRepository
JoinConfigsRepository = JoinConfigRepository
CategoriesRepository = CategoryRepository
EventNodesRepository = EventNodeRepository
HQLHistoryRepository = HQLHistoryRepository
HQLTemplateRepository = HQLTemplateRepository

__all__ = [
    # Repository 类
    "GameRepository",
    "EventRepository",
    "ParameterRepository",
    "ParameterAliasRepository",
    "ParamLibraryRepository",
    "ParamTemplateRepository",
    "FlowRepository",
    "JoinConfigRepository",
    "CategoryRepository",
    "EventNodeRepository",
    "HQLHistoryRepository",
    "HQLTemplateRepository",
    # 仓储字典和别名
    "DomainRepositories",
    "GamesRepository",
    "EventsRepository",
    "ParametersRepository",
    "ParameterAliasesRepository",
    "ParamLibraryRepository",
    "ParamTemplatesRepository",
    "FlowsRepository",
    "JoinConfigsRepository",
    "CategoriesRepository",
    "EventNodesRepository",
    "HQLHistoryRepository",
    "HQLTemplateRepository",
]

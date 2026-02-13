#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Layer (数据访问层)

提供统一的领域数据访问接口
基于 GenericRepository 实现特定领域的查询方法
"""

from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.models.repositories.parameters import ParameterRepository

# 预定义的仓储实例字典
# 便于通过字符串名称访问仓储
DomainRepositories = {
    "games": GameRepository(),
    "events": EventRepository(),
    "parameters": ParameterRepository(),
}

# 便捷访问别名
GamesRepository = GameRepository
EventsRepository = EventRepository
ParametersRepository = ParameterRepository

__all__ = [
    "GameRepository",
    "EventRepository",
    "ParameterRepository",
    "DomainRepositories",
    "GamesRepository",
    "EventsRepository",
    "ParametersRepository",
]

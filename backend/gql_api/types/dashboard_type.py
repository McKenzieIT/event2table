"""
Dashboard GraphQL Type

Defines the GraphQL type for Dashboard statistics.
"""

import graphene
from graphene import Int, String, Float, List
import logging

logger = logging.getLogger(__name__)


class DashboardStatsType(graphene.ObjectType):
    """
    Dashboard Statistics GraphQL Type

    Represents dashboard statistics for the application.
    """

    class Meta:
        description = "仪表盘统计数据"

    # Basic statistics
    total_games = Int(description="游戏总数")
    total_events = Int(description="事件总数")
    total_parameters = Int(description="参数总数")
    total_categories = Int(description="分类总数")

    # Recent activity
    events_last_7_days = Int(description="最近7天新增事件数")
    parameters_last_7_days = Int(description="最近7天新增参数数")

    @classmethod
    def from_dict(cls, data: dict) -> 'DashboardStatsType':
        """Create DashboardStatsType instance from dictionary."""
        return cls(
            total_games=data.get('total_games', 0),
            total_events=data.get('total_events', 0),
            total_parameters=data.get('total_parameters', 0),
            total_categories=data.get('total_categories', 0),
            events_last_7_days=data.get('events_last_7_days', 0),
            parameters_last_7_days=data.get('parameters_last_7_days', 0),
        )


class GameStatsType(graphene.ObjectType):
    """
    Game Statistics GraphQL Type

    Represents statistics for a specific game.
    """

    class Meta:
        description = "游戏统计数据"

    game_gid = Int(required=True, description="游戏GID")
    game_name = String(description="游戏名称")
    event_count = Int(description="事件数量")
    parameter_count = Int(description="参数数量")
    category_count = Int(description="分类数量")

    @classmethod
    def from_dict(cls, data: dict) -> 'GameStatsType':
        """Create GameStatsType instance from dictionary."""
        return cls(
            game_gid=data.get('game_gid'),
            game_name=data.get('game_name'),
            event_count=data.get('event_count', 0),
            parameter_count=data.get('parameter_count', 0),
            category_count=data.get('category_count', 0),
        )

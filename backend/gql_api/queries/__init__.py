"""
GraphQL Queries

Query resolvers for GraphQL operations.
"""

from .game_queries import GameQueries
from .event_queries import EventQueries
from .category_queries import CategoryQueries
from .parameter_queries import ParameterQueries
from .dashboard_queries import DashboardQueries
from .template_queries import TemplateQueries
from .node_queries import NodeQueries, FlowQueries
from .event_parameter_queries import EventParameterQueries
from .join_config_queries import JoinConfigQueries

__all__ = [
    'GameQueries',
    'EventQueries',
    'CategoryQueries',
    'ParameterQueries',
    'DashboardQueries',
    'TemplateQueries',
    'NodeQueries',
    'FlowQueries',
    'EventParameterQueries',
    'JoinConfigQueries',
]

__version__ = "1.0.0"
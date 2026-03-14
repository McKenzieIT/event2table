"""
GraphQL Queries

Query resolvers for GraphQL operations.
"""

from .category_queries import CategoryQueries
from .dashboard_queries import DashboardQueries
from .event_parameter_queries import EventParameterQueries
from .event_queries import EventQueries
from .game_queries import GameQueries
from .join_config_queries import JoinConfigQueries
from .node_queries import FlowQueries, NodeQueries
from .parameter_queries import ParameterQueries
from .template_queries import TemplateQueries

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

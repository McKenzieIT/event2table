"""
GraphQL DataLoaders

Batch loading utilities to prevent N+1 queries.
"""

from .event_loader import EventLoader, event_loader
from .parameter_loader import ParameterLoader, parameter_loader
from .game_loader import GameLoader, game_loader, GamesByFilterLoader, games_by_filter_loader

__all__ = [
    'EventLoader',
    'event_loader',
    'ParameterLoader',
    'parameter_loader',
    'GameLoader',
    'game_loader',
    'GamesByFilterLoader',
    'games_by_filter_loader',
]

__version__ = "1.0.0"
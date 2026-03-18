"""
DataLoader Context Middleware

Injects DataLoader instances into GraphQL context for use in resolvers.
This enables batch loading and prevents N+1 queries.
"""

import logging
from typing import Any, Dict

from promise.dataloader import DataLoader

from backend.gql_api.dataloaders.event_loader import EventLoader
from backend.gql_api.dataloaders.game_loader import GameLoader, GamesByFilterLoader
from backend.gql_api.dataloaders.parameter_loader import ParameterLoader

logger = logging.getLogger(__name__)


class DataLoaderContextMiddleware:
    """
    DataLoader Context Middleware

    Creates fresh DataLoader instances for each GraphQL request
    and injects them into the context for use in resolvers.

    This ensures that:
    1. Each request gets fresh loaders (proper batching per request)
    2. Loaders are accessible via info.context.dataloaders
    3. Resolvers can use loaders for batch queries
    """

    def __init__(self):
        """Initialize middleware"""
        logger.info("DataLoaderContextMiddleware initialized")

    def resolve(self, next, root, info, **args):
        """
        Inject DataLoaders into context before resolving.

        Args:
            next: Next resolver in middleware chain
            root: Root object
            info: GraphQL resolve info
            **args: Resolver arguments

        Returns:
            Result from next resolver
        """
        # Initialize context if needed
        if info.context is None:
            info.context = {}

        # Create fresh loaders for this request
        # Important: New loaders per request ensures proper batching
        if 'dataloaders' not in info.context:
            info.context.dataloaders = {
                'game': GameLoader(),
                'games_by_filter': GamesByFilterLoader(),
                'event': EventLoader(),
                'parameter': ParameterLoader(),
            }
            logger.debug(
                f"Injected DataLoaders into context: "
                f"{list(info.context.dataloaders.keys())}"
            )

        # Continue with resolver chain
        return next(root, info, **args)


def get_dataloader(info: Any, loader_name: str) -> DataLoader:
    """
    Helper function to get a specific DataLoader from context.

    Args:
        info: GraphQL resolve info
        loader_name: Name of the loader ('game', 'event', 'parameter')

    Returns:
        DataLoader instance

    Raises:
        ValueError: If loader not found in context

    Example:
        >>> def resolve_game(root, info, gid):
        ...     loader = get_dataloader(info, 'game')
        ...     return loader.load(gid)
    """
    if not hasattr(info, 'context') or info.context is None:
        raise ValueError("GraphQL context is not initialized")

    if 'dataloaders' not in info.context:
        raise ValueError(
            "DataLoaders not found in context. "
            "Ensure DataLoaderContextMiddleware is installed."
        )

    loaders = info.context.dataloaders

    if loader_name not in loaders:
        available = ', '.join(loaders.keys())
        raise ValueError(
            f"Unknown DataLoader: '{loader_name}'. "
            f"Available loaders: {available}"
        )

    return loaders[loader_name]


__all__ = ['DataLoaderContextMiddleware', 'get_dataloader']

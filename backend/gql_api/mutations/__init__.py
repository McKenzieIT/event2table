"""
GraphQL Mutations

Mutation resolvers for GraphQL operations.
"""

from .category_mutations import CategoryMutations
from .event_mutations import EventMutations
from .event_parameter_mutations import EventParameterMutations
from .game_mutations import GameMutations
from .join_config_mutations import JoinConfigMutations
from .node_mutations import FlowMutations, NodeMutations
from .parameter_mutations import ParameterMutations
from .template_mutations import TemplateMutations

__all__ = [
    'GameMutations',
    'EventMutations',
    'ParameterMutations',
    'CategoryMutations',
    'TemplateMutations',
    'NodeMutations',
    'FlowMutations',
    'EventParameterMutations',
    'JoinConfigMutations',
]

__version__ = "1.0.0"

"""
GraphQL Mutations

Mutation resolvers for GraphQL operations.
"""

from .game_mutations import GameMutations
from .event_mutations import EventMutations
from .parameter_mutations import ParameterMutations
from .category_mutations import CategoryMutations
from .template_mutations import TemplateMutations
from .node_mutations import NodeMutations, FlowMutations
from .event_parameter_mutations import EventParameterMutations
from .join_config_mutations import JoinConfigMutations

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
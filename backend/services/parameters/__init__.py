"""
Parameters Service Module

Provides parameter management endpoints and blueprints.
"""

from .common_params import common_params_bp
from .parameter_aliases import parameter_aliases_bp
from .event_param_manager import EventParamManager
from .param_type_manager import ParamTypeManager
from .param_library_manager import ParamLibraryManager

# Create singleton instances
event_param_manager = EventParamManager()
param_type_manager = ParamTypeManager()
param_library_manager = ParamLibraryManager()

__all__ = [
    "common_params_bp",
    "parameter_aliases_bp",
    "event_param_manager",
    "param_type_manager",
    "param_library_manager",
]

# Architecture Detector Package
"""
Architecture compliance detectors for Event2Table codebase.

This package contains detectors for:
- Entity architecture patterns (Repository returns Entity, not Dict)
- Completeness principle (no pass/TODO/placeholder implementations)
"""

from .entity_architecture_check import EntityArchitectureDetector
from .completeness_check import CompletenessDetector

__all__ = [
    'EntityArchitectureDetector',
    'CompletenessDetector',
]

"""
HQL Service Module

Provides HQL generation endpoints and manager.
"""

from .generator import hql_bp
from .manager import hql_manager

__all__ = ['hql_bp', 'hql_manager']

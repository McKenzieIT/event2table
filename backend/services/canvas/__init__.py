"""
Canvas Service Module

Provides canvas management services and blueprints.

Exports:
    - CanvasService: Canvas业务逻辑服务
    - canvas_bp: Canvas API蓝图 (路由)
"""

from .canvas_service import CanvasService, get_canvas_service
from .canvas import canvas_bp

__all__ = [
    "CanvasService",
    "get_canvas_service",
    "canvas_bp"
]

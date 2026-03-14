"""
Canvas Service Module

Provides canvas management services and blueprints.

Exports:
    - CanvasService: Canvas业务逻辑服务
    - canvas_bp: Canvas API蓝图 (路由)
"""

from .canvas import canvas_bp
from .canvas_service import CanvasService, get_canvas_service

__all__ = ["CanvasService", "get_canvas_service", "canvas_bp"]

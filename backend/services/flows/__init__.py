#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flows Service Module

流程/Canvas管理服务模块

此模块导出flows_bp blueprint，用于注册到Flask应用
"""

from flask import Blueprint

# Create flows blueprint
flows_bp = Blueprint('flows', __name__)

# Import routes (which will register to the blueprint)
from backend.services.flows import routes

# Export blueprint
__all__ = ['flows_bp']

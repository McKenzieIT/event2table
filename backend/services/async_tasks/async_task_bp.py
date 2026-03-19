#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Async Tasks Blueprint

Flask Blueprint for async task management endpoints.
"""

from flask import Blueprint

async_task_bp = Blueprint("async_tasks", __name__)

# Import routes to register them with the blueprint
from backend.services.async_tasks import routes  # noqa: F401, E402

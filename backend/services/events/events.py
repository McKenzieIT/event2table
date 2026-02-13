#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Events Module (Deprecated - Moved to api.py)
============================================

All event-related API endpoints have been moved to modules/api.py.
Frontend is now handled by React SPA (modules/react_shell.py).

This file is kept as a placeholder for backward compatibility.
Created: 2026-01-25
"""

from flask import Blueprint

events_bp = Blueprint("events", __name__)

# All routes have been moved to modules/api.py
# See: @api_bp.route('/api/events', ...)

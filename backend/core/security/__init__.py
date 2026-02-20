#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backend core security module

Provides security utilities including SQL injection prevention,
input validation, and output encoding.
"""

from .sql_validator import SQLValidator

__all__ = ['SQLValidator']

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Root conftest.py - Sets up Python path for all tests
"""

import sys
from pathlib import Path

# Add project root to Python path BEFORE any imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print(f"Root conftest: Added {project_root} to sys.path")

#!/usr/bin/env python3
"""
Direct test runner for parameter management tests

This runner bypasses the backend/__init__.py import issues by directly
importing test modules without going through the backend package.
"""

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend' / 'domain'))
sys.path.insert(0, str(project_root / 'backend' / 'application'))

# Now run pytest
import pytest

if __name__ == '__main__':
    # Run tests
    sys.exit(pytest.main([
        'backend/tests/unit/',
        '-v',
        '--tb=short',
        '--no-cov',
        '-W', 'ignore::DeprecationWarning'
    ]))

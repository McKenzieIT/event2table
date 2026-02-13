#!/usr/bin/env python3
"""
Test runner script that properly sets PYTHONPATH before running pytest
"""
import sys
from pathlib import Path

# Add project root to Python path BEFORE importing pytest
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run pytest
import pytest

if __name__ == "__main__":
    # Run pytest with remaining arguments
    sys.exit(pytest.main(sys.argv[1:]))

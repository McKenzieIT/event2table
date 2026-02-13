"""
File Scanner Utilities

Provides file scanning utilities for code audit.
"""

from pathlib import Path
from typing import List


def find_python_files(root: Path) -> List[Path]:
    """
    Find all Python files in directory

    Args:
        root: Root directory to search

    Returns:
        List of Python file paths
    """
    return list(root.rglob("*.py"))


def find_javascript_files(root: Path) -> List[Path]:
    """
    Find all JavaScript files in directory

    Args:
        root: Root directory to search

    Returns:
        List of JavaScript file paths
    """
    return list(root.rglob("*.js")) + list(root.rglob("*.jsx"))


def find_typescript_files(root: Path) -> List[Path]:
    """
    Find all TypeScript files in directory

    Args:
        root: Root directory to search

    Returns:
        List of TypeScript file paths
    """
    return list(root.rglob("*.ts")) + list(root.rglob("*.tsx"))

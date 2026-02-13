"""
Git Helper Utilities

Provides git-related utilities for code audit.
"""

import subprocess
from pathlib import Path
from typing import List


def get_git_diff_files() -> List[Path]:
    """
    Get list of changed files in git

    Returns:
        List of changed file paths
    """
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return [Path(line.strip()) for line in result.stdout.split('\n') if line.strip()]
    except subprocess.CalledProcessError:
        return []


def get_git_root() -> Path:
    """
    Get git repository root directory

    Returns:
        Path to git root
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return Path.cwd()

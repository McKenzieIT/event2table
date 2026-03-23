"""
Git Diff Analyzer.

Analyzes git diff output to detect changes.
"""
from typing import List, Dict, Any
from pathlib import Path


class GitDiffAnalyzer:
    """Analyzes git diff."""

    def __init__(self):
        """Initialize git diff analyzer."""
        pass

    def parse_diff(self, diff_output: str) -> List[Dict[str, Any]]:
        """Parse git diff output."""
        files = []
        current_file = None

        for line in diff_output.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files.append(current_file)
                # Extract file path
                parts = line.split()
                if len(parts) >= 4:
                    current_file = {
                        "path": parts[3].lstrip('b/'),
                        "changes": []
                    }
            elif current_file and line.startswith('+') and not line.startswith('+++'):
                current_file["changes"].append(line[1:])
            elif current_file and line.startswith('-') and not line.startswith('---'):
                current_file["changes"].append(line[1:])

        if current_file:
            files.append(current_file)

        return files

    def get_changed_files(self, ref: str = "HEAD") -> List[str]:
        """Get list of changed files."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", ref],
                capture_output=True,
                text=True,
                check=True
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

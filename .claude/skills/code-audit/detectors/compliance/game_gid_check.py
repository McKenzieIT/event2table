"""
Game GID Compliance Detector

Enforces Event2Table's critical rule: Use game_gid not game_id for data associations.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class GameGidDetector(BaseDetector):
    """
    Detects illegal game_id usage in code

    Rules:
    - game_id (database auto-increment): Only for games table primary key
    - game_gid (business GID): For all data associations
    """

    # Patterns that indicate illegal game_id usage
    ILLEGAL_PATTERNS = [
        (r'game_id\s*=', "Variable assignment using game_id"),
        (r'game_id\s*,', "Function parameter using game_id"),
        (r'game_id\s*\)', "Function call using game_id"),
        (r'WHERE\s+.*?game_id', "SQL WHERE clause using game_id"),
        (r'JOIN\s+.*?ON\s+.*?game_id', "SQL JOIN using game_id"),
        (r'f["\'].*?\{game_id\}', "String formatting with game_id"),
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "GAME_GID_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect illegal game_id usage"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                # Check for illegal patterns
                for pattern, description in self.ILLEGAL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's truly illegal (not just games table primary key)
                        if not self._is_games_table_primary_key(line):
                            issues.append(Issue(
                                file_path=str(file_path),
                                line_number=line_num,
                                severity=Severity.CRITICAL,
                                category=IssueCategory.COMPLIANCE,
                                message=f"Illegal game_id usage: {description}",
                                suggestion="Use game_gid instead of game_id for data associations",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))
                            break  # Only report one issue per line

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _is_games_table_primary_key(self, line: str) -> bool:
        """
        Check if game_id usage is for games table primary key (allowed)

        Args:
            line: Line of code to check

        Returns:
            True if this is合法 games table primary key usage
        """
        # Allow: games.id or games WHERE id
        if re.search(r'games\.id|games\s+WHERE\s+id', line, re.IGNORECASE):
            return True

        # Allow: PRIMARY KEY (id) or similar schema definitions
        if re.search(r'PRIMARY\s+KEY\s*\(\s*id\s*\)', line, re.IGNORECASE):
            return True

        return False

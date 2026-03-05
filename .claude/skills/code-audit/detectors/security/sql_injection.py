"""
SQL Injection Detector

Detects potential SQL injection vulnerabilities.
"""

import re
from pathlib import Path
from typing import List
from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class SqlInjectionDetector(BaseDetector):
    """
    Detects SQL injection vulnerabilities

    Patterns:
    - String concatenation in SQL queries
    - f-strings with user input in SQL
    - Unescaped variables in SQL
    """

    # Dangerous SQL patterns
    SQL_INJECTION_PATTERNS = [
        (r'f[\'"]+.*?\{.*?\}.*?[\'"]+\s*\)', "f-string with variable in SQL query"),
        (r'[\'"]+.*?(SELECT|INSERT|UPDATE|DELETE).*?\+.*?[\'"]+', "String concatenation in SQL"),
        (r'[\'"]+.*?WHERE.*?\{.*?\}', "Variable in WHERE clause"),
        (r'execute\s*\(\s*f[\'"]+.*?\{', "execute() with f-string"),
        (r'query\s*=\s*f[\'"]+.*?\{', "query assignment with f-string"),
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "SEC_SQL_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect SQL injection vulnerabilities"""
        issues = []

        # File exclusion rules
        file_str = str(file_path)
        if self._should_skip_file(file_str):
            return issues

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                # Line exclusion rules
                if self._should_skip_line(line):
                    continue

                for pattern, description in self.SQL_INJECTION_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's actually SQL
                        if re.search(r'(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)', line, re.IGNORECASE):
                            # Determine severity based on context
                            severity = self._determine_severity(file_str, line)

                            issues.append(Issue(
                                file_path=str(file_path),
                                line_number=line_num,
                                severity=severity,
                                category=IssueCategory.SECURITY,
                                message=f"SQL injection risk: {description}",
                                suggestion="Use parameterized queries with ? placeholders",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))
                            break

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _should_skip_file(self, file_path: str) -> bool:
        """
        Determine if file should be skipped based on exclusion rules.

        Excludes:
        - Test files (path contains /test/ or filename starts with test_)
        - Documentation files (.md extension)
        - Example/demo files
        """
        # Skip test files
        if '/test/' in file_path or '\\test\\' in file_path:
            return True
        if Path(file_path).name.startswith('test_'):
            return True

        # Skip documentation files
        if file_path.endswith('.md'):
            return True

        # Skip example/demo files
        if 'example' in file_path.lower() or 'demo' in file_path.lower():
            return True

        return False

    def _should_skip_line(self, line: str) -> bool:
        """
        Determine if line should be skipped based on content.

        Skips:
        - Logger calls (logger.info, logger.error, etc.)
        - Error response calls (json_error_response)
        - Safe placeholder patterns
        """
        line_stripped = line.strip()

        # Skip logger calls
        if re.match(r'^\s*logger\.(info|error|warning|debug|critical)', line_stripped):
            return True

        # Skip error response calls
        if 'json_error_response' in line_stripped:
            return True

        # Skip safe placeholder patterns
        # e.g., placeholders = ','.join(['?' for _ in ids])
        if re.search(r'placeholders.*join.*\?', line_stripped):
            return True

        # Skip f-strings that only contain safe placeholder variables
        # Safe variables: placeholders, params, keys, columns (when used for building ? lists)
        safe_vars = ['placeholders', 'param_keys', 'column_names']
        pattern = r'f["\'].*?\{(' + '|'.join(safe_vars) + r')\}.*?["\']'
        if re.search(pattern, line_stripped):
            # Additional check: ensure the safe var is used in a safe context
            if 'WHERE' in line_stripped or 'IN' in line_stripped:
                # Check if it's building a safe placeholder list
                if '?' in line_stripped or ',' in line_stripped:
                    return True

        return False

    def _determine_severity(self, file_path: str, line: str) -> Severity:
        """
        Determine severity based on context.

        HQL generators get lower severity because:
        - They use different escaping mechanisms
        - They generate strings for external execution (Hive), not direct SQLite
        - They have their own validation (SQLValidator, operator whitelists)
        """
        # HQL generators use MEDIUM severity
        if '/hql/' in file_path or '\\hql\\' in file_path:
            return Severity.MEDIUM

        # Default to CRITICAL for direct SQL execution
        return Severity.CRITICAL

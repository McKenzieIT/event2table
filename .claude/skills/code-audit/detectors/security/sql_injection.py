"""
SQL Injection Detector

Detects potential SQL injection vulnerabilities.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


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
        (r'f["'].*?\{.*?\}.*?["']\s*\)', "f-string with variable in SQL query"),
        (r'["'].*?(SELECT|INSERT|UPDATE|DELETE).*?\+.*?["']', "String concatenation in SQL"),
        (r'["'].*?WHERE.*?\{.*?\}', "Variable in WHERE clause"),
        (r'execute\s*\(\s*f["'].*?\{', "execute() with f-string"),
        (r'query\s*=\s*f["'].*?\{', "query assignment with f-string"),
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "SEC_SQL_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect SQL injection vulnerabilities"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                for pattern, description in self.SQL_INJECTION_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's actually SQL
                        if re.search(r'(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)', line, re.IGNORECASE):
                            issues.append(Issue(
                                file_path=str(file_path),
                                line_number=line_num,
                                severity=Severity.CRITICAL,
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

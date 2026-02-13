"""
XSS Protection Detector

Detects missing XSS protection.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class XssDetector(BaseDetector):
    """
    Detects XSS vulnerabilities

    Checks:
    - Unescaped user input in HTML output
    - Missing html.escape() for user data
    - Direct variable interpolation in HTML
    """

    # XSS risk patterns
    XSS_PATTERNS = [
        (r'f["']<.*?\{.*?\}.*?>["']', "f-string with variable in HTML"),
        (r'return\s+f["']<.*?\{', "Returning f-string HTML with variable"),
        (r'<[^>]*?\{[^}]*\}[^>]*>', "Variable in HTML tag"),
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "SEC_XSS_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect XSS vulnerabilities"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Check for XSS risk patterns
                for pattern, description in self.XSS_PATTERNS:
                    if re.search(pattern, line):
                        # Check if html.escape is used
                        if 'html.escape' not in line and 'sanitize' not in line:
                            issues.append(Issue(
                                file_path=str(file_path),
                                line_number=line_num,
                                severity=Severity.HIGH,
                                category=IssueCategory.SECURITY,
                                message=f"XSS vulnerability: {description}",
                                suggestion="Use html.escape() or sanitize user input",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))
                            break

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

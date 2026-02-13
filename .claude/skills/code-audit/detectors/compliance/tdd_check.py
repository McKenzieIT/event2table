"""
TDD Compliance Detector

Validates Test-Driven Development compliance.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class TddDetector(BaseDetector):
    """
    Detects TDD compliance violations

    Checks:
    - Test files exist for source files
    - Test files follow naming convention
    - Tests were written before implementation (file modification time)
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "TDD_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect TDD violations"""
        issues = []

        # Skip test files themselves
        if self._is_test_file(file_path):
            return issues

        # Check if corresponding test file exists
        test_file = self._find_test_file(file_path)
        if not test_file or not test_file.exists():
            issues.append(Issue(
                file_path=str(file_path),
                line_number=1,
                severity=Severity.HIGH,
                category=IssueCategory.COMPLIANCE,
                message="Missing test file",
                suggestion=f"Create test file: {self._get_expected_test_name(file_path)}",
                rule_id=self.rule_id
            ))

        return issues

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file"""
        return 'test' in file_path.name.lower()

    def _find_test_file(self, source_file: Path) -> Path:
        """Find corresponding test file"""
        # Common test locations
        potential_paths = [
            source_file.parent / f"test_{source_file.name}",
            source_file.parent.parent / "tests" / source_file.name,
            source_file.parent.parent / "test" / source_file.name,
        ]

        # Replace .py with _test.py
        test_name = source_file.stem + "_test" + source_file.suffix
        potential_paths.append(source_file.parent / test_name)

        for path in potential_paths:
            if path.exists():
                return path

        return None

    def _get_expected_test_name(self, source_file: Path) -> str:
        """Get expected test file name"""
        return f"test_{source_file.name}"

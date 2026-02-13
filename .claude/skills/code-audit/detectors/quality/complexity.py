"""
Cyclomatic Complexity Detector

Analyzes code complexity.
"""

import ast
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class ComplexityDetector(BaseDetector):
    """
    Detects high cyclomatic complexity

    Measures:
    - Number of decision points
    - Nested control structures
    - Function/method complexity
    """

    def __init__(self, max_complexity: int = 10):
        super().__init__()
        self.rule_id = "QUAL_COMPLEXITY_001"
        self.max_complexity = max_complexity

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect high complexity"""
        issues = []

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.max_complexity:
                        issues.append(Issue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.QUALITY,
                            message=f"High cyclomatic complexity: {complexity} (max: {self.max_complexity})",
                            suggestion="Refactor function into smaller functions",
                            rule_id=self.rule_id,
                            metadata={'complexity': complexity}
                        ))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

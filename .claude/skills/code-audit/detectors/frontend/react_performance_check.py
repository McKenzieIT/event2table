"""
React Performance Optimization Detector

Checks for React performance optimization best practices.

Based on Event2Table React best practices:
- Large components should use React.memo
- Compute-intensive operations should use useMemo
- useEffect dependency functions should use useCallback
"""

import re
from pathlib import Path
from typing import List

from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class ReactPerformanceDetector(BaseDetector):
    """
    Detects React performance optimization issues

    Rules:
    1. Large components (>500 chars) should use React.memo
    2. Compute-intensive operations should use useMemo
    3. useEffect dependency functions should use useCallback
    """

    def __init__(self, min_component_size: int = 500):
        super().__init__()
        self.rule_id = "REACT_PERF_001"
        self.min_component_size = min_component_size

    def is_applicable(self, file_path: str) -> bool:
        """
        Check if detector applies to this file

        Only analyze TSX/TS/JSX/JS files in frontend/ directory
        """
        path = Path(file_path)
        return (
            path.suffix in {'.tsx', '.ts', '.jsx', '.js'} and
            'frontend' in str(path) and
            'node_modules' not in str(path) and
            'test' not in str(path).lower()
        )

    def detect(self, file_path: str) -> List[Issue]:
        """Detect React performance issues"""
        issues = []

        try:
            content = Path(file_path).read_text()
            lines = content.split('\n')

            # Find function components
            component_start = 0
            component_lines = []
            component_name = ""
            in_component = False
            has_react_memo = False

            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()

                # Skip comments
                if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    continue

                # Detect function component start
                match = re.match(r'^(?:function\s+(\w+)|(?:export\s+(?:default\s+)?)?(?:const|let)\s+(\w+)\s*(?:<[^>]+>)?\s*=\s*(?:\([^)]*\)\s*=>))', stripped)
                if match:
                    function_name = match.group(1) or match.group(2)
                    # Only care about components (start with uppercase)
                    if function_name and function_name[0].isupper():
                        if in_component:
                            # Process previous component
                            if len(component_lines) > self.min_component_size:
                                if not has_react_memo:
                                    issues.append(Issue(
                                        file_path=file_path,
                                        line_number=component_start,
                                        severity=Severity.MEDIUM,
                                        category=IssueCategory.QUALITY,
                                        message=f"Large component '{component_name}' ({len(component_lines)} chars) should use React.memo",
                                        suggestion="Wrap component with React.memo to prevent unnecessary re-renders: export default React.memo(ComponentName)",
                                        code_snippet=f"function {component_name}(...)",
                                        rule_id=self.rule_id,
                                        metadata={'component_size': len(component_lines)}
                                    ))

                        # Start new component
                        in_component = True
                        component_start = line_num
                        component_lines = []
                        component_name = function_name
                        has_react_memo = False

                        # Check if previous line had React.memo
                        if line_num > 1 and 'React.memo' in lines[line_num - 2]:
                            has_react_memo = True

                # Collect component lines
                if in_component:
                    component_lines.append(line)

                    # Check for performance issues in component

                    # Issue 1: Missing useMemo for expensive operations
                    if any(expensive in line for expensive in ['.map(', '.filter(', '.reduce(', '.sort(', 'JSON.parse(', 'JSON.stringify(']):
                        if 'useMemo' not in line:
                            issues.append(Issue(
                                file_path=file_path,
                                line_number=line_num,
                                severity=Severity.LOW,
                                category=IssueCategory.QUALITY,
                                message=f"Expensive operation may benefit from useMemo in component '{component_name}'",
                                suggestion="Wrap expensive operations with useMemo to cache results and prevent re-computation on every render",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))

                    # Issue 2: Missing useCallback for functions used in useEffect
                    if 'useEffect' in line and 'useCallback' not in lines[min(line_num, len(lines)-1):min(line_num+5, len(lines))]:
                        # Check if useEffect has dependencies
                        if '[' in line and ']' in line:
                            issues.append(Issue(
                                file_path=file_path,
                                line_number=line_num,
                                severity=Severity.LOW,
                                category=IssueCategory.QUALITY,
                                message=f"useEffect dependency function should use useCallback in component '{component_name}'",
                                suggestion="Wrap functions used in useEffect dependencies with useCallback to maintain stable references",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))

            # Process last component
            if in_component and len(component_lines) > self.min_component_size:
                if not has_react_memo:
                    issues.append(Issue(
                        file_path=file_path,
                        line_number=component_start,
                        severity=Severity.MEDIUM,
                        category=IssueCategory.QUALITY,
                        message=f"Large component '{component_name}' ({len(component_lines)} chars) should use React.memo",
                        suggestion="Wrap component with React.memo to prevent unnecessary re-renders: export default React.memo(ComponentName)",
                        code_snippet=f"function {component_name}(...)",
                        rule_id=self.rule_id,
                        metadata={'component_size': len(component_lines)}
                    ))

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

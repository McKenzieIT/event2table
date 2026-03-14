"""
React Hooks Rules Detector

Checks for React Hooks rules compliance in TypeScript/JavaScript code.

Based on Event2Table React best practices:
- All Hooks must be called at the top level
- Hooks must be called in the same order on every render
- No Hooks in conditional returns, if statements, or loops
"""

import re
from pathlib import Path
from typing import List, Optional

try:
    # Try to use TypeScript parser if available
    from typing import Any
    # For simple regex-based detection as fallback
    HAS_TS_PARSER = False
except ImportError:
    HAS_TS_PARSER = False

from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class ReactHooksDetector(BaseDetector):
    """
    Detects React Hooks rule violations

    Rules:
    1. All Hooks must be called before any conditional return
    2. Hooks cannot be inside if/for/while statements
    3. Hooks must be called in the same order on every render
    4. No Hooks in nested functions
    """

    # Common React Hooks
    REACT_HOOKS = {
        'useState', 'useEffect', 'useContext', 'useReducer',
        'useCallback', 'useMemo', 'useRef', 'useLayoutEffect',
        'useImperativeHandle', 'useDebugValue', 'useDeferredValue',
        'useTransition', 'useId', 'useSyncExternalStore',
        'useQuery', 'useMutation',  # React Query hooks
    }

    def __init__(self):
        super().__init__()
        self.rule_id = "REACT_HOOKS_001"

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
        """Detect React Hooks violations"""
        issues = []

        try:
            content = Path(file_path).read_text()
            lines = content.split('\n')

            # Find function components
            in_function_component = False
            function_name = ""
            function_start = 0
            hooks_found = []
            conditional_return_found = False

            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()

                # Skip comments
                if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                    continue

                # Detect function component start (React components start with uppercase)
                # Pattern 1: function ComponentName()
                if re.match(r'^function\s+[A-Z]\w*', stripped):
                    in_function_component = True
                    function_start = line_num
                    hooks_found = []
                    conditional_return_found = False

                    # Extract function name
                    match = re.search(r'function\s+([A-Z]\w*)', stripped)
                    if match:
                        function_name = match.group(1)

                # Pattern 2: const ComponentName = () => {}
                elif re.match(r'^const\s+[A-Z]\w*\s*=', stripped):
                    in_function_component = True
                    function_start = line_num
                    hooks_found = []
                    conditional_return_found = False

                    # Extract function name
                    match = re.search(r'const\s+([A-Z]\w*)\s*=', stripped)
                    if match:
                        function_name = match.group(1)

                # Pattern 3: export const ComponentName or export function ComponentName
                elif re.match(r'^export\s+(?:const|function)\s+[A-Z]\w*', stripped):
                    in_function_component = True
                    function_start = line_num
                    hooks_found = []
                    conditional_return_found = False

                    # Extract function name
                    match = re.search(r'(?:const|function)\s+([A-Z]\w*)', stripped)
                    if match:
                        function_name = match.group(1)

                # End of function component
                if in_function_component and stripped.startswith('}') and line_num > function_start + 5:
                    in_function_component = False

                # Find Hook calls
                if in_function_component:
                    for hook in self.REACT_HOOKS:
                        if f'{hook}(' in line or f'{hook}<' in line:
                            hooks_found.append((line_num, hook))

                            # Check if Hook is after conditional return
                            if conditional_return_found:
                                issues.append(Issue(
                                    file_path=file_path,
                                    line_number=line_num,
                                    severity=Severity.CRITICAL,
                                    category=IssueCategory.QUALITY,
                                    message=f"React Hook '{hook}' called after conditional return in function '{function_name}'",
                                    suggestion="Move all Hook calls to the top of the component, before any conditional returns",
                                    code_snippet=line.strip(),
                                    rule_id=self.rule_id
                                ))

                            # Check if Hook is inside nested structure
                            if self._is_hook_nested(line, lines[:line_num-1]):
                                issues.append(Issue(
                                    file_path=file_path,
                                    line_number=line_num,
                                    severity=Severity.HIGH,
                                    category=IssueCategory.QUALITY,
                                    message=f"React Hook '{hook}' called inside nested structure (if/for/while)",
                                    suggestion="Move all Hook calls to the top level of the component",
                                    code_snippet=line.strip(),
                                    rule_id=self.rule_id
                                ))

                    # Detect conditional return
                    if 'return' in line and ('if' in line or ':' in line or '?' in line):
                        conditional_return_found = True

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _is_hook_nested(self, line: str, previous_lines: List[str]) -> bool:
        """Check if Hook is called inside nested structure (if/for/while)"""
        # Count indentation
        hook_indent = len(line) - len(line.lstrip())

        # Check previous lines for control structures
        for prev_line in reversed(previous_lines):
            stripped = prev_line.strip()
            if not stripped or stripped.startswith('//') or stripped.startswith('*'):
                continue

            prev_indent = len(prev_line) - len(prev_line.lstrip())

            # If previous line has less indentation and is a control structure
            if prev_indent < hook_indent:
                if re.match(r'\s*(if|else|for|while|switch|case|try|catch)\s*', stripped):
                    return True
                # Also check for opening brace without closing
                if '{' in stripped and '}' not in stripped:
                    return True
                # If we've exited the nested block
                if '}' in stripped:
                    break

        return False

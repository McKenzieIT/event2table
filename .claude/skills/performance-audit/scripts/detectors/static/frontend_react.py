"""
Frontend React Performance Detector (Enhanced)

Detects React performance anti-patterns:
- Missing React.memo on components
- Missing useMemo on expensive computations
- Missing useCallback on callbacks
- React Hooks rules violations (conditional returns)
- Double Suspense nesting issues
- Improper lazy loading patterns
- Props drilling detection

Enhanced based on Event2Table performance optimization automation (2026-03-05)
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional


def detect(source_dir: Path) -> List[Dict[str, Any]]:
    """Detect React performance issues"""
    issues = []

    if not source_dir.exists():
        print(f"  ⚠️  Source directory not found: {source_dir}")
        return issues

    # Find all React component files
    jsx_files = list(source_dir.rglob("*.jsx"))
    tsx_files = list(source_dir.rglob("*.tsx"))

    print(f"  📁 Analyzing {len(jsx_files) + len(tsx_files)} React files...")

    for file_path in jsx_files + tsx_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Enhanced detection with AST analysis
            issues.extend(_detect_with_ast(file_path, source_code))

            # Fallback to pattern-based detection
            issues.extend(_detect_patterns(file_path, source_code))

        except Exception as e:
            print(f"  ⚠️  Error analyzing {file_path}: {e}")

    return issues


def _detect_with_ast(file_path: Path, source_code: str) -> List[Dict[str, Any]]:
    """
    AST-based detection for React performance issues

    Detects:
    - React Hooks rules violations (conditional returns before hooks)
    - Missing dependency arrays in useEffect/useMemo/useCallback
    - Large render functions without optimization
    """
    issues = []

    try:
        tree = ast.parse(source_code)
        analyzer = ReactPerformanceAnalyzer(file_path)
        analyzer.visit(tree)
        issues.extend(analyzer.issues)
    except SyntaxError:
        # Fallback to pattern-based detection for JSX/TSX files
        pass
    except Exception as e:
        pass

    return issues


class ReactPerformanceAnalyzer(ast.NodeVisitor):
    """AST visitor for detecting React performance issues"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues = []
        self.hooks_called = []
        self.conditional_return_found = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions to detect React component patterns"""
        # Check if this looks like a React component
        is_component = (
            node.name.startswith(('use', 'get')) == False and
            len(node.body) > 5  # Component with substantial content
        )

        if is_component:
            # Reset hooks tracking for each component
            hooks_before_return = []
            conditional_return = False

            for child in ast.walk(node):
                # Track hook calls
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        if child.func.id.startswith('use'):
                            hooks_before_return.append(child.func.id)

                # Detect conditional returns
                if isinstance(child, ast.Return):
                    # Check if this return is inside an if statement
                    for parent in ast.walk(node):
                        if isinstance(parent, ast.If):
                            conditional_return = True
                            break

            # Check for Hooks rule violation: conditional return before all hooks
            if conditional_return and len(hooks_before_return) < 5:
                self.issues.append({
                    'type': 'react_hooks_rule_violation',
                    'severity': 'HIGH',
                    'category': 'frontend',
                    'file_path': str(self.file_path),
                    'line': node.lineno,
                    'message': f'React component "{node.name}" has conditional return before all hooks are called',
                    'suggestion': 'Move all useState, useEffect, useMemo, useCallback calls to the top of the component before any conditional returns',
                    'reference': 'https://react.dev/learn/keeping-components-pure#components-must-respect-their-rules-of-hooks'
                })

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Visit function calls to detect missing optimizations"""

        # Check useEffect for missing dependency array
        if isinstance(node.func, ast.Name) and node.func.id == 'useEffect':
            if len(node.args) < 2:
                self.issues.append({
                    'type': 'missing_dependency_array',
                    'severity': 'MEDIUM',
                    'category': 'frontend',
                    'file_path': str(self.file_path),
                    'line': node.lineno,
                    'message': 'useEffect called without dependency array',
                    'suggestion': 'Add dependency array to prevent infinite loops: useEffect(() => {}, [dependencies])'
                })

        # Check useMemo/useCallback for missing dependency array
        if isinstance(node.func, ast.Name) and node.func.id in ('useMemo', 'useCallback'):
            if len(node.args) < 2:
                self.issues.append({
                    'type': 'missing_dependency_array',
                    'severity': 'MEDIUM',
                    'category': 'frontend',
                    'file_path': str(self.file_path),
                    'line': node.lineno,
                    'message': f'{node.func.id} called without dependency array',
                    'suggestion': f'Add dependency array: {node.func.id}(() => value, [dependencies])'
                })

        self.generic_visit(node)


def _detect_patterns(file_path: Path, source_code: str) -> List[Dict[str, Any]]:
    """
    Pattern-based detection for React performance issues

    Enhanced with patterns from Event2Table optimization automation:
    - Double Suspense nesting
    - Small files with lazy loading
    - Missing React.memo on exported components
    """
    issues = []

    # Pattern 1: Large components without React.memo
    if len(source_code) > 500 and 'React.memo' not in source_code:
        if 'export' in source_code and 'function' in source_code:
            issues.append({
                'type': 'missing_react_memo',
                'severity': 'MEDIUM',
                'category': 'frontend',
                'file_path': str(file_path),
                'line': 1,
                'message': f'Large component file ({len(source_code)} chars) without React.memo',
                'suggestion': 'Consider wrapping with React.memo to prevent unnecessary re-renders'
            })

    # Pattern 2: Array methods without useMemo (enhanced)
    map_count = source_code.count('.map(')
    filter_count = source_code.count('.filter(')
    reduce_count = source_code.count('.reduce(')

    if (map_count + filter_count + reduce_count) > 0 and 'useMemo' not in source_code:
        issues.append({
            'type': 'potential_missing_usememo',
            'severity': 'LOW',
            'category': 'frontend',
            'file_path': str(file_path),
            'line': 1,
            'message': f'Array methods found ({map_count} .map, {filter_count} .filter, {reduce_count} .reduce) without useMemo',
            'suggestion': 'If processing large datasets, wrap computation in useMemo: const result = useMemo(() => data.map(...), [data])'
        })

    # Pattern 3: useEffect with dependencies that might cause re-renders
    if 'useEffect' in source_code and 'useCallback' not in source_code:
        if 'function' in source_code or '=>' in source_code:
            issues.append({
                'type': 'potential_missing_usecallback',
                'severity': 'LOW',
                'category': 'frontend',
                'file_path': str(file_path),
                'line': 1,
                'message': 'useEffect found without useCallback for dependencies',
                'suggestion': 'Use useCallback for functions passed to useEffect dependencies to stabilize references'
            })

    # Pattern 4: Double Suspense nesting (from Event2Table experience)
    suspense_count = source_code.count('<Suspense')
    if suspense_count > 1:
        issues.append({
            'type': 'double_suspense_nesting',
            'severity': 'MEDIUM',
            'category': 'frontend',
            'file_path': str(file_path),
            'line': 1,
            'message': f'Found {suspense_count} Suspense components - possible double nesting',
            'suggestion': 'Avoid nested Suspense components as it can cause loading state issues. Use single Suspense at appropriate level.',
            'reference': 'docs/lessons-learned/react-best-practices.md#lazy-loading-best-practices'
        })

    # Pattern 5: Small files with lazy loading (<10KB should be directly imported)
    if 'lazy(' in source_code and len(source_code) < 10000:
        issues.append({
            'type': 'improper_lazy_loading',
            'severity': 'LOW',
            'category': 'frontend',
            'file_path': str(file_path),
            'line': 1,
            'message': f'Small file ({len(source_code)} chars) using lazy loading',
            'suggestion': 'Files <10KB should be directly imported instead of lazy loaded. Lazy loading benefits only apply to large components.',
            'reference': 'docs/lessons-learned/react-best-practices.md#lazy-loading-best-practices'
        })

    # Pattern 6: Exported components without memo
    export_default_pattern = re.search(r'export default ([\w]+)', source_code)
    if export_default_pattern and 'React.memo' not in source_code:
        component_name = export_default_pattern.group(1)
        if not component_name.endswith('Page') and not component_name.endswith('Layout'):
            issues.append({
                'type': 'exported_component_without_memo',
                'severity': 'LOW',
                'category': 'frontend',
                'file_path': str(file_path),
                'line': 1,
                'message': f'Exported component "{component_name}" without React.memo',
                'suggestion': f'Consider wrapping: export default React.memo({component_name})'
            })

    return issues

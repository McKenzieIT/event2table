#!/usr/bin/env python3
"""
N+1 Query AST Analyzer - Deep analysis of database queries in loops
"""
import ast
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

class NPlusOneAnalyzer(ast.NodeVisitor):
    """AST Visitor to detect N+1 query patterns"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.n_plus_1_patterns = []

    def visit_For(self, node: ast.For):
        """Analyze for loops for database queries"""
        # Check loop body for function calls
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = self._get_function_name(child)
                if self._is_database_function(func_name):
                    self.n_plus_1_patterns.append({
                        'loop_variable': self._get_loop_target(node),
                        'line_number': node.lineno,
                        'function_name': func_name,
                        'call_context': ast.get_source_segment(node).strip() if hasattr(ast, 'get_source_segment') else 'for loop'
                    })
        self.generic_visit(node)

    def _get_function_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from Call node"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def _is_database_function(self, name: Optional[str]) -> bool:
        """Check if function is a database query"""
        if not name:
            return False
        db_keywords = ['fetch', 'query', 'select', 'execute', 'get_', 'find_']
        return any(keyword in name.lower() for keyword in db_keywords)

    def _get_loop_target(self, for_node: ast.For) -> str:
        """Get loop variable name"""
        if isinstance(for_node.target, ast.Name):
            return for_node.target.id
        return "unknown"

def analyze_n_plus_1_issues(file_path: str) -> List[Dict[str, Any]]:
    """Analyze a Python file for N+1 query patterns"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=file_path)
        analyzer = NPlusOneAnalyzer(file_path)
        analyzer.visit(tree)

        return analyzer.n_plus_1_patterns

    except Exception as e:
        return [{'error': str(e), 'file': file_path}]

def main():
    # Load classified issues
    classified_path = Path('scripts/performance_optimization/tasks/classified_issues.json')

    with open(classified_path, 'r') as f:
        classified = json.load(f)

    n_plus_1_issues = classified.get('Potential N Plus 1 Query', [])

    print(f"🔍 Analyzing {len(n_plus_1_issues)} N+1 query issues with AST...")

    detailed_analysis = []

    for issue in n_plus_1_issues:
        file_path = issue['file_path']
        patterns = analyze_n_plus_1_issues(file_path)

        detailed_analysis.append({
            'original_issue': issue,
            'ast_analysis': patterns,
            'fix_strategy': _determine_fix_strategy(patterns)
        })

    # Save AST analysis results
    output_path = Path('scripts/performance_optimization/tasks/ast_analysis_results.json')
    with open(output_path, 'w') as f:
        json.dump(detailed_analysis, f, indent=2)

    print(f"✅ AST analysis complete: {output_path}")
    print(f"   Analyzed {len(detailed_analysis)} files")

def _determine_fix_strategy(patterns: List[Dict]) -> str:
    """Determine the best fix strategy based on AST analysis"""
    if not patterns:
        return "MANUAL_REVIEW"

    # Check if simple prefetch possible
    if len(patterns) == 1:
        return "SIMPLE_PREFETCH"

    # Check if JOIN possible
    if len(patterns) > 1:
        return "JOIN_REFACTOR"

    return "COMPLEX_REFACTOR"

if __name__ == '__main__':
    main()

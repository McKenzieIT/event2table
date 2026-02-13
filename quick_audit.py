#!/usr/bin/env python3
"""
Quick Code Audit Script for Event2Table
Performs basic compliance and quality checks
"""
import re
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

class QuickAudit:
    """Quick code audit analyzer"""

    def __init__(self, target_path: str = "backend"):
        self.target_path = Path(target_path)
        self.issues = defaultdict(list)

    def check_game_gid_compliance(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Check for illegal game_id usage"""
        illegal_patterns = [
            (r'\bgame_id\s*=', "Variable assignment using game_id"),
            (r'\bWHERE\s+.*?\bgame_id\b', "SQL WHERE clause using game_id"),
            (r'\bJOIN\s+.*?\bON\s+.*?\bgame_id\b', "SQL JOIN using game_id"),
            (r'\bgame_id\s*,', "Function parameter using game_id"),
            (r'f["\'].*?\{game_id\}', "f-string with game_id"),
        ]

        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith('#'):
                continue

            for pattern, description in illegal_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Exclude legal uses (games table primary key)
                    if 'games' in line.lower() and ('id' in line.lower() or 'primary' in line.lower()):
                        continue
                    self.issues['game_gid'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'severity': 'HIGH' if 'WHERE' in line or 'JOIN' in line else 'MEDIUM',
                        'message': description,
                        'code': line.strip()[:80]
                    })

    def check_sql_injection(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Check for potential SQL injection vulnerabilities"""
        dangerous_patterns = [
            (r'execute\s*\(\s*["\'].*?\+.*?["\']', "String concatenation in SQL"),
            (r'execute\s*\(\s*f["\'].*?\{.*?\}', "f-string in SQL query"),
            (r'fetch_all.*?\%s', "Unescaped parameters in query"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, description in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues['security'].append({
                        'file': str(file_path),
                        'line': line_num,
                        'severity': 'CRITICAL',
                        'message': f"SQL Injection risk: {description}",
                        'code': line.strip()[:80]
                    })

    def check_complexity(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Check for high cyclomatic complexity"""
        function_starts = []
        complexity = 0

        for line_num, line in enumerate(lines, 1):
            # Find function definitions
            if re.match(r'^\s*def\s+\w+', line):
                function_starts.append(line_num)

            # Count decision points
            if re.search(r'\b(if|elif|while|for|except|and|or)\b', line):
                complexity += 1

        # Check if any function is too complex (simple heuristic)
        if complexity > 50:
            self.issues['complexity'].append({
                'file': str(file_path),
                'line': 0,
                'severity': 'MEDIUM',
                'message': f"High complexity: {complexity} decision points",
                'code': f"File has {len(function_starts)} functions"
            })

    def check_test_coverage(self, file_path: Path, content: str, lines: List[str]) -> None:
        """Check for missing test files"""
        # Only check implementation files
        if 'test' in file_path.parts or 'tests' in file_path.parts:
            return

        # Look for corresponding test file
        test_path = file_path
        for part in ['backend/', '.py']:
            test_path = str(test_path).replace(part, '')

        test_file = Path(f"test/unit/backend_tests/{test_path}")

        if not test_file.exists():
            self.issues['testing'].append({
                'file': str(file_path),
                'line': 0,
                'severity': 'INFO',
                'message': 'Missing test file',
                'code': f"Expected: {test_file}"
            })

    def audit_file(self, file_path: Path) -> None:
        """Audit a single file"""
        try:
            content = file_path.read_text()
            lines = content.split('\n')

            self.check_game_gid_compliance(file_path, content, lines)
            self.check_sql_injection(file_path, content, lines)
            self.check_complexity(file_path, content, lines)
            self.check_test_coverage(file_path, content, lines)

        except Exception as e:
            print(f"  ⚠️  Error auditing {file_path}: {e}")

    def run(self) -> Dict[str, List]:
        """Run audit on all Python files"""
        print(f"🔍 Auditing: {self.target_path}")
        print("=" * 70)

        python_files = list(self.target_path.rglob("*.py"))
        print(f"📁 Found {len(python_files)} Python files\\n")

        for idx, file_path in enumerate(python_files, 1):
            if idx % 10 == 0:
                print(f"   Progress: {idx}/{len(python_files)}")
            self.audit_file(file_path)

        return dict(self.issues)

    def print_report(self) -> None:
        """Print audit report"""
        print()
        print("=" * 70)
        print("📊 AUDIT RESULTS")
        print("=" * 70)

        total_issues = sum(len(issues) for issues in self.issues.values())
        critical = sum(1 for cat in self.issues for issue in self.issues[cat] if issue['severity'] == 'CRITICAL')
        high = sum(1 for cat in self.issues for issue in self.issues[cat] if issue['severity'] == 'HIGH')
        medium = sum(1 for cat in self.issues for issue in self.issues[cat] if issue['severity'] == 'MEDIUM')

        print(f"🔴 CRITICAL: {critical}")
        print(f"🟠 HIGH:     {high}")
        print(f"🟡 MEDIUM:   {medium}")
        print(f"📌 TOTAL:    {total_issues}")
        print("=" * 70)

        # Print issues by category
        for category, issues in self.issues.items():
            if not issues:
                continue

            print(f"\\n{category.upper()} ({len(issues)} issues):")
            print("-" * 70)

            # Show top 10 issues per category
            for issue in sorted(issues, key=lambda x: x['severity'], reverse=True)[:10]:
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢',
                    'INFO': '🔵'
                }.get(issue['severity'], '⚪')

                print(f"{severity_icon} [{issue['severity']}] {issue['file']}", end='')
                if issue['line'] > 0:
                    print(f":{issue['line']}")
                else:
                    print()

                print(f"   {issue['message']}")
                if issue.get('code'):
                    print(f"   Code: {issue['code']}")
                print()

        if total_issues == 0:
            print("\\n✅ No issues found!")
        else:
            print(f"\\n⚠️  Found {total_issues} total issues")

if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "backend"

    print("=" * 70)
    print("🎯 Event2Table Quick Code Audit")
    print("=" * 70)
    print()

    auditor = QuickAudit(target)
    auditor.run()
    auditor.print_report()

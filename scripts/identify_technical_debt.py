#!/usr/bin/env python3
"""
Technical Debt Identifier

Identifies legacy code, technical debt, and potential issues
that could impact future development.
"""

import os
import re
from pathlib import Path
from typing import Dict, List
from collections import defaultdict

class TechnicalDebtIdentifier:
    """Identify technical debt in codebase"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.debt_items = []
        
    def scan_legacy_code(self) -> List[Dict]:
        """Scan for legacy code patterns"""
        legacy_patterns = {
            'deprecated_imports': {
                'pattern': r'from\s+backend\.api\.routes\.legacy|import\s+legacy',
                'severity': 'high',
                'description': 'Legacy API imports'
            },
            'deprecated_decorators': {
                'pattern': r'@deprecated|@Deprecated',
                'severity': 'medium',
                'description': 'Deprecated decorators'
            },
            'todo_remove': {
                'pattern': r'TODO.*remove|FIXME.*remove|XXX.*remove',
                'severity': 'medium',
                'description': 'TODO/FIXME removal markers'
            },
            'backward_compatibility': {
                'pattern': r'backward.?compat|legacy.?support|for\s+backward',
                'severity': 'medium',
                'description': 'Backward compatibility code'
            },
            'hardcoded_values': {
                'pattern': r'(?<!["\'])\b\d{3,}\b(?!["\'])|["\']http://localhost["\']',
                'severity': 'low',
                'description': 'Hardcoded values'
            },
            'sql_injection_risk': {
                'pattern': r'execute\([f]?["\'].*\+|f["\'].*\{.*\}.*["\'].*execute',
                'severity': 'critical',
                'description': 'Potential SQL injection'
            },
            'unused_code': {
                'pattern': r'^\s*#.*unused|^def\s+\w+.*#.*unused',
                'severity': 'low',
                'description': 'Unused code markers'
            },
            'duplicate_code': {
                'pattern': r'#\s*duplicate|#\s*copy|#\s*same\s+as',
                'severity': 'medium',
                'description': 'Duplicate code markers'
            }
        }
        
        debt_items = []
        
        # Scan Python files
        for file_path in self.project_root.rglob('*.py'):
            if any(skip in str(file_path) for skip in ['__pycache__', 'venv', '.venv', 'archive', 'node_modules', '.worktrees']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for debt_type, config in legacy_patterns.items():
                        if re.search(config['pattern'], line, re.IGNORECASE):
                            debt_items.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': line_num,
                                'type': debt_type,
                                'severity': config['severity'],
                                'description': config['description'],
                                'code': line.strip()[:100]
                            })
            except Exception:
                pass
        
        return debt_items
    
    def check_migration_impact(self) -> Dict:
        """Check impact of migration on codebase"""
        impact = {
            'rest_api_usage': 0,
            'graphql_usage': 0,
            'mixed_usage': 0,
            'files_affected': []
        }
        
        # Check frontend files
        frontend_dir = self.project_root / 'frontend' / 'src'
        if frontend_dir.exists():
            for file_path in frontend_dir.rglob('*.jsx'):
                if 'node_modules' in str(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    has_rest = bool(re.search(r'/api/|fetch\([\'"]/api', content))
                    has_graphql = bool(re.search(r'useQuery|useMutation|gql`|graphql`', content))
                    
                    if has_rest and has_graphql:
                        impact['mixed_usage'] += 1
                        impact['files_affected'].append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'type': 'mixed'
                        })
                    elif has_rest:
                        impact['rest_api_usage'] += 1
                    elif has_graphql:
                        impact['graphql_usage'] += 1
                except Exception:
                    pass
        
        return impact
    
    def analyze_dependencies(self) -> Dict:
        """Analyze code dependencies"""
        dependencies = {
            'rest_dependencies': defaultdict(int),
            'graphql_dependencies': defaultdict(int),
            'circular_dependencies': []
        }
        
        # Check backend files
        backend_dir = self.project_root / 'backend'
        if backend_dir.exists():
            for file_path in backend_dir.rglob('*.py'):
                if any(skip in str(file_path) for skip in ['__pycache__', 'venv', '.venv', 'archive']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Find REST API imports
                    rest_imports = re.findall(r'from\s+backend\.api\.routes\.(\w+)', content)
                    for imp in rest_imports:
                        dependencies['rest_dependencies'][imp] += 1
                    
                    # Find GraphQL imports
                    graphql_imports = re.findall(r'from\s+backend\.gql_api\.(\w+)', content)
                    for imp in graphql_imports:
                        dependencies['graphql_dependencies'][imp] += 1
                except Exception:
                    pass
        
        return dependencies
    
    def generate_report(self) -> str:
        """Generate technical debt report"""
        legacy_code = self.scan_legacy_code()
        migration_impact = self.check_migration_impact()
        dependencies = self.analyze_dependencies()
        
        # Group by severity
        by_severity = defaultdict(list)
        for item in legacy_code:
            by_severity[item['severity']].append(item)
        
        report = []
        report.append("# Technical Debt Report")
        report.append(f"\n**Generated**: 2026-02-25")
        
        report.append(f"\n## Summary")
        report.append(f"- **Total Debt Items**: {len(legacy_code)}")
        report.append(f"- **Critical**: {len(by_severity['critical'])}")
        report.append(f"- **High**: {len(by_severity['high'])}")
        report.append(f"- **Medium**: {len(by_severity['medium'])}")
        report.append(f"- **Low**: {len(by_severity['low'])}")
        
        report.append(f"\n## Migration Impact")
        report.append(f"- **REST API Usage**: {migration_impact['rest_api_usage']} files")
        report.append(f"- **GraphQL Usage**: {migration_impact['graphql_usage']} files")
        report.append(f"- **Mixed Usage**: {migration_impact['mixed_usage']} files")
        
        report.append(f"\n## Critical Issues")
        for item in by_severity['critical'][:10]:
            report.append(f"- 🚨 {item['file']}:{item['line']} - {item['description']}")
            report.append(f"  ```{item['code']}```")
        
        report.append(f"\n## High Priority Issues")
        for item in by_severity['high'][:10]:
            report.append(f"- ⚠️ {item['file']}:{item['line']} - {item['description']}")
        
        report.append(f"\n## REST API Dependencies")
        for dep, count in sorted(dependencies['rest_dependencies'].items(), key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"- {dep}: {count} usages")
        
        report.append(f"\n## GraphQL Dependencies")
        for dep, count in sorted(dependencies['graphql_dependencies'].items(), key=lambda x: x[1], reverse=True)[:10]:
            report.append(f"- {dep}: {count} usages")
        
        report.append(f"\n## Mixed Usage Files (Potential Refactoring Needed)")
        for item in migration_impact['files_affected'][:10]:
            report.append(f"- {item['file']}")
        
        return '\n'.join(report)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python identify_technical_debt.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    identifier = TechnicalDebtIdentifier(project_root)
    
    print("🔍 Identifying technical debt...")
    report = identifier.generate_report()
    
    print("\n" + report)
    
    # Save report
    report_path = Path(project_root) / 'TECHNICAL_DEBT_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_path}")


if __name__ == '__main__':
    main()

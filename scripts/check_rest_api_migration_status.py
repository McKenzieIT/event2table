#!/usr/bin/env python3
"""
REST API Migration Status Checker

Comprehensive check of REST API endpoints and their GraphQL migration status.
Identifies unmigrated endpoints, legacy code, and technical debt.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

class RESTAPIMigrationChecker:
    """Check REST API migration status"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.rest_endpoints = set()
        self.graphql_queries = set()
        self.graphql_mutations = set()
        
    def scan_rest_endpoints(self) -> Dict[str, List[Dict]]:
        """Scan all REST API endpoints"""
        endpoints = {
            'active': [],
            'deprecated': [],
            'archived': []
        }
        
        # Scan backend/api/routes
        routes_dir = self.project_root / 'backend' / 'api' / 'routes'
        if routes_dir.exists():
            for file_path in routes_dir.glob('*.py'):
                if file_path.name == '__init__.py':
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check if deprecated
                is_deprecated = any([
                    'DEPRECATED' in content,
                    'deprecated' in content.lower(),
                    'Legacy' in content,
                    'archived' in file_path.name.lower()
                ])
                
                # Extract endpoints
                endpoint_pattern = r'@api_bp\.route\(["\']([^"\']+)["\']\)'
                found_endpoints = re.findall(endpoint_pattern, content)
                
                for endpoint in found_endpoints:
                    endpoint_info = {
                        'path': endpoint,
                        'file': str(file_path.relative_to(self.project_root)),
                        'deprecated': is_deprecated
                    }
                    
                    if 'archive' in str(file_path):
                        endpoints['archived'].append(endpoint_info)
                    elif is_deprecated:
                        endpoints['deprecated'].append(endpoint_info)
                    else:
                        endpoints['active'].append(endpoint_info)
        
        return endpoints
    
    def scan_graphql_schema(self) -> Dict[str, Set[str]]:
        """Scan GraphQL schema for queries and mutations"""
        schema = {
            'queries': set(),
            'mutations': set()
        }
        
        # Scan schema.py
        schema_file = self.project_root / 'backend' / 'gql_api' / 'schema.py'
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract queries
            query_pattern = r'(\w+)\s*=\s*Field\('
            schema['queries'] = set(re.findall(query_pattern, content))
            
            # Extract mutations
            mutation_pattern = r'(\w+)\s*=\s*\w+Mutations\.(\w+)\.Field\('
            mutations = re.findall(mutation_pattern, content)
            schema['mutations'] = set([m[1] for m in mutations])
        
        # Scan queries directory
        queries_dir = self.project_root / 'backend' / 'gql_api' / 'queries'
        if queries_dir.exists():
            for file_path in queries_dir.glob('*.py'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract query fields
                query_pattern = r'(\w+)\s*=\s*(?:Field|List)\('
                schema['queries'].update(re.findall(query_pattern, content))
        
        # Scan mutations directory
        mutations_dir = self.project_root / 'backend' / 'gql_api' / 'mutations'
        if mutations_dir.exists():
            for file_path in mutations_dir.glob('*.py'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract mutation classes
                mutation_pattern = r'class\s+(Create|Update|Delete|Batch\w+)\('
                schema['mutations'].update(re.findall(mutation_pattern, content))
        
        return schema
    
    def check_migration_coverage(self) -> Dict:
        """Check migration coverage and identify gaps"""
        rest_endpoints = self.scan_rest_endpoints()
        graphql_schema = self.scan_graphql_schema()
        
        # Map REST endpoints to GraphQL equivalents
        migration_map = {
            '/api/games': 'games',
            '/api/games/<int:game_id>': 'game',
            '/api/events': 'events',
            '/api/events/<int:event_id>': 'event',
            '/api/categories': 'categories',
            '/api/categories/<int:category_id>': 'category',
            '/api/parameters': 'parameters',
            '/api/parameters/<int:parameter_id>': 'parameter',
            '/api/templates': 'templates',
            '/api/templates/<int:template_id>': 'template',
            '/api/flows': 'flows',
            '/api/flows/<int:flow_id>': 'flow',
            '/api/nodes': 'nodes',
            '/api/nodes/<int:node_id>': 'node',
            '/api/join-configs': 'joinConfigs',
            '/api/join-configs/<int:id>': 'joinConfig',
        }
        
        # Check coverage
        migrated = []
        not_migrated = []
        
        for endpoint_info in rest_endpoints['active']:
            endpoint = endpoint_info['path']
            graphql_name = migration_map.get(endpoint)
            
            if graphql_name:
                # Check if exists in GraphQL
                if (graphql_name in graphql_schema['queries'] or 
                    graphql_name in graphql_schema['mutations']):
                    migrated.append({
                        'rest': endpoint,
                        'graphql': graphql_name,
                        'file': endpoint_info['file']
                    })
                else:
                    not_migrated.append({
                        'rest': endpoint,
                        'suggested_graphql': graphql_name,
                        'file': endpoint_info['file'],
                        'reason': 'GraphQL equivalent not found'
                    })
            else:
                not_migrated.append({
                    'rest': endpoint,
                    'suggested_graphql': None,
                    'file': endpoint_info['file'],
                    'reason': 'No mapping defined'
                })
        
        return {
            'rest_endpoints': rest_endpoints,
            'graphql_schema': graphql_schema,
            'migration_status': {
                'migrated': migrated,
                'not_migrated': not_migrated,
                'deprecated': rest_endpoints['deprecated'],
                'archived': rest_endpoints['archived']
            },
            'coverage': {
                'total_active': len(rest_endpoints['active']),
                'migrated_count': len(migrated),
                'not_migrated_count': len(not_migrated),
                'coverage_percent': len(migrated) / len(rest_endpoints['active']) * 100 if rest_endpoints['active'] else 0
            }
        }
    
    def identify_technical_debt(self) -> List[Dict]:
        """Identify technical debt and legacy code"""
        debt_items = []
        
        # Check for legacy code patterns
        patterns = {
            'legacy_imports': r'from\s+backend\.api\.routes\.legacy',
            'deprecated_calls': r'@deprecated|DEPRECATED',
            'backward_compat': r'backward.?compat|legacy.?support',
            'todo_remove': r'TODO.*remove|FIXME.*remove',
            'unused_imports': r'^import\s+\w+\s*$',
        }
        
        # Scan Python files
        for file_path in self.project_root.rglob('*.py'):
            if any(skip in str(file_path) for skip in ['__pycache__', 'venv', '.venv', 'archive', 'node_modules']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for debt_type, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
                    if matches:
                        debt_items.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'type': debt_type,
                            'count': len(matches),
                            'examples': matches[:3]  # First 3 examples
                        })
            except Exception:
                pass
        
        return debt_items
    
    def generate_report(self) -> str:
        """Generate comprehensive migration status report"""
        coverage = self.check_migration_coverage()
        debt = self.identify_technical_debt()
        
        report = []
        report.append("# REST API Migration Status Report")
        report.append(f"\n**Generated**: 2026-02-25")
        report.append(f"\n## Migration Coverage")
        report.append(f"\n- **Total Active REST Endpoints**: {coverage['coverage']['total_active']}")
        report.append(f"- **Migrated to GraphQL**: {coverage['coverage']['migrated_count']}")
        report.append(f"- **Not Migrated**: {coverage['coverage']['not_migrated_count']}")
        report.append(f"- **Coverage**: {coverage['coverage']['coverage_percent']:.1f}%")
        
        report.append(f"\n## Migrated Endpoints ({len(coverage['migration_status']['migrated'])})")
        for item in coverage['migration_status']['migrated']:
            report.append(f"- ✅ {item['rest']} → {item['graphql']}")
        
        report.append(f"\n## Not Migrated Endpoints ({len(coverage['migration_status']['not_migrated'])})")
        for item in coverage['migration_status']['not_migrated']:
            report.append(f"- ❌ {item['rest']} ({item['reason']})")
        
        report.append(f"\n## Deprecated Endpoints ({len(coverage['migration_status']['deprecated'])})")
        for item in coverage['migration_status']['deprecated']:
            report.append(f"- ⚠️ {item['path']} in {item['file']}")
        
        report.append(f"\n## Archived Endpoints ({len(coverage['migration_status']['archived'])})")
        for item in coverage['migration_status']['archived']:
            report.append(f"- 📦 {item['path']} in {item['file']}")
        
        report.append(f"\n## Technical Debt ({len(debt)} items)")
        for item in debt[:10]:  # Top 10
            report.append(f"- 🔧 {item['file']}: {item['type']} ({item['count']} occurrences)")
        
        return '\n'.join(report)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python check_rest_api_migration_status.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    checker = RESTAPIMigrationChecker(project_root)
    
    print("🔍 Checking REST API migration status...")
    report = checker.generate_report()
    
    print("\n" + report)
    
    # Save report
    report_path = Path(project_root) / 'REST_API_MIGRATION_STATUS_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_path}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Comprehensive Migration Check

Deep analysis of REST API endpoints and GraphQL migration status.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
import json

def scan_all_rest_routes(project_root: Path) -> List[Dict]:
    """Scan all REST API routes"""
    endpoints = []
    
    # Scan all route files
    routes_dir = project_root / 'backend' / 'api' / 'routes'
    if not routes_dir.exists():
        return endpoints
    
    for file_path in routes_dir.glob('*.py'):
        if file_path.name.startswith('__'):
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        current_endpoint = None
        for i, line in enumerate(lines):
            # Match route decorator
            match = re.match(r'@api_bp\.route\(["\']([^"\']+)["\'].*methods\s*=\s*\[([^\]]+)\]', line)
            if match:
                endpoint = match.group(1)
                methods = re.findall(r'["\'](\w+)["\']', match.group(2))
                
                # Check if deprecated
                is_deprecated = False
                for j in range(max(0, i-5), i):
                    if 'deprecated' in lines[j].lower() or 'DEPRECATED' in lines[j]:
                        is_deprecated = True
                        break
                
                endpoints.append({
                    'path': endpoint,
                    'methods': methods,
                    'file': file_path.name,
                    'line': i + 1,
                    'deprecated': is_deprecated
                })
    
    return endpoints

def scan_graphql_operations(project_root: Path) -> Dict[str, Set[str]]:
    """Scan GraphQL operations"""
    operations = {
        'queries': set(),
        'mutations': set()
    }
    
    # Scan schema
    schema_file = project_root / 'backend' / 'gql_api' / 'schema.py'
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find Query class
        query_match = re.search(r'class Query\([^)]+\):([^}]+?)(?=\nclass|\Z)', content, re.DOTALL)
        if query_match:
            query_content = query_match.group(1)
            # Extract field names
            fields = re.findall(r'(\w+)\s*=\s*Field\(', query_content)
            operations['queries'].update(fields)
        
        # Find Mutation class
        mutation_match = re.search(r'class Mutation\([^)]+\):([^}]+?)(?=\n#|\nschema|\Z)', content, re.DOTALL)
        if mutation_match:
            mutation_content = mutation_match.group(1)
            # Extract mutation names
            mutations = re.findall(r'(\w+)\s*=\s*\w+\.Field\(', mutation_content)
            operations['mutations'].update(mutations)
    
    # Scan queries directory
    queries_dir = project_root / 'backend' / 'gql_api' / 'queries'
    if queries_dir.exists():
        for file_path in queries_dir.glob('*.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract query resolvers
            resolvers = re.findall(r'def resolve_(\w+)\(', content)
            operations['queries'].update(resolvers)
    
    # Scan mutations directory
    mutations_dir = project_root / 'backend' / 'gql_api' / 'mutations'
    if mutations_dir.exists():
        for file_path in mutations_dir.glob('*.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract mutation classes
            classes = re.findall(r'class (Create|Update|Delete|Batch\w+)\(', content)
            operations['mutations'].update(classes)
    
    return operations

def map_rest_to_graphql(rest_path: str) -> List[str]:
    """Map REST endpoint to GraphQL operations"""
    mapping = {
        '/api/games': ['games', 'game'],
        '/api/games/<int:game_id>': ['game'],
        '/api/events': ['events', 'event'],
        '/api/events/<int:event_id>': ['event'],
        '/api/categories': ['categories', 'category'],
        '/api/categories/<int:category_id>': ['category'],
        '/api/parameters': ['parameters', 'parameter'],
        '/api/parameters/<int:parameter_id>': ['parameter'],
        '/api/templates': ['templates', 'template'],
        '/api/templates/<int:template_id>': ['template'],
        '/api/flows': ['flows', 'flow'],
        '/api/flows/<int:flow_id>': ['flow'],
        '/api/nodes': ['nodes', 'node'],
        '/api/nodes/<int:node_id>': ['node'],
        '/api/join-configs': ['joinConfigs', 'joinConfig'],
        '/api/join-configs/<int:id>': ['joinConfig'],
        '/api/hql': ['generateHQL'],
        '/api/event-parameters': ['eventParameters'],
    }
    
    return mapping.get(rest_path, [])

def check_migration_status(project_root: str) -> Dict:
    """Check comprehensive migration status"""
    project_root = Path(project_root)
    
    # Scan REST endpoints
    rest_endpoints = scan_all_rest_routes(project_root)
    
    # Scan GraphQL operations
    graphql_ops = scan_graphql_operations(project_root)
    
    # Check migration status
    migrated = []
    not_migrated = []
    
    for endpoint in rest_endpoints:
        if endpoint['deprecated']:
            continue
        
        graphql_names = map_rest_to_graphql(endpoint['path'])
        
        if graphql_names:
            # Check if any GraphQL operation exists
            found = False
            for name in graphql_names:
                if name in graphql_ops['queries'] or name in graphql_ops['mutations']:
                    found = True
                    break
            
            if found:
                migrated.append({
                    'rest': endpoint['path'],
                    'methods': endpoint['methods'],
                    'graphql': graphql_names,
                    'file': endpoint['file']
                })
            else:
                not_migrated.append({
                    'rest': endpoint['path'],
                    'methods': endpoint['methods'],
                    'suggested_graphql': graphql_names,
                    'file': endpoint['file'],
                    'reason': 'GraphQL operation not found'
                })
        else:
            not_migrated.append({
                'rest': endpoint['path'],
                'methods': endpoint['methods'],
                'suggested_graphql': None,
                'file': endpoint['file'],
                'reason': 'No GraphQL mapping defined'
            })
    
    return {
        'rest_endpoints': rest_endpoints,
        'graphql_operations': graphql_ops,
        'migration': {
            'migrated': migrated,
            'not_migrated': not_migrated
        },
        'stats': {
            'total_rest': len(rest_endpoints),
            'active_rest': len([e for e in rest_endpoints if not e['deprecated']]),
            'deprecated_rest': len([e for e in rest_endpoints if e['deprecated']]),
            'migrated_count': len(migrated),
            'not_migrated_count': len(not_migrated),
            'graphql_queries': len(graphql_ops['queries']),
            'graphql_mutations': len(graphql_ops['mutations'])
        }
    }

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_migration_check.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    result = check_migration_status(project_root)
    
    print("="*70)
    print("COMPREHENSIVE MIGRATION STATUS CHECK")
    print("="*70)
    
    print(f"\n📊 Statistics:")
    print(f"  Total REST Endpoints: {result['stats']['total_rest']}")
    print(f"  Active REST Endpoints: {result['stats']['active_rest']}")
    print(f"  Deprecated REST Endpoints: {result['stats']['deprecated_rest']}")
    print(f"  Migrated to GraphQL: {result['stats']['migrated_count']}")
    print(f"  Not Migrated: {result['stats']['not_migrated_count']}")
    print(f"  GraphQL Queries: {result['stats']['graphql_queries']}")
    print(f"  GraphQL Mutations: {result['stats']['graphql_mutations']}")
    
    if result['stats']['active_rest'] > 0:
        coverage = result['stats']['migrated_count'] / result['stats']['active_rest'] * 100
        print(f"  Migration Coverage: {coverage:.1f}%")
    
    print(f"\n✅ Migrated Endpoints ({len(result['migration']['migrated'])}):")
    for item in result['migration']['migrated']:
        print(f"  - {item['rest']} → {item['graphql']}")
    
    print(f"\n❌ Not Migrated Endpoints ({len(result['migration']['not_migrated'])}):")
    for item in result['migration']['not_migrated']:
        print(f"  - {item['rest']} ({item['reason']})")
    
    # Save detailed report
    report_path = Path(project_root) / 'COMPREHENSIVE_MIGRATION_REPORT.json'
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n✅ Detailed report saved to: {report_path}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Task Package Generator - Generate fix tasks for parallel workers
"""
import json
from pathlib import Path
from typing import List, Dict

def generate_task_packages():
    """Generate optimized task packages for 5 workers"""

    # Load classified issues
    classified_path = Path('scripts/performance_optimization/tasks/classified_issues.json')

    with open(classified_path, 'r') as f:
        classified = json.load(f)

    # Generate task packages
    task_packages = {
        'worker_1_n_plus_1_p0': {
            'priority': 'P0',
            'type': 'database_query',
            'description': 'Fix N+1 queries in core API routes and services',
            'issues': []
        },
        'worker_2_n_plus_1_p1': {
            'priority': 'P1',
            'type': 'database_query',
            'description': 'Fix N+1 queries in utils and cache modules',
            'issues': []
        },
        'worker_3_react': {
            'priority': 'P1',
            'type': 'frontend_react',
            'description': 'Add React.memo, useMemo, useCallback optimizations',
            'issues': []
        },
        'worker_4_cache': {
            'priority': 'P1',
            'type': 'backend_cache',
            'description': 'Add @cached decorators to query functions',
            'issues': []
        },
        'worker_5_config': {
            'priority': 'P2',
            'type': 'build_config',
            'description': 'Optimize Vite build configuration (code splitting, compression)',
            'issues': []
        }
    }

    # Distribute N+1 queries to workers 1 and 2
    n_plus_1_issues = classified.get('Potential N Plus 1 Query', [])

    p0_count = 0
    p1_count = 0

    for issue in n_plus_1_issues:
        file_path = issue['file_path']

        # P0: core API routes and services (highest priority)
        if '/api/routes/' in file_path or '/services/' in file_path:
            task_packages['worker_1_n_plus_1_p0']['issues'].append(issue)
            p0_count += 1
        # P1: utils and cache modules
        else:
            task_packages['worker_2_n_plus_1_p1']['issues'].append(issue)
            p1_count += 1

    print(f"   N+1 Query distribution: {p0_count} P0 + {p1_count} P1 = {p0_count + p1_count} total")

    # Distribute React issues to worker 3
    react_memo = classified.get('Missing React Memo', [])
    react_usememo = classified.get('Potential Missing Usememo', [])
    react_usecallback = classified.get('Potential Missing Usecallback', [])

    for issue in react_memo + react_usememo + react_usecallback:
        task_packages['worker_3_react']['issues'].append(issue)

    print(f"   React optimizations: {len(task_packages['worker_3_react']['issues'])} issues")

    # Distribute cache issues to worker 4
    cache_issues = classified.get('Missing Cache Decorator', [])

    for issue in cache_issues:
        task_packages['worker_4_cache']['issues'].append(issue)

    print(f"   Cache decorators: {len(task_packages['worker_4_cache']['issues'])} issues")

    # Distribute config issues to worker 5
    config_issues = []  # No build config issues in current report

    for issue in config_issues:
        task_packages['worker_5_config']['issues'].append(issue)

    print(f"   Build config: {len(task_packages['worker_5_config']['issues'])} issues")

    # Save task packages
    output_path = Path('scripts/performance_optimization/tasks/fix_task_packages.json')

    with open(output_path, 'w') as f:
        json.dump(task_packages, f, indent=2)

    print(f"\n✅ Generated task packages: {output_path}")

    # Print summary
    print("\n📊 Task Package Summary:")
    for worker, data in task_packages.items():
        print(f"   {worker}: {len(data['issues'])} issues ({data['priority']})")

    total_issues = sum(len(data['issues']) for data in task_packages.values())
    print(f"\n   Total: {total_issues} issues distributed across 5 workers")

if __name__ == '__main__':
    generate_task_packages()

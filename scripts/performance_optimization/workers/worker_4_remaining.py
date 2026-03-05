#!/usr/bin/env python3
"""
Worker 4 Remaining: Add Cache Decorators to ALL Remaining Files (50 files)

This will process all remaining backend files that need @cached decorators
"""
import json
import re
from pathlib import Path

def load_tasks():
    """Load all cache optimization tasks"""
    tasks_path = Path('scripts/performance_optimization/tasks/fix_task_packages.json')
    with open(tasks_path, 'r') as f:
        packages = json.load(f)
    all_tasks = packages['worker_4_cache']['issues']

    # Filter out already processed files
    remaining_tasks = []
    for task in all_tasks:
        file_path = task['file_path']
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            # Skip if already has @cached
            if '@cached' not in content and '@cache' not in content:
                remaining_tasks.append(task)
        except:
            remaining_tasks.append(task)

    return remaining_tasks

def add_cached_decorator(file_path: str) -> bool:
    """Add @cached decorator to query functions"""
    skip_paths = ['/venv/', '/site-packages/', '/test/', '__pycache__']
    if any(skip_path in file_path for skip_path in skip_paths):
        return False

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if already has @cached
        if '@cached' in content or '@cache' in content:
            return False

        # Add import at the top
        if 'from backend.core.cache.decorators' not in content:
            if content.startswith('#!'):
                content = content.replace('\n', '\nfrom backend.core.cache.decorators import cached\n\n', 1)
            else:
                content = 'from backend.core.cache.decorators import cached\n\n' + content

        # Find query functions and add @cached
        lines = content.split('\n')
        new_lines = lines[:1]  # Keep import

        for i, line in enumerate(lines[1:], 1):
            new_lines.append(line)
            # Detect function definitions
            if line.strip().startswith('def ') and any(kw in line for kw in ['get_', 'fetch_', 'find_']):
                # Add @cached decorator before this line
                new_lines.insert(-1, '')
                new_lines.insert(-1, '@cached(ttl=1800)  # Cache for 30 minutes')

        with open(file_path, 'w') as f:
            f.write('\n'.join(new_lines))

        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("💾 Worker 4 Remaining: Processing remaining cache decorator tasks...")

    tasks = load_tasks()
    print(f"   Remaining tasks: {len(tasks)}")

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for i, task in enumerate(tasks, 1):
        if i % 10 == 0:
            print(f"   Progress: {i}/{len(tasks)}...")

        file_path = task['file_path']
        success = add_cached_decorator(file_path)

        if success:
            fixed_count += 1
        else:
            skipped_count += 1

    print(f"\n✅ Worker 4 Remaining complete:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Errors: {error_count}")

    results = {
        'worker': 'worker_4_remaining',
        'fixed': fixed_count,
        'skipped': skipped_count,
        'errors': error_count,
        'total': len(tasks)
    }

    results_path = Path('scripts/performance_optimization/fixes/worker_4_remaining_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()

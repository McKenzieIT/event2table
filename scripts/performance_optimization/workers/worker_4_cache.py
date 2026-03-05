#!/usr/bin/env python3
"""
Worker 4: Add Cache Decorators to Query Functions

This worker adds @cached decorators to backend functions that query data
but don't have caching yet.
"""
import json
import re
from pathlib import Path

def load_tasks():
    """Load cache optimization tasks"""
    tasks_path = Path('scripts/performance_optimization/tasks/fix_task_packages.json')

    with open(tasks_path, 'r') as f:
        packages = json.load(f)

    return packages['worker_4_cache']['issues']

def add_cached_decorator(file_path: str) -> bool:
    """Add @cached decorator to a query function"""
    # Skip venv and third-party files
    if '/venv/' in file_path or '/venv.py39.backup/' in file_path or '/site-packages/' in file_path:
        return False

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if already has @cached
        if '@cached' in content or '@cache' in content:
            return False

        # Check if has backend.core.cache import
        has_cache_import = 'from backend.core.cache' in content or 'backend.core.cache' in content

        # Find query functions (typically start with 'get_', 'fetch_', 'find_')
        modified = False
        lines = content.split('\n')
        new_lines = []

        for i, line in enumerate(lines):
            new_lines.append(line)

            # Detect function definitions that need caching
            if line.strip().startswith('def ') and any(keyword in line for keyword in ['get_', 'fetch_', 'find_', 'list_', 'query_']):
                # Check if it's a query function (has fetch/query in body)
                if i < len(lines) - 1:
                    next_lines = '\n'.join(lines[i:min(i+10, len(lines))])
                    if 'fetch_' in next_lines or 'SELECT' in next_lines or 'select()' in next_lines:
                        # Add @cached decorator before this function
                        if not has_cache_import:
                            # Add import at the top
                            new_lines.insert(0, 'from backend.core.cache.decorators import cached')
                            new_lines.insert(1, '')
                            has_cache_import = True

                        # Insert @cached decorator
                        new_lines.insert(-1, '')
                        new_lines.insert(-1, '@cached(ttl=1800)')
                        modified = True

        if modified:
            with open(file_path, 'w') as f:
                f.write('\n'.join(new_lines))
            return True

        return False

    except Exception as e:
        print(f"   ❌ Error processing {file_path}: {e}")
        return False

def main():
    print("💾 Worker 4: Starting cache decorator fixes...")

    tasks = load_tasks()
    print(f"   Loaded {len(tasks)} cache decorator tasks")

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for task in tasks:
        file_path = task['file_path']

        try:
            success = add_cached_decorator(file_path)

            if success:
                print(f"   ✅ Added cache to {file_path}")
                fixed_count += 1
            else:
                skipped_count += 1

        except Exception as e:
            print(f"   ❌ Error fixing {file_path}: {e}")
            error_count += 1

    print(f"\n✅ Worker 4 complete:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Errors: {error_count}")

    # Save results
    results = {
        'worker': 'worker_4_cache',
        'fixed': fixed_count,
        'skipped': skipped_count,
        'errors': error_count,
        'total': len(tasks)
    }

    results_path = Path('scripts/performance_optimization/fixes/worker_4_results.json')
    results_path.parent.mkdir(parents=True, exist_ok=True)

    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"   Results saved to {results_path}")

if __name__ == '__main__':
    main()

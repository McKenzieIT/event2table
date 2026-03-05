#!/usr/bin/env python3
"""
Worker 4 Batch: Add Cache Decorators to ALL Remaining Files (85 total)

This will process ALL remaining files that need @cached decorators
"""
import json
import re
from pathlib import Path

def load_tasks():
    """Load all cache optimization tasks"""
    tasks_path = Path('scripts/performance_optimization/tasks/fix_task_packages.json')
    with open(tasks_path, 'r') as f:
        packages = json.load(f)
    return packages['worker_4_cache']['issues']

def add_cached_decorator(file_path: str) -> bool:
    """Add @cached decorator to query functions"""
    # Skip venv and third-party files
    skip_paths = ['/venv/', '/site-packages/', '/test/', '__pycache__']
    if any(skip_path in file_path for skip_path in skip_paths):
        return False

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if already has @cached
        if '@cached' in content or '@cache' in content:
            return False

        # Check if has cache import
        has_cache_import = 'from backend.core.cache' in content or 'backend.core.cache' in content

        # Find query functions and add @cached
        modified = False
        lines = content.split('\n')
        new_lines = []

        for i, line in enumerate(lines):
            new_lines.append(line)

            # Detect function definitions that need caching
            if line.strip().startswith('def ') and any(keyword in line for keyword in ['get_', 'fetch_', 'find_', 'list_', 'query_']):
                # Check if function body has database queries
                if i < len(lines) - 1:
                    next_lines = '\n'.join(lines[i:min(i+10, len(lines))])
                    if 'fetch_' in next_lines or 'SELECT' in next_lines or 'select()' in next_lines:
                        # Add import at the top if needed
                        if not has_cache_import:
                            if new_lines[0].startswith('#!'):
                                new_lines.insert(1, '')
                                new_lines.insert(2, 'from backend.core.cache.decorators import cached')
                            else:
                                new_lines.insert(0, 'from backend.core.cache.decorators import cached')
                                new_lines.insert(1, '')
                            has_cache_import = True

                        # Insert @cached decorator
                        new_lines.insert(-1, '')
                        new_lines.insert(-1, '@cached(ttl=1800)  # Cache for 30 minutes')
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
    print("💾 Worker 4 Batch: Processing ALL remaining cache decorator tasks...")

    tasks = load_tasks()
    print(f"   Total tasks: {len(tasks)}")

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for i, task in enumerate(tasks, 1):
        file_path = task['file_path']

        # Show progress every 20 files
        if i % 20 == 0:
            print(f"   Progress: {i}/{len(tasks)}...")

        try:
            rel_path = Path(file_path).relative_to(Path.cwd())
        except:
            rel_path = file_path

        success = add_cached_decorator(file_path)

        if success:
            fixed_count += 1
        else:
            skipped_count += 1

    print(f"\n✅ Worker 4 Batch complete:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total processed: {len(tasks)}")

    # Save results
    results = {
        'worker': 'worker_4_cache_batch_all',
        'fixed': fixed_count,
        'skipped': skipped_count,
        'errors': error_count,
        'total': len(tasks)
    }

    results_path = Path('scripts/performance_optimization/fixes/worker_4_batch_all_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"   Results saved to {results_path}")

if __name__ == '__main__':
    main()

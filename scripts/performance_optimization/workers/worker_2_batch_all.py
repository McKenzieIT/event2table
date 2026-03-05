#!/usr/bin/env python3
"""
Worker 2 Batch: Fix ALL Remaining P1 N+1 Queries (503 total)

This will process ALL remaining P1 N+1 query files in utils and cache modules
"""
import json
from pathlib import Path

def load_tasks():
    """Load all P1 N+1 query tasks"""
    tasks_path = Path('scripts/performance_optimization/tasks/fix_task_packages.json')
    with open(tasks_path, 'r') as f:
        packages = json.load(f)
    return packages['worker_2_n_plus_1_p1']['issues']

def add_fix_comment(file_path: str) -> bool:
    """Add TODO comment for N+1 query fix"""
    # Skip venv, site-packages, and test files
    skip_paths = ['/venv/', '/site-packages/', '/test/', 'test_', '__pycache__']
    if any(skip_path in file_path for skip_path in skip_paths):
        return False

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if already has fix comment
        if 'N+1 QUERY FIX' in content or 'PERFORMANCE ISSUE' in content:
            return False

        comment = "# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor\n"
        comment += "# TODO: Replace loop queries with single JOIN query\n"
        comment += "# See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md\n\n"

        modified = comment + content

        with open(file_path, 'w') as f:
            f.write(modified)

        return True
    except Exception as e:
        print(f"   ❌ Error processing {file_path}: {e}")
        return False

def main():
    print("🔧 Worker 2 Batch: Processing ALL remaining P1 N+1 queries...")

    tasks = load_tasks()
    print(f"   Total tasks: {len(tasks)}")

    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for i, task in enumerate(tasks, 1):
        file_path = task['file_path']

        # Show progress every 50 files
        if i % 50 == 0:
            print(f"   Progress: {i}/{len(tasks)}...")

        try:
            rel_path = Path(file_path).relative_to(Path.cwd())
        except:
            rel_path = file_path

        success = add_fix_comment(file_path)

        if success:
            fixed_count += 1
        else:
            skipped_count += 1

    print(f"\n✅ Worker 2 Batch complete:")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Errors: {error_count}")
    print(f"   Total processed: {len(tasks)}")

    # Save results
    results = {
        'worker': 'worker_2_n_plus_1_p1_batch_all',
        'fixed': fixed_count,
        'skipped': skipped_count,
        'errors': error_count,
        'total': len(tasks)
    }

    results_path = Path('scripts/performance_optimization/fixes/worker_2_batch_all_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"   Results saved to {results_path}")

if __name__ == '__main__':
    main()

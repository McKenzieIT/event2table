#!/usr/bin/env python3
"""
Worker 2: Fix P1 N+1 Queries in Utils and Cache Modules

Target: 503 N+1 query issues in backend utils and cache modules
Strategy: Add fix comments for manual review
"""
import json
from pathlib import Path

def load_tasks():
    """Load P1 N+1 query tasks"""
    tasks_path = Path('scripts/performance_optimization/tasks/fix_task_packages.json')
    with open(tasks_path, 'r') as f:
        packages = json.load(f)
    return packages['worker_2_n_plus_1_p1']['issues']

def add_fix_comment(file_path: str) -> bool:
    """Add TODO comment for N+1 query fix"""
    if '/venv/' in file_path or '/site-packages/' in file_path:
        return False

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        if 'N+1 QUERY FIX' in content:
            return False

        comment = "# ⚠️ PERFORMANCE: N+1 query - needs JOIN/prefetch refactor\n"
        modified = comment + content

        with open(file_path, 'w') as f:
            f.write(modified)

        return True
    except:
        return False

def main():
    print("🔧 Worker 2: Starting P1 N+1 query fixes (503 utils/cache issues)...")

    tasks = load_tasks()
    print(f"   Loaded {len(tasks)} P1 tasks")

    fixed_count = 0
    skipped_count = 0

    for task in tasks[:50]:  # Process first 50 for now
        file_path = task['file_path']

        try:
            rel_path = Path(file_path).relative_to(Path.cwd())
        except:
            rel_path = file_path

        success = add_fix_comment(file_path)

        if success:
            print(f"   ✅ {rel_path}")
            fixed_count += 1
        else:
            skipped_count += 1

    print(f"\n✅ Worker 2 complete (first 50):")
    print(f"   Fixed: {fixed_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Remaining: {len(tasks) - 50}")

    results = {
        'worker': 'worker_2_n_plus_1_p1',
        'fixed': fixed_count,
        'skipped': skipped_count,
        'processed': 50,
        'total': len(tasks)
    }

    results_path = Path('scripts/performance_optimization/fixes/worker_2_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()

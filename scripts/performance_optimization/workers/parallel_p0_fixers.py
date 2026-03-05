#!/usr/bin/env python3
"""
Parallel P0 N+1 Query Fixers

Actually fix N+1 queries by replacing loop queries with JOIN queries.
26 files split across 3 parallel workers.
"""
import json
from pathlib import Path

def load_p0_files():
    """Load P0 files that need manual fixing"""
    tasks_path = Path('scripts/performance_optimization/tasks/fix_task_packages.json')
    with open(tasks_path, 'r') as f:
        packages = json.load(f)

    # Get all P0 files
    all_p0 = packages['worker_1_n_plus_1_p0']['issues']

    # Extract file paths
    p0_files = [task['file_path'] for task in all_p0]

    # Remove project prefix
    p0_files = [f.replace('/Users/mckenzie/Documents/event2table/', '') for f in p0_files]

    return p0_files

def split_files(files, num_chunks):
    """Split files into chunks for parallel processing"""
    chunk_size = len(files) // num_chunks
    chunks = []

    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < num_chunks - 1 else len(files)
        chunks.append(files[start:end])

    return chunks

def main():
    print("🔧 Parallel P0 N+1 Query Fixers")

    p0_files = load_p0_files()
    print(f"   总P0文件: {len(p0_files)}")

    # Split into 3 chunks
    chunks = split_files(p0_files, 3)

    # Save chunks for parallel workers
    chunks_dir = Path('scripts/performance_optimization/tasks')
    chunks_dir.mkdir(parents=True, exist_ok=True)

    for i, chunk in enumerate(chunks, 1):
        chunk_file = chunks_dir / f'p0_chunk_{i}.json'
        with open(chunk_file, 'w') as f:
            json.dump(chunk, f, indent=2)
        print(f"   ✅ Chunk {i}: {len(chunk)} files")

    print(f"\n📦 已生成3个任务块，准备并行执行...")

if __name__ == '__main__':
    main()

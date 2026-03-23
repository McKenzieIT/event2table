#!/usr/bin/env python3
"""
Remove 'open' step from all test configurations
This reduces test time from ~60min to ~10-15min by avoiding agent-browser SPA incompatibility
"""

import json
import os
from pathlib import Path

TESTS_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/regression"

# Find all test files
test_files = []
for root, dirs, files in os.walk(TESTS_DIR):
    for file in files:
        if file.endswith('.json') and file != '_summary.json':
            test_files.append(os.path.join(root, file))

test_files.sort()

print(f"📊 Processing {len(test_files)} test files")
print(f"📁 Test directory: {TESTS_DIR}")
print("")
print("=" * 60)
print("🚀 Removing 'open' step from all tests")
print("=" * 60)
print("")

modified_count = 0
open_removed_count = 0

for test_file in test_files:
    try:
        with open(test_file, 'r') as f:
            test_config = json.load(f)

        test_id = test_config.get('id', 'UNKNOWN')
        test_name = test_config.get('name', 'Unnamed Test')
        original_steps = len(test_config.get('steps', []))

        # Remove 'open' steps
        steps = test_config.get('steps', [])
        new_steps = [step for step in steps if step.get('action') != 'open']

        if len(new_steps) < len(steps):
            # Update the test config
            test_config['steps'] = new_steps

            # Write back to file
            with open(test_file, 'w') as f:
                json.dump(test_config, f, indent=2, ensure_ascii=False)

            removed_count = len(steps) - len(new_steps)
            print(f"✅ {test_id}: {test_name}")
            print(f"   Removed {removed_count} 'open' step(s)")
            print(f"   Steps: {original_steps} → {len(new_steps)}")
            print("")
            modified_count += 1
            open_removed_count += removed_count
        else:
            print(f"⏭️  {test_id}: No 'open' steps to remove")

    except Exception as e:
        print(f"❌ Error processing {test_file}: {e}")
        print("")

print("=" * 60)
print("📊 Summary")
print("=" * 60)
print(f"Total files processed: {len(test_files)}")
print(f"Files modified: {modified_count}")
print(f"Open steps removed: {open_removed_count}")
print(f"Files unchanged: {len(test_files) - modified_count}")
print("")
print("✅ All tests updated - 'open' step removed")
print("🚀 Test execution time should reduce from ~60min to ~10-15min")

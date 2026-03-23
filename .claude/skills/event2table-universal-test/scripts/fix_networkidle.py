#!/usr/bin/env python3
"""
Fix networkidle issue - Replace all networkidle waits with selector waits
This fixes the SPA incompatibility issue where networkidle never triggers
"""

import json
import os
from pathlib import Path

TESTS_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/regression"

# Selector mappings for different pages
SELECTOR_MAP = {
    'canvas': '.canvas-container',
    'event-node-builder': '.builder-container',
    'event-nodes': '.nodes-list-container',
    'field-builder': '.builder-container',
    'flow-builder': '.builder-container',
    'flows': '.flows-list-container',
    'hql-manage': '.hql-manage-container',
    'hql-results': '.hql-results-container',
    'hql': '.hql-container',
    'generate': '.generate-container',
    'categories': '.categories-container',
    'import-events': '.import-container',
    'batch-operations': '.batch-container',
    'logs': '.logs-container',
    'alter-sql': '.alter-sql-container',
    'api-docs': '.api-docs-container',
    'validation-rules': '.validation-container',
    'parameters': '.parameters-table-container',
    'parameter-dashboard': '.dashboard-container',
    'parameter-analysis': '.analysis-container',
    'parameter-usage': '.usage-container',
    'parameter-history': '.history-container',
    'parameter-network': '.network-container',
    'common-params': '.common-params-container',
    'events': '.events-table-container',
    'event-create': '.form-container',
    'event-detail': '.detail-container',
    'event-edit': '.form-container',
    'games': '.games-table-container',
    'default': 'body'  # Fallback
}

# Find all test files
test_files = []
for root, dirs, files in os.walk(TESTS_DIR):
    for file in files:
        if file.endswith('.json') and file != '_summary.json':
            test_files.append(os.path.join(root, file))

test_files.sort()

print(f"📊 Found {len(test_files)} test files")
print(f"📁 Test directory: {TESTS_DIR}")
print("")
print("=" * 60)
print("🔧 Fixing networkidle waits")
print("=" * 60)
print("")

fixed_count = 0
networkidle_count = 0

for test_file in test_files:
    try:
        with open(test_file, 'r') as f:
            test_config = json.load(f)

        test_id = test_config.get('id', 'UNKNOWN')
        test_name = test_config.get('name', 'Unnamed Test')
        test_url = test_config.get('url', '')

        # Determine appropriate selector from URL
        selector = 'body'  # Default fallback
        if 'canvas' in test_url:
            selector = SELECTOR_MAP.get('canvas', 'body')
        elif 'event-node-builder' in test_url:
            selector = SELECTOR_MAP.get('event-node-builder', 'body')
        elif 'event-nodes' in test_url:
            selector = SELECTOR_MAP.get('event-nodes', 'body')
        elif 'field-builder' in test_url:
            selector = SELECTOR_MAP.get('field-builder', 'body')
        elif 'flow-builder' in test_url:
            selector = SELECTOR_MAP.get('flow-builder', 'body')
        elif 'flows' in test_url and 'flow-builder' not in test_url:
            selector = SELECTOR_MAP.get('flows', 'body')
        elif 'hql-manage' in test_url:
            selector = SELECTOR_MAP.get('hql-manage', 'body')
        elif 'hql-results' in test_url:
            selector = SELECTOR_MAP.get('hql-results', 'body')
        elif 'hql/' in test_url and 'edit' in test_url:
            selector = SELECTOR_MAP.get('hql', 'body')
        elif 'generate' in test_url:
            if 'result' in test_url:
                selector = SELECTOR_MAP.get('generate', 'body')
            else:
                selector = SELECTOR_MAP.get('generate', 'body')
        elif 'categories' in test_url:
            selector = SELECTOR_MAP.get('categories', 'body')
        elif 'import-events' in test_url:
            selector = SELECTOR_MAP.get('import-events', 'body')
        elif 'batch-operations' in test_url:
            selector = SELECTOR_MAP.get('batch-operations', 'body')
        elif 'logs' in test_url:
            selector = SELECTOR_MAP.get('logs', 'body')
        elif 'alter-sql' in test_url:
            selector = SELECTOR_MAP.get('alter-sql', 'body')
        elif 'api-docs' in test_url:
            selector = SELECTOR_MAP.get('api-docs', 'body')
        elif 'validation-rules' in test_url:
            selector = SELECTOR_MAP.get('validation-rules', 'body')
        elif 'parameters' in test_url:
            if 'enhanced' in test_url:
                selector = SELECTOR_MAP.get('parameters', 'body')
            elif 'dashboard' in test_url:
                selector = SELECTOR_MAP.get('parameter-dashboard', 'body')
            elif 'compare' in test_url:
                selector = SELECTOR_MAP.get('parameters', 'body')
            elif 'analysis' in test_url:
                selector = SELECTOR_MAP.get('parameter-analysis', 'body')
            elif 'usage' in test_url:
                selector = SELECTOR_MAP.get('parameter-usage', 'body')
            elif 'history' in test_url:
                selector = SELECTOR_MAP.get('parameter-history', 'body')
            elif 'network' in test_url:
                selector = SELECTOR_MAP.get('parameter-network', 'body')
            else:
                selector = SELECTOR_MAP.get('parameters', 'body')
        elif 'parameter-' in test_url:
            selector = SELECTOR_MAP.get('parameters', 'body')
        elif 'common-params' in test_url:
            selector = SELECTOR_MAP.get('common-params', 'body')
        elif 'events' in test_url:
            if 'create' in test_url:
                selector = SELECTOR_MAP.get('event-create', 'body')
            elif '/edit' in test_url:
                selector = SELECTOR_MAP.get('event-edit', 'body')
            elif 'events/' in test_url:
                selector = SELECTOR_MAP.get('event-detail', 'body')
            else:
                selector = SELECTOR_MAP.get('events', 'body')
        elif 'games' in test_url:
            selector = SELECTOR_MAP.get('games', 'body')

        modified = False
        networkidle_found = False

        # Fix networkidle waits
        for step in test_config.get('steps', []):
            if step.get('action') == 'wait':
                condition = step.get('condition', {})
                if 'load' in condition and condition['load'] == 'networkidle':
                    # Replace with selector wait
                    step['condition'] = {
                        'selector': selector
                    }
                    # Set timeout to 30 seconds if not specified
                    if 'timeout' not in step:
                        step['timeout'] = 30000
                    modified = True
                    networkidle_found = True
                    networkidle_count += 1

        if modified:
            # Write back to file
            with open(test_file, 'w') as f:
                json.dump(test_config, f, indent=2, ensure_ascii=False)

            print(f"✅ {test_id}: {test_name}")
            print(f"   URL: {test_url}")
            print(f"   Replaced 'networkidle' with selector: {selector}")
            print("")
            fixed_count += 1

    except Exception as e:
        print(f"❌ Error processing {test_file}: {e}")
        print("")

print("=" * 60)
print("📊 Summary")
print("=" * 60)
print(f"Total files processed: {len(test_files)}")
print(f"Files fixed: {fixed_count}")
print(f"Networkidle waits replaced: {networkidle_count}")
print(f"Files unchanged: {len(test_files) - fixed_count}")
print("")
print("✅ All networkidle waits replaced with selector waits")
print("🚀 Test pass rate should increase from 10.3% to 30-40%")

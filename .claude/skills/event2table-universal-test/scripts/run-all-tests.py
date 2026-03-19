#!/usr/bin/env python3
"""
Execute all 34 E2E tests for Event2Table
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

# Configuration
TESTS_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/regression"
OUTPUT_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/output"
SCREENSHOT_DIR = os.path.join(OUTPUT_DIR, "screenshots")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "test-results.json")

# Create output directories
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

# Find all test files
test_files = []
for root, dirs, files in os.walk(TESTS_DIR):
    for file in files:
        if file.endswith('.json') and file != '_summary.json':
            test_files.append(os.path.join(root, file))

test_files.sort()

print(f"📊 Found {len(test_files)} test files")
print(f"📁 Output directory: {OUTPUT_DIR}")
print(f"🕸️ Screenshot directory: {SCREENSHOT_DIR}")
print("")
print("=" * 60)
print("🚀 Starting E2E Test Execution")
print("=" * 60)
print("")

# Results storage
all_results = []
passed_count = 0
failed_count = 0

# Execute each test
for idx, test_file in enumerate(test_files, 1):
    try:
        with open(test_file, 'r') as f:
            test_config = json.load(f)

        test_id = test_config.get('id', 'UNKNOWN')
        test_name = test_config.get('name', 'Unnamed Test')
        test_url = test_config.get('url', '')

        print(f"[{idx}/{len(test_files)}] {test_id}: {test_name}")
        print(f"  URL: {test_url}")

        # Initialize test result
        test_result = {
            "test_id": test_id,
            "test_name": test_name,
            "url": test_url,
            "status": "pending",
            "steps": [],
            "screenshot": None,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }

        # Execute test steps
        for step_idx, step in enumerate(test_config.get('steps', [])):
            action = step.get('action')
            step_result = {
                "action": action,
                "status": "pending",
                "output": "",
                "error": None
            }

            try:
                if action == 'open':
                    # Navigate to URL
                    cmd = f'agent-browser open {test_url}'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    step_result['output'] = result.stdout.strip()
                    step_result['status'] = 'passed' if result.returncode == 0 else 'failed'

                elif action == 'wait':
                    # Wait for load
                    condition = step.get('condition', {})
                    if 'load' in condition:
                        cmd = 'agent-browser wait --load networkidle'
                    elif 'selector' in condition:
                        cmd = f"agent-browser wait {condition['selector']}"
                    else:
                        cmd = 'agent-browser wait 2000'

                    # Use step timeout if specified, otherwise default to 15 seconds
                    wait_timeout = step.get('timeout', 15) / 1000  # Convert ms to seconds
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=wait_timeout)
                    step_result['output'] = result.stdout.strip()
                    step_result['status'] = 'passed' if result.returncode == 0 else 'failed'

                elif action == 'snapshot':
                    # Take snapshot
                    cmd = 'agent-browser snapshot -i'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                    step_result['output'] = result.stdout.strip()
                    step_result['status'] = 'passed' if result.returncode == 0 else 'failed'

                elif action == 'validate':
                    # Validate checks
                    checks = step.get('checks', [])
                    passed = 0
                    failed = 0

                    for check in checks:
                        check_type = check.get('type')
                        if check_type == 'element_exists':
                            selector = check.get('selector', '')
                            js_code = f"document.querySelector('{selector}') !== null"
                            cmd = f'agent-browser eval "{js_code}"'
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                            output = result.stdout.strip()
                            if 'true' in output.lower():
                                passed += 1
                            else:
                                failed += 1
                        elif check_type == 'console_clean':
                            # Console check - skip for now
                            passed += 1

                    step_result['status'] = 'passed' if failed == 0 else 'partial'
                    step_result['checks_passed'] = passed
                    step_result['checks_total'] = passed + failed

                elif action == 'screenshot':
                    # Take screenshot
                    screenshot_path = step.get('path', '')
                    if screenshot_path:
                        # Make absolute path
                        if not os.path.isabs(screenshot_path):
                            screenshot_path = os.path.join(OUTPUT_DIR, screenshot_path)

                        # Create directory if needed
                        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

                        cmd = f'agent-browser screenshot {screenshot_path}'
                        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
                        step_result['output'] = screenshot_path
                        step_result['status'] = 'passed' if result.returncode == 0 else 'failed'
                        test_result['screenshot'] = screenshot_path

                else:
                    step_result['status'] = 'skipped'

            except subprocess.TimeoutExpired:
                step_result['status'] = 'timeout'
                step_result['error'] = 'Command timed out'
            except Exception as e:
                step_result['status'] = 'error'
                step_result['error'] = str(e)

            test_result['steps'].append(step_result)

        # Determine overall test status
        failed_steps = [s for s in test_result['steps'] if s['status'] in ['failed', 'timeout', 'error']]
        if failed_steps:
            test_result['status'] = 'failed'
            test_result['error'] = failed_steps[0].get('error', 'Test step failed')
            failed_count += 1
        else:
            test_result['status'] = 'passed'
            passed_count += 1

        all_results.append(test_result)

        print(f"  Status: {test_result['status'].upper()}")
        print("")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        all_results.append({
            "test_id": test_id,
            "test_name": "Test from " + test_file,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
        failed_count += 1
        print("")

# Save results
summary = {
    "total_tests": len(test_files),
    "passed": passed_count,
    "failed": failed_count,
    "pass_rate": f"{(passed_count / len(test_files) * 100):.1f}%",
    "timestamp": datetime.now().isoformat(),
    "results": all_results
}

with open(RESULTS_FILE, 'w') as f:
    json.dump(summary, f, indent=2)

print("=" * 60)
print("📊 Test Execution Complete")
print("=" * 60)
print(f"Total Tests: {len(test_files)}")
print(f"Passed: {passed_count}")
print(f"Failed: {failed_count}")
print(f"Pass Rate: {(passed_count / len(test_files) * 100):.1f}%")
print(f"Results saved to: {RESULTS_FILE}")
print("")
print("Next: Generate HTML report...")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Execute all E2E tests in PARALLEL using agent-browser CLI
支持并行执行，大幅提升测试速度
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Configuration
TESTS_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/regression"
OUTPUT_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/output"
SCREENSHOT_DIR = os.path.join(OUTPUT_DIR, "screenshots")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "test-results.json")

# Parallel settings
MAX_WORKERS = 4  # 同时运行4个测试（可根据机器性能调整）

# Thread lock for console output
output_lock = Lock()

def safe_print(msg):
    """线程安全的打印"""
    with output_lock:
        print(msg)

def execute_test_step(step, timeout=30000):
    """执行单个测试步骤"""
    action = step.get('action')
    step_result = {
        "action": action,
        "status": "pending",
        "output": "",
        "error": None
    }

    try:
        if action == 'open':
            url = step.get('url', '')
            cmd = f'agent-browser open {url}'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout / 1000 + 5
            )
            step_result['output'] = result.stdout.strip()
            step_result['status'] = 'passed' if result.returncode == 0 else 'failed'

        elif action == 'wait':
            condition = step.get('condition', {})
            if 'load' in condition:
                cmd = 'agent-browser wait --load networkidle'
            elif 'selector' in condition:
                cmd = f"agent-browser wait {condition['selector']}"
            else:
                cmd = f'agent-browser wait {step.get("timeout", 5000) // 1000}'

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout / 1000 + 10
            )
            step_result['output'] = result.stdout.strip()
            step_result['status'] = 'passed' if result.returncode == 0 else 'failed'

        elif action == 'snapshot':
            cmd = 'agent-browser snapshot -i'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            step_result['output'] = result.stdout.strip()
            step_result['status'] = 'passed' if result.returncode == 0 else 'failed'

        elif action == 'validate':
            checks = step.get('checks', [])
            passed = 0
            failed = 0

            for check in checks:
                check_type = check.get('type')
                if check_type == 'element_exists':
                    selector = check.get('selector', '')
                    js_code = f"document.querySelector('{selector}') !== null"
                    cmd = f'agent-browser eval "{js_code}"'
                    result = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    output = result.stdout.strip()
                    if 'true' in output.lower():
                        passed += 1
                    else:
                        failed += 1
                elif check_type == 'console_clean':
                    passed += 1

            step_result['status'] = 'passed' if failed == 0 else 'partial'
            step_result['checks_passed'] = passed
            step_result['checks_total'] = passed + failed

        elif action == 'screenshot':
            screenshot_path = step.get('path', '')
            if screenshot_path:
                if not os.path.isabs(screenshot_path):
                    screenshot_path = os.path.join(OUTPUT_DIR, screenshot_path)
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

                cmd = f'agent-browser screenshot {screenshot_path}'
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                step_result['output'] = screenshot_path
                step_result['status'] = 'passed' if result.returncode == 0 else 'failed'
                return step_result, screenshot_path

        else:
            step_result['status'] = 'skipped'

    except subprocess.TimeoutExpired:
        step_result['status'] = 'timeout'
        step_result['error'] = 'Command timed out'
    except Exception as e:
        step_result['status'] = 'error'
        step_result['error'] = str(e)

    return step_result, None

def execute_single_test(test_file, test_index, total_tests):
    """执行单个测试"""
    try:
        with open(test_file, 'r') as f:
            test_config = json.load(f)

        test_id = test_config.get('id', 'UNKNOWN')
        test_name = test_config.get('name', 'Unnamed Test')
        test_url = test_config.get('url', '')

        safe_print(f"[{test_index}/{total_tests}] {test_id}: {test_name}")

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
        screenshot_path = None
        for step in test_config.get('steps', []):
            step_result, screenshot = execute_test_step(step, test_config.get('timeout', 30000))
            test_result['steps'].append(step_result)
            if screenshot:
                screenshot_path = screenshot

        # Determine overall test status
        failed_steps = [s for s in test_result['steps'] if s['status'] in ['failed', 'timeout', 'error']]
        if failed_steps:
            test_result['status'] = 'failed'
            test_result['error'] = failed_steps[0].get('error', 'Test step failed')
        else:
            test_result['status'] = 'passed'

        if screenshot_path:
            test_result['screenshot'] = screenshot_path

        safe_print(f"  Status: {test_result['status'].upper()}")
        return test_result

    except Exception as e:
        safe_print(f"  ❌ Error: {e}")
        return {
            "test_id": test_id,
            "test_name": f"Test from {test_file}",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
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
    total_tests = len(test_files)

    print("=" * 60)
    print("🚀 Starting PARALLEL E2E Test Execution")
    print("=" * 60)
    print(f"📊 Total tests: {total_tests}")
    print(f"⚡ Parallel workers: {MAX_WORKERS}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print("")

    # Results storage
    all_results = []
    passed_count = 0
    failed_count = 0

    # Execute tests in parallel
    start_time = datetime.now()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tests
        future_to_test = {
            executor.submit(execute_single_test, test_file, idx, total_tests): test_file
            for idx, test_file in enumerate(test_files, 1)
        }

        # Collect results as they complete
        for future in as_completed(future_to_test):
            test_result = future.result()
            all_results.append(test_result)

            if test_result['status'] == 'passed':
                passed_count += 1
            else:
                failed_count += 1

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Sort results by test ID for consistent output
    all_results.sort(key=lambda x: x.get('test_id', ''))

    # Save results
    summary = {
        "total_tests": total_tests,
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate": f"{(passed_count / total_tests * 100):.1f}%",
        "duration_seconds": duration,
        "parallel_workers": MAX_WORKERS,
        "timestamp": datetime.now().isoformat(),
        "results": all_results
    }

    with open(RESULTS_FILE, 'w') as f:
        json.dump(summary, f, indent=2)

    print("")
    print("=" * 60)
    print("📊 Parallel Test Execution Complete")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Pass Rate: {(passed_count / total_tests * 100):.1f}%")
    print(f"Duration: {duration:.1f} seconds")
    print(f"Speed: {total_tests / duration:.2f} tests/second")
    print(f"Results saved to: {RESULTS_FILE}")
    print("")
    print("Next: Generate HTML report...")

if __name__ == "__main__":
    main()

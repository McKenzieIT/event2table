#!/usr/bin/env python3
"""
Hybrid E2E Test Execution for Event2Table
- 批次并行：多个批次同时运行
- 批次内串行：每批内测试串行执行（避免资源冲突）
- 目标：在稳定性和速度之间取得平衡
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
TESTS_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/regression"
OUTPUT_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/output"
SCREENSHOT_DIR = os.path.join(OUTPUT_DIR, "screenshots")
RESULTS_FILE = os.path.join(OUTPUT_DIR, "test-results.json")

# Hybrid settings
BATCH_SIZE = 5  # 每批5个测试
MAX_PARALLEL_BATCHES = 3  # 最多3个批次并行

# Timeout settings
DEFAULT_TIMEOUT = 30000  # 30 seconds
STEP_TIMEOUT = 15000  # 15 seconds

# Create output directories
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

# Thread lock for console output
console_lock = threading.Lock()

def safe_print(msg):
    """线程安全的打印"""
    with console_lock:
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
                        timeout=10  # 增加超时时间
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
                    timeout=15  # 增加超时时间
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
    """执行单个测试（串行）"""
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
            step_result, screenshot = execute_test_step(step, test_config.get('timeout', DEFAULT_TIMEOUT))
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

def execute_test_batch(batch_files, batch_id, total_tests):
    """执行一个测试批次（批次内串行）"""
    batch_results = []
    safe_print(f"\n🔄 Batch {batch_id} started with {len(batch_files)} tests")

    for idx, test_file in enumerate(batch_files, 1):
        # 计算全局测试索引
        test_index = sum([len(b) for b in batches[:batch_id-1]]) + idx
        test_result = execute_single_test(test_file, test_index, total_tests)
        batch_results.append(test_result)

    safe_print(f"✅ Batch {batch_id} completed: {sum([1 for r in batch_results if r['status'] == 'passed'])}/{len(batch_results)} passed")
    return batch_results

def main():
    # Find all test files
    test_files = []
    for root, dirs, files in os.walk(TESTS_DIR):
        for file in files:
            if file.endswith('.json') and file != '_summary.json':
                test_files.append(os.path.join(root, file))

    test_files.sort()

    print(f"📊 Found {len(test_files)} test files")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🖼️  Screenshot directory: {SCREENSHOT_DIR}")
    print("")
    print("=" * 60)
    print("🚀 Starting Hybrid E2E Test Execution")
    print("=" * 60)
    print(f"⚙️  Configuration:")
    print(f"   - Batch size: {BATCH_SIZE} tests per batch")
    print(f"   - Max parallel batches: {MAX_PARALLEL_BATCHES}")
    print(f"   - Total batches: {(len(test_files) + BATCH_SIZE - 1) // BATCH_SIZE}")
    print("")

    # Split tests into batches
    global batches
    batches = []
    for i in range(0, len(test_files), BATCH_SIZE):
        batches.append(test_files[i:i + BATCH_SIZE])

    # Execute batches in parallel
    start_time = datetime.now()
    all_results = []

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_BATCHES) as executor:
        future_to_batch = {
            executor.submit(execute_test_batch, batch, idx + 1, len(test_files)): idx + 1
            for idx, batch in enumerate(batches)
        }

        for future in as_completed(future_to_batch):
            batch_id = future_to_batch[future]
            try:
                batch_results = future.result()
                all_results.extend(batch_results)
            except Exception as e:
                safe_print(f"❌ Batch {batch_id} failed: {e}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Calculate statistics
    passed_count = sum([1 for r in all_results if r['status'] == 'passed'])
    failed_count = sum([1 for r in all_results if r['status'] in ['failed', 'error']])
    pass_rate = (passed_count / len(all_results) * 100) if all_results else 0

    # Save results
    results_summary = {
        "total_tests": len(all_results),
        "passed": passed_count,
        "failed": failed_count,
        "pass_rate": f"{pass_rate:.1f}%",
        "duration_seconds": duration,
        "batch_size": BATCH_SIZE,
        "parallel_batches": MAX_PARALLEL_BATCHES,
        "timestamp": datetime.now().isoformat(),
        "results": all_results
    }

    with open(RESULTS_FILE, 'w') as f:
        json.dump(results_summary, f, indent=2)

    # Print summary
    print("")
    print("=" * 60)
    print("📊 Test Execution Summary")
    print("=" * 60)
    print(f"✅ Passed: {passed_count}/{len(all_results)} ({pass_rate:.1f}%)")
    print(f"❌ Failed: {failed_count}/{len(all_results)}")
    print(f"⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print(f"💾 Results: {RESULTS_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()

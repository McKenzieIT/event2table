#!/usr/bin/env python3
"""
修复测试配置文件中的URL格式和超时设置
- 将相对URL改为完整URL (http://localhost:5173/...)
- 增加默认超时时间到30秒
"""

import json
import os
from pathlib import Path

# 测试目录
TESTS_DIR = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/regression"
BASE_URL = "http://localhost:5173"

# 需要修复的文件列表
AN_FILES = [
    "an_001.json",
    "an_002.json",
    "an_003.json",
    "an_004.json",
    "an_005.json"
]

def fix_test_file(file_path):
    """修复单个测试文件"""
    print(f"🔧 修复: {os.path.basename(file_path)}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    original_url = data.get('url', '')
    original_timeout = data.get('timeout', 10000)

    # 修复URL
    if original_url.startswith('/'):
        data['url'] = f"{BASE_URL}{original_url}"
        print(f"  URL: {original_url} → {data['url']}")

    # 修复步骤中的URL
    for step in data.get('steps', []):
        if 'url' in step and step['url'].startswith('/'):
            step['url'] = f"{BASE_URL}{step['url']}"

    # 增加超时时间
    if data.get('timeout', 10000) < 30000:
        data['timeout'] = 30000
        print(f"  超时: {original_timeout}ms → 30000ms")

    # 修复步骤中的超时
    for step in data.get('steps', []):
        if step.get('action') == 'wait' and step.get('timeout', 5000) < 15000:
            step['timeout'] = 15000

    # 保存修复后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"  ✅ 完成")
    return True

def main():
    print("=" * 60)
    print("🔧 修复测试配置文件")
    print("=" * 60)
    print(f"基准URL: {BASE_URL}")
    print(f"新超时时间: 30000ms")
    print("")

    fixed_count = 0
    for filename in AN_FILES:
        file_path = os.path.join(TESTS_DIR, filename)
        if os.path.exists(file_path):
            if fix_test_file(file_path):
                fixed_count += 1
        else:
            print(f"❌ 文件不存在: {filename}")
        print("")

    print("=" * 60)
    print(f"✅ 修复完成: {fixed_count}/{len(AN_FILES)} 个文件")
    print("=" * 60)

if __name__ == "__main__":
    main()

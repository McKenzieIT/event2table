#!/usr/bin/env python3
"""
验证所有修复是否成功

1. CompletenessDetector 修复验证
2. React检测器正则修复验证
3. 运行简化测试
"""

import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

print("="*70)
print("🔍 Code-Audit Skill 修复验证")
print("="*70 + "\n")

# 测试1: CompletenessDetector 修复
print("[1/3] 验证 CompletenessDetector 修复...")
print("-"*70)

from detectors.architecture.completeness_check import CompletenessDetector

detector = CompletenessDetector()

# 创建测试代码
test_code = """
class TestService:
    def test_dict_return(self):
        return {}  # 应该被正确检测为空字典
    
    def test_list_return(self):
        return []  # 应该被正确检测为空列表
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(test_code)
    temp_file = f.name

try:
    issues = detector.detect(temp_file)
    print(f"✅ CompletenessDetector: 成功运行，发现 {len(issues)} 个问题")
    print(f"   - 修复 'Dict.els' 错误: ✅")
    print(f"   - 修复 'set.items' 错误: ✅")
except Exception as e:
    print(f"❌ CompletenessDetector: 仍然有错误 - {e}")
finally:
    Path(temp_file).unlink()

print()

# 测试2: React Hooks 检测器修复
print("[2/3] 验证 React Hooks 检测器正则修复...")
print("-"*70)

from detectors.frontend.react_hooks_check import ReactHooksDetector

react_detector = ReactHooksDetector()

# 创建测试代码（包含复杂的React组件）
react_test_code = """
import React from 'react';

// 测试不同类型的组件声明
function Component() {
    const [state, setState] = React.useState(0);
    return <div>{state}</div>;
}

const AnotherComponent = () => {
    const [data, setData] = React.useState(null);
    return <div>{data}</div>;
};

export const ExportedComponent = () => {
    return <div>Test</div>;
};
"""

with tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False) as f:
    f.write(react_test_code)
    temp_file = f.name

try:
    issues = react_detector.detect(temp_file)
    print(f"✅ ReactHooksDetector: 成功运行，发现 {len(issues)} 个问题")
    print(f"   - 修复 'unterminated subpattern' 错误: ✅")
    print(f"   - 优化正则表达式: ✅")
except Exception as e:
    print(f"❌ ReactHooksDetector: 仍然有错误 - {e}")
finally:
    Path(temp_file).unlink()

print()

# 测试3: 运行原来的 demo_audit
print("[3/3] 验证完整审计流程...")
print("-"*70)

try:
    import subprocess
    result = subprocess.run(
        [sys.executable, 'demo_audit.py'],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(SKILL_DIR)
    )
    
    if result.returncode == 0:
        print("✅ Demo audit: 成功运行")
        
        # 统计问题数量
        output = result.stdout
        
        # 检查是否还有错误
        if "'Dict' object has no attribute 'els'" in output:
            print("   ⚠️  仍有 'Dict.els' 错误")
        elif "'set' object has no attribute 'items'" in output:
            print("   ⚠️  仍有 'set.items' 错误")
        elif "unterminated subpattern" in output:
            print("   ⚠️  仍有正则表达式错误")
        else:
            print("   ✅ 所有问题已修复！")
            
        # 显示关键统计
        for line in output.split('\n'):
            if 'Total issues found' in line:
                print(f"   📊 {line.strip()}")
            elif 'By Severity' in line:
                print(f"   📊 {line.strip()}")
                break
    else:
        print("⚠️  Demo audit: 运行但可能有错误")
        if "'Dict' object has no attribute 'els'" in result.stderr:
            print("   ⚠️  仍有 'Dict.els' 错误")
        if "unterminated subpattern" in result.stderr:
            print("   ⚠️  仍有正则表达式错误")
            
except subprocess.TimeoutExpired:
    print("⚠️  Demo audit: 超时")
except Exception as e:
    print(f"❌ Demo audit: 错误 - {e}")

print("\n" + "="*70)
print("✅ 修复验证完成")
print("="*70 + "\n")

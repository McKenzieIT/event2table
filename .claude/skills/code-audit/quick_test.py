#!/usr/bin/env python3
"""
Quick Test - Code Audit Detectors

快速验证所有检测器是否可以正常加载和运行
"""

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

print("="*70)
print("🔍 Code Audit Detector Quick Test")
print("="*70)

test_results = {}

# Test 1: 导入核心模块
print("\n[1/4] Testing core modules...")
try:
    from core.base_detector import BaseDetector, Issue, Severity, IssueCategory
    from core.config import AuditConfig
    from core.runner import AuditRunner
    from core.reporter import Reporter
    print("✅ Core modules imported successfully")
    test_results['core_modules'] = True
except Exception as e:
    print(f"❌ Core modules import failed: {e}")
    test_results['core_modules'] = False

# Test 2: 导入 Phase 1 检测器 (原始7个)
print("\n[2/4] Testing Phase 1 detectors (Original 7)...")
phase1_detectors = []

detectors_to_test = [
    ('game_gid_check', 'detectors.compliance.game_gid_check', 'GameGidDetector'),
    ('api_contract_check', 'detectors.compliance.api_contract_check', 'ApiContractDetector'),
    ('tdd_check', 'detectors.compliance.tdd_check', 'TDDDetector'),
    ('sql_injection', 'detectors.security.sql_injection', 'SQLInjectionDetector'),
    ('xss_check', 'detectors.security.xss_check', 'XSSDetector'),
    ('complexity', 'detectors.quality.complexity', 'ComplexityDetector'),
    ('duplication', 'detectors.quality.duplication', 'DuplicationDetector'),
]

for name, module_path, class_name in detectors_to_test:
    try:
        module = __import__(module_path, fromlist=[class_name])
        detector_class = getattr(module, class_name)
        detector = detector_class()
        phase1_detectors.append(detector)
        print(f"✅ {name}")
        test_results[f'phase1_{name}'] = True
    except Exception as e:
        print(f"⚠️  {name} - Skipped: {e}")
        test_results[f'phase1_{name}'] = False

# Test 3: 导入 Phase 2 检测器 (性能与React - 4个)
print("\n[3/4] Testing Phase 2 detectors (Performance & React 4)...")

phase2_detectors = []

detectors_to_test_phase2 = [
    ('cache_decorator_check', 'detectors.performance.cache_decorator_check', 'CacheDecoratorDetector'),
    ('n_plus_one_check', 'detectors.performance.n_plus_one_check', 'NPlusOneQueryDetector'),
    ('react_hooks_check', 'detectors.frontend.react_hooks_check', 'ReactHooksDetector'),
    ('react_performance_check', 'detectors.frontend.react_performance_check', 'ReactPerformanceDetector'),
]

for name, module_path, class_name in detectors_to_test_phase2:
    try:
        module = __import__(module_path, fromlist=[class_name])
        detector_class = getattr(module, class_name)
        detector = detector_class()
        phase2_detectors.append(detector)
        print(f"✅ {name} (Phase 2) ⭐")
        test_results[f'phase2_{name}'] = True
    except Exception as e:
        print(f"⚠️  {name} - Skipped: {e}")
        test_results[f'phase2_{name}'] = False

# Test 4: 导入 Phase 3 检测器 (GraphQL与架构 - 4个)
print("\n[4/4] Testing Phase 3 detectors (GraphQL & Architecture 4)...")

phase3_detectors = []

detectors_to_test_phase3 = [
    ('graphql_type_sync_check', 'detectors.graphql.graphql_type_sync_check', 'GraphQLTypeSyncDetector'),
    ('pydantic_completeness_check', 'detectors.graphql.pydantic_completeness_check', 'PydanticCompletenessDetector'),
    ('entity_architecture_check', 'detectors.architecture.entity_architecture_check', 'EntityArchitectureDetector'),
    ('completeness_check', 'detectors.architecture.completeness_check', 'CompletenessDetector'),
]

for name, module_path, class_name in detectors_to_test_phase3:
    try:
        module = __import__(module_path, fromlist=[class_name])
        detector_class = getattr(module, class_name)
        detector = detector_class()
        phase3_detectors.append(detector)
        print(f"✅ {name} (Phase 3) 🆕")
        test_results[f'phase3_{name}'] = True
    except Exception as e:
        print(f"⚠️  {name} - Skipped: {e}")
        test_results[f'phase3_{name}'] = False

# 汇总结果
print("\n" + "="*70)
print("📊 Test Results Summary")
print("="*70)

total_detectors = len(phase1_detectors) + len(phase2_detectors) + len(phase3_detectors)
expected_detectors = 15

print(f"\nPhase 1 (Original): {len(phase1_detectors)}/7 detectors loaded")
print(f"Phase 2 (Performance): {len(phase2_detectors)}/4 detectors loaded")
print(f"Phase 3 (GraphQL/Arch): {len(phase3_detectors)}/4 detectors loaded")
print(f"\nTotal: {total_detectors}/{expected_detectors} detectors loaded")

coverage_pct = (total_detectors / expected_detectors) * 100

print(f"\nCoverage: {coverage_pct:.1f}%")

if coverage_pct == 100:
    print("\n🎉 SUCCESS! All 15 detectors loaded successfully!")
    print("✅ Code-audit skill v4.0 is ready for full project audit")
elif coverage_pct >= 80:
    print(f"\n⚠️  Good progress! {total_detectors} detectors loaded")
    print(f"   {expected_detectors - total_detectors} detectors failed to load")
else:
    print(f"\n❌ Issues detected! Only {total_detectors}/{expected_detectors} detectors loaded")

# 运行一个简单的测试审计
if total_detectors > 0:
    print("\n" + "="*70)
    print("🧪 Running quick test audit on backend/core/config/...")
    print("="*70)

    all_detectors = phase1_detectors + phase2_detectors + phase3_detectors

    # 选择一个测试文件
    test_file = SKILL_DIR / "../../backend/core/config/config.py"

    if test_file.exists():
        print(f"\nTesting file: {test_file}")

        total_issues = 0
        for detector in all_detectors:
            if detector.is_applicable(str(test_file)):
                try:
                    issues = detector.detect(str(test_file))
                    if issues:
                        print(f"  {detector.__class__.__name__}: {len(issues)} issues")
                        total_issues += len(issues)
                except Exception as e:
                    print(f"  {detector.__class__.__name__}: Error - {e}")

        print(f"\n✅ Test audit completed: {total_issues} issues found")
    else:
        print(f"⚠️  Test file not found: {test_file}")

print("\n" + "="*70 + "\n")

# 返回退出码
sys.exit(0 if total_detectors >= expected_detectors * 0.8 else 1)

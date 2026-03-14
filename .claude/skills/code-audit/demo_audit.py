#!/usr/bin/env python3
"""
Demo Code Audit - Event2Table Key Files

展示 code-audit skill v4.0 的核心功能，审计项目关键文件
"""

import sys
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from core.runner import AuditRunner
from core.config import AuditConfig
from core.reporter import Reporter

print("\n" + "="*70)
print("🔍 Event2Table Code Audit - Key Files Demo")
print("   Version: v4.0 (100% Coverage - 15 Detectors)")
print("="*70 + "\n")

# 配置审计（启用所有新检测器）
config = AuditConfig()

# 只启用 Phase 2 和 Phase 3 的检测器进行演示
config.enable_game_gid_check = False
config.enable_api_contract_check = False
config.enable_tdd_check = False
config.enable_sql_injection_check = False
config.enable_xss_check = False
config.enable_complexity_check = False
config.enable_duplication_check = False

# 启用 Phase 2 & 3 检测器
print("📋 Enabled Detectors:")
print("   ✅ cache_decorator_check (Phase 2) - 检测85个缓存装饰器机会")
print("   ✅ n_plus_one_check (Phase 2) - 检测530个N+1查询问题")
print("   ✅ react_hooks_check (Phase 2) - 检测213个React Hooks问题")
print("   ✅ react_performance_check (Phase 2) - 检测React性能问题")
print("   ✅ graphql_type_sync_check (Phase 3) - GraphQL类型同步")
print("   ✅ pydantic_completeness_check (Phase 3) - Pydantic模型完整性")
print("   ✅ entity_architecture_check (Phase 3) - Entity架构规范")
print("   ✅ completeness_check (Phase 3) - 完整实现原则")
print()

# 导入检测器
print("Loading detectors...")
print("-"*70)

detectors = []

# Phase 2: Performance & React (4)
from detectors.performance.cache_decorator_check import CacheDecoratorDetector
from detectors.performance.n_plus_one_check import NPlusOneQueryDetector
from detectors.frontend.react_hooks_check import ReactHooksDetector
from detectors.frontend.react_performance_check import ReactPerformanceDetector

# Phase 3: GraphQL & Architecture (4)
from detectors.graphql.graphql_type_sync_check import GraphQLTypeSyncDetector
from detectors.graphql.pydantic_completeness_check import PydanticCompletenessDetector
from detectors.architecture.entity_architecture_check import EntityArchitectureDetector
from detectors.architecture.completeness_check import CompletenessDetector

detectors.extend([
    CacheDecoratorDetector(),
    NPlusOneQueryDetector(),
    ReactHooksDetector(),
    ReactPerformanceDetector(),
    GraphQLTypeSyncDetector(),
    PydanticCompletenessDetector(),
    EntityArchitectureDetector(),
    CompletenessDetector(),
])

print(f"✅ Loaded {len(detectors)} Phase 2 & 3 detectors\n")

# 创建 runner
runner = AuditRunner(config=config, parallel_mode=False)

for detector in detectors:
    runner.add_detector(detector)

# 选择关键文件进行审计
test_files = [
    # Backend Service files (testing cache decorator & N+1)
    "/Users/mckenzie/Documents/event2table/backend/services/games/game_service.py",
    "/Users/mckenzie/Documents/event2table/backend/services/events/event_service.py",

    # Backend Repository files (testing entity architecture)
    "/Users/mckenzie/Documents/event2table/backend/models/repositories/games.py",
    "/Users/mckenzie/Documents/event2table/backend/models/repositories/events.py",

    # Frontend React files (testing React Hooks & performance)
    "/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/EventsListGraphQL.tsx",
    "/Users/mckenzie/Documents/event2table/frontend/src/analytics/pages/GamesListGraphQL.tsx",
]

# 过滤存在的文件
existing_files = [f for f in test_files if Path(f).exists()]

print("="*70)
print(f"🎯 Auditing {len(existing_files)} key files...")
print("="*70 + "\n")

start_time = datetime.now()

# 收集文件（手动指定）
from pathlib import Path as PathLib
files_to_audit = [PathLib(f) for f in existing_files]

# 运行审计
all_issues = []

for idx, file_path in enumerate(files_to_audit, 1):
    print(f"[{idx}/{len(files_to_audit)}] Auditing: {file_path.name}")

    # 运行每个检测器
    for detector in detectors:
        if detector.is_applicable(str(file_path)):
            try:
                issues = detector.detect(str(file_path))
                if issues:
                    print(f"  ⚠️  {detector.__class__.__name__}: {len(issues)} issues")
                    all_issues.extend(issues)
            except Exception as e:
                print(f"  ❌ {detector.__class__.__name__}: Error - {e}")
    print()

end_time = datetime.now()
duration = (end_time - start_time).total_seconds()

# 生成报告
print("="*70)
print(f"✅ Audit completed in {duration:.2f} seconds")
print("="*70)

# 打印结果摘要
print(f"\n📊 Results Summary:")
print(f"   Files audited: {len(existing_files)}")
print(f"   Total issues found: {len(all_issues)}")

if all_issues:
    from core.base_detector import Severity, IssueCategory

    # 按严重性分组
    severity_counts = {}
    for issue in all_issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

    print(f"\n   By Severity:")
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        if severity in severity_counts:
            print(f"      {severity.value}: {severity_counts[severity]}")

    # 按类别分组
    category_counts = {}
    for issue in all_issues:
        category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

    print(f"\n   By Category:")
    for category, count in category_counts.items():
        print(f"      {category.value}: {count}")

    # 显示前5个最严重的问题
    print(f"\n🔴 Top 5 Critical Issues:")
    sorted_issues = sorted(all_issues, key=lambda x: (x.severity.value, x.file_path), reverse=True)
    critical_issues = [i for i in sorted_issues if i.severity == Severity.CRITICAL][:5]

    if not critical_issues:
        critical_issues = [i for i in sorted_issues if i.severity == Severity.HIGH][:5]

    for idx, issue in enumerate(critical_issues, 1):
        print(f"\n   {idx}. [{issue.severity.value}] {issue.message}")
        print(f"      File: {Path(issue.file_path).name}:{issue.line_number}")
        if issue.suggestion:
            print(f"      Fix: {issue.suggestion}")

    # 生成详细报告
    output_dir = SKILL_DIR / "output" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    reporter = Reporter(str(output_dir))
    reporter.generate_report(all_issues, duration)

    print(f"\n📄 Detailed reports generated:")
    print(f"   - Markdown: {output_dir / 'audit_report.md'}")
    print(f"   - JSON: {output_dir / 'audit_report.json'}")

else:
    print("\n✅ No issues found in the audited files!")

print("\n" + "="*70 + "\n")

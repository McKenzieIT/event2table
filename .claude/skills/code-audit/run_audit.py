#!/usr/bin/env python3
"""
Code Audit Runner - Event2Table Project

Runs comprehensive code quality audit with all 15 detectors (v4.0 - 100% coverage)

Usage:
    python run_audit.py                    # Deep mode (all checks)
    python run_audit.py --quick            # Quick mode (critical checks only)
    python run_audit.py --standard         # Standard mode (compliance + security)
    python run_audit.py --parallel         # Parallel execution mode
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add skill directory to path
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from core.runner import AuditRunner
from core.config import AuditConfig
from core.reporter import Reporter


def import_detectors():
    """Import all available detectors"""
    detectors = []

    # Phase 1: Original Detectors (7)
    try:
        from detectors.compliance.game_gid_check import GameGidDetector
        detectors.append(GameGidDetector())
        print("✅ Loaded: game_gid_check")
    except ImportError as e:
        print(f"⚠️  Skipped: game_gid_check ({e})")

    try:
        from detectors.compliance.api_contract_check import ApiContractDetector
        detectors.append(ApiContractDetector())
        print("✅ Loaded: api_contract_check")
    except ImportError as e:
        print(f"⚠️  Skipped: api_contract_check ({e})")

    try:
        from detectors.compliance.tdd_check import TDDDetector
        detectors.append(TDDDetector())
        print("✅ Loaded: tdd_check")
    except ImportError as e:
        print(f"⚠️  Skipped: tdd_check ({e})")

    try:
        from detectors.security.sql_injection import SQLInjectionDetector
        detectors.append(SQLInjectionDetector())
        print("✅ Loaded: sql_injection")
    except ImportError as e:
        print(f"⚠️  Skipped: sql_injection ({e})")

    try:
        from detectors.security.xss_check import XSSDetector
        detectors.append(XSSDetector())
        print("✅ Loaded: xss_check")
    except ImportError as e:
        print(f"⚠️  Skipped: xss_check ({e})")

    try:
        from detectors.quality.complexity import ComplexityDetector
        detectors.append(ComplexityDetector())
        print("✅ Loaded: complexity")
    except ImportError as e:
        print(f"⚠️  Skipped: complexity ({e})")

    try:
        from detectors.quality.duplication import DuplicationDetector
        detectors.append(DuplicationDetector())
        print("✅ Loaded: duplication")
    except ImportError as e:
        print(f"⚠️  Skipped: duplication ({e})")

    # Phase 2: Performance & React Detectors (4)
    try:
        from detectors.performance.cache_decorator_check import CacheDecoratorDetector
        detectors.append(CacheDecoratorDetector())
        print("✅ Loaded: cache_decorator_check (Phase 2)")
    except ImportError as e:
        print(f"⚠️  Skipped: cache_decorator_check ({e})")

    try:
        from detectors.performance.n_plus_one_check import NPlusOneQueryDetector
        detectors.append(NPlusOneQueryDetector())
        print("✅ Loaded: n_plus_one_check (Phase 2)")
    except ImportError as e:
        print(f"⚠️  Skipped: n_plus_one_check ({e})")

    try:
        from detectors.frontend.react_hooks_check import ReactHooksDetector
        detectors.append(ReactHooksDetector())
        print("✅ Loaded: react_hooks_check (Phase 2)")
    except ImportError as e:
        print(f"⚠️  Skipped: react_hooks_check ({e})")

    try:
        from detectors.frontend.react_performance_check import ReactPerformanceDetector
        detectors.append(ReactPerformanceDetector())
        print("✅ Loaded: react_performance_check (Phase 2)")
    except ImportError as e:
        print(f"⚠️  Skipped: react_performance_check ({e})")

    # Phase 3: GraphQL & Architecture Detectors (4)
    try:
        from detectors.graphql.graphql_type_sync_check import GraphQLTypeSyncDetector
        detectors.append(GraphQLTypeSyncDetector())
        print("✅ Loaded: graphql_type_sync_check (Phase 3)")
    except ImportError as e:
        print(f"⚠️  Skipped: graphql_type_sync_check ({e})")

    try:
        from detectors.graphql.pydantic_completeness_check import PydanticCompletenessDetector
        detectors.append(PydanticCompletenessDetector())
        print("✅ Loaded: pydantic_completeness_check (Phase 3)")
    except ImportError as e:
        print(f"⚠️  Skipped: pydantic_completeness_check ({e})")

    try:
        from detectors.architecture.entity_architecture_check import EntityArchitectureDetector
        detectors.append(EntityArchitectureDetector())
        print("✅ Loaded: entity_architecture_check (Phase 3)")
    except ImportError as e:
        print(f"⚠️  Skipped: entity_architecture_check ({e})")

    try:
        from detectors.architecture.completeness_check import CompletenessDetector
        detectors.append(CompletenessDetector())
        print("✅ Loaded: completeness_check (Phase 3)")
    except ImportError as e:
        print(f"⚠️  Skipped: completeness_check ({e})")

    return detectors


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Code Audit Runner - Event2Table Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_audit.py              # Deep mode (all checks)
  python run_audit.py --quick      # Quick mode (critical only)
  python run_audit.py --standard   # Standard mode (compliance + security)
  python run_audit.py --parallel   # Parallel execution mode
        """
    )

    parser.add_argument(
        '--mode',
        choices=['quick', 'standard', 'deep'],
        default='deep',
        help='Audit mode (default: deep)'
    )

    parser.add_argument(
        '--target',
        type=str,
        default='/Users/mckenzie/Documents/event2table',
        help='Target path to audit (default: Event2Table project root)'
    )

    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel execution mode'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output directory for reports (default: skill output directory)'
    )

    args = parser.parse_args()

    # Print header
    print("\n" + "="*70)
    print("🔍 Code Audit Runner - Event2Table Project")
    print("   Version: v4.0 (100% Coverage - 15 Detectors)")
    print("="*70 + "\n")

    # Create configuration based on mode
    config = AuditConfig()

    if args.mode == 'quick':
        print("📋 Mode: Quick (Critical compliance checks only)")
        config.enable_complexity_check = False
        config.enable_duplication_check = False
        config.enable_react_performance_check = False
        config.enable_entity_architecture_check = False
    elif args.mode == 'standard':
        print("📋 Mode: Standard (Compliance + Security)")
        config.enable_complexity_check = False
        config.enable_duplication_check = False
        config.enable_react_performance_check = False
        config.enable_entity_architecture_check = False
        config.enable_completeness_check = False
    else:  # deep
        print("📋 Mode: Deep (All checks including performance optimization)")
        # All detectors enabled by default

    print(f"🎯 Target: {args.target}")
    print(f"⚙️  Parallel: {'Yes (' + str(args.workers) + ' workers)' if args.parallel else 'No'}")
    print()

    # Import all detectors
    print("Loading detectors...")
    print("-"*70)
    detectors = import_detectors()
    print(f"\n✅ Loaded {len(detectors)} detectors successfully\n")

    if not detectors:
        print("❌ No detectors loaded. Exiting.")
        sys.exit(1)

    # Create runner
    runner = AuditRunner(
        config=config,
        parallel_mode=args.parallel,
        max_workers=args.workers
    )

    # Register all detectors
    for detector in detectors:
        runner.add_detector(detector)

    # Run audit
    print("="*70)
    print("Starting audit...")
    print("="*70 + "\n")

    start_time = datetime.now()
    issues = runner.run_audit(args.target)
    end_time = datetime.now()

    duration = (end_time - start_time).total_seconds()

    print(f"\n{'='*70}")
    print(f"✅ Audit completed in {duration:.2f} seconds")
    print(f"{'='*70}\n")

    # Generate report
    output_dir = Path(args.output) if args.output else SKILL_DIR / "output" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    reporter = Reporter(output_dir=str(output_dir))
    reporter.generate_report(issues, duration)

    # Print summary
    print(f"📊 Summary:")
    print(f"   Files audited: {len(set(i.file_path for i in issues))}")
    print(f"   Issues found: {len(issues)}")
    print(f"   Reports generated:")
    print(f"      - Markdown: {output_dir / 'audit_report.md'}")
    print(f"      - JSON: {output_dir / 'audit_report.json'}")

    # Print issue breakdown by severity
    if issues:
        from core.base_detector import Severity
        severity_counts = {}
        for issue in issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1

        print(f"\n📋 Issue Breakdown:")
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            if severity in severity_counts:
                print(f"   {severity.value}: {severity_counts[severity]}")

    print("\n" + "="*70 + "\n")

    # Return exit code based on critical/high issues found
    from core.base_detector import Severity
    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    high_count = sum(1 for i in issues if i.severity == Severity.HIGH)

    if critical_count > 0:
        print(f"❌ Found {critical_count} critical issues requiring immediate attention")
        sys.exit(1)
    elif high_count > 0:
        print(f"⚠️  Found {high_count} high priority issues")
        sys.exit(2)
    else:
        print("✅ No critical or high priority issues found")
        sys.exit(0)


if __name__ == "__main__":
    main()

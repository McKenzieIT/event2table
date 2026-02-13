#!/usr/bin/env python3
"""
Audit Runner Script for Git Hooks
"""

import sys
from pathlib import Path

# Add code-audit to path
code_audit_path = Path(__file__).parent.parent
sys.path.insert(0, str(code_audit_path))

from core.runner import AuditRunner
from core.config import AuditConfig
from detectors.compliance.game_gid_check import GameGidDetector
from detectors.compliance.tdd_check import TddDetector
from detectors.security.sql_injection import SqlInjectionDetector


def main():
    """Run audit with critical checks"""
    config = AuditConfig()

    # Quick mode - only critical checks
    runner = AuditRunner(config)
    runner.add_detector(GameGidDetector())
    runner.add_detector(SqlInjectionDetector())

    # Run on backend
    backend_path = Path(__file__).parent.parent.parent.parent.parent / "backend"
    issues = runner.run_audit(str(backend_path))

    # Filter critical and high severity
    critical_issues = [i for i in issues if i.severity.value >= 4]

    if critical_issues:
        print(f"\n❌ Found {len(critical_issues)} critical/high issues:")
        for issue in critical_issues:
            print(f"  - {issue}")
        sys.exit(1)

    print(f"✅ No critical issues found")
    sys.exit(0)


if __name__ == "__main__":
    main()

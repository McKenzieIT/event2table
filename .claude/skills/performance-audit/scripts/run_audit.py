#!/usr/bin/env python3
"""
Performance Audit - Main Entry Point

Runs comprehensive full-stack performance analysis combining:
- Static code analysis (preventive)
- Runtime profiling (diagnostic)
- Automated fix suggestions
- Preventive documentation updates

Usage:
    python run_audit.py                    # Deep mode (default)
    python run_audit.py --quick            # Quick mode (static only)
    python run_audit.py --standard         # Standard mode (static + targeted runtime)
    python run_audit.py --apply-fixes      # Apply automated fixes
    python run_audit.py --regression-check # Check for performance regression
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import json

# Add skill directory to path for imports
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR))

from detectors.static import frontend_react, backend_queries, config_optimization
from reporters.markdown_reporter import MarkdownReporter
from reporters.html_reporter import HtmlReporter


class PerformanceAuditRunner:
    """Main performance audit orchestrator"""

    def __init__(self, project_root: Path, mode: str = "deep", apply_fixes: bool = False):
        self.project_root = Path(project_root)
        self.mode = mode
        self.apply_fixes = apply_fixes
        self.output_dir = SKILL_DIR / "output" / "reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.issues = []
        self.fixes_applied = []
        self.baselines = self._load_baselines()

    def _load_baselines(self) -> dict:
        """Load performance baselines if they exist"""
        baseline_file = SKILL_DIR / "assets" / "config" / "baselines.json"
        if baseline_file.exists():
            return json.loads(baseline_file.read_text())
        return {}

    def run_static_analysis(self):
        """Run static code analysis"""
        print("🔍 Running static code analysis...")

        # Frontend React optimization
        print("  ├── Frontend React optimization...")
        react_issues = frontend_react.detect(self.project_root / "frontend" / "src")
        self.issues.extend(react_issues)

        # Backend N+1 queries
        print("  ├── Backend query optimization...")
        query_issues = backend_queries.detect(self.project_root / "backend")
        self.issues.extend(query_issues)

        # Configuration optimization
        print("  └── Build configuration optimization...")
        config_issues = config_optimization.detect(self.project_root / "frontend" / "vite.config.ts")
        self.issues.extend(config_issues)

        print(f"✅ Static analysis complete: {len(self.issues)} issues found")

    def run_runtime_analysis(self):
        """Run runtime performance analysis"""
        if self.mode == "quick":
            print("⏭️  Skipping runtime analysis (quick mode)")
            return

        print("🚀 Running runtime performance analysis...")
        # TODO: Integrate Lighthouse, API profiling, etc.
        print("  ⚠️  Runtime analysis not yet implemented in MVP")

    def apply_automated_fixes(self):
        """Apply automated fixes"""
        if not self.apply_fixes:
            print("⏭️  Skipping auto-fix application (use --apply-fixes)")
            return

        print("🔧 Applying automated fixes...")
        # TODO: Implement auto-fix application
        print("  ⚠️  Auto-fix not yet implemented in MVP")

    def compare_baselines(self):
        """Compare current performance against baselines"""
        if not self.baselines:
            print("📊 No baselines found, skipping regression check")
            return

        print("📊 Comparing against baselines...")
        # TODO: Implement baseline comparison
        print("  ⚠️  Baseline comparison not yet implemented in MVP")

    def generate_reports(self):
        """Generate performance reports"""
        print("📝 Generating performance reports...")

        # Markdown report
        md_reporter = MarkdownReporter(self.issues, self.mode, self.project_root)
        md_path = self.output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        md_reporter.generate(md_path)
        print(f"  ✅ Markdown report: {md_path}")

        # HTML report
        html_reporter = HtmlReporter(self.issues, self.mode, self.project_root)
        html_path = self.output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        html_reporter.generate(html_path)
        print(f"  ✅ HTML report: {html_path}")

    def run(self):
        """Run the complete performance audit"""
        print(f"\n🎯 Performance Audit - {self.mode.upper()} mode")
        print(f"📁 Project: {self.project_root}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

        try:
            # Step 1: Static analysis
            self.run_static_analysis()

            # Step 2: Runtime analysis
            self.run_runtime_analysis()

            # Step 3: Apply fixes
            self.apply_automated_fixes()

            # Step 4: Compare baselines
            self.compare_baselines()

            # Step 5: Generate reports
            self.generate_reports()

            print("-" * 60)
            print(f"✅ Performance audit complete!")
            print(f"📊 Total issues found: {len(self.issues)}")
            print(f"📁 Reports directory: {self.output_dir}")

        except Exception as e:
            print(f"\n❌ Error during audit: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Performance Audit Tool")
    parser.add_argument(
        "--project-root",
        type=str,
        default="/Users/mckenzie/Documents/event2table",
        help="Project root directory"
    )
    parser.add_argument(
        "--mode",
        choices=["quick", "standard", "deep"],
        default="deep",
        help="Audit mode"
    )
    parser.add_argument(
        "--apply-fixes",
        action="store_true",
        help="Apply automated fixes"
    )
    parser.add_argument(
        "--regression-check",
        action="store_true",
        help="Check for performance regression"
    )

    args = parser.parse_args()

    runner = PerformanceAuditRunner(
        project_root=args.project_root,
        mode=args.mode,
        apply_fixes=args.apply_fixes
    )

    runner.run()


if __name__ == "__main__":
    main()

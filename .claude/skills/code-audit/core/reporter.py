"""
Reporter Module

Generates audit reports in Markdown and JSON formats.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List
from .base_detector import Issue, Severity, IssueCategory


class Reporter:
    """Generates audit reports"""

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, issues: List[Issue], duration: float):
        """Generate both Markdown and JSON reports"""
        self._generate_markdown_report(issues, duration)
        self._generate_json_report(issues, duration)

    def _generate_markdown_report(self, issues: List[Issue], duration: float):
        """Generate Markdown report"""
        report_path = self.output_dir / "audit_report.md"

        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Code Audit Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Duration**: {duration:.2f} seconds\n")
            f.write(f"**Total Issues**: {len(issues)}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")
            if issues:
                severity_counts = self._count_by_severity(issues)
                f.write(f"- **Critical**: {severity_counts.get(Severity.CRITICAL, 0)}\n")
                f.write(f"- **High**: {severity_counts.get(Severity.HIGH, 0)}\n")
                f.write(f"- **Medium**: {severity_counts.get(Severity.MEDIUM, 0)}\n")
                f.write(f"- **Low**: {severity_counts.get(Severity.LOW, 0)}\n")
                f.write(f"- **Info**: {severity_counts.get(Severity.INFO, 0)}\n\n")
            else:
                f.write("✅ No issues found!\n\n")

            # Issues by Category
            if issues:
                f.write("## Issues by Category\n\n")
                for category in [IssueCategory.COMPLIANCE, IssueCategory.SECURITY,
                                IssueCategory.QUALITY, 
                                IssueCategory.ARCHITECTURE]:
                    category_issues = [i for i in issues if i.category == category]
                    if category_issues:
                        f.write(f"### {category.value}\n\n")
                        for issue in sorted(category_issues, key=lambda x: x.severity.value, reverse=True):
                            f.write(f"#### {issue.severity.value} - {issue.message}\n\n")
                            f.write(f"**File**: `{issue.file_path}:{issue.line_number}`\n\n")
                            if issue.suggestion:
                                f.write(f"**Suggestion**: {issue.suggestion}\n\n")
                            if issue.code_snippet:
                                f.write(f"**Code**:\n```python\n{issue.code_snippet}\n```\n\n")
                            f.write("---\n\n")

        print(f"✅ Markdown report: {report_path}")

    def _generate_json_report(self, issues: List[Issue], duration: float):
        """Generate JSON report"""
        report_path = self.output_dir / "audit_report.json"

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "total_issues": len(issues),
            "summary": {
                "critical": sum(1 for i in issues if i.severity == Severity.CRITICAL),
                "high": sum(1 for i in issues if i.severity == Severity.HIGH),
                "medium": sum(1 for i in issues if i.severity == Severity.MEDIUM),
                "low": sum(1 for i in issues if i.severity == Severity.LOW),
                "info": sum(1 for i in issues if i.severity == Severity.INFO),
            },
            "issues": [
                {
                    "file_path": issue.file_path,
                    "line_number": issue.line_number,
                    "severity": issue.severity.value,
                    "category": issue.category.value,
                    "message": issue.message,
                    "suggestion": issue.suggestion,
                    "code_snippet": issue.code_snippet,
                    "rule_id": issue.rule_id,
                    "metadata": issue.metadata
                }
                for issue in issues
            ]
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"✅ JSON report: {report_path}")

    def _count_by_severity(self, issues: List[Issue]) -> dict:
        """Count issues by severity"""
        counts = {}
        for issue in issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts

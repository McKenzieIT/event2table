"""
Markdown Reporter

Generates Markdown audit reports.
"""

from pathlib import Path
from typing import List
from datetime import datetime
from ..core.base_detector import Issue


class MarkdownReporter:
    """Generates Markdown format reports"""

    def generate_report(self, issues: List[Issue], output_path: str):
        """
        Generate Markdown report

        Args:
            issues: List of issues to report
            output_path: Path to output file
        """
        # Sort issues by severity and file
        sorted_issues = sorted(issues, key=lambda i: (i.severity.value, i.file_path, i.line_number), reverse=True)

        # Generate markdown content
        lines = [
            "# Code Audit Report",
            f"",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Issues**: {len(issues)}",
            f"",
            "---",
            f"",
        ]

        # Group by severity
        from ..core.base_detector import Severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_issues = [i for i in sorted_issues if i.severity == severity]
            if severity_issues:
                lines.append(f"## {severity.name} Issues ({len(severity_issues)})")
                lines.append("")
                for issue in severity_issues:
                    lines.append(f"### {issue.file_path}:{issue.line_number}")
                    lines.append(f"**Category**: {issue.category.value}")
                    lines.append(f"**Message**: {issue.message}")
                    if issue.suggestion:
                        lines.append(f"**Suggestion**: {issue.suggestion}")
                    if issue.code_snippet:
                        lines.append(f"**Code**:")
                        lines.append(f"```")
                        lines.append(issue.code_snippet)
                        lines.append(f"```")
                    lines.append("")

        # Write to file
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write('\n'.join(lines))

        return '\n'.join(lines)

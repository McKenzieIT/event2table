"""
Console Reporter

Prints audit reports to console.
"""

from typing import List
from ..core.base_detector import Issue, Severity


class ConsoleReporter:
    """Prints reports to console"""

    def generate_report(self, issues: List[Issue], output_path: str = None):
        """
        Print report to console

        Args:
            issues: List of issues to report
            output_path: Ignored (always prints to console)
        """
        # Sort issues by severity
        sorted_issues = sorted(issues, key=lambda i: i.severity.value, reverse=True)

        # Print header
        print("=" * 80)
        print("CODE AUDIT REPORT")
        print("=" * 80)
        print(f"Total Issues: {len(issues)}")
        print()

        # Group by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_issues = [i for i in sorted_issues if i.severity == severity]
            if severity_issues:
                # Print severity header
                color = self._get_color(severity)
                print(f"\n{color}{'=' * 80}\033[0m")
                print(f"{color}{severity.name} ISSUES ({len(severity_issues)})\033[0m")
                print(f"{color}{'=' * 80}\033[0m\n")

                # Print issues
                for issue in severity_issues:
                    print(f"  📍 {issue.file_path}:{issue.line_number}")
                    print(f"  📁 [{issue.category.value}] {issue.message}")
                    if issue.suggestion:
                        print(f"  💡 {issue.suggestion}")
                    print()

    def _get_color(self, severity: Severity) -> str:
        """Get ANSI color code for severity"""
        colors = {
            Severity.CRITICAL: "\033[91m",  # Red
            Severity.HIGH: "\033[93m",      # Yellow
            Severity.MEDIUM: "\033[94m",    # Blue
            Severity.LOW: "\033[96m",       # Cyan
            Severity.INFO: "\033[97m",      # White
        }
        return colors.get(severity, "")

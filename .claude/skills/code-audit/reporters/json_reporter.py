"""
JSON Reporter

Generates JSON audit reports.
"""

import json
from pathlib import Path
from typing import List
from datetime import datetime
from ..core.base_detector import Issue


class JsonReporter:
    """Generates JSON format reports"""

    def generate_report(self, issues: List[Issue], output_path: str):
        """
        Generate JSON report

        Args:
            issues: List of issues to report
            output_path: Path to output file
        """
        # Sort issues by severity and file
        sorted_issues = sorted(issues, key=lambda i: (i.severity.value, i.file_path, i.line_number), reverse=True)

        # Generate report data
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_issues": len(issues),
            "summary": self._generate_summary(issues),
            "issues": [issue.to_dict() for issue in sorted_issues]
        }

        # Write to file
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

        return report

    def _generate_summary(self, issues: List[Issue]) -> dict:
        """Generate summary statistics"""
        from ..core.base_detector import Severity, IssueCategory

        summary = {
            "by_severity": {},
            "by_category": {}
        }

        for severity in Severity:
            count = len([i for i in issues if i.severity == severity])
            summary["by_severity"][severity.name] = count

        for category in IssueCategory:
            count = len([i for i in issues if i.category == category])
            summary["by_category"][category.value] = count

        return summary

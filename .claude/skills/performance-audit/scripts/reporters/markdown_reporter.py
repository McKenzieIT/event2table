"""
Markdown Performance Report Generator
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class MarkdownReporter:
    """Generate Markdown performance reports"""
    
    def __init__(self, issues: List[Dict[str, Any]], mode: str, project_root: Path):
        self.issues = issues
        self.mode = mode
        self.project_root = project_root
    
    def generate(self, output_path: Path):
        """Generate Markdown report"""
        report = self._build_report()
        output_path.write_text(report, encoding='utf-8')
    
    def _build_report(self) -> str:
        """Build report content"""
        lines = []
        
        # Header
        lines.append("# Performance Audit Report")
        lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Mode**: {self.mode.upper()}")
        lines.append(f"**Project**: {self.project_root}")
        lines.append(f"**Issues Found**: {len(self.issues)}")
        
        # Summary
        lines.append("\n## 📊 Executive Summary\n")
        lines.append(self._generate_summary())
        
        # Issues by category
        lines.append("\n## 🔍 Performance Issues\n")
        lines.append(self._generate_issues_by_category())
        
        # Recommendations
        lines.append("\n## 💡 Recommendations\n")
        lines.append(self._generate_recommendations())
        
        return "\n".join(lines)
    
    def _generate_summary(self) -> str:
        """Generate summary section"""
        if not self.issues:
            return "✅ No performance issues detected!"
        
        # Count by severity
        high = sum(1 for i in self.issues if i['severity'] == 'HIGH')
        medium = sum(1 for i in self.issues if i['severity'] == 'MEDIUM')
        low = sum(1 for i in self.issues if i['severity'] == 'LOW')
        
        lines = [
            f"- **High Priority**: {high} issue(s)",
            f"- **Medium Priority**: {medium} issue(s)",
            f"- **Low Priority**: {low} issue(s)",
        ]
        
        return "\n".join(lines)
    
    def _generate_issues_by_category(self) -> str:
        """Group issues by category"""
        categories = {}
        for issue in self.issues:
            cat = issue['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(issue)
        
        lines = []
        for category, issues in categories.items():
            lines.append(f"\n### {category.title()}\n")
            for issue in issues:
                lines.append(f"#### {issue['type'].replace('_', ' ').title()}")
                lines.append(f"- **Severity**: {issue['severity']}")
                lines.append(f"- **File**: `{issue['file_path']}`")
                lines.append(f"- **Message**: {issue['message']}")
                lines.append(f"- **Suggestion**: {issue['suggestion']}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on issues"""
        if not self.issues:
            return "No recommendations - code looks good!"
        
        lines = [
            "Based on the detected issues, here are the top priorities:",
            ""
        ]
        
        # Group by type
        issue_types = {}
        for issue in self.issues:
            itype = issue['type']
            if itype not in issue_types:
                issue_types[itype] = 0
            issue_types[itype] += 1
        
        # Sort by count
        sorted_types = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)
        
        for itype, count in sorted_types[:5]:
            lines.append(f"1. **Fix {count} {itype} issues**")
            lines.append("")
        
        return "\n".join(lines)

#!/usr/bin/env python3
"""
Issue Classifier - Load and classify 829 performance issues
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict

def load_performance_report(report_path: Path) -> List[Dict[str, Any]]:
    """Load issues from performance audit report"""
    issues = []

    with open(report_path, 'r') as f:
        current_issue = {}
        in_issue = False

        for line in f:
            if line.startswith('#### '):
                if in_issue and current_issue:
                    issues.append(current_issue)
                # Extract full type name (e.g., "Missing React Memo" instead of just "Missing")
                type_match = re.match(r'#### (.+)', line)
                issue_type = type_match.group(1).strip() if type_match else "Unknown"
                current_issue = {'type': issue_type, 'raw_lines': [line]}
                in_issue = True
            elif in_issue:
                if line.startswith('- **Severity**:'):
                    current_issue['severity'] = line.split(':', 1)[1].strip()
                elif line.startswith('- **File**:'):
                    current_issue['file_path'] = line.split(':', 1)[1].strip().strip('`')
                elif line.startswith('- **Message**:'):
                    current_issue['message'] = line.split(':', 1)[1].strip()
                elif line.startswith('- **Suggestion**:'):
                    current_issue['suggestion'] = line.split(':', 1)[1].strip()
                current_issue['raw_lines'].append(line)

    return issues

def classify_issues(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """Classify issues by type and priority"""
    classified = defaultdict(list)

    for issue in issues:
        issue_type = issue['type']
        classified[issue_type].append(issue)

    return dict(classified)

def main():
    report_path = Path('.claude/skills/performance-audit/output/reports/performance_report_20260305_003833.md')

    print("📊 Loading performance report...")
    issues = load_performance_report(report_path)
    print(f"   Loaded {len(issues)} issues")

    print("📋 Classifying issues...")
    classified = classify_issues(issues)

    for issue_type, issue_list in classified.items():
        print(f"   {issue_type}: {len(issue_list)} issues")

    # Save classified issues
    output_path = Path('scripts/performance_optimization/tasks/classified_issues.json')
    with open(output_path, 'w') as f:
        json.dump(classified, f, indent=2)

    print(f"✅ Saved to {output_path}")

if __name__ == '__main__':
    main()

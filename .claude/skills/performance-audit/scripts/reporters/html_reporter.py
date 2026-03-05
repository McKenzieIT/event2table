"""
HTML Performance Report Generator (MVP - Placeholder)
"""

from pathlib import Path
from typing import List, Dict, Any


class HtmlReporter:
    """Generate HTML performance reports"""
    
    def __init__(self, issues: List[Dict[str, Any]], mode: str, project_root: Path):
        self.issues = issues
        self.mode = mode
        self.project_root = project_root
    
    def generate(self, output_path: Path):
        """Generate HTML report (MVP placeholder)"""
        html = self._build_html()
        output_path.write_text(html, encoding='utf-8')
    
    def _build_html(self) -> str:
        """Build HTML content (simplified MVP version)"""
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Performance Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .issue {{ margin: 10px 0; padding: 10px; border-left: 3px solid #ccc; }}
        .high {{ border-color: #f44336; }}
        .medium {{ border-color: #ff9800; }}
        .low {{ border-color: #4caf50; }}
    </style>
</head>
<body>
    <h1>Performance Audit Report</h1>
    <p><strong>Mode:</strong> {self.mode.upper()}</p>
    <p><strong>Issues Found:</strong> {len(self.issues)}</p>
    <p><em>Note: Full HTML visualization coming in Phase 2</em></p>
</body>
</html>"""

"""
API Contract Detector

Validates frontend-backend API contract consistency.
"""

import re
from pathlib import Path
from typing import List, Dict, Set
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class ApiContractDetector(BaseDetector):
    """
    Detects API contract violations between frontend and backend

    Scans:
    - Frontend: API calls (fetch, axios, etc.)
    - Backend: API routes (Flask @route decorators)
    """

    # Frontend API call patterns
    FRONTEND_PATTERNS = [
        r'fetch\(["'](/api/[^"']+)["']',
        r'axios\.(get|post|put|delete|patch)\(["'](/api/[^"']+)["']',
        r'\.(get|post|put|delete|patch)\(["'](/api/[^"']+)["']',
    ]

    # Backend route patterns
    BACKEND_PATTERNS = [
        r'@.*\.route\(["'](/api/[^"']+)["']\s*,\s*methods=\["']([^"']+)["']',
        r'@.*\.route\(["'](/api/[^"']+)["']',
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "API_CONTRACT_001"
        self.backend_routes: Dict[str, Set[str]] = {}

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect API contract violations"""
        issues = []

        file_str = str(file_path)

        # Check if this is a frontend file
        if self._is_frontend_file(file_path):
            api_calls = self._extract_frontend_api_calls(file_path)
            # Would need to check against backend routes
            # For now, just report potential API calls for manual review

        # Check if this is a backend file
        elif self._is_backend_file(file_path):
            routes = self._extract_backend_routes(file_path)
            # Store routes for validation

        return issues

    def _is_frontend_file(self, file_path: Path) -> bool:
        """Check if file is a frontend file"""
        return any(ext in file_path.suffix for ext in ['.js', '.jsx', '.ts', '.tsx'])

    def _is_backend_file(self, file_path: Path) -> bool:
        """Check if file is a backend file"""
        return 'backend' in file_path.parts and file_path.suffix == '.py'

    def _extract_frontend_api_calls(self, file_path: Path) -> List[Dict]:
        """Extract API calls from frontend file"""
        calls = []
        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern in self.FRONTEND_PATTERNS:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        endpoint = match.group(1) if match.lastindex >= 1 else match.group(2)
                        method = match.group(2).upper() if match.lastindex >= 2 else 'GET'
                        calls.append({
                            'endpoint': endpoint,
                            'method': method,
                            'line': line_num,
                            'file': str(file_path)
                        })
        except Exception as e:
            print(f"Error extracting API calls from {file_path}: {e}")

        return calls

    def _extract_backend_routes(self, file_path: Path) -> List[Dict]:
        """Extract routes from backend file"""
        routes = []
        try:
            content = file_path.read_text()
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern in self.BACKEND_PATTERNS:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        endpoint = match.group(1)
                        methods = match.group(2).split(',') if match.lastindex >= 2 else ['GET']
                        routes.append({
                            'endpoint': endpoint,
                            'methods': [m.strip().strip('"'') for m in methods],
                            'line': line_num,
                            'file': str(file_path)
                        })
        except Exception as e:
            print(f"Error extracting routes from {file_path}: {e}")

        return routes

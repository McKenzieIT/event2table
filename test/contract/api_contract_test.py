#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Contract Validator

Compares frontend API calls with backend routes to detect inconsistencies.
Validates that all frontend API calls have matching backend routes with correct
HTTP methods and consistent parameter naming (especially game_gid vs game_id).

Usage:
    python test/contract/api_contract_test.py                # Scan and validate
    python test/contract/api_contract_test.py --scan         # Rescan both
    python test/contract/api_contract_test.py --fix          # Generate fixes
    python test/contract/api_contract_test.py --verify       # Validate only
"""

import sys
import os
import json
import re
import ast
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
from difflib import SequenceMatcher


class APIContractValidator:
    """Validates API contracts between frontend and backend"""

    def __init__(
        self,
        frontend_path: str = "frontend/src",
        backend_app: str = "web_app.py"
    ):
        """
        Initialize validator

        Args:
            frontend_path: Path to frontend source directory
            backend_app: Path to Flask app file
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.frontend_path = self.project_root / frontend_path
        self.backend_app = self.project_root / backend_app

        self.backend_routes: Dict[str, Dict[str, Any]] = {}
        self.frontend_calls: Dict[str, List[Dict[str, Any]]] = {}

        # Validation results
        self.missing_backend: List[Dict[str, Any]] = []
        self.missing_frontend: List[Dict[str, Any]] = []
        self.method_mismatches: List[Dict[str, Any]] = []
        self.param_mismatches: List[Dict[str, Any]] = []

    def scan(self, force: bool = False) -> bool:
        """
        Scan both frontend and backend

        Args:
            force: Force rescan even if fixtures exist

        Returns:
            True if scan successful
        """
        print("📡 Scanning API contracts...")

        # Check if fixtures exist
        backend_fixture = self.project_root / "test/contract/fixtures/backend_routes.json"
        frontend_fixture = self.project_root / "test/contract/fixtures/frontend_calls.json"

        if not force and backend_fixture.exists() and frontend_fixture.exists():
            print("✅ Using existing fixtures")
            self._load_fixtures()
            return True

        print("🔄 Running scanners...")

        # Scan backend
        if not self._scan_backend():
            return False

        # Scan frontend
        if not self._scan_frontend():
            return False

        print("✅ Scan completed")
        return True

    def _scan_backend(self) -> bool:
        """Run backend route scanner"""
        print("  📡 Scanning backend routes...")

        try:
            result = subprocess.run(
                [sys.executable, "test/contract/contract_scanner.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"❌ Backend scan failed:\n{result.stderr}")
                return False

            # Load results
            fixture_path = self.project_root / "test/contract/fixtures/backend_routes.json"
            with open(fixture_path) as f:
                self.backend_routes = json.load(f)

            print(f"  ✅ Found {len(self.backend_routes)} backend routes")
            return True

        except subprocess.TimeoutExpired:
            print("❌ Backend scan timed out")
            return False
        except Exception as e:
            print(f"❌ Backend scan error: {e}")
            return False

    def _scan_frontend(self) -> bool:
        """Run frontend API call scanner"""
        print("  📡 Scanning frontend API calls...")

        try:
            result = subprocess.run(
                [sys.executable, "test/contract/frontend_scanner.py"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"❌ Frontend scan failed:\n{result.stderr}")
                return False

            # Load results
            fixture_path = self.project_root / "test/contract/fixtures/frontend_calls.json"
            with open(fixture_path) as f:
                self.frontend_calls = json.load(f)

            total_calls = sum(len(calls) for calls in self.frontend_calls.values())
            print(f"  ✅ Found {total_calls} frontend API calls")
            return True

        except subprocess.TimeoutExpired:
            print("❌ Frontend scan timed out")
            return False
        except Exception as e:
            print(f"❌ Frontend scan error: {e}")
            return False

    def _load_fixtures(self):
        """Load existing fixture files"""
        # Load backend routes
        backend_fixture = self.project_root / "test/contract/fixtures/backend_routes.json"
        with open(backend_fixture) as f:
            self.backend_routes = json.load(f)

        # Load frontend calls
        frontend_fixture = self.project_root / "test/contract/fixtures/frontend_calls.json"
        with open(frontend_fixture) as f:
            self.frontend_calls = json.load(f)

    def validate(self) -> bool:
        """
        Validate API contracts

        Returns:
            True if all contracts valid
        """
        print("\n🔍 Validating API contracts...")

        # Reset results
        self.missing_backend = []
        self.missing_frontend = []
        self.method_mismatches = []
        self.param_mismatches = []

        # Check for missing backend routes
        self._check_missing_backend()

        # Check for missing frontend calls
        self._check_missing_frontend()

        # Check for method mismatches
        self._check_method_mismatches()

        # Check for parameter mismatches
        self._check_parameter_mismatches()

        # Print results
        self._print_results()

        # Return True if no issues found
        return (
            not self.missing_backend and
            not self.method_mismatches and
            not self.param_mismatches
        )

    def _check_missing_backend(self):
        """Check for frontend calls without backend routes"""
        for file_path, calls in self.frontend_calls.items():
            for call in calls:
                path = call['path']

                # Skip unknown paths
                if path == 'UNKNOWN':
                    continue

                # Check if backend route exists
                if not self._backend_route_exists(path):
                    self.missing_backend.append({
                        'file': file_path,
                        'line': call['line'],
                        'path': path,
                        'method': call['method'],
                        'type': call['type']
                    })

    def _check_missing_frontend(self):
        """Check for backend routes without frontend calls"""
        # Build set of all frontend paths
        frontend_paths = set()
        for calls in self.frontend_calls.values():
            for call in calls:
                if call['path'] != 'UNKNOWN':
                    frontend_paths.add(call['path'])

        # Find backend routes not used by frontend
        for path, info in self.backend_routes.items():
            # Skip static files and admin routes
            if any(skip in path for skip in ['/static', '/admin', '/test']):
                continue

            # Check if frontend uses this route
            if not self._frontend_uses_path(path, frontend_paths):
                self.missing_frontend.append({
                    'path': path,
                    'methods': info['methods'],
                    'endpoint': info['endpoint']
                })

    def _check_method_mismatches(self):
        """Check for HTTP method mismatches"""
        for file_path, calls in self.frontend_calls.items():
            for call in calls:
                path = call['path']

                # Skip unknown paths
                if path == 'UNKNOWN':
                    continue

                # Find matching backend route
                backend_info = self._find_backend_route(path)
                if not backend_info:
                    continue

                # Check if frontend method is supported by backend
                frontend_method = call['method']
                if frontend_method not in backend_info['methods']:
                    self.method_mismatches.append({
                        'file': file_path,
                        'line': call['line'],
                        'path': path,
                        'frontend_method': frontend_method,
                        'backend_methods': backend_info['methods'],
                        'type': call['type']
                    })

    def _check_parameter_mismatches(self):
        """Check for parameter naming inconsistencies (game_id vs game_gid)"""
        for file_path, calls in self.frontend_calls.items():
            for call in calls:
                path = call['path']

                # Skip unknown paths
                if path == 'UNKNOWN':
                    continue

                # Find matching backend route
                backend_info = self._find_backend_route(path)
                if not backend_info:
                    continue

                # Check for game_id vs game_gid mismatches
                frontend_params = self._extract_frontend_params(path, call)
                backend_params = backend_info['parameters']

                # Check if frontend uses game_id when backend expects game_gid
                if 'game_id' in frontend_params and 'game_gid' in backend_params:
                    self.param_mismatches.append({
                        'file': file_path,
                        'line': call['line'],
                        'path': path,
                        'frontend_param': 'game_id',
                        'backend_param': 'game_gid',
                        'severity': 'error',
                        'fix': f"Replace 'game_id' with 'game_gid' in API call"
                    })

                # Check if frontend uses game_gid when backend expects game_id
                if 'game_gid' in frontend_params and 'game_id' in backend_params:
                    self.param_mismatches.append({
                        'file': file_path,
                        'line': call['line'],
                        'path': path,
                        'frontend_param': 'game_gid',
                        'backend_param': 'game_id',
                        'severity': 'warning',
                        'fix': f"Backend should use 'game_gid' instead of 'game_id'"
                    })

    def _backend_route_exists(self, path: str) -> bool:
        """Check if backend route exists for given path"""
        # Direct match
        if path in self.backend_routes:
            return True

        # Pattern match (e.g., /api/games/123 matches /api/games/<int:game_id>)
        for backend_path in self.backend_routes.keys():
            if self._path_matches_pattern(path, backend_path):
                return True

        return False

    def _find_backend_route(self, path: str) -> Dict[str, Any]:
        """Find backend route info for given path"""
        # Direct match
        if path in self.backend_routes:
            return self.backend_routes[path]

        # Pattern match
        for backend_path, info in self.backend_routes.items():
            if self._path_matches_pattern(path, backend_path):
                return info

        return None

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches route pattern"""
        # Convert Flask pattern to regex
        # e.g., /api/games/<int:game_gid> -> /api/games/\d+
        regex_pattern = pattern
        regex_pattern = re.sub(r'<\w+:\w+>', r'\\d+', regex_pattern)  # <int:id>
        regex_pattern = re.sub(r'<\w+>', r'[^/]+', regex_pattern)  # <id>
        regex_pattern = regex_pattern.replace('.', r'\.')
        regex_pattern = '^' + regex_pattern + '$'

        return bool(re.match(regex_pattern, path))

    def _frontend_uses_path(self, backend_path: str, frontend_paths: Set[str]) -> bool:
        """Check if frontend uses given backend path"""
        # Direct match
        if backend_path in frontend_paths:
            return True

        # Check if any frontend path matches backend pattern
        for frontend_path in frontend_paths:
            if self._path_matches_pattern(frontend_path, backend_path):
                return True

        return False

    def _extract_frontend_params(self, path: str, call: Dict[str, Any]) -> List[str]:
        """Extract parameter names from frontend API call"""
        params = []

        # Check path parameters
        path_params = re.findall(r'/(\w+)', path)
        params.extend(path_params)

        # Check query parameters (from full URL if available)
        if 'params' in call:
            params.extend(call['params'])

        return params

    def _print_results(self):
        """Print validation results"""
        print("\n" + "=" * 80)
        print("🔍 API Contract Validation Report")
        print("=" * 80)

        # Missing backend routes
        if self.missing_backend:
            print(f"\n❌ Missing Backend Routes ({len(self.missing_backend)}):")
            print("-" * 80)
            for issue in self.missing_backend[:10]:  # Show first 10
                print(f"  Frontend: {issue['file']}:{issue['line']}")
                print(f"    calls {issue['method']} {issue['path']}")
                print(f"    Backend: Route not found")
                print()

            if len(self.missing_backend) > 10:
                print(f"  ... and {len(self.missing_backend) - 10} more\n")

        # Method mismatches
        if self.method_mismatches:
            print(f"\n⚠️  Method Mismatches ({len(self.method_mismatches)}):")
            print("-" * 80)
            for issue in self.method_mismatches[:10]:
                print(f"  Frontend: {issue['file']}:{issue['line']}")
                print(f"    uses {issue['frontend_method']} but backend has: {', '.join(issue['backend_methods'])}")
                print(f"    Path: {issue['path']}")
                print()

            if len(self.method_mismatches) > 10:
                print(f"  ... and {len(self.method_mismatches) - 10} more\n")

        # Parameter mismatches
        if self.param_mismatches:
            print(f"\n⚠️  Parameter Mismatches ({len(self.param_mismatches)}):")
            print("-" * 80)
            for issue in self.param_mismatches[:10]:
                icon = "❌" if issue['severity'] == 'error' else "⚠️ "
                print(f"  {icon} {issue['file']}:{issue['line']}")
                print(f"    Frontend uses '{issue['frontend_param']}' but backend expects '{issue['backend_param']}'")
                print(f"    Path: {issue['path']}")
                print(f"    Fix: {issue['fix']}")
                print()

            if len(self.param_mismatches) > 10:
                print(f"  ... and {len(self.param_mismatches) - 10} more\n")

        # Missing frontend calls (informational)
        if self.missing_frontend:
            print(f"\n💡 Missing Frontend Calls ({len(self.missing_frontend)}):")
            print("-" * 80)
            print("  Backend routes not called by frontend (may be intentional):")
            for issue in self.missing_frontend[:10]:
                methods = ', '.join(issue['methods'])
                print(f"    {methods:8} {issue['path']}")
                print(f"              Endpoint: {issue['endpoint']}")

            if len(self.missing_frontend) > 10:
                print(f"\n  ... and {len(self.missing_frontend) - 10} more\n")
            else:
                print()

        # Summary
        print("=" * 80)
        issues_found = (
            len(self.missing_backend) +
            len(self.method_mismatches) +
            len(self.param_mismatches)
        )

        if issues_found == 0:
            print("✅ Validation: PASSED")
            print("   All frontend API calls have matching backend routes!")
        else:
            print(f"❌ Validation: FAILED")
            print(f"   Found {issues_found} issue(s):")
            print(f"   - {len(self.missing_backend)} missing backend routes")
            print(f"   - {len(self.method_mismatches)} method mismatches")
            print(f"   - {len(self.param_mismatches)} parameter mismatches")

        print("=" * 80)

    def generate_fixes(self):
        """Generate fix suggestions for detected issues"""
        print("\n🔧 Generating fix suggestions...")

        fixes_file = self.project_root / "test/contract/fixtures/fix_suggestions.json"
        fixes = {
            'missing_backend_routes': [],
            'method_mismatches': [],
            'parameter_mismatches': []
        }

        # Missing backend routes
        for issue in self.missing_backend:
            fixes['missing_backend_routes'].append({
                'issue': f"Frontend calls {issue['method']} {issue['path']} but backend doesn't implement it",
                'location': f"{issue['file']}:{issue['line']}",
                'suggestion': f"Add route handler for {issue['method']} {issue['path']} in backend",
                'priority': 'high'
            })

        # Method mismatches
        for issue in self.method_mismatches:
            fixes['method_mismatches'].append({
                'issue': f"Frontend uses {issue['frontend_method']} but backend supports {issue['backend_methods']}",
                'location': f"{issue['file']}:{issue['line']}",
                'suggestion': f"Either add {issue['frontend_method']} method to backend route or change frontend to use one of: {', '.join(issue['backend_methods'])}",
                'priority': 'high'
            })

        # Parameter mismatches
        for issue in self.param_mismatches:
            if issue['severity'] == 'error':
                fixes['parameter_mismatches'].append({
                    'issue': f"Frontend uses '{issue['frontend_param']}' but backend expects '{issue['backend_param']}'",
                    'location': f"{issue['file']}:{issue['line']}",
                    'suggestion': issue['fix'],
                    'priority': 'high'
                })

        # Save fixes
        with open(fixes_file, 'w') as f:
            json.dump(fixes, f, indent=2)

        print(f"💾 Fix suggestions saved to: {fixes_file}")
        print(f"\n📋 Summary:")
        print(f"   - {len(fixes['missing_backend_routes'])} missing backend routes")
        print(f"   - {len(fixes['method_mismatches'])} method mismatches")
        print(f"   - {len(fixes['parameter_mismatches'])} parameter mismatches")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate API contracts between frontend and backend"
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Rescan both frontend and backend (ignore existing fixtures)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Generate fix suggestions for detected issues'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Only validate, do not scan (requires existing fixtures)'
    )
    parser.add_argument(
        '--frontend-path',
        default='frontend/src',
        help='Path to frontend source directory (default: frontend/src)'
    )
    parser.add_argument(
        '--backend-app',
        default='web_app.py',
        help='Path to Flask app file (default: web_app.py)'
    )

    args = parser.parse_args()

    try:
        # Initialize validator
        validator = APIContractValidator(
            frontend_path=args.frontend_path,
            backend_app=args.backend_app
        )

        # Scan if needed
        if not args.verify:
            if not validator.scan(force=args.scan):
                print("\n❌ Scan failed")
                return 1
        else:
            # Load existing fixtures
            validator._load_fixtures()

        # Validate contracts
        valid = validator.validate()

        # Generate fixes if requested
        if args.fix and not valid:
            validator.generate_fixes()

        # Return exit code
        return 0 if valid else 1

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

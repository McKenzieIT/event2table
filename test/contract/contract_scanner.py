#!/usr/bin/env python3
"""
Backend Route Scanner for API Contract Testing

Scans Flask application and extracts all registered routes with their HTTP methods,
parameters, and endpoint information. Saves results to JSON fixture file.

Usage:
    python test/contract/contract_scanner.py
    python test/contract/contract_scanner.py --output custom_output.json
"""

import sys
import os
import json
import re
import ast
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
from flask import Flask
from werkzeug.routing import Rule

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class BackendRouteScanner:
    """Scans Flask application for all registered routes"""

    def __init__(self, app_path: str = "web_app.py"):
        """
        Initialize scanner

        Args:
            app_path: Path to Flask app file (relative to project root)
        """
        self.app_path = project_root / app_path
        self.routes: Dict[str, Dict[str, Any]] = {}

    def scan(self) -> Dict[str, Dict[str, Any]]:
        """
        Scan Flask application and extract all routes

        Returns:
            Dictionary mapping route paths to their metadata
        """
        print(f"📡 Scanning Flask app at: {self.app_path}")

        # Import Flask app
        import importlib.util

        spec = importlib.util.spec_from_file_location("web_app", self.app_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load Flask app from {self.app_path}")

        web_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(web_app)

        # Get Flask app
        if not hasattr(web_app, 'app'):
            raise AttributeError("Flask app not found in module")

        app: Flask = web_app.app

        # Extract routes - merge methods for same path
        for rule in app.url_map.iter_rules():
            if self._should_skip_route(rule):
                continue

            route_info = self._extract_route_info(rule)

            # Merge methods if path already exists (Flask creates separate rules for each method)
            if rule.rule in self.routes:
                existing = self.routes[rule.rule]
                # Combine methods, remove duplicates, sort
                existing_methods = set(existing.get('methods', []))
                new_methods = set(route_info.get('methods', []))
                merged_methods = sorted(existing_methods.union(new_methods))

                # Update existing entry
                existing['methods'] = merged_methods
                # Store multiple endpoints if different
                if existing.get('endpoint') != route_info.get('endpoint'):
                    if 'endpoints' not in existing:
                        existing['endpoints'] = [existing.get('endpoint')]
                    existing['endpoints'].append(route_info.get('endpoint'))
            else:
                # New route path
                self.routes[rule.rule] = route_info

        print(f"✅ Found {len(self.routes)} routes")
        return self.routes

    def _should_skip_route(self, rule: Rule) -> bool:
        """
        Check if route should be skipped

        Args:
            rule: Flask route rule

        Returns:
            True if route should be skipped
        """
        # Skip static files
        if rule.rule.startswith('/static'):
            return True

        # Skip health checks
        if rule.endpoint in ['static', 'health']:
            return True

        return False

    def _extract_route_info(self, rule: Rule) -> Dict[str, Any]:
        """
        Extract route information

        Args:
            rule: Flask route rule

        Returns:
            Dictionary with route metadata
        """
        methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]

        # Extract parameters from route path
        parameters = self._extract_parameters(rule.rule)

        return {
            "methods": sorted(methods),
            "endpoint": rule.endpoint,
            "parameters": parameters
        }

    def _extract_parameters(self, path: str) -> List[str]:
        """
        Extract parameter names from route path

        Args:
            path: Route path (e.g., '/api/games/<int:game_gid>')

        Returns:
            List of parameter names (e.g., ['game_gid'])
        """
        # Match Flask route parameters: <type:param_name> or <param_name>
        # Pattern matches <int:id> or <id> and captures id
        pattern = r'<(?:\w+:)?(\w+)>'
        matches = re.findall(pattern, path)
        return matches

    def save_to_fixture(self, output_path: str = None) -> str:
        """
        Save scanned routes to JSON fixture file

        Args:
            output_path: Custom output path (default: test/contract/fixtures/backend_routes.json)

        Returns:
            Absolute path to saved file
        """
        if output_path is None:
            output_path = project_root / "test/contract/fixtures/backend_routes.json"
        else:
            output_path = Path(output_path)
            if not output_path.is_absolute():
                output_path = project_root / output_path

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.routes, f, indent=2, sort_keys=True)

        print(f"💾 Saved backend routes to: {output_path}")
        return str(output_path)

    def print_summary(self):
        """Print summary of scanned routes"""
        print("\n📊 Backend Routes Summary:")
        print("=" * 60)

        # Group by endpoint prefix
        grouped = defaultdict(list)
        for path, info in sorted(self.routes.items()):
            prefix = path.split('/')[1] if '/' in path else 'root'
            grouped[prefix].append((path, info))

        for prefix, routes in sorted(grouped.items()):
            print(f"\n📁 {prefix.upper()} ({len(routes)} routes)")
            for path, info in routes:
                methods = ', '.join(info['methods'])
                params = ', '.join(info['parameters']) if info['parameters'] else 'none'
                endpoint = info.get('endpoint', '')
                endpoints = info.get('endpoints', [])

                # Show endpoint(s)
                if endpoints:
                    endpoint_str = ', '.join(endpoints[:2])
                    if len(endpoints) > 2:
                        endpoint_str += f" (+{len(endpoints)-2} more)"
                else:
                    endpoint_str = endpoint

                print(f"  {methods:12} {path:50} params: {params}")
                if endpoint_str:
                    print(f"               -> {endpoint_str}")

        print("\n" + "=" * 60)
        print(f"Total: {len(self.routes)} unique paths")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan Flask application for API routes"
    )
    parser.add_argument(
        '--app',
        default='web_app.py',
        help='Path to Flask app file (default: web_app.py)'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path (default: test/contract/fixtures/backend_routes.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed route information'
    )

    args = parser.parse_args()

    try:
        # Scan routes
        scanner = BackendRouteScanner(app_path=args.app)
        scanner.scan()

        # Print summary if verbose
        if args.verbose:
            scanner.print_summary()

        # Save to fixture
        output_path = scanner.save_to_fixture(args.output)

        print("\n✅ Backend route scanning completed!")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

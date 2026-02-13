#!/usr/bin/env python3
"""
Frontend API Call Scanner for API Contract Testing

Scans frontend source files for all API calls (fetch, axios, API clients).
Extracts call paths, methods, and locations. Saves results to JSON fixture file.

Usage:
    python test/contract/frontend_scanner.py
    python test/contract/frontend_scanner.py --output custom_output.json
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict


class FrontendAPIScanner:
    """Scans frontend source files for API calls"""

    def __init__(self, frontend_path: str = "frontend/src"):
        """
        Initialize scanner

        Args:
            frontend_path: Path to frontend source directory (relative to project root)
        """
        self.frontend_path = Path(__file__).parent.parent.parent / frontend_path
        self.api_calls: Dict[str, List[Dict[str, Any]]] = {}

    def scan(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan frontend source files for API calls

        Returns:
            Dictionary mapping file paths to their API calls
        """
        print(f"🔍 Scanning frontend source at: {self.frontend_path}")

        if not self.frontend_path.exists():
            print(f"⚠️  Frontend path not found: {self.frontend_path}")
            return self.api_calls

        # Find all source files
        source_files = self._find_source_files()
        print(f"📄 Found {len(source_files)} source files")

        # Scan each file
        for source_file in source_files:
            calls = self._scan_file(source_file)
            if calls:
                # Store relative path from frontend/src
                rel_path = str(source_file.relative_to(self.frontend_path))
                self.api_calls[rel_path] = calls

        total_calls = sum(len(calls) for calls in self.api_calls.values())
        print(f"✅ Found {total_calls} API calls in {len(self.api_calls)} files")

        return self.api_calls

    def _find_source_files(self) -> List[Path]:
        """
        Find all TypeScript and JavaScript source files

        Returns:
            List of file paths
        """
        extensions = ['.ts', '.tsx', '.js', '.jsx']
        source_files = []

        for ext in extensions:
            source_files.extend(self.frontend_path.rglob(f'*{ext}'))

        return sorted(source_files)

    def _scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Scan a single file for API calls

        Args:
            file_path: Path to source file

        Returns:
            List of API call metadata
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            calls = []

            # Scan for different API call patterns
            calls.extend(self._find_fetch_calls(lines))
            calls.extend(self._find_axios_calls(lines))
            calls.extend(self._find_api_client_calls(lines))

            return calls

        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
            return []

    def _find_fetch_calls(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Find fetch() API calls

        Args:
            lines: File content as lines

        Returns:
            List of API call metadata
        """
        calls = []
        pattern = r'fetch\s*\(\s*["\'](/api/[^"\']+)["\']'

        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                path = match.group(1)

                # Try to extract method from current line and next few lines
                # (fetch() options object often spans multiple lines)
                method = self._extract_http_method_from_context(lines, line_num - 1)

                calls.append({
                    "path": path,
                    "method": method,
                    "line": line_num,
                    "type": "fetch"
                })

        return calls

    def _find_axios_calls(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Find axios API calls

        Args:
            lines: File content as lines

        Returns:
            List of API call metadata
        """
        calls = []
        pattern = r'axios\.(get|post|put|delete|patch)\s*\(\s*["\'](/api/[^"\']+)["\']'

        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(pattern, line)
            for match in matches:
                method = match.group(1).upper()
                path = match.group(2)

                calls.append({
                    "path": path,
                    "method": method,
                    "line": line_num,
                    "type": "axios"
                })

        return calls

    def _find_api_client_calls(self, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Find API client method calls

        Args:
            lines: File content as lines

        Returns:
            List of API call metadata
        """
        calls = []

        # Pattern for client method calls: GamesAPI.getGame(gameGid)
        # This is more complex and may need customization based on actual API client patterns
        patterns = [
            # Generic API client pattern
            r'(\w+API)\.(\w+)\s*\(',
            # Hook-based patterns
            r'use\w+Query\([''"](/api/[^''"]+)[''"]',
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    # For now, just note that an API call was found
                    # More sophisticated parsing would be needed for full extraction
                    calls.append({
                        "path": "UNKNOWN",
                        "method": "UNKNOWN",
                        "line": line_num,
                        "type": "api_client",
                        "raw": line.strip()[:100]  # Store raw line for manual review
                    })

        return calls

    def _extract_http_method_from_context(self, lines: List[str], start_idx: int) -> str:
        """
        Extract HTTP method from fetch call by checking current and next few lines

        Args:
            lines: All lines in the file
            start_idx: Index of the line with the fetch() call (0-based)

        Returns:
            HTTP method (default: GET)
        """
        # Check current line and next 5 lines for method specification
        end_idx = min(start_idx + 6, len(lines))

        for i in range(start_idx, end_idx):
            line = lines[i]

            # Check for method: 'POST', etc.
            method_pattern = r'method\s*:\s*["\'](\w+)["\']'
            match = re.search(method_pattern, line)
            if match:
                return match.group(1).upper()

            # Stop looking if we hit the closing parenthesis
            if ')' in line and i > start_idx:
                break

        # Default to GET
        return 'GET'

    def save_to_fixture(self, output_path: str = None) -> str:
        """
        Save scanned API calls to JSON fixture file

        Args:
            output_path: Custom output path (default: test/contract/fixtures/frontend_calls.json)

        Returns:
            Absolute path to saved file
        """
        if output_path is None:
            output_path = Path(__file__).parent / "fixtures/frontend_calls.json"
        else:
            output_path = Path(output_path)
            if not output_path.is_absolute():
                output_path = Path(__file__).parent.parent.parent / output_path

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.api_calls, f, indent=2, sort_keys=True)

        print(f"💾 Saved frontend calls to: {output_path}")
        return str(output_path)

    def print_summary(self):
        """Print summary of scanned API calls"""
        print("\n📊 Frontend API Calls Summary:")
        print("=" * 60)

        # Group by API path prefix
        grouped = defaultdict(list)
        for file_path, calls in sorted(self.api_calls.items()):
            for call in calls:
                if call['path'] != 'UNKNOWN':
                    prefix = call['path'].split('/')[2] if len(call['path'].split('/')) > 2 else 'root'
                    grouped[prefix].append((file_path, call))

        for prefix, calls in sorted(grouped.items()):
            print(f"\n📁 /api/{prefix} ({len(calls)} calls)")
            for file_path, call in calls[:10]:  # Show first 10
                method = call['method']
                path = call['path']
                line = call['line']
                print(f"  {method:8} {path:40} {file_path}:{line}")

            if len(calls) > 10:
                print(f"  ... and {len(calls) - 10} more")

        # Show unknown calls
        unknown_count = sum(
            1 for calls in self.api_calls.values()
            for call in calls
            if call['path'] == 'UNKNOWN'
        )
        if unknown_count > 0:
            print(f"\n⚠️  {unknown_count} API client calls (need manual review)")

        print("\n" + "=" * 60)

        total_calls = sum(len(calls) for calls in self.api_calls.values())
        print(f"Total: {total_calls} API calls in {len(self.api_calls)} files")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan frontend source files for API calls"
    )
    parser.add_argument(
        '--frontend-path',
        default='frontend/src',
        help='Path to frontend source directory (default: frontend/src)'
    )
    parser.add_argument(
        '--output',
        help='Output JSON file path (default: test/contract/fixtures/frontend_calls.json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed API call information'
    )

    args = parser.parse_args()

    try:
        # Scan API calls
        scanner = FrontendAPIScanner(frontend_path=args.frontend_path)
        scanner.scan()

        # Print summary if verbose
        if args.verbose:
            scanner.print_summary()

        # Save to fixture
        output_path = scanner.save_to_fixture(args.output)

        print("\n✅ Frontend API call scanning completed!")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

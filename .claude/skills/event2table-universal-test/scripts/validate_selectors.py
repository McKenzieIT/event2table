#!/usr/bin/env python3
"""
Selector Validation Tool for Event2Table Universal Test System

This script validates all CSS selectors used in test configurations by checking
if they exist in the actual web application using agent-browser.

Usage:
    python validate_selectors.py [--url URL] [--output FILE]

Author: Event2Table Test System
Version: 1.0.0
Date: 2026-03-20
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from collections import defaultdict


class SelectorValidator:
    """Validates CSS selectors using agent-browser"""

    def __init__(self, base_url: str = "http://localhost:5173"):
        """
        Initialize the selector validator

        Args:
            base_url: Base URL of the application to test
        """
        self.base_url = base_url
        self.results = {
            "total": 0,
            "valid": 0,
            "invalid": 0,
            "errors": 0,
            "invalid_selectors": [],
            "error_selectors": []
        }
        self.test_configs_dir = Path(__file__).parent.parent / "config" / "test_configs"

    def load_test_configs(self) -> List[Dict[str, Any]]:
        """
        Load all test configuration files

        Returns:
            List of test configuration dictionaries
        """
        configs = []

        if not self.test_configs_dir.exists():
            print(f"❌ Test configs directory not found: {self.test_configs_dir}")
            return configs

        for config_file in self.test_configs_dir.glob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    config['_source_file'] = config_file.name
                    configs.append(config)
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse {config_file.name}: {e}")
            except Exception as e:
                print(f"⚠️  Error reading {config_file.name}: {e}")

        return configs

    def extract_selectors(self, configs: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
        """
        Extract all selectors from test configurations

        Args:
            configs: List of test configuration dictionaries

        Returns:
            List of tuples (selector, test_id, test_name)
        """
        selectors = []

        for config in configs:
            test_id = config.get("test_id", "UNKNOWN")
            test_name = config.get("name", "Unnamed Test")

            # Extract selectors from navigation
            if "navigation" in config:
                nav = config["navigation"]
                if "target_element" in nav:
                    selectors.append((nav["target_element"], test_id, test_name))

            # Extract selectors from assertions
            if "assertions" in config:
                for assertion in config["assertions"]:
                    if "selector" in assertion:
                        selectors.append((assertion["selector"], test_id, test_name))

            # Extract selectors from actions
            if "actions" in config:
                for action in config["actions"]:
                    if "selector" in action:
                        selectors.append((action["selector"], test_id, test_name))

        return selectors

    def check_selector_with_browser(self, selector: str) -> Tuple[bool, str]:
        """
        Check if a selector exists using agent-browser

        Args:
            selector: CSS selector to validate

        Returns:
            Tuple of (is_valid, message)
        """
        # Escape single quotes in selector for JavaScript
        escaped_selector = selector.replace("'", "\\'")

        # JavaScript to check if selector exists
        js_code = f'''
        (function() {{
            try {{
                const element = document.querySelector('{escaped_selector}');
                return {{
                    exists: element !== null,
                    tagName: element ? element.tagName : null,
                    className: element ? element.className : null,
                    id: element ? element.id : null
                }};
            }} catch (e) {{
                return {{
                    exists: false,
                    error: e.message
                }};
            }}
        }})()
        '''

        try:
            # Run agent-browser eval command
            result = subprocess.run(
                ['agent-browser', 'eval', js_code],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse the output
                output = result.stdout.strip()
                try:
                    data = json.loads(output)
                    if data.get('exists'):
                        return True, f"Found: {data.get('tagName')} (class={data.get('className')}, id={data.get('id')})"
                    else:
                        error = data.get('error', 'Element not found')
                        return False, f"Error: {error}"
                except json.JSONDecodeError:
                    # Output might not be JSON, check if it contains "true" or "false"
                    if 'true' in output.lower():
                        return True, "Element exists"
                    else:
                        return False, "Element not found"
            else:
                return False, f"agent-browser error: {result.stderr}"

        except subprocess.TimeoutExpired:
            return False, "Timeout checking selector"
        except FileNotFoundError:
            return False, "agent-browser not found"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def validate_selectors(self, selectors: List[Tuple[str, str, str]]) -> None:
        """
        Validate all selectors and update results

        Args:
            selectors: List of tuples (selector, test_id, test_name)
        """
        # Remove duplicates while preserving test info
        unique_selectors = {}
        for selector, test_id, test_name in selectors:
            if selector not in unique_selectors:
                unique_selectors[selector] = []
            unique_selectors[selector].append((test_id, test_name))

        self.results["total"] = len(unique_selectors)

        print(f"\n🔍 Validating {self.results['total']} unique selectors...")
        print("=" * 60)

        for i, (selector, test_info) in enumerate(unique_selectors.items(), 1):
            print(f"\n[{i}/{self.results['total']}] Checking: {selector}")

            # Check selector
            is_valid, message = self.check_selector_with_browser(selector)

            if is_valid:
                self.results["valid"] += 1
                print(f"  ✅ VALID - {message}")
            else:
                self.results["invalid"] += 1
                print(f"  ❌ INVALID - {message}")

                # Record invalid selector with all tests using it
                test_list = ", ".join([f"{tid} ({name})" for tid, name in test_info])
                self.results["invalid_selectors"].append({
                    "selector": selector,
                    "message": message,
                    "tests": test_list
                })

            # Small delay to avoid overwhelming the browser
            time.sleep(0.1)

    def generate_report(self) -> str:
        """
        Generate a detailed validation report

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("Selector Validation Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Application: {self.base_url}")
        report.append("")

        # Summary
        report.append("Summary")
        report.append("-" * 40)
        report.append(f"Total Selectors:  {self.results['total']}")
        report.append(f"Valid:            {self.results['valid']} ({self.results['valid']/self.results['total']*100:.1f}%)" if self.results['total'] > 0 else "Valid:            0 (0.0%)")
        report.append(f"Invalid:          {self.results['invalid']} ({self.results['invalid']/self.results['total']*100:.1f}%)" if self.results['total'] > 0 else "Invalid:          0 (0.0%)")
        report.append("")

        # Invalid selectors
        if self.results["invalid_selectors"]:
            report.append("Invalid Selectors")
            report.append("-" * 40)

            for i, item in enumerate(self.results["invalid_selectors"], 1):
                report.append(f"\n{i}. {item['selector']}")
                report.append(f"   Reason: {item['message']}")
                report.append(f"   Used in: {item['tests']}")

                # Suggest fixes
                suggestion = self.suggest_fix(item['selector'])
                if suggestion:
                    report.append(f"   💡 Suggestion: {suggestion}")

            report.append("")

        # Recommendations
        report.append("Recommendations")
        report.append("-" * 40)

        if self.results["invalid"] == 0:
            report.append("✅ All selectors are valid! No action needed.")
        else:
            invalid_rate = (self.results["invalid"] / self.results["total"]) * 100
            if invalid_rate > 20:
                report.append("🚨 HIGH: More than 20% of selectors are invalid.")
                report.append("   Action: Review and fix all invalid selectors immediately.")
            elif invalid_rate > 10:
                report.append("⚠️  MEDIUM: More than 10% of selectors are invalid.")
                report.append("   Action: Fix invalid selectors before running tests.")
            else:
                report.append("ℹ️  LOW: Some selectors are invalid.")
                report.append("   Action: Fix invalid selectors when convenient.")

        report.append("")

        # Common issues
        common_issues = self.analyze_common_issues()
        if common_issues:
            report.append("Common Issues Detected")
            report.append("-" * 40)
            for issue, count in common_issues.items():
                report.append(f"• {issue}: {count} occurrences")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)

    def suggest_fix(self, selector: str) -> str:
        """
        Suggest a fix for an invalid selector

        Args:
            selector: Invalid CSS selector

        Returns:
            Suggestion string or None
        """
        suggestions = []

        # Check for common issues
        if selector.startswith('.') and selector.count('.') > 1:
            # Multiple class selector
            classes = selector[1:].split('.')
            suggested = '.' + '.'.join(classes)
            if suggested != selector:
                suggestions.append(f"Try combining classes: {suggested}")

        if selector.startswith('#') and len(selector) > 20:
            suggestions.append("ID is very long - verify it's correct")

        if ' ' not in selector and '>' not in selector:
            # Single element selector
            if selector.startswith('.'):
                suggestions.append("Check if class name has changed or is dynamically generated")

        if '::' in selector or ':' in selector:
            suggestions.append("Pseudo-elements/classes may not work with querySelector")

        return "; ".join(suggestions) if suggestions else None

    def analyze_common_issues(self) -> Dict[str, int]:
        """
        Analyze common patterns in invalid selectors

        Returns:
            Dictionary of issue patterns and their counts
        """
        issues = defaultdict(int)

        for item in self.results["invalid_selectors"]:
            selector = item["selector"]

            if "::" in selector or ":" in selector:
                issues["Pseudo-element/class usage"] += 1

            if selector.startswith('.') and selector.count('.') > 2:
                issues["Complex class selector"] += 1

            if len(selector) > 50:
                issues["Very long selector"] += 1

            if "=" in selector or "[" in selector:
                issues["Attribute selector"] += 1

            if " " not in selector:
                issues["Single element selector"] += 1

        return dict(issues)

    def save_report(self, report: str, output_file: str = None) -> None:
        """
        Save report to file

        Args:
            report: Report string to save
            output_file: Optional output file path
        """
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = Path(__file__).parent.parent / "output" / f"selector_validation_{timestamp}.txt"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 Report saved to: {output_path}")

    def run(self, output_file: str = None) -> int:
        """
        Run the complete validation workflow

        Args:
            output_file: Optional output file path for the report

        Returns:
            Exit code (0 for success, 1 for failures)
        """
        print("🚀 Starting Selector Validation...")
        print(f"📍 Application URL: {self.base_url}")
        print(f"📂 Test configs dir: {self.test_configs_dir}")

        # Load configurations
        configs = self.load_test_configs()
        if not configs:
            print("❌ No test configurations found")
            return 1

        print(f"✅ Loaded {len(configs)} test configuration(s)")

        # Extract selectors
        selectors = self.extract_selectors(configs)
        if not selectors:
            print("⚠️  No selectors found in configurations")
            return 0

        print(f"✅ Extracted {len(selectors)} selector(s)")

        # Validate selectors
        self.validate_selectors(selectors)

        # Generate and display report
        report = self.generate_report()
        print("\n" + report)

        # Save report
        self.save_report(report, output_file)

        # Return exit code based on results
        if self.results["invalid"] > 0:
            print(f"\n⚠️  Validation completed with {self.results['invalid']} invalid selector(s)")
            return 1
        else:
            print(f"\n✅ Validation completed successfully - all selectors valid!")
            return 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate CSS selectors in test configurations"
    )
    parser.add_argument(
        '--url',
        default='http://localhost:5173',
        help='Application URL to test (default: http://localhost:5173)'
    )
    parser.add_argument(
        '--output',
        help='Output file for the validation report'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Check if agent-browser is available
    try:
        subprocess.run(
            ['agent-browser', '--version'],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ agent-browser not found or not working")
        print("   Please install agent-browser first:")
        print("   npm install -g @agent-browser/cli")
        return 1

    # Run validator
    validator = SelectorValidator(base_url=args.url)
    exit_code = validator.run(output_file=args.output)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

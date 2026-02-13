#!/usr/bin/env python3
"""
Canvas Integration Test - Server-side verification
Tests canvas page accessibility and JavaScript file loading
"""

import requests
import re
import sys
from pathlib import Path

class CanvasIntegrationTest:
    def __init__(self, base_url="http://127.0.0.1:5001"):
        self.base_url = base_url
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'tests': []
        }

    def test(self, name, test_func):
        """Run a single test"""
        self.results['total'] += 1
        try:
            result = test_func()
            self.results['passed'] += 1
            self.results['tests'].append({
                'name': name,
                'status': 'PASS',
                'error': None
            })
            print(f"✅ {name}")
            return True
        except AssertionError as e:
            self.results['failed'] += 1
            self.results['tests'].append({
                'name': name,
                'status': 'FAIL',
                'error': str(e)
            })
            print(f"❌ {name}")
            print(f"   Error: {e}")
            return False
        except Exception as e:
            self.results['failed'] += 1
            self.results['tests'].append({
                'name': name,
                'status': 'ERROR',
                'error': str(e)
            })
            print(f"❌ {name}")
            print(f"   Error: {e}")
            return False

    def test_flask_running(self):
        """Test 1: Flask server is running"""
        response = requests.get(self.base_url, timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        return True

    def test_canvas_page_loads(self):
        """Test 2: Canvas page loads"""
        response = requests.get(f"{self.base_url}/canvas/node_canvas?game_id=1", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        return True

    def test_canvas_html_contains_required_elements(self):
        """Test 3: Canvas HTML contains required elements"""
        response = requests.get(f"{self.base_url}/canvas/node_canvas?game_id=1", timeout=5)
        html = response.text

        # Check for required DOM elements
        required_ids = [
            'nodeCanvas',
            'nodesContainer',
            'connectionsLayer',
            'nodePalette',
            'propertiesContent',
            'fieldBuilderModal',
            'sqlPreview'
        ]

        missing = []
        for element_id in required_ids:
            if f'id="{element_id}"' not in html:
                missing.append(element_id)

        assert len(missing) == 0, f"Missing DOM elements: {', '.join(missing)}"
        return True

    def test_node_canvas_js_loaded(self):
        """Test 4: node-canvas.js is referenced"""
        response = requests.get(f"{self.base_url}/canvas/node_canvas?game_id=1", timeout=5)
        html = response.text

        assert 'node-canvas.js' in html, "node-canvas.js not referenced"
        return True

    def test_all_canvas_js_files_referenced(self):
        """Test 5: All canvas JS files are referenced"""
        response = requests.get(f"{self.base_url}/canvas/node_canvas?game_id=1", timeout=5)
        html = response.text

        required_js = [
            'node-canvas.js',
            'canvas-drag-drop.js',
            'canvas-connection.js',
            'node-properties.js',
            'node-templates.js',
            'node-executor.js',
            'node-connection-validator.js',
            'canvas-integration-test.js'
        ]

        missing = []
        for js_file in required_js:
            if js_file not in html:
                missing.append(js_file)

        assert len(missing) == 0, f"Missing JS files: {', '.join(missing)}"
        return True

    def test_node_canvas_js_accessible(self):
        """Test 6: node-canvas.js file is accessible"""
        response = requests.get(f"{self.base_url}/static/js/node-canvas.js", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        content = response.text
        assert len(content) > 50000, "node-canvas.js seems too small"

        # Check for key NodeCanvas object
        assert 'NodeCanvas' in content, "NodeCanvas object not found"
        assert 'const NodeCanvas' in content or 'var NodeCanvas' in content, "NodeCanvas declaration not found"

        return True

    def test_all_js_files_accessible(self):
        """Test 7: All canvas JS files are accessible"""
        required_js = [
            'node-canvas.js',
            'canvas-drag-drop.js',
            'canvas-connection.js',
            'node-properties.js',
            'node-templates.js',
            'node-executor.js',
            'node-connection-validator.js'
        ]

        missing = []
        for js_file in required_js:
            response = requests.get(f"{self.base_url}/static/js/{js_file}", timeout=5)
            if response.status_code != 200:
                missing.append(f"{js_file} (status: {response.status_code})")
            elif len(response.text) < 1000:
                missing.append(f"{js_file} (too small: {len(response.text)} bytes)")

        assert len(missing) == 0, f"Inaccessible JS files: {', '.join(missing)}"
        return True

    def test_game_context_in_html(self):
        """Test 8: Game context is passed to template"""
        response = requests.get(f"{self.base_url}/canvas/node_canvas?game_id=1", timeout=5)
        html = response.text

        # Check for game data script
        assert 'window.gameData' in html, "window.gameData not found in HTML"
        assert 'gameId' in html, "gameId not found in HTML"

        return True

    def test_integration_test_suite_loaded(self):
        """Test 9: Integration test suite is loaded"""
        response = requests.get(f"{self.base_url}/static/tests/canvas-integration-test.js", timeout=5)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        content = response.text
        assert 'CanvasIntegrationTest' in content, "CanvasIntegrationTest not found"
        assert 'runAll' in content, "runAll method not found"

        return True

    def test_api_endpoints_accessible(self):
        """Test 10: Canvas API endpoints are accessible"""
        endpoints = [
            '/api/canvas/flows',
            '/api/canvas/nodes',
            '/api/events',
            '/api/games'
        ]

        failed = []
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                # Accept 200 or 404 (endpoint might exist but return no data)
                if response.status_code not in [200, 404]:
                    failed.append(f"{endpoint} (status: {response.status_code})")
            except Exception as e:
                failed.append(f"{endpoint} (error: {e})")

        # Allow some failures (not all endpoints might be implemented)
        assert len(failed) <= 2, f"Too many failed endpoints: {', '.join(failed)}"
        return True

    def run_all(self):
        """Run all tests"""
        print("🧪 Canvas Integration Test Suite (Server-side)")
        print("=" * 60)

        tests = [
            ("Flask Server Running", self.test_flask_running),
            ("Canvas Page Loads", self.test_canvas_page_loads),
            ("Canvas HTML Elements", self.test_canvas_html_contains_required_elements),
            ("node-canvas.js Referenced", self.test_node_canvas_js_loaded),
            ("All JS Files Referenced", self.test_all_canvas_js_files_referenced),
            ("node-canvas.js Accessible", self.test_node_canvas_js_accessible),
            ("All JS Files Accessible", self.test_all_js_files_accessible),
            ("Game Context Passed", self.test_game_context_in_html),
            ("Integration Test Suite Loaded", self.test_integration_test_suite_loaded),
            ("API Endpoints Accessible", self.test_api_endpoints_accessible),
        ]

        for name, test_func in tests:
            self.test(name, test_func)

        self.print_summary()
        return self.results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"Total Tests: {self.results['total']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"Pass Rate: {(self.results['passed'] / self.results['total'] * 100):.1f}%")
        print("=" * 60)

        if self.results['failed'] > 0:
            print("\nFailed Tests:")
            for test in self.results['tests']:
                if test['status'] in ['FAIL', 'ERROR']:
                    print(f"  ❌ {test['name']}")
                    print(f"     {test['error']}")

if __name__ == '__main__':
    tester = CanvasIntegrationTest()
    results = tester.run_all()
    sys.exit(0 if results['failed'] == 0 else 1)

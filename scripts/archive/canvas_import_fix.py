#!/usr/bin/env python3
"""
Canvas Import Verification Test Script

This script verifies that all Canvas module imports work correctly
after fixing the import path issues.

Author: Claude Code
Date: 2026-02-10
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_canvas_imports():
    """Test that Canvas module imports work correctly"""
    print("=" * 70)
    print("Testing Canvas Module Imports")
    print("=" * 70)

    all_passed = True

    # Test 1: Canvas service __init__ import
    print("\n[Test 1] Testing Canvas service __init__ import...")
    try:
        from backend.services.canvas import canvas_bp
        print("✅ PASS: Canvas service imported successfully")
        print(f"   Blueprint name: {canvas_bp.name}")
    except ImportError as e:
        print(f"❌ FAIL: Canvas service import failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        all_passed = False

    # Test 2: Canvas blueprint import
    print("\n[Test 2] Testing Canvas blueprint import...")
    try:
        from backend.services.canvas.canvas import canvas_bp as canvas_bp_direct
        print("✅ PASS: Canvas blueprint imported successfully")
        print(f"   Blueprint name: {canvas_bp_direct.name}")
        print(f"   Number of routes: {len(canvas_bp_direct.deferred_functions)}")
    except ImportError as e:
        print(f"❌ FAIL: Canvas blueprint import failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        all_passed = False

    # Test 3: Node canvas flows module
    print("\n[Test 3] Testing node canvas flows module...")
    try:
        from backend.services.canvas import node_canvas_flows
        print("✅ PASS: Node canvas flows module imported successfully")
        print(f"   Module: {node_canvas_flows.__name__}")

        # Check if key functions exist
        functions = [
            'build_dependency_graph',
            'topological_sort',
        ]
        for func_name in functions:
            if hasattr(node_canvas_flows, func_name):
                print(f"   ✓ Function '{func_name}' found")
            else:
                print(f"   ✗ Function '{func_name}' NOT found")
    except ImportError as e:
        print(f"❌ FAIL: Node canvas flows import failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        all_passed = False

    # Test 4: Event nodes service
    print("\n[Test 4] Testing Event nodes service...")
    try:
        from backend.services.events.event_nodes import event_nodes_bp
        print("✅ PASS: Event nodes blueprint imported successfully")
        print(f"   Blueprint name: {event_nodes_bp.name}")
    except ImportError as e:
        print(f"❌ FAIL: Event nodes import failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        all_passed = False

    # Test 5: Verify backend.services.node does NOT exist (the old incorrect path)
    print("\n[Test 5] Verifying old incorrect path does NOT exist...")
    try:
        from backend.services.node import event_node_builder_bp
        print(f"❌ FAIL: Old incorrect path still exists! This should have been removed.")
        all_passed = False
    except ImportError:
        print("✅ PASS: Old incorrect path correctly does not exist")
    except Exception as e:
        print(f"⚠️  WARNING: Unexpected error: {e}")

    # Test 6: List all Canvas API routes
    print("\n[Test 6] Listing Canvas API routes...")
    try:
        from backend.services.canvas.canvas import canvas_bp

        # Get routes from the blueprint
        print(f"   Canvas blueprint has {len(canvas_bp.deferred_functions)} deferred functions")

        # Try to access registered routes
        if hasattr(canvas_bp, 'routes'):
            routes = canvas_bp.routes
            print(f"   Total routes: {len(routes)}")
            for rule in routes[:5]:  # Show first 5 routes
                print(f"   - {rule.methods} {rule.rule}")
        else:
            print("   (Route listing not available in deferred mode)")

        print("✅ PASS: Canvas routes accessible")
    except Exception as e:
        print(f"⚠️  WARNING: Could not list routes: {e}")

    # Test 7: Verify key Canvas functions exist
    print("\n[Test 7] Verifying key Canvas functions exist...")
    try:
        from backend.services.canvas.canvas import (
            generate_mock_results,
            validate_flow,
            health_check
        )
        print("✅ PASS: Key Canvas functions imported successfully")
        print("   ✓ generate_mock_results")
        print("   ✓ validate_flow")
        print("   ✓ health_check")
    except ImportError as e:
        print(f"❌ FAIL: Canvas functions import failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"❌ FAIL: Unexpected error: {e}")
        all_passed = False

    # Summary
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nCanvas module imports are working correctly.")
        print("The import path fix was successful.")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        print("\nPlease review the failed tests above.")
        return 1


if __name__ == '__main__':
    exit_code = test_canvas_imports()
    sys.exit(exit_code)

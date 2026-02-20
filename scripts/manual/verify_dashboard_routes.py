#!/usr/bin/env python3
"""
Verify Dashboard Routes are Registered

This script checks if the dashboard routes are properly registered
by checking the Flask application's URL map.

Usage:
    python3 scripts/manual/verify_dashboard_routes.py
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def check_dashboard_routes():
    """Check if dashboard routes are registered"""
    try:
        # Import Flask app
        from web_app import app

        print("=" * 80)
        print("Checking Dashboard Routes Registration")
        print("=" * 80)

        # Get all routes
        rules = list(app.url_map.iter_rules())

        # Check for dashboard routes
        dashboard_routes = [r for r in rules if 'dashboard' in r.rule]

        if dashboard_routes:
            print(f"\n✅ Found {len(dashboard_routes)} dashboard route(s):")
            for route in dashboard_routes:
                methods = ', '.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
                print(f"   - {route.rule:50s} [{methods}]")
            return True
        else:
            print("\n❌ No dashboard routes found!")
            print("\nAvailable API routes:")
            api_routes = [r for r in rules if r.rule.startswith('/api/')]
            for route in sorted(api_routes, key=lambda x: x.rule)[:20]:
                methods = ', '.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
                print(f"   - {route.rule:50s} [{methods}]")

            if len(api_routes) > 20:
                print(f"   ... and {len(api_routes) - 20} more")

            return False

    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = check_dashboard_routes()
    sys.exit(0 if success else 1)

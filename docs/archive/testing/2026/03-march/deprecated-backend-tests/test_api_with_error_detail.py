#!/usr/bin/env python3
"""Direct test of event_node_builder API with full error details"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import Flask app to test directly
from web_app import app


def test_search_endpoint():
    """Test /event_node_builder/api/search endpoint"""
    print("Testing /event_node_builder/api/search...")

    with app.test_client() as client:
        try:
            response = client.get('/event_node_builder/api/search?game_gid=10000147')
            print(f"Status: {response.status_code}")
            print(f"Data: {response.get_data(as_text=True)[:500]}")

            if response.status_code != 200:
                # Get detailed error
                print(f"\nFull response:")
                print(response.get_data(as_text=True))

            return response.status_code == 200
        except Exception as e:
            print(f"Exception: {e}")
            import traceback

            traceback.print_exc()
            return False


def test_stats_endpoint():
    """Test /event_node_builder/api/stats endpoint"""
    print("\nTesting /event_node_builder/api/stats...")

    with app.test_client() as client:
        try:
            response = client.get('/event_node_builder/api/stats?game_gid=10000147')
            print(f"Status: {response.status_code}")
            print(f"Data: {response.get_data(as_text=True)[:500]}")

            if response.status_code != 200:
                # Get detailed error
                print(f"\nFull response:")
                print(response.get_data(as_text=True))

            return response.status_code == 200
        except Exception as e:
            print(f"Exception: {e}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Flask app with test client (shows full errors)")
    print("=" * 60)

    results = []
    results.append(test_search_endpoint())
    results.append(test_stats_endpoint())

    print(f"\n{'='*60}")
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print(f"{'='*60}")

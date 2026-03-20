#!/usr/bin/env python3
"""Direct test of event_node_builder API endpoints"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import json


def test_search_endpoint():
    """Test /event_node_builder/api/search endpoint"""
    print("Testing /event_node_builder/api/search...")
    try:
        response = requests.get(
            'http://127.0.0.1:5001/event_node_builder/api/search',
            params={'game_gid': 10000147},
            timeout=5,
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers.get('content-type')}")
        print(f"Response: {response.text[:500]}")
        return response.status_code == 200
    except Exception as e:
        print(f"Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_stats_endpoint():
    """Test /event_node_builder/api/stats endpoint"""
    print("\nTesting /event_node_builder/api/stats...")
    try:
        response = requests.get(
            'http://127.0.0.1:5001/event_node_builder/api/stats',
            params={'game_gid': 10000147},
            timeout=5,
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers.get('content-type')}")
        print(f"Response: {response.text[:500]}")
        return response.status_code == 200
    except Exception as e:
        print(f"Exception: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == '__main__':
    results = []
    results.append(test_search_endpoint())
    results.append(test_stats_endpoint())

    print(f"\n{'='*50}")
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print(f"{'='*50}")

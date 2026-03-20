#!/usr/bin/env python3
"""Comprehensive verification of all TDD fixes"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import requests
import json


def test_backend_api():
    """Test backend API endpoints"""
    print("=" * 60)
    print("Testing Backend API Endpoints")
    print("=" * 60)

    results = []

    # Test 1: /event_node_builder/api/search
    print("\n1. Testing /event_node_builder/api/search...")
    try:
        response = requests.get(
            'http://127.0.0.1:5001/event_node_builder/api/search',
            params={'game_gid': 10000147},
            timeout=5,
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Valid JSON returned: {data.get('message')}")
            results.append(True)
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ✗ Error: {e}")
        results.append(False)

    # Test 2: /event_node_builder/api/stats
    print("\n2. Testing /event_node_builder/api/stats...")
    try:
        response = requests.get(
            'http://127.0.0.1:5001/event_node_builder/api/stats',
            params={'game_gid': 10000147},
            timeout=5,
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Valid JSON returned: {data.get('message')}")
            print(f"   ✓ Stats: {data.get('data')}")
            results.append(True)
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            results.append(False)
    except Exception as e:
        print(f"   ✗ Error: {e}")
        results.append(False)

    print(f"\nBackend API: {sum(results)}/{len(results)} tests passed")
    return all(results)


def test_frontend_page():
    """Test frontend page loads"""
    print("\n" + "=" * 60)
    print("Testing Frontend Page")
    print("=" * 60)

    print("\n1. Testing event-nodes page...")
    try:
        response = requests.get('http://localhost:5173/#/event-nodes?game_gid=10000147', timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Page loads successfully")
            return True
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def main():
    print("\n" + "█" * 60)
    print("█ TDD FIXES VERIFICATION")
    print("█" * 60 + "\n")

    results = []

    # Test backend APIs
    results.append(test_backend_api())

    # Test frontend
    results.append(test_frontend_page())

    print("\n" + "=" * 60)
    print(f"FINAL RESULTS: {sum(results)}/{len(results)} categories passed")
    print("=" * 60)

    if all(results):
        print("\n✓ ALL FIXES VERIFIED SUCCESSFULLY!")
        return 0
    else:
        print("\n✗ Some fixes need attention")
        return 1


if __name__ == '__main__':
    sys.exit(main())

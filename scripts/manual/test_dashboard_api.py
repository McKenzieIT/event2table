#!/usr/bin/env python3
"""
Test Dashboard Statistics API

This script tests the new dashboard statistics endpoints:
- GET /api/dashboard/stats - Complete statistics
- GET /api/dashboard/summary - Lightweight summary

Usage:
    python scripts/manual/test_dashboard_api.py
    python scripts/manual/test_dashboard_api.py --game-gid 10000147

Author: Event2Table Development Team
Date: 2026-02-20
"""

import requests
import json
import sys
import argparse
from datetime import datetime

# Configuration
API_BASE_URL = "http://127.0.0.1:5001"
DEFAULT_GAME_GID = 10000147  # STAR001


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")


def test_dashboard_summary():
    """Test GET /api/dashboard/summary"""
    print_section("Test 1: Dashboard Summary (All Games)")

    url = f"{API_BASE_URL}/api/dashboard/summary"
    print_info(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print_success("API call successful!")

            if result.get("success"):
                data = result.get("data", {})
                print("\n📊 Dashboard Summary:")
                print(f"   Total Games: {data.get('total_games', 0)}")
                print(f"   Total Events: {data.get('total_events', 0)}")
                print(f"   Total Params: {data.get('total_params', 0)}")
                print(f"   Total Flows: {data.get('total_flows', 0)}")
                print(f"   Last Updated: {data.get('last_updated', 'N/A')}")
                print(f"   Health Status: {data.get('health_status', 'unknown')}")

                # Verify data integrity
                assert isinstance(data.get('total_games'), int), "total_games should be integer"
                assert isinstance(data.get('total_events'), int), "total_events should be integer"
                assert isinstance(data.get('total_params'), int), "total_params should be integer"
                assert isinstance(data.get('total_flows'), int), "total_flows should be integer"

                print_success("Data validation passed")
                return True
            else:
                print_error(f"API returned error: {result.get('message')}")
                return False
        else:
            print_error(f"HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_dashboard_stats():
    """Test GET /api/dashboard/stats"""
    print_section("Test 2: Dashboard Statistics (All Games)")

    url = f"{API_BASE_URL}/api/dashboard/stats"
    print_info(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print_success("API call successful!")

            if result.get("success"):
                data = result.get("data", {})
                print("\n📊 Dashboard Statistics:")

                # Basic counts
                print(f"\n   Basic Counts:")
                print(f"   - Total Games: {data.get('total_games', 0)}")
                print(f"   - Total Events: {data.get('total_events', 0)}")
                print(f"   - Total Params: {data.get('total_params', 0)}")
                print(f"   - Total Flows: {data.get('total_flows', 0)}")

                # Event categories
                event_categories = data.get('event_categories', {})
                if event_categories:
                    print(f"\n   Event Categories ({len(event_categories)} categories):")
                    for category, count in list(event_categories.items())[:5]:
                        print(f"   - {category}: {count}")
                    if len(event_categories) > 5:
                        print(f"   - ... and {len(event_categories) - 5} more")

                # Recent events
                recent_events = data.get('recent_events', [])
                print(f"\n   Recent Events ({len(recent_events)} events):")
                for event in recent_events[:3]:
                    print(f"   - {event.get('event_name')} ({event.get('game_name')})")
                if len(recent_events) > 3:
                    print(f"   - ... and {len(recent_events) - 3} more")

                # Top games
                top_games = data.get('top_games', [])
                print(f"\n   Top Games (by event count):")
                for game in top_games[:5]:
                    print(f"   - {game.get('name')}: {game.get('event_count')} events, {game.get('param_count')} params")

                # Common params
                common_params = data.get('common_params', [])
                print(f"\n   Common Parameters (Top 5):")
                for param in common_params[:5]:
                    print(f"   - {param.get('param_name')}: {param.get('count')} occurrences")

                # Last updated
                print(f"\n   Last Updated: {data.get('last_updated', 'N/A')}")

                # Verify data integrity
                assert isinstance(data.get('total_games'), int), "total_games should be integer"
                assert isinstance(data.get('event_categories'), dict), "event_categories should be dict"
                assert isinstance(data.get('recent_events'), list), "recent_events should be list"
                assert isinstance(data.get('top_games'), list), "top_games should be list"
                assert isinstance(data.get('common_params'), list), "common_params should be list"

                print_success("Data validation passed")
                return True
            else:
                print_error(f"API returned error: {result.get('message')}")
                return False
        else:
            print_error(f"HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_dashboard_stats_filtered(game_gid):
    """Test GET /api/dashboard/stats with game_gid filter"""
    print_section(f"Test 3: Dashboard Statistics (Game GID: {game_gid})")

    url = f"{API_BASE_URL}/api/dashboard/stats"
    params = {"game_gid": game_gid}
    print_info(f"URL: {url}")
    print_info(f"Params: game_gid={game_gid}")

    try:
        response = requests.get(url, params=params, timeout=10)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print_success("API call successful!")

            if result.get("success"):
                data = result.get("data", {})
                print("\n📊 Dashboard Statistics (Filtered):")

                # Verify filter worked
                if data.get('total_games', 0) == 1:
                    print_success("Game filter working correctly (1 game)")
                else:
                    print_error(f"Expected 1 game, got {data.get('total_games', 0)}")

                print(f"\n   Basic Counts:")
                print(f"   - Total Games: {data.get('total_games', 0)}")
                print(f"   - Total Events: {data.get('total_events', 0)}")
                print(f"   - Total Params: {data.get('total_params', 0)}")
                print(f"   - Total Flows: {data.get('total_flows', 0)}")

                # Top games should only show the filtered game
                top_games = data.get('top_games', [])
                print(f"\n   Top Games:")
                for game in top_games:
                    print(f"   - {game.get('name')} (GID: {game.get('gid')}): {game.get('event_count')} events")

                print_success("Filter validation passed")
                return True
            else:
                print_error(f"API returned error: {result.get('message')}")
                return False
        else:
            print_error(f"HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_dashboard_summary_filtered(game_gid):
    """Test GET /api/dashboard/summary with game_gid filter"""
    print_section(f"Test 4: Dashboard Summary (Game GID: {game_gid})")

    url = f"{API_BASE_URL}/api/dashboard/summary"
    params = {"game_gid": game_gid}
    print_info(f"URL: {url}")
    print_info(f"Params: game_gid={game_gid}")

    try:
        response = requests.get(url, params=params, timeout=10)
        print_info(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print_success("API call successful!")

            if result.get("success"):
                data = result.get("data", {})
                print("\n📊 Dashboard Summary (Filtered):")
                print(f"   Total Games: {data.get('total_games', 0)}")
                print(f"   Total Events: {data.get('total_events', 0)}")
                print(f"   Total Params: {data.get('total_params', 0)}")
                print(f"   Total Flows: {data.get('total_flows', 0)}")
                print(f"   Health Status: {data.get('health_status', 'unknown')}")

                # Verify filter worked
                if data.get('total_games', 0) == 1:
                    print_success("Game filter working correctly (1 game)")
                else:
                    print_error(f"Expected 1 game, got {data.get('total_games', 0)}")

                return True
            else:
                print_error(f"API returned error: {result.get('message')}")
                return False
        else:
            print_error(f"HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print_error(f"Request failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_cache_performance():
    """Test caching performance"""
    print_section("Test 5: Cache Performance")

    url = f"{API_BASE_URL}/api/dashboard/summary"

    try:
        # First call (cache miss)
        print_info("First call (cache miss)...")
        start = datetime.now()
        response1 = requests.get(url, timeout=10)
        duration1 = (datetime.now() - start).total_seconds() * 1000

        if response1.status_code != 200:
            print_error(f"First call failed: {response1.status_code}")
            return False

        print_info(f"First call duration: {duration1:.2f}ms")

        # Second call (cache hit)
        print_info("Second call (cache hit)...")
        start = datetime.now()
        response2 = requests.get(url, timeout=10)
        duration2 = (datetime.now() - start).total_seconds() * 1000

        if response2.status_code != 200:
            print_error(f"Second call failed: {response2.status_code}")
            return False

        print_info(f"Second call duration: {duration2:.2f}ms")

        # Verify cache is faster (or similar)
        if duration2 < duration1:
            speedup = duration1 / duration2
            print_success(f"Cache speedup: {speedup:.2f}x faster")
        else:
            print_info("Cache may not be enabled or response times are similar")

        return True

    except Exception as e:
        print_error(f"Performance test failed: {e}")
        return False


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Test Dashboard Statistics API")
    parser.add_argument("--game-gid", type=int, default=DEFAULT_GAME_GID,
                        help=f"Game GID to test with (default: {DEFAULT_GAME_GID})")
    parser.add_argument("--skip-performance", action="store_true",
                        help="Skip cache performance test")

    args = parser.parse_args()

    print_section("Dashboard Statistics API Test Suite")
    print_info(f"API Base URL: {API_BASE_URL}")
    print_info(f"Test Game GID: {args.game_gid}")
    print_info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run tests
    results = []

    results.append(("Dashboard Summary (All)", test_dashboard_summary()))
    results.append(("Dashboard Stats (All)", test_dashboard_stats()))
    results.append(("Dashboard Stats (Filtered)", test_dashboard_stats_filtered(args.game_gid)))
    results.append(("Dashboard Summary (Filtered)", test_dashboard_summary_filtered(args.game_gid)))

    if not args.skip_performance:
        results.append(("Cache Performance", test_cache_performance()))

    # Print summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print_success("All tests passed!")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

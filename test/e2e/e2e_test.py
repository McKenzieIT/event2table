#!/usr/bin/env python3
"""
E2E (End-to-End) Test Suite for event2table project

This script performs comprehensive API endpoint testing to verify all critical user journeys.
It tests the Flask backend by making actual HTTP requests to the running server.

Usage:
    1. Start the Flask server: python3 web_app.py
    2. In another terminal, run: python3 e2e_test.py
"""

import sys
import os
import json
import time
import sqlite3
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode

# Try to import requests, provide helpful message if not available
try:
    import requests
except ImportError:
    print("ERROR: 'requests' library is not installed.")
    print("Please install it using: pip3 install requests")
    sys.exit(1)

# Configuration
BASE_URL = "http://localhost:5001"
TEST_RESULTS_DIR = Path("/Users/mckenzie/Documents/event2table/test_results")
TEST_RESULTS_FILE = TEST_RESULTS_DIR / "e2e_test_results.txt"

# Test tracking
test_results = {
    "start_time": datetime.now().isoformat(),
    "end_time": None,
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": [],
    "tests": []
}

# Test data cleanup tracking
test_data_created = []

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def print_test(test_name, status, details=""):
    """Print test result"""
    symbol = "✅ PASS" if status == "PASS" else "❌ FAIL"
    print(f"{symbol}: {test_name}")
    if details:
        print(f"   Details: {details}")

    # Track results
    test_results["total_tests"] += 1
    if status == "PASS":
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append({
            "test": test_name,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    test_results["tests"].append({
        "name": test_name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })

def api_request(method, endpoint, data=None, params=None, expected_status=200):
    """
    Make an API request and return the response

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint path
        data: Request body data (for POST/PUT)
        params: Query parameters
        expected_status: Expected HTTP status code

    Returns:
        tuple: (status_code, response_data)
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}

    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, params=params, headers=headers, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, params=params, headers=headers, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, params=params, headers=headers, timeout=10)
        else:
            return None, "Unsupported HTTP method"

        try:
            response_data = response.json()
        except:
            response_data = response.text

        return response.status_code, response_data

    except requests.exceptions.ConnectionError:
        return None, "Connection refused - Is the Flask server running?"
    except requests.exceptions.Timeout:
        return None, "Request timeout"
    except Exception as e:
        return None, str(e)

# ============================================================================
# 1. Server Health Check
# ============================================================================

def test_server_health():
    """Test if the Flask server is running"""
    print_header("1. SERVER HEALTH CHECK")

    try:
        # Use games endpoint for health check since root may not exist
        response = requests.get(f"{BASE_URL}/api/games", timeout=5)
        if response.status_code == 200:
            print_test("Server is running", "PASS", f"Status: {response.status_code}")
            return True
        else:
            print_test("Server health check", "FAIL", f"Unexpected status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test("Server connection", "FAIL", "Connection refused - Is the Flask server running on http://localhost:5001?")
        return False
    except Exception as e:
        print_test("Server health check", "FAIL", str(e))
        return False

# ============================================================================
# 2. Game Management Tests
# ============================================================================

def test_game_list():
    """Test GET /api/games - List all games"""
    print("\n2.1 Testing GET /api/games - List all games")

    status, data = api_request("GET", "/api/games", expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            games = data["data"]
            print_test("GET /api/games", "PASS", f"Found {len(games)} games")
            return games
        elif isinstance(data, list):
            print_test("GET /api/games", "PASS", f"Found {len(data)} games")
            return data
        else:
            print_test("GET /api/games", "FAIL", f"Unexpected response format: {type(data)}")
            return []
    else:
        print_test("GET /api/games", "FAIL", f"Status: {status}, Response: {data}")
        return []

def test_game_create():
    """Test POST /api/games - Create a new game"""
    print("\n2.2 Testing POST /api/games - Create a new game")

    # Generate unique test GID
    import random
    test_gid = 90000000 + random.randint(1000, 9999)

    game_data = {
        "gid": str(test_gid),
        "name": "TEST_E2E_Game",
        "ods_db": "ieu_ods",
        "description": "E2E test game - should be deleted"
    }

    status, data = api_request("POST", "/api/games", data=game_data, expected_status=201)

    if status == 201 or status == 200:
        print_test("POST /api/games", "PASS", f"Created game with GID: {test_gid}")
        test_data_created.append(("game", test_gid))
        return test_gid
    else:
        print_test("POST /api/games", "FAIL", f"Status: {status}, Response: {data}")
        return None

def test_game_get(game_gid):
    """Test GET /api/games/<gid> - Get a specific game"""
    print(f"\n2.3 Testing GET /api/games/{game_gid} - Get specific game")

    status, data = api_request("GET", f"/api/games/{game_gid}", expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            game = data["data"]
        else:
            game = data

        if game and "gid" in game:
            print_test(f"GET /api/games/{game_gid}", "PASS", f"Retrieved game: {game.get('name', 'N/A')}")
            return True
        else:
            print_test(f"GET /api/games/{game_gid}", "FAIL", f"Invalid game data: {data}")
            return False
    else:
        print_test(f"GET /api/games/{game_gid}", "FAIL", f"Status: {status}, Response: {data}")
        return False

def test_game_update(game_gid):
    """Test PUT /api/games/<gid> - Update a game"""
    print(f"\n2.4 Testing PUT /api/games/{game_gid} - Update game")

    update_data = {
        "name": "TEST_E2E_Game_Updated",
        "description": "E2E test game - updated"
    }

    status, data = api_request("PUT", f"/api/games/{game_gid}", data=update_data, expected_status=200)

    if status == 200:
        print_test(f"PUT /api/games/{game_gid}", "PASS", "Game updated successfully")
        return True
    else:
        print_test(f"PUT /api/games/{game_gid}", "FAIL", f"Status: {status}, Response: {data}")
        return False

def test_game_delete(game_gid):
    """Test DELETE /api/games/<gid> - Delete a game"""
    print(f"\n2.5 Testing DELETE /api/games/{game_gid} - Delete game")

    status, data = api_request("DELETE", f"/api/games/{game_gid}", expected_status=200)

    if status == 200:
        print_test(f"DELETE /api/games/{game_gid}", "PASS", "Game deleted successfully")
        return True
    else:
        print_test(f"DELETE /api/games/{game_gid}", "FAIL", f"Status: {status}, Response: {data}")
        return False

# ============================================================================
# 3. Event Management Tests
# ============================================================================

def test_events_list():
    """Test GET /api/events - List events for a game"""
    print("\n3.1 Testing GET /api/events?game_gid=10000147 - List events")

    # Use existing game that likely has events
    status, data = api_request("GET", "/api/events", params={"game_gid": "10000147"}, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            events = data["data"]
        else:
            events = data if isinstance(data, list) else []

        print_test("GET /api/events", "PASS", f"Found {len(events)} events")
        return events
    else:
        print_test("GET /api/events", "FAIL", f"Status: {status}, Response: {data}")
        return []

def test_events_create(game_gid):
    """Test POST /api/events - Create a new event"""
    print(f"\n3.2 Testing POST /api/events - Create event for game {game_gid}")

    event_data = {
        "game_gid": game_gid,
        "event_name": f"test_e2e_event_{int(time.time())}",
        "event_name_cn": "E2E Test Event",
        "category_id": 1,  # Assuming category 1 exists
        "description": "E2E test event - should be deleted"
    }

    status, data = api_request("POST", "/api/events", data=event_data, expected_status=201)

    if status == 201 or status == 200:
        event_name = event_data["event_name"]
        print_test("POST /api/events", "PASS", f"Created event: {event_name}")
        test_data_created.append(("event", event_name))
        return event_name
    else:
        print_test("POST /api/events", "FAIL", f"Status: {status}, Response: {data}")
        return None

# ============================================================================
# 4. HQL Generation Tests
# ============================================================================

def test_hql_generate_v2_single():
    """Test POST /api/hql/generate_v2 - Generate HQL for single event"""
    print("\n4.1 Testing POST /api/hql/generate_v2 - Single event mode")

    hql_request = {
        "game_gid": "10000147",
        "events": [{"event_id": 55}],
        "mode": "single",
        "name": "e2e_test_single",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"}
        ]
    }

    status, data = api_request("POST", "/api/hql/generate_v2", data=hql_request, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            result = data["data"]
        else:
            result = data

        if result and "hql" in result:
            print_test("POST /api/hql/generate_v2 (single)", "PASS", "HQL generated successfully")
            return True
        else:
            print_test("POST /api/hql/generate_v2 (single)", "FAIL", f"No HQL in response: {data}")
            return False
    else:
        print_test("POST /api/hql/generate_v2 (single)", "FAIL", f"Status: {status}, Response: {data}")
        return False

def test_hql_generate_v2_join():
    """Test POST /api/hql/generate_v2 - Generate HQL for join mode"""
    print("\n4.2 Testing POST /api/hql/generate_v2 - Join mode")

    hql_request = {
        "game_gid": "10000147",
        "events": [{"event_id": 55}, {"event_id": 56}],
        "mode": "join",
        "name": "e2e_test_join",
        "join_key": "user_id",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"}
        ]
    }

    status, data = api_request("POST", "/api/hql/generate_v2", data=hql_request, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            result = data["data"]
        else:
            result = data

        if result and "hql" in result:
            print_test("POST /api/hql/generate_v2 (join)", "PASS", "HQL join generated successfully")
            return True
        else:
            print_test("POST /api/hql/generate_v2 (join)", "FAIL", f"No HQL in response: {data}")
            return False
    else:
        print_test("POST /api/hql/generate_v2 (join)", "FAIL", f"Status: {status}, Response: {data}")
        return False

def test_hql_generate_v2_union():
    """Test POST /api/hql/generate_v2 - Generate HQL for union mode"""
    print("\n4.3 Testing POST /api/hql/generate_v2 - Union mode")

    hql_request = {
        "game_gid": "10000147",
        "events": [{"event_id": 55}, {"event_id": 56}],
        "mode": "union",
        "name": "e2e_test_union",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"}
        ]
    }

    status, data = api_request("POST", "/api/hql/generate_v2", data=hql_request, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            result = data["data"]
        else:
            result = data

        if result and "hql" in result:
            print_test("POST /api/hql/generate_v2 (union)", "PASS", "HQL union generated successfully")
            return True
        else:
            print_test("POST /api/hql/generate_v2 (union)", "FAIL", f"No HQL in response: {data}")
            return False
    else:
        print_test("POST /api/hql/generate_v2 (union)", "FAIL", f"Status: {status}, Response: {data}")
        return False

# ============================================================================
# 5. Canvas System Tests
# ============================================================================

def test_canvas_nodes_list():
    """Test GET /api/canvas/nodes - List canvas nodes"""
    print("\n5.1 Testing GET /api/canvas/nodes - List canvas nodes")

    status, data = api_request("GET", "/api/canvas/nodes", expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            nodes = data["data"]
        else:
            nodes = data if isinstance(data, list) else []

        print_test("GET /api/canvas/nodes", "PASS", f"Found {len(nodes)} canvas nodes")
        return nodes
    else:
        print_test("GET /api/canvas/nodes", "FAIL", f"Status: {status}, Response: {data}")
        return []

def test_canvas_nodes_create():
    """Test POST /api/canvas/nodes - Create a canvas node"""
    print("\n5.2 Testing POST /api/canvas/nodes - Create canvas node")

    node_data = {
        "game_gid": "10000147",
        "name": f"TEST_E2E_NODE_{int(time.time())}",
        "node_type": "event",
        "event_id": 55,
        "description": "E2E test node - should be deleted",
        "position_x": 100,
        "position_y": 100
    }

    status, data = api_request("POST", "/api/canvas/nodes", data=node_data, expected_status=201)

    if status == 201 or status == 200:
        print_test("POST /api/canvas/nodes", "PASS", "Canvas node created successfully")
        if isinstance(data, dict) and "data" in data:
            node_id = data["data"].get("id")
            if node_id:
                test_data_created.append(("canvas_node", node_id))
        return True
    else:
        print_test("POST /api/canvas/nodes", "FAIL", f"Status: {status}, Response: {data}")
        return False

# ============================================================================
# 6. Parameter Management Tests
# ============================================================================

def test_parameters_list():
    """Test GET /api/parameters - List parameters"""
    print("\n6.1 Testing GET /api/parameters - List parameters")

    status, data = api_request("GET", "/api/parameters", params={"game_gid": "10000147"}, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            params = data["data"]
        else:
            params = data if isinstance(data, list) else []

        print_test("GET /api/parameters", "PASS", f"Found {len(params)} parameters")
        return True
    else:
        print_test("GET /api/parameters", "FAIL", f"Status: {status}, Response: {data}")
        return False

# ============================================================================
# 7. Cleanup Test Data
# ============================================================================

def cleanup_test_data():
    """Clean up test data created during testing"""
    print_header("7. CLEANUP TEST DATA")

    for data_type, identifier in test_data_created:
        print(f"\nCleaning up {data_type}: {identifier}")

        try:
            if data_type == "game":
                status, data = api_request("DELETE", f"/api/games/{identifier}", expected_status=200)
                if status == 200:
                    print(f"✅ Deleted game {identifier}")
                else:
                    print(f"⚠️  Failed to delete game {identifier}: {data}")

            elif data_type == "event":
                # Events might need game_gid parameter
                status, data = api_request("DELETE", f"/api/events/{identifier}",
                                          params={"game_gid": "10000147"},
                                          expected_status=200)
                if status == 200:
                    print(f"✅ Deleted event {identifier}")
                else:
                    print(f"⚠️  Failed to delete event {identifier}: {data}")

            elif data_type == "canvas_node":
                status, data = api_request("DELETE", f"/api/canvas/nodes/{identifier}", expected_status=200)
                if status == 200:
                    print(f"✅ Deleted canvas node {identifier}")
                else:
                    print(f"⚠️  Failed to delete canvas node {identifier}: {data}")

        except Exception as e:
            print(f"⚠️  Error cleaning up {data_type} {identifier}: {e}")

# ============================================================================
# Main Test Execution
# ============================================================================

def run_e2e_tests():
    """Run all E2E tests"""
    print_header("EVENT2TABLE E2E TEST SUITE")
    print(f"Start Time: {test_results['start_time']}")
    print(f"Base URL: {BASE_URL}")
    print(f"Results File: {TEST_RESULTS_FILE}")

    # Check server health first
    if not test_server_health():
        print("\n❌ FATAL: Cannot connect to Flask server. Please start the server first:")
        print("   python3 web_app.py")
        save_results()
        return False

    # 1. Game Management Tests
    print_header("2. GAME MANAGEMENT")
    games = test_game_list()
    game_gid = test_game_create()
    if game_gid:
        test_game_get(game_gid)
        test_game_update(game_gid)
        # Note: Don't delete yet, need it for event tests

    # 2. Event Management Tests
    print_header("3. EVENT MANAGEMENT")
    events = test_events_list()
    if game_gid:
        test_events_create(game_gid)

    # 3. HQL Generation Tests
    print_header("4. HQL GENERATION")
    test_hql_generate_v2_single()
    test_hql_generate_v2_join()
    test_hql_generate_v2_union()

    # 4. Canvas System Tests
    print_header("5. CANVAS SYSTEM")
    test_canvas_nodes_list()
    test_canvas_nodes_create()

    # 5. Parameter Management Tests
    print_header("6. PARAMETER MANAGEMENT")
    test_parameters_list()

    # Cleanup
    if game_gid:
        test_game_delete(game_gid)
    cleanup_test_data()

    # Save results
    test_results["end_time"] = datetime.now().isoformat()
    save_results()

    # Print summary
    print_header("E2E TEST SUMMARY")
    print(f"Total Tests: {test_results['total_tests']}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Success Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%")

    if test_results['failed'] > 0:
        print(f"\nFailed Tests:")
        for error in test_results['errors']:
            print(f"  - {error['test']}: {error['details']}")

    print(f"\nResults saved to: {TEST_RESULTS_FILE}")

    return test_results['failed'] == 0

def save_results():
    """Save test results to file"""
    TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    with open(TEST_RESULTS_FILE, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("EVENT2TABLE E2E TEST RESULTS\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Start Time: {test_results['start_time']}\n")
        f.write(f"End Time: {test_results['end_time']}\n")
        f.write(f"Base URL: {BASE_URL}\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Tests: {test_results['total_tests']}\n")
        f.write(f"Passed: {test_results['passed']}\n")
        f.write(f"Failed: {test_results['failed']}\n")
        f.write(f"Success Rate: {(test_results['passed']/test_results['total_tests']*100):.1f}%\n\n")

        if test_results['tests']:
            f.write("DETAILED RESULTS\n")
            f.write("-" * 40 + "\n")
            for test in test_results['tests']:
                status_symbol = "✅" if test['status'] == "PASS" else "❌"
                f.write(f"{status_symbol} {test['name']}\n")
                f.write(f"   Status: {test['status']}\n")
                f.write(f"   Time: {test['timestamp']}\n")
                if test['details']:
                    f.write(f"   Details: {test['details']}\n")
                f.write("\n")

        if test_results['errors']:
            f.write("FAILED TESTS DETAILS\n")
            f.write("-" * 40 + "\n")
            for error in test_results['errors']:
                f.write(f"Test: {error['test']}\n")
                f.write(f"Details: {error['details']}\n")
                f.write(f"Time: {error['timestamp']}\n\n")

        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")

if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)

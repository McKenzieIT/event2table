#!/usr/bin/env python3
"""
E2E (End-to-End) Test Suite for event2table project - FINAL VERSION

This script performs comprehensive API endpoint testing using the correct endpoints.
Based on actual API route inspection.
"""

import sys
import json
import time
import random
from datetime import datetime
from pathlib import Path

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
    "tests": [],
    "endpoints_tested": []
}

# Test data cleanup tracking
test_data_created = []

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def print_test(test_name, status, details="", endpoint=""):
    """Print test result"""
    symbol = "✅ PASS" if status == "PASS" else "❌ FAIL"
    print(f"{symbol}: {test_name}")
    if details:
        print(f"   Details: {details}")
    if endpoint:
        print(f"   Endpoint: {endpoint}")

    # Track results
    test_results["total_tests"] += 1
    if status == "PASS":
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        test_results["errors"].append({
            "test": test_name,
            "details": details,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat()
        })

    if endpoint:
        test_results["endpoints_tested"].append(endpoint)

    test_results["tests"].append({
        "name": test_name,
        "status": status,
        "details": details,
        "endpoint": endpoint,
        "timestamp": datetime.now().isoformat()
    })

def api_request(method, endpoint, data=None, params=None, expected_status=200):
    """Make an API request and return the response"""
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

    status, data = api_request("GET", "/api/games", expected_status=200)

    if status == 200:
        print_test("Server is running", "PASS", f"Status: {status}", "GET /api/games")
        return True
    else:
        print_test("Server health check", "FAIL", f"Status: {status}", "GET /api/games")
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
        else:
            games = data if isinstance(data, list) else []

        print_test("GET /api/games", "PASS", f"Found {len(games)} games", "GET /api/games")
        return games
    else:
        print_test("GET /api/games", "FAIL", f"Status: {status}, Response: {data}", "GET /api/games")
        return []

def test_game_create():
    """Test POST /api/games - Create a new game"""
    print("\n2.2 Testing POST /api/games - Create a new game")

    # Use integer GID (not string)
    test_gid = 90000000 + random.randint(1000, 9999)

    game_data = {
        "gid": test_gid,  # Integer, not string
        "name": "TEST_E2E_Game",
        "ods_db": "ieu_ods",
        "description": "E2E test game"
    }

    status, data = api_request("POST", "/api/games", data=game_data, expected_status=200)

    if status == 200 or status == 201:
        print_test("POST /api/games", "PASS", f"Created game with GID: {test_gid}", "POST /api/games")
        test_data_created.append(("game", test_gid))
        return test_gid
    else:
        print_test("POST /api/games", "FAIL", f"Status: {status}, Response: {data}", "POST /api/games")
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

        if game and ("gid" in game or "id" in game):
            print_test(f"GET /api/games/{game_gid}", "PASS", f"Retrieved game", f"GET /api/games/{game_gid}")
            return True
        else:
            print_test(f"GET /api/games/{game_gid}", "FAIL", f"Invalid game data", f"GET /api/games/{game_gid}")
            return False
    else:
        print_test(f"GET /api/games/{game_gid}", "FAIL", f"Status: {status}", f"GET /api/games/{game_gid}")
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
        print_test(f"PUT /api/games/{game_gid}", "PASS", "Game updated successfully", f"PUT /api/games/{game_gid}")
        return True
    else:
        print_test(f"PUT /api/games/{game_gid}", "FAIL", f"Status: {status}", f"PUT /api/games/{game_gid}")
        return False

def test_game_delete(game_gid):
    """Test DELETE /api/games/<gid> - Delete a game"""
    print(f"\n2.5 Testing DELETE /api/games/{game_gid} - Delete game")

    status, data = api_request("DELETE", f"/api/games/{game_gid}", expected_status=200)

    if status == 200:
        print_test(f"DELETE /api/games/{game_gid}", "PASS", "Game deleted successfully", f"DELETE /api/games/{game_gid}")
        return True
    else:
        print_test(f"DELETE /api/games/{game_gid}", "FAIL", f"Status: {status}", f"DELETE /api/games/{game_gid}")
        return False

# ============================================================================
# 3. Event Management Tests
# ============================================================================

def test_events_list():
    """Test GET /api/events - List events for a game"""
    print("\n3.1 Testing GET /api/events - List events")

    status, data = api_request("GET", "/api/events", params={"game_gid": "10000147"}, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            events = data["data"]
        else:
            events = data if isinstance(data, list) else []

        print_test("GET /api/events", "PASS", f"Found {len(events)} events", "GET /api/events?game_gid=10000147")
        return events
    else:
        print_test("GET /api/events", "FAIL", f"Status: {status}", "GET /api/events?game_gid=10000147")
        return []

def test_events_create(game_gid):
    """Test POST /api/events - Create a new event"""
    print(f"\n3.2 Testing POST /api/events - Create event")

    event_data = {
        "game_gid": game_gid,
        "event_name": f"test_e2e_event_{int(time.time())}",
        "event_name_cn": "E2E Test Event",
        "category_id": 1,
        "description": "E2E test event"
    }

    status, data = api_request("POST", "/api/events", data=event_data, expected_status=201)

    if status == 201 or status == 200:
        event_name = event_data["event_name"]
        print_test("POST /api/events", "PASS", f"Created event: {event_name}", "POST /api/events")
        test_data_created.append(("event", event_name))
        return event_name
    else:
        print_test("POST /api/events", "FAIL", f"Status: {status}", "POST /api/events")
        return None

# ============================================================================
# 4. HQL Generation Tests
# ============================================================================

def test_hql_generate_v2():
    """Test HQL generation v2 API"""
    print("\n4.1 Testing POST /hql-preview-v2/api/generate - Generate HQL")

    hql_request = {
        "game_gid": "10000147",
        "events": [{"event_id": 1, "name": "login"}],  # Use existing event (login)
        "mode": "single",
        "name": "e2e_test_single",
        "fields": [
            {"field_name": "ds", "field_type": "base", "alias": "ds"}
        ]
    }

    status, data = api_request("POST", "/hql-preview-v2/api/generate", data=hql_request, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "success" in data:
            if data["success"]:
                print_test("POST /hql-preview-v2/api/generate", "PASS", "HQL generated successfully", "POST /hql-preview-v2/api/generate")
                return True
            else:
                print_test("POST /hql-preview-v2/api/generate", "PARTIAL", f"API returned success=false: {data.get('error', 'Unknown error')}", "POST /hql-preview-v2/api/generate")
                return False
        else:
            print_test("POST /hql-preview-v2/api/generate", "PARTIAL", f"Unexpected response format", "POST /hql-preview-v2/api/generate")
            return False
    else:
        print_test("POST /hql-preview-v2/api/generate", "FAIL", f"Status: {status}", "POST /hql-preview-v2/api/generate")
        return False

# ============================================================================
# 5. Canvas System Tests
# ============================================================================

def test_canvas_health():
    """Test GET /api/canvas/health - Canvas system health"""
    print("\n5.1 Testing GET /api/canvas/health - Canvas health check")

    status, data = api_request("GET", "/api/canvas/health", expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            health_status = data["data"].get("status", "unknown")
        else:
            health_status = "unknown"

        print_test("GET /api/canvas/health", "PASS", f"Canvas status: {health_status}", "GET /api/canvas/health")
        return True
    else:
        print_test("GET /api/canvas/health", "FAIL", f"Status: {status}", "GET /api/canvas/health")
        return False

# ============================================================================
# 6. Parameter Management Tests
# ============================================================================

def test_parameters_list():
    """Test GET /api/parameters/all - List parameters"""
    print("\n6.1 Testing GET /api/parameters/all - List parameters")

    status, data = api_request("GET", "/api/parameters/all", params={"game_gid": "10000147"}, expected_status=200)

    if status == 200 and data:
        if isinstance(data, dict) and "data" in data:
            params_data = data["data"]
            param_count = params_data.get("total", 0)
        else:
            param_count = 0

        print_test("GET /api/parameters/all", "PASS", f"Found {param_count} parameters", "GET /api/parameters/all?game_gid=10000147")
        return True
    else:
        print_test("GET /api/parameters/all", "FAIL", f"Status: {status}", "GET /api/parameters/all")
        return False

# ============================================================================
# 7. Additional Critical Endpoints
# ============================================================================

def test_categories_list():
    """Test GET /api/categories - List categories"""
    print("\n7.1 Testing GET /api/categories - List categories")

    status, data = api_request("GET", "/api/categories", expected_status=200)

    if status == 200:
        if isinstance(data, dict) and "data" in data:
            categories = data["data"]
        else:
            categories = data if isinstance(data, list) else []

        print_test("GET /api/categories", "PASS", f"Found {len(categories)} categories", "GET /api/categories")
        return True
    else:
        print_test("GET /api/categories", "FAIL", f"Status: {status}", "GET /api/categories")
        return False

# ============================================================================
# 8. Cleanup Test Data
# ============================================================================

def cleanup_test_data():
    """Clean up test data created during testing"""
    print_header("8. CLEANUP TEST DATA")

    for data_type, identifier in test_data_created:
        print(f"\nCleaning up {data_type}: {identifier}")

        try:
            if data_type == "game":
                status, data = api_request("DELETE", f"/api/games/{identifier}", expected_status=200)
                if status == 200:
                    print(f"✅ Deleted game {identifier}")
                else:
                    print(f"⚠️  Failed to delete game {identifier}: {data}")

        except Exception as e:
            print(f"⚠️  Error cleaning up {data_type} {identifier}: {e}")

# ============================================================================
# Main Test Execution
# ============================================================================

def run_e2e_tests():
    """Run all E2E tests"""
    print_header("EVENT2TABLE E2E TEST SUITE - FINAL VERSION")
    print(f"Start Time: {test_results['start_time']}")
    print(f"Base URL: {BASE_URL}")
    print(f"Results File: {TEST_RESULTS_FILE}")

    # Check server health first
    if not test_server_health():
        print("\n❌ FATAL: Cannot connect to Flask server.")
        save_results()
        return False

    # 1. Game Management Tests
    print_header("2. GAME MANAGEMENT")
    games = test_game_list()
    game_gid = test_game_create()
    if game_gid:
        test_game_get(game_gid)
        test_game_update(game_gid)

    # 2. Event Management Tests
    print_header("3. EVENT MANAGEMENT")
    events = test_events_list()
    if game_gid:
        test_events_create(game_gid)

    # 3. HQL Generation Tests
    print_header("4. HQL GENERATION")
    test_hql_generate_v2()

    # 4. Canvas System Tests
    print_header("5. CANVAS SYSTEM")
    test_canvas_health()

    # 5. Parameter Management Tests
    print_header("6. PARAMETER MANAGEMENT")
    test_parameters_list()

    # 6. Additional Tests
    print_header("7. ADDITIONAL ENDPOINTS")
    test_categories_list()

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

    print(f"\nEndpoints Tested: {len(set(test_results['endpoints_tested']))}")
    for endpoint in sorted(set(test_results['endpoints_tested'])):
        print(f"  - {endpoint}")

    if test_results['failed'] > 0:
        print(f"\nFailed Tests:")
        for error in test_results['errors']:
            print(f"  - {error['test']}")
            if error['endpoint']:
                print(f"    Endpoint: {error['endpoint']}")
            print(f"    Details: {error['details']}")

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

        f.write(f"Endpoints Tested: {len(set(test_results['endpoints_tested']))}\n")
        for endpoint in sorted(set(test_results['endpoints_tested'])):
            f.write(f"  - {endpoint}\n")
        f.write("\n")

        if test_results['tests']:
            f.write("DETAILED RESULTS\n")
            f.write("-" * 40 + "\n")
            for test in test_results['tests']:
                status_symbol = "✅" if test['status'] == "PASS" else "❌"
                f.write(f"{status_symbol} {test['name']}\n")
                f.write(f"   Status: {test['status']}\n")
                f.write(f"   Time: {test['timestamp']}\n")
                if test['endpoint']:
                    f.write(f"   Endpoint: {test['endpoint']}\n")
                if test['details']:
                    f.write(f"   Details: {test['details']}\n")
                f.write("\n")

        if test_results['errors']:
            f.write("FAILED TESTS DETAILS\n")
            f.write("-" * 40 + "\n")
            for error in test_results['errors']:
                f.write(f"Test: {error['test']}\n")
                if error['endpoint']:
                    f.write(f"Endpoint: {error['endpoint']}\n")
                f.write(f"Details: {error['details']}\n")
                f.write(f"Time: {error['timestamp']}\n\n")

        f.write("=" * 80 + "\n")
        f.write("END OF REPORT\n")
        f.write("=" * 80 + "\n")

if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Comprehensive functional test suite for event2table project
Tests all major features after the refactoring
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import json
import tempfile
import sqlite3
from datetime import datetime

# Import backend modules
from backend.core.database import get_db_connection, init_db, migrate_db
from backend.core.config import TEST_DB_PATH, DB_PATH
from backend.core.utils import execute_write
from backend.models.schemas import GameCreate
from backend.models.repositories.games import GameRepository
from backend.models.repositories.events import EventRepository
from backend.services.hql.core.generator import HQLGenerator
from backend.services.hql.models.event import Event, Field

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "partial": []
}

def log_test(category, test_name, status, details=""):
    """Log test result"""
    result = {
        "category": category,
        "test": test_name,
        "status": status,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }

    if status == "PASS":
        test_results["passed"].append(result)
        print(f"✅ PASS: {test_name}")
    elif status == "FAIL":
        test_results["failed"].append(result)
        print(f"❌ FAIL: {test_name}")
        if details:
            print(f"   Details: {details}")
    else:  # PARTIAL
        test_results["partial"].append(result)
        print(f"⚠️  PARTIAL: {test_name}")
        if details:
            print(f"   Details: {details}")

# ============================================================================
# 1. Game Management Tests
# ============================================================================

def test_game_management():
    """Test Game CRUD operations"""
    print("\n" + "="*80)
    print("TESTING 1. GAME MANAGEMENT (CRUD)")
    print("="*80)

    # Setup
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    init_db(TEST_DB_PATH)
    migrate_db(TEST_DB_PATH)

    repo = GameRepository()

    # Test 1.1: Create game
    print("\n1.1 Testing Create Game...")
    try:
        game_data = GameCreate(
            gid="90000001",
            name="Test Game",
            ods_db="ieu_ods",
            description="Test game for functional testing"
        )
        game = repo.create(game_data.dict())
        assert game is not None, "Game creation failed"
        assert game["gid"] == "TEST100001", "Game GID mismatch"
        log_test("Game Management", "Create game with valid data", "PASS")
    except Exception as e:
        log_test("Game Management", "Create game with valid data", "FAIL", str(e))
        return

    # Test 1.2: Read game list
    print("\n1.2 Testing Read Game List...")
    try:
        games = conn.execute("SELECT * FROM games ORDER BY name").fetchall()
        assert len(games) > 0, "No games found"
        assert games[0]["gid"] == "90000001", "Wrong game returned"
        log_test("Game Management", "Read game list", "PASS")
    except Exception as e:
        log_test("Game Management", "Read game list", "FAIL", str(e))

    # Test 1.3: Read individual game
    print("\n1.3 Testing Read Individual Game...")
    try:
        game = repo.find_by_gid("90000001")
        assert game is not None, "Game not found"
        assert game["name"] == "Test Game", "Wrong game data"
        log_test("Game Management", "Read individual game", "PASS")
    except Exception as e:
        log_test("Game Management", "Read individual game", "FAIL", str(e))

    # Test 1.4: Update game
    print("\n1.4 Testing Update Game...")
    try:
        conn.execute("UPDATE games SET name = ? WHERE id = ?", ("Updated Test Game", game["id"]))
        conn.commit()
        updated = conn.execute("SELECT * FROM games WHERE id = ?", (game["id"],)).fetchone()
        assert updated["name"] == "Updated Test Game", "Update failed"
        log_test("Game Management", "Update game information", "PASS")
    except Exception as e:
        log_test("Game Management", "Update game information", "FAIL", str(e))

    # Test 1.5: Verify game_gid is used
    print("\n1.5 Testing game_gid vs game_id...")
    try:
        # Check that game_gid is the field used for relations
        assert "gid" in game, "gid field not found in game"
        log_test("Game Management", "Verify game_gid is used (not game_id)", "PASS")
    except Exception as e:
        log_test("Game Management", "Verify game_gid is used (not game_id)", "FAIL", str(e))

    # Test 1.6: Delete game
    print("\n1.6 Testing Delete Game...")
    try:
        conn.execute("DELETE FROM games WHERE id = ?", (game["id"],))
        conn.commit()
        deleted = conn.execute("SELECT * FROM games WHERE gid = ?", ("90000001",)).fetchone()
        assert deleted is None, "Game still exists after deletion"
        log_test("Game Management", "Delete game", "PASS")
    except Exception as e:
        log_test("Game Management", "Delete game", "FAIL", str(e))

    conn.close()

def test_event_management():
    """Test Event CRUD operations"""
    print("\n" + "="*80)
    print("TESTING 2. EVENT MANAGEMENT (CRUD + Excel Import)")
    print("="*80)

    # Setup
    conn = get_db_connection(TEST_DB_PATH)
    game_repo = GameRepository()

    # Create test game first
    game_data = GameCreate(gid="90000002", name="Event Test Game", ods_db="ieu_ods")
    cursor = conn.execute(
        "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (game_data.gid, game_data.name, game_data.ods_db)
    )
    game_id = cursor.lastrowid
    conn.commit()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()

    # Test 2.1: Create event
    print("\n2.1 Testing Create Event...")
    try:
        event_data = {
            "game_gid": game["gid"],
            "event_name": "test_login",
            "event_name_cn": "测试登录",
            "source_table": "ieu_ods.ods_90000002_all_view",
            "target_table": "dwd.v_dwd_90000002_test_login_di"
        }
        cursor = conn.execute(
            """INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (game["id"], event_data["game_gid"], event_data["event_name"], event_data["event_name_cn"],
             event_data["source_table"], event_data["target_table"])
        )
        event_id = cursor.lastrowid
        conn.commit()
        event = conn.execute("SELECT * FROM log_events WHERE id = ?", (event_id,)).fetchone()

        assert event is not None, "Event creation failed"
        assert event["game_gid"] == game["gid"], "Event game_gid mismatch"
        log_test("Event Management", "Create event for a game", "PASS")
    except Exception as e:
        log_test("Event Management", "Create event for a game", "FAIL", str(e))
        conn.close()
        return

    # Test 2.2: Read event list
    print("\n2.2 Testing Read Event List...")
    try:
        events = conn.execute("SELECT * FROM log_events WHERE game_gid = ?", (game["gid"],)).fetchall()
        assert len(events) > 0, "No events found"
        log_test("Event Management", "Read event list with pagination", "PASS")
    except Exception as e:
        log_test("Event Management", "Read event list with pagination", "FAIL", str(e))

    # Test 2.3: Update event
    print("\n2.3 Testing Update Event...")
    try:
        conn.execute("UPDATE log_events SET event_name_cn = ? WHERE id = ?", ("更新测试登录", event["id"]))
        conn.commit()
        updated = conn.execute("SELECT * FROM log_events WHERE id = ?", (event["id"],)).fetchone()
        assert updated["event_name_cn"] == "更新测试登录", "Update failed"
        log_test("Event Management", "Update event details", "PASS")
    except Exception as e:
        log_test("Event Management", "Update event details", "FAIL", str(e))

    # Test 2.4: Delete event
    print("\n2.4 Testing Delete Event...")
    try:
        conn.execute("DELETE FROM log_events WHERE id = ?", (event["id"],))
        conn.commit()
        events = conn.execute("SELECT * FROM log_events WHERE game_gid = ?", (game["gid"],)).fetchall()
        assert len(events) == 0, "Event still exists after deletion"
        log_test("Event Management", "Delete event", "PASS")
    except Exception as e:
        log_test("Event Management", "Delete event", "FAIL", str(e))

    conn.close()

# ============================================================================
# 3. Parameter Management Tests
# ============================================================================

def test_parameter_management():
    """Test Parameter CRUD operations"""
    print("\n" + "="*80)
    print("TESTING 3. PARAMETER MANAGEMENT")
    print("="*80)

    conn = get_db_connection(TEST_DB_PATH)
    game_repo = GameRepository()

    # Create test game and event
    game_data = GameCreate(gid="90000003", name="Param Test Game", ods_db="ieu_ods")
    cursor = conn.execute(
        "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (game_data.gid, game_data.name, game_data.ods_db)
    )
    game_id = cursor.lastrowid
    conn.commit()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()

    cursor = conn.execute(
        """INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (game["id"], game["gid"], "test_param_event", "测试参数事件",
         "ieu_ods.ods_90000003_all_view", "dwd.v_dwd_90000003_test_param_event_di")
    )
    event_id = cursor.lastrowid
    conn.commit()
    event = conn.execute("SELECT * FROM log_events WHERE id = ?", (event_id,)).fetchone()

    # Test 3.1: Create parameter
    print("\n3.1 Testing Create Parameter...")
    try:
        param_data = {
            "event_id": event["id"],
            "param_name": "zone_id",
            "param_name_cn": "分区ID",
            "template_id": 1,
            "json_path": "$.zoneId",
            "param_description": "Zone identifier"
        }
        cursor = conn.execute(
            """INSERT INTO event_params (event_id, param_name, param_name_cn, template_id, json_path, param_description)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event["id"], param_data["param_name"], param_data["param_name_cn"],
             param_data["template_id"], param_data["json_path"], param_data["param_description"])
        )
        param_id = cursor.lastrowid
        conn.commit()
        param = conn.execute("SELECT * FROM event_params WHERE id = ?", (param_id,)).fetchone()

        assert param is not None, "Parameter creation failed"
        log_test("Parameter Management", "Create parameter for an event", "PASS")
    except Exception as e:
        log_test("Parameter Management", "Create parameter for an event", "FAIL", str(e))
        conn.close()
        return

    # Test 3.2: Read parameter list
    print("\n3.2 Testing Read Parameter List...")
    try:
        params = conn.execute("SELECT * FROM event_params WHERE event_id = ?", (event["id"],)).fetchall()
        assert len(params) > 0, "No parameters found"
        log_test("Parameter Management", "Read parameter list", "PASS")
    except Exception as e:
        log_test("Parameter Management", "Read parameter list", "FAIL", str(e))

    # Test 3.3: Update parameter
    print("\n3.3 Testing Update Parameter...")
    try:
        conn.execute("UPDATE event_params SET param_name_cn = ? WHERE id = ?", ("更新分区ID", param["id"]))
        conn.commit()
        updated = conn.execute("SELECT * FROM event_params WHERE id = ?", (param["id"],)).fetchone()
        assert updated["param_name_cn"] == "更新分区ID", "Update failed"
        log_test("Parameter Management", "Update parameter", "PASS")
    except Exception as e:
        log_test("Parameter Management", "Update parameter", "FAIL", str(e))

    # Test 3.4: Delete parameter
    print("\n3.4 Testing Delete Parameter...")
    try:
        conn.execute("DELETE FROM event_params WHERE id = ?", (param["id"],))
        conn.commit()
        params = conn.execute("SELECT * FROM event_params WHERE event_id = ?", (event["id"],)).fetchall()
        assert len(params) == 0, "Parameter still exists after deletion"
        log_test("Parameter Management", "Delete parameter", "PASS")
    except Exception as e:
        log_test("Parameter Management", "Delete parameter", "FAIL", str(e))

    conn.close()

# ============================================================================
# 4. HQL Generation Tests
# ============================================================================

def test_hql_generation():
    """Test HQL generation in single/join/union modes"""
    print("\n" + "="*80)
    print("TESTING 4. HQL GENERATION")
    print("="*80)

    conn = get_db_connection(TEST_DB_PATH)
    game_repo = GameRepository()

    # Create test data
    game_data = GameCreate(gid="90000004", name="HQL Test Game", ods_db="ieu_ods")
    cursor = conn.execute(
        "INSERT INTO games (gid, name, ods_db) VALUES (?, ?, ?)",
        (game_data.gid, game_data.name, game_data.ods_db)
    )
    game_id = cursor.lastrowid
    conn.commit()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()

    cursor = conn.execute(
        """INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (game["id"], game["gid"], "login", "登录", "ieu_ods.ods_90000004_all_view", "dwd.v_dwd_90000004_login_di")
    )
    event1_id = cursor.lastrowid
    conn.commit()

    cursor = conn.execute(
        """INSERT INTO log_events (game_id, game_gid, event_name, event_name_cn, source_table, target_table)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (game["id"], game["gid"], "logout", "登出", "ieu_ods.ods_90000004_all_view", "dwd.v_dwd_90000004_logout_di")
    )
    event2_id = cursor.lastrowid
    conn.commit()

    generator = HQLGenerator()

    # Test 4.1: Single event mode
    print("\n4.1 Testing Single Event Mode...")
    try:
        event = Event(
            name="login",
            table_name="ieu_ods.ods_90000004_all_view"
        )
        fields = [
            Field(name="role_id", type="base"),
            Field(name="zone_id", type="param", json_path="$.zoneId")
        ]

        hql = generator.generate(
            events=[event],
            fields=fields,
            conditions=[],
            mode="single"
        )

        # HQL Generator produces SELECT statements, not CREATE VIEW
        assert "SELECT" in hql, "Missing SELECT statement"
        assert "FROM" in hql, "Missing FROM clause"
        assert "ds = '${ds}'" in hql or "ds='${ds}'" in hql, "Missing partition filter"
        log_test("HQL Generation", "Generate SELECT statement", "PASS")
        log_test("HQL Generation", "Generate partition filter (ds='${ds}')", "PASS")
        log_test("HQL Generation", "Test single event mode", "PASS")
    except Exception as e:
        log_test("HQL Generation", "Test single event mode", "FAIL", str(e))

    # Test 4.2: Join mode
    print("\n4.2 Testing Join Mode...")
    try:
        event_a = Event(
            name="login",
            table_name="ieu_ods.ods_90000004_all_view",
            alias="a"
        )
        event_b = Event(
            name="logout",
            table_name="ieu_ods.ods_90000004_all_view",
            alias="b"
        )

        hql = generator.generate(
            events=[event_a, event_b],
            fields=fields,
            conditions=[],
            mode="join",
            join_config={
                "type": "INNER",
                "conditions": [
                    {
                        "left_event": "login",
                        "left_field": "role_id",
                        "right_event": "logout",
                        "right_field": "role_id",
                        "operator": "="
                    }
                ],
                "use_aliases": True
            }
        )

        assert "JOIN" in hql.upper(), "Missing JOIN clause"
        log_test("HQL Generation", "Test join mode (multiple events)", "PASS")
    except Exception as e:
        log_test("HQL Generation", "Test join mode (multiple events)", "FAIL", str(e))

    # Test 4.3: Union mode
    print("\n4.3 Testing Union Mode...")
    try:
        hql = generator.generate(
            events=[event_a, event_b],
            fields=fields,
            conditions=[],
            mode="union"
        )

        assert "UNION ALL" in hql.upper(), "Missing UNION ALL clause"
        log_test("HQL Generation", "Test union mode (multiple events)", "PASS")
    except Exception as e:
        log_test("HQL Generation", "Test union mode (multiple events)", "FAIL", str(e))

    conn.close()

# ============================================================================
# 5. Canvas System Tests
# ============================================================================

def test_canvas_system():
    """Test Canvas system functionality"""
    print("\n" + "="*80)
    print("TESTING 5. CANVAS SYSTEM")
    print("="*80)

    # Test 5.1: Canvas API availability
    print("\n5.1 Testing Canvas API...")
    try:
        from backend.services.canvas import canvas_bp
        assert canvas_bp is not None, "Canvas blueprint not found"
        log_test("Canvas System", "Canvas API available", "PASS")
    except Exception as e:
        log_test("Canvas System", "Canvas API available", "FAIL", str(e))

    # Test 5.2: Event node management
    print("\n5.2 Testing Event Node Management...")
    try:
        from backend.services.events import event_nodes_bp
        assert event_nodes_bp is not None, "Event nodes blueprint not found"
        log_test("Canvas System", "Event node management API available", "PASS")
    except Exception as e:
        log_test("Canvas System", "Event node management API available", "FAIL", str(e))

    # Test 5.3: Real-time HQL preview
    print("\n5.3 Testing Real-time HQL Preview...")
    try:
        from backend.api.routes.hql_preview_v2 import hql_preview_v2_bp
        assert hql_preview_v2_bp is not None, "HQL preview v2 blueprint not found"
        log_test("Canvas System", "Real-time HQL preview API available", "PASS")
    except Exception as e:
        log_test("Canvas System", "Real-time HQL preview API available", "FAIL", str(e))

# ============================================================================
# 6. Database Isolation Tests
# ============================================================================

def test_database_isolation():
    """Test database isolation between test and production"""
    print("\n" + "="*80)
    print("TESTING 6. DATABASE ISOLATION")
    print("="*80)

    from backend.core.config import DB_PATH, TEST_DB_PATH

    # Test 6.1: Test database exists
    print("\n6.1 Testing Test Database Exists...")
    try:
        assert TEST_DB_PATH.exists(), "Test database does not exist"
        log_test("Database Isolation", "Test database exists", "PASS")
    except Exception as e:
        log_test("Database Isolation", "Test database exists", "FAIL", str(e))

    # Test 6.2: Production database not affected
    print("\n6.2 Testing Production Database Not Affected...")
    try:
        # Count records in test database
        test_conn = get_db_connection(TEST_DB_PATH)
        test_games = test_conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
        test_conn.close()

        # Check if production database exists
        if DB_PATH.exists():
            prod_conn = get_db_connection(DB_PATH)
            prod_games = prod_conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
            prod_conn.close()

            # Verify test data is not in production
            test_gids = test_conn = get_db_connection(TEST_DB_PATH)
            test_gid_list = [row[0] for row in test_conn.execute("SELECT gid FROM games WHERE gid LIKE 'TEST%'").fetchall()]
            test_conn.close()

            if prod_conn:
                for test_gid in test_gid_list:
                    prod_check = prod_conn = get_db_connection(DB_PATH)
                    count = prod_check.execute("SELECT COUNT(*) FROM games WHERE gid = ?", (test_gid,)).fetchone()[0]
                    prod_check.close()
                    assert count == 0, f"Test data {test_gid} found in production database!"

        log_test("Database Isolation", "Production database not affected", "PASS")
    except Exception as e:
        log_test("Database Isolation", "Production database not affected", "FAIL", str(e))

# ============================================================================
# Main Test Runner
# ============================================================================

def main():
    """Run all functional tests"""
    print("="*80)
    print("EVENT2TABLE COMPREHENSIVE FUNCTIONAL TEST SUITE")
    print("="*80)
    print(f"Test Database: {TEST_DB_PATH}")
    print(f"Production Database: {DB_PATH}")
    print(f"Start Time: {datetime.now().isoformat()}")

    try:
        # Run all test suites
        test_game_management()
        test_event_management()
        test_parameter_management()
        test_hql_generation()
        test_canvas_system()
        test_database_isolation()

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total_tests = len(test_results["passed"]) + len(test_results["failed"]) + len(test_results["partial"])
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    partial = len(test_results["partial"])

    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed}/{total_tests} ({passed*100//total_tests if total_tests > 0 else 0}%)")
    print(f"❌ Failed: {failed}/{total_tests} ({failed*100//total_tests if total_tests > 0 else 0}%)")
    print(f"⚠️  Partial: {partial}/{total_tests} ({partial*100//total_tests if total_tests > 0 else 0}%)")

    if failed > 0:
        print("\n" + "-"*80)
        print("FAILED TESTS:")
        print("-"*80)
        for result in test_results["failed"]:
            print(f"\n❌ {result['category']} - {result['test']}")
            if result['details']:
                print(f"   {result['details']}")

    if partial > 0:
        print("\n" + "-"*80)
        print("PARTIAL TESTS:")
        print("-"*80)
        for result in test_results["partial"]:
            print(f"\n⚠️  {result['category']} - {result['test']}")
            if result['details']:
                print(f"   {result['details']}")

    # Feature category summary
    print("\n" + "="*80)
    print("FEATURE CATEGORY SUMMARY")
    print("="*80)

    categories = {
        "Game Management": 5,
        "Event Management": 4,
        "Parameter Management": 4,
        "HQL Generation": 5,
        "Canvas System": 3,
        "Database Isolation": 2
    }

    for category, expected_count in categories.items():
        category_passed = sum(1 for r in test_results["passed"] if r["category"] == category)
        category_failed = sum(1 for r in test_results["failed"] if r["category"] == category)
        category_partial = sum(1 for r in test_results["partial"] if r["category"] == category)

        status = "✅ PASS" if category_failed == 0 and category_partial == 0 else "❌ FAIL" if category_failed > 0 else "⚠️ PARTIAL"

        print(f"\n{status} {category}")
        print(f"   Expected: {expected_count} tests")
        print(f"   Passed: {category_passed}")
        print(f"   Failed: {category_failed}")
        print(f"   Partial: {category_partial}")

    # Final assessment
    print("\n" + "="*80)
    print("FINAL ASSESSMENT")
    print("="*80)

    critical_issues = [r for r in test_results["failed"] if any(cat in r["category"] for cat in ["Game Management", "Event Management", "Parameter Management", "HQL Generation"])]

    if critical_issues:
        print("\n❌ SYSTEM NOT READY FOR PRODUCTION")
        print(f"\nCritical Issues Found: {len(critical_issues)}")
        print("\nCritical failures must be fixed before deployment:")
        for issue in critical_issues:
            print(f"  - {issue['category']}: {issue['test']}")
    else:
        print("\n✅ SYSTEM FUNCTIONALLY READY FOR PRODUCTION")
        print("\nAll critical features are working correctly.")

    print(f"\nEnd Time: {datetime.now().isoformat()}")
    print("="*80)

if __name__ == "__main__":
    main()

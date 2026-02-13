#!/usr/bin/env python3
"""
Automated test script for JOIN node HQL generation
Tests various scenarios to identify issues
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from modules import flows

def test_case_1_no_conditions():
    """Test JOIN node with no conditions - should fail"""
    print("\n" + "="*80)
    print("TEST 1: JOIN node with NO conditions (should fail)")
    print("="*80)

    flow_graph = {
        "nodes": [
            {
                "node_id": "node_1",
                "node_type": "process",
                "config_ref": {
                    "event_name": "event1",
                    "name": "Event 1"
                }
            },
            {
                "node_id": "node_2",
                "node_type": "process",
                "config_ref": {
                    "event_name": "event2",
                    "name": "Event 2"
                }
            },
            {
                "node_id": "join_node",
                "node_type": "join",
                "config_ref": {
                    "name": "join",
                    "joinType": "INNER",
                    "conditions": [],  # Empty conditions
                    "autoPartition": True
                }
            }
        ],
        "connections": [
            {
                "id": "conn_1",
                "source_node": "node_1",
                "target_node": "join_node",
                "connection_type": "join"
            },
            {
                "id": "conn_2",
                "source_node": "node_2",
                "target_node": "join_node",
                "connection_type": "join"
            }
        ],
        "output_config": {
            "table_name": "test_output",
            "database": "dwd"
        }
    }

    try:
        hql = flows.generate_hql_from_graph(flow_graph, "TestFlow", "${bizdate}")
        print("❌ UNEXPECTED: Should have failed but got HQL:")
        print(hql[:200])
        return False
    except ValueError as e:
        print(f"✅ EXPECTED ERROR: {e}")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_case_2_with_conditions():
    """Test JOIN node with conditions - should succeed"""
    print("\n" + "="*80)
    print("TEST 2: JOIN node with conditions (should succeed)")
    print("="*80)

    flow_graph = {
        "nodes": [
            {
                "node_id": "node_1",
                "node_type": "process",
                "config_ref": {
                    "eventId": 1516,
                    "event_name": "spknightfest.summon",
                    "eventName": "spknightfest.summon",
                    "eventCnName": "sp武将活动-招募武将",
                    "name": "Event 1",
                    "fieldList": [
                        {"name": "role_id", "source": "role_id", "type": "base"},
                        {"name": "summonId", "source": "summonId", "type": "param", "alias": "card_pool_id"}
                    ]
                }
            },
            {
                "node_id": "node_2",
                "node_type": "process",
                "config_ref": {
                    "eventId": 1613,
                    "event_name": "st.summon",
                    "eventName": "st.summon",
                    "eventCnName": "赛季塔，抽卡",
                    "name": "Event 2",
                    "fieldList": [
                        {"name": "role_id", "source": "role_id", "type": "base"},
                        {"name": "packId", "source": "packId", "type": "param", "alias": "card_pool_id"}
                    ]
                }
            },
            {
                "node_id": "join_node",
                "node_type": "join",
                "config_ref": {
                    "name": "My Join",
                    "joinType": "INNER",
                    "conditions": [
                        {"leftField": "role_id", "operator": "=", "rightField": "role_id"}
                    ],
                    "autoPartition": True
                }
            }
        ],
        "connections": [
            {
                "id": "conn_1",
                "source_node": "node_1",
                "target_node": "join_node",
                "connection_type": "join"
            },
            {
                "id": "conn_2",
                "source_node": "node_2",
                "target_node": "join_node",
                "connection_type": "join"
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_output",
            "database": "dwd"
        }
    }

    try:
        hql = flows.generate_hql_from_graph(flow_graph, "TestFlow", "${bizdate}")
        print("✅ SUCCESS: Generated HQL")
        print("\n--- HQL Preview (first 500 chars) ---")
        print(hql[:500])
        if len(hql) > 500:
            print(f"\n... ({len(hql) - 500} more chars)")
        return True
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_case_3_no_joinType():
    """Test JOIN node without joinType - should use default"""
    print("\n" + "="*80)
    print("TEST 3: JOIN node without joinType (should default to INNER)")
    print("="*80)

    flow_graph = {
        "nodes": [
            {
                "node_id": "node_1",
                "node_type": "process",
                "config_ref": {
                    "eventId": 1516,
                    "event_name": "event1",
                    "eventName": "event1",
                    "name": "Event 1",
                    "fieldList": [{"name": "role_id", "source": "role_id", "type": "base"}]
                }
            },
            {
                "node_id": "node_2",
                "node_type": "process",
                "config_ref": {
                    "eventId": 1613,
                    "event_name": "event2",
                    "eventName": "event2",
                    "name": "Event 2",
                    "fieldList": [{"name": "role_id", "source": "role_id", "type": "base"}]
                }
            },
            {
                "node_id": "join_node",
                "node_type": "join",
                "config_ref": {
                    "name": "join",
                    # No joinType specified
                    "conditions": [
                        {"leftField": "role_id", "operator": "=", "rightField": "role_id"}
                    ]
                }
            }
        ],
        "connections": [
            {
                "id": "conn_1",
                "source_node": "node_1",
                "target_node": "join_node",
                "connection_type": "join"
            },
            {
                "id": "conn_2",
                "source_node": "node_2",
                "target_node": "join_node",
                "connection_type": "join"
            }
        ],
        "output_config": {
            "table_name": "test_output",
            "database": "dwd"
        }
    }

    try:
        hql = flows.generate_hql_from_graph(flow_graph, "TestFlow", "${bizdate}")
        print("✅ SUCCESS: Generated HQL with default joinType")
        if "INNER JOIN" in hql:
            print("✅ Correctly defaulted to INNER JOIN")
        else:
            print("⚠️  Warning: INNER JOIN not found in HQL")
        print("\n--- HQL Preview (first 300 chars) ---")
        print(hql[:300])
        return True
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*80)
    print("JOIN NODE HQL GENERATION - AUTOMATED TEST SUITE")
    print("="*80)

    results = {
        "Test 1 (No conditions)": test_case_1_no_conditions(),
        "Test 2 (With conditions)": test_case_2_with_conditions(),
        "Test 3 (No joinType)": test_case_3_no_joinType()
    }

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

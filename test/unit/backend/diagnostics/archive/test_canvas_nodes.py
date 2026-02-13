#!/usr/bin/env python3
"""
Test UNION ALL generation using REAL canvas node configuration format
This simulates exactly what the canvas sends to the backend
"""
import sys
import os
import json

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.flows import generate_hql_from_graph

def test_canvas_empty_fieldlist_nodes():
    """
    测试场景：用户在canvas中创建了3个事件节点，但没有添加任何字段
    这是用户报告的实际问题场景
    """
    print("=" * 60)
    print("测试1: Canvas空字段节点")
    print("=" * 60)
    print("\n场景：用户在canvas创建3个事件节点，点击保存时未添加字段")
    print("这是用户报告问题的实际场景")

    # 这是canvas实际发送的flow_graph格式
    canvas_flow_graph = {
        "nodes": [
            {
                "node_id": "node_1768824784037_1",
                "node_type": "process",
                "position": {"x": 100, "y": 100},
                "config_ref": {  # 这是canvas实际保存的节点配置
                    "eventId": 1,
                    "eventName": "game.role.knightsoulsummon",
                    "eventCnName": "将魂抽卡",
                    "fieldList": []  # 空fieldList - 用户没添加字段
                }
            },
            {
                "node_id": "node_1768824784037_2",
                "node_type": "process",
                "position": {"x": 100, "y": 300},
                "config_ref": {
                    "eventId": 2,
                    "eventName": "role.create",
                    "eventCnName": "创角",
                    "fieldList": []
                }
            },
            {
                "node_id": "node_1768824784037_3",
                "node_type": "process",
                "position": {"x": 100, "y": 500},
                "config_ref": {
                    "eventId": 3,
                    "eventName": "role.firstOnline",
                    "eventCnName": "首次登陆",
                    "fieldList": []
                }
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": "node_1768824784037_1",
                "target_node": "node_union",
                "connection_type": "union_all"
            },
            {
                "id": "conn2",
                "source_node": "node_1768824784037_2",
                "target_node": "node_union",
                "connection_type": "union_all"
            },
            {
                "id": "conn3",
                "source_node": "node_1768824784037_3",
                "target_node": "node_union",
                "connection_type": "union_all"
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_canvas",
            "database": "ieu_cdm"
        }
    }

    print("\n节点配置:")
    for node in canvas_flow_graph['nodes'][:3]:
        cfg = node['config_ref']
        print(f"  {node['node_id']}: eventId={cfg.get('eventId')}, "
              f"eventName={cfg.get('eventName')}, fieldList长度={len(cfg.get('fieldList', []))}")

    print("\n开始生成HQL...")
    print("-" * 60)

    try:
        # 使用canvas实际调用的API格式
        hql = generate_hql_from_graph(
            canvas_flow_graph,
            "Canvas Empty FieldList Test",
            "${ds}"
        )

        if hql.startswith("-- Error:"):
            print("❌ FAILED: 这是用户报告的错误!")
            for line in hql.split('\n')[:10]:
                print(f"  {line}")
            return False
        else:
            print("✅ SUCCESS: 成功生成HQL!")
            print(f"\n生成的HQL:")
            print("-" * 60)
            print(hql)
            print("-" * 60)

            # 验证CTE格式
            if "WITH" not in hql or "event1 AS" not in hql:
                print(f"\n❌ FAILED: 缺少CTE格式")
                return False

            # 验证包含默认字段
            required_fields = ['ds', 'role_id', 'account_id', 'utdid', 'tm', 'ts']
            all_present = all(f in hql for f in required_fields)

            # 验证WHERE条件
            if "WHERE ds = ${ds}" not in hql:
                print(f"\n❌ FAILED: 缺少分区过滤条件")
                return False

            if "AND event =" not in hql:
                print(f"\n❌ FAILED: 缺少事件过滤条件")
                return False

            if all_present:
                print(f"\n✅ VERIFIED: 包含所有默认基础字段")
                print(f"✅ VERIFIED: 使用CTE格式")
                print(f"✅ VERIFIED: WHERE条件包含分区和事件过滤")
                return True
            else:
                missing = [f for f in required_fields if f not in hql]
                print(f"\n⚠️  WARNING: 缺少字段 {missing}")
                return False

    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_canvas_partial_fieldlist_nodes():
    """
    测试场景：部分节点有字段，部分没有
    """
    print("\n" + "=" * 60)
    print("测试2: Canvas混合字段节点")
    print("=" * 60)
    print("\n场景：一个节点有自定义字段，另一个为空")

    canvas_flow_graph = {
        "nodes": [
            {
                "node_id": "node_1768824784037_1",
                "node_type": "process",
                "config_ref": {
                    "eventId": 1,
                    "eventName": "game.role.knightsoulsummon",
                    "eventCnName": "将魂抽卡",
                    "fieldList": []  # 空
                }
            },
            {
                "node_id": "node_1768824784037_2",
                "node_type": "process",
                "config_ref": {
                    "eventId": 2,
                    "eventName": "role.create",
                    "eventCnName": "创角",
                    "fieldList": [
                        {"id": "base_ds", "name": "ds", "type": "base", "source": "ds"},
                        {"id": "base_role", "name": "role_id", "type": "base", "source": "role_id"},
                        {"id": "param_zone", "type": "param", "source": "zoneId", "alias": "zone_id"}
                    ]
                }
            }
        ],
        "connections": [
            {"id": "conn1", "source_node": "node_1768824784037_1", "target_node": "node_union", "connection_type": "union_all"},
            {"id": "conn2", "source_node": "node_1768824784037_2", "target_node": "node_union", "connection_type": "union_all"}
        ],
        "output_config": {
            "table_name": "v_dwd_test_mixed_canvas",
            "database": "ieu_cdm"
        }
    }

    print("\n节点配置:")
    print("  node1: fieldList=[] (空)")
    print("  node2: fieldList=[ds, role_id, zone_id]")

    print("\n预期: 使用公共字段 (ds, role_id)")
    print("-" * 60)

    try:
        hql = generate_hql_from_graph(
            canvas_flow_graph,
            "Canvas Mixed FieldList Test",
            "${ds}"
        )

        if hql.startswith("-- Error:"):
            print("❌ FAILED")
            return False
        else:
            print("✅ SUCCESS")
            print("\n生成的HQL:")
            print("-" * 60)
            print(hql)
            print("-" * 60)

            # 验证CTE格式
            if "WITH" not in hql:
                print("\n❌ FAILED: 缺少CTE格式")
                return False

            # 验证只有公共字段
            if "ds" in hql and "role_id" in hql and "zone_id" not in hql.split("UNION ALL")[0]:
                print("\n✅ VERIFIED: 正确使用字段交集")
                print("✅ VERIFIED: 使用CTE格式")
                return True
            else:
                print("\n⚠️  WARNING: 字段交集可能有问题")
                return False

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_canvas_real_world_scenario():
    """
    测试真实场景：模拟用户在canvas中的完整操作流程
    """
    print("\n" + "=" * 60)
    print("测试3: Canvas真实场景模拟")
    print("=" * 60)
    print("\n完整流程模拟:")
    print("1. 用户创建3个事件节点")
    print("2. 用户添加UNION ALL节点并连接")
    print("3. 用户添加输出节点")
    print("4. 用户点击生成HQL（此时事件节点都没有配置字段）")

    # 获取真实事件
    from backend.core.utils import fetch_all_as_dict
    events = fetch_all_as_dict('''
        SELECT id, event_name, event_name_cn, game_id
        FROM log_events
        ORDER BY id
        LIMIT 3
    ''')

    if len(events) < 3:
        print("❌ 数据库事件不足3个")
        return False

    # 构建真实的canvas flow_graph
    canvas_flow_graph = {
        "nodes": [
            {
                "node_id": f"node_{events[0]['id']}",
                "node_type": "process",
                "position": {"x": 100, "y": 100},
                "config_ref": {
                    "eventId": events[0]['id'],
                    "eventName": events[0]['event_name'],
                    "eventCnName": events[0]['event_name_cn'],
                    "fieldList": []  # 用户未配置
                }
            },
            {
                "node_id": f"node_{events[1]['id']}",
                "node_type": "process",
                "position": {"x": 100, "y": 300},
                "config_ref": {
                    "eventId": events[1]['id'],
                    "eventName": events[1]['event_name'],
                    "eventCnName": events[1]['event_name_cn'],
                    "fieldList": []
                }
            },
            {
                "node_id": f"node_{events[2]['id']}",
                "node_type": "process",
                "position": {"x": 100, "y": 500},
                "config_ref": {
                    "eventId": events[2]['id'],
                    "eventName": events[2]['event_name'],
                    "eventCnName": events[2]['event_name_cn'],
                    "fieldList": []
                }
            }
        ],
        "connections": [
            {"id": "c1", "source_node": f"node_{events[0]['id']}", "target_node": "union", "connection_type": "union_all"},
            {"id": "c2", "source_node": f"node_{events[1]['id']}", "target_node": "union", "connection_type": "union_all"},
            {"id": "c3", "source_node": f"node_{events[2]['id']}", "target_node": "union", "connection_type": "union_all"}
        ],
        "output_config": {
            "table_name": "v_dwd_real_world_test",
            "database": "ieu_cdm"
        }
    }

    print(f"\n使用事件:")
    for e in events:
        print(f"  [{e['id']}] {e['event_name']} ({e['event_name_cn']})")

    print("\n所有节点的fieldList都为空")
    print("-" * 60)

    try:
        hql = generate_hql_from_graph(
            canvas_flow_graph,
            f"Real World Canvas Test - {events[0]['event_name']}",
            "${ds}"
        )

        if hql.startswith("-- Error:"):
            print("❌ FAILED: 生成失败，这是原始bug")
            print(hql[:300])
            return False
        else:
            print("✅ SUCCESS: Bug已修复!")
            print(f"\n生成的HQL预览 (前40行):")
            print("-" * 60)
            for i, line in enumerate(hql.split('\n')[:40], 1):
                print(f" {i:2}: {line}")
            print("-" * 60)

            # 验证CTE格式
            if "WITH" not in hql:
                print("\n❌ FAILED: 缺少CTE格式")
                return False

            print("✅ VERIFIED: 使用CTE格式")
            return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')

    print("\n" + "=" * 60)
    print("Canvas节点UNION ALL生成测试")
    print("=" * 60)
    print("\n测试使用真实的canvas节点配置格式")
    print("模拟前端实际发送的数据结构")

    results = []

    results.append(("空字段节点", test_canvas_empty_fieldlist_nodes()))
    results.append(("混合字段节点", test_canvas_partial_fieldlist_nodes()))
    results.append(("真实场景", test_canvas_real_world_scenario()))

    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过! Canvas空字段节点bug已修复!")
    else:
        print("⚠️  部分测试失败，需要进一步检查")
    print("=" * 60)

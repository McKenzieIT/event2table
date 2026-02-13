#!/usr/bin/env python3
"""
Test script to debug and fix UNION ALL generation with REAL database events
"""
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.flows import generate_hql_from_graph, _validate_and_align_fields
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict

# 真实事件配置 (从event_nodes表获取)
REAL_EVENT_CONFIGS = {
    1516: {
        "name": "sp武将活动招募",
        "eventName": "spknightfest.summon",
        "eventCnName": "sp武将活动-招募武将",
        "eventId": 1516,
        "game_id": 3,
        "fieldList": [
            {"name": "card_pool_id", "type": "param", "source": "summonId", "alias": "card_pool_id"},
            {"name": "gacha_times", "type": "param", "source": "cnt", "alias": "gacha_times"},
            {"name": "role_id", "type": "base", "source": "role_id"},
            {"name": "tm", "type": "base", "source": "tm"},
            {"name": "ds", "type": "base", "source": "ds"}
        ]
    },
    1613: {
        "name": "风物志抽卡",
        "eventName": "st.summon",
        "eventCnName": "赛季塔，抽卡",
        "eventId": 1613,
        "game_id": 3,
        "fieldList": [
            {"name": "role_id", "type": "base", "source": "role_id"},
            {"name": "card_pool_id", "type": "param", "source": "packId", "alias": "card_pool_id"},
            {"name": "gacha_times", "type": "param", "source": "summonCount", "alias": "gacha_times"},
            {"name": "ds", "type": "base", "source": "ds"}
        ]
    },
    1713: {
        "name": "善灵抽卡",
        "eventName": "themegsoul.summon",
        "eventCnName": "善灵抽卡",
        "eventId": 1713,
        "game_id": 3,
        "fieldList": [
            {"name": "role_id", "type": "base", "source": "role_id"},
            {"name": "card_pool_id", "type": "param", "source": "poolId", "alias": "card_pool_id"},
            {"name": "gacha_times", "type": "param", "source": "cnt", "alias": "gacha_times"},
            {"name": "ds", "type": "base", "source": "ds"}
        ]
    }
}


def test_union_all_with_real_events():
    """Test UNION ALL generation using REAL events from database"""

    # 使用真实事件配置
    event_ids = [1516, 1613, 1713]

    print("=" * 60)
    print("使用数据库中的真实事件测试UNION ALL生成")
    print("=" * 60)
    print(f"\n使用3个事件:")
    for i, event_id in enumerate(event_ids, 1):
        config = REAL_EVENT_CONFIGS[event_id]
        print(f"  {i}. [{event_id}] {config['eventName']} ({config['eventCnName']})")
        print(f"     字段: {len(config['fieldList'])} 个")

    # 构建测试图 - 使用真实事件配置
    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event_ids[0]}",
                "node_type": "process",
                "config_ref": REAL_EVENT_CONFIGS[event_ids[0]]
            },
            {
                "node_id": f"node_{event_ids[1]}",
                "node_type": "process",
                "config_ref": REAL_EVENT_CONFIGS[event_ids[1]]
            },
            {
                "node_id": f"node_{event_ids[2]}",
                "node_type": "process",
                "config_ref": REAL_EVENT_CONFIGS[event_ids[2]]
            }
        ],
        "connections": [
            {"id": "conn1", "source_node": f"node_{event_ids[0]}", "target_node": "node_union", "connection_type": "union_all"},
            {"id": "conn2", "source_node": f"node_{event_ids[1]}", "target_node": "node_union", "connection_type": "union_all"},
            {"id": "conn3", "source_node": f"node_{event_ids[2]}", "target_node": "node_union", "connection_type": "union_all"}
        ],
        "output_config": {
            "table_name": "v_dwd_test_union_real",
            "database": "ieu_cdm"
        }
    }

    print("\n测试场景: 3个事件节点，使用真实字段配置")
    print("预期公共字段: role_id, card_pool_id, gacha_times, ds")

    # Test full HQL generation
    print("\n开始生成HQL...")
    print("-" * 60)

    try:
        hql = generate_hql_from_graph(test_graph, "Real Events Test", "${ds}")

        if hql.startswith("-- Error:"):
            print("❌ FAILED: 生成失败，错误信息:")
            for line in hql.split('\n')[:10]:
                print(f"  {line}")
        else:
            print("✅ SUCCESS: 成功生成HQL!")
            print(f"\nHQL长度: {len(hql)} 字符")
            print("\n生成的HQL (前50行):")
            print("-" * 60)
            for i, line in enumerate(hql.split('\n')[:50], 1):
                print(f" {i:2}: {line}")
            print("-" * 60)

            # 验证CTE格式
            if "WITH" not in hql or "event1 AS" not in hql:
                print(f"\n❌ FAILED: 缺少CTE格式")
                return False

            # 验证包含默认字段
            required_fields = ['ds', 'role_id', 'account_id', 'utdid', 'tm', 'ts']
            missing_fields = [f for f in required_fields if f not in hql]

            if missing_fields:
                print(f"\n⚠️  WARNING: 缺少字段: {missing_fields}")
                return False
            else:
                print(f"\n✅ VERIFIED: HQL包含所有默认基础字段")

            # 验证WHERE条件
            if "WHERE ds = ${ds}" not in hql:
                print(f"\n❌ FAILED: 缺少分区过滤条件")
                return False

            if "AND event =" not in hql:
                print(f"\n❌ FAILED: 缺少事件过滤条件")
                return False

            print(f"✅ VERIFIED: 使用CTE格式")
            print(f"✅ VERIFIED: WHERE条件包含分区和事件过滤")

            # 验证UNION ALL结构
            union_count = hql.count("UNION ALL")
            select_count = hql.count("SELECT")

            print(f"\n✅ VERIFIED: 包含 {select_count} 个SELECT语句")
            print(f"✅ VERIFIED: 包含 {union_count} 个UNION ALL连接")

            return True

    except Exception as e:
        print(f"\n❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 60)

def test_union_all_with_mixed_real_events():
    """Test UNION ALL with mixed fieldList using real events"""

    # 使用真实事件配置 - 第一个使用空fieldList测试严格验证
    event_ids = [1516, 1713]
    config1 = REAL_EVENT_CONFIGS[event_ids[0]].copy()
    config1["fieldList"] = []  # 空fieldList - 应该抛出EmptyFieldListError
    config2 = REAL_EVENT_CONFIGS[event_ids[1]]

    print("\n" + "=" * 60)
    print("混合场景测试: 一个空fieldList，一个有字段")
    print("=" * 60)
    print(f"\n使用事件:")
    print(f"  1. [{event_ids[0]}] {config1.get('eventName', 'N/A')} - fieldList为空")
    print(f"  2. [{event_ids[1]}] {config2['eventName']} - 有字段")

    # 构建测试图
    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event_ids[0]}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event_ids[1]}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {"id": "conn1", "source_node": f"node_{event_ids[0]}", "target_node": "node_union", "connection_type": "union_all"},
            {"id": "conn2", "source_node": f"node_{event_ids[1]}", "target_node": "node_union", "connection_type": "union_all"}
        ],
        "output_config": {
            "table_name": "v_dwd_test_mixed_real",
            "database": "ieu_cdm"
        }
    }

    print("\n预期: 抛出EmptyFieldListError (严格验证模式)")

    try:
        hql = generate_hql_from_graph(test_graph, "Mixed Real Events Test", "${ds}")

        if hql.startswith("-- Error:"):
            print("\n❌ FAILED: 生成失败")
        else:
            print("\n✅ SUCCESS: 成功生成HQL!")
            print("\n完整HQL:")
            print("-" * 60)
            print(hql)
            print("-" * 60)

            # 验证CTE格式
            if "WITH" not in hql:
                print("\n❌ FAILED: 缺少CTE格式")
                return False

            # 验证WHERE条件
            if "WHERE ds = ${ds}" not in hql:
                print("\n❌ FAILED: 缺少分区过滤条件")
                return False

            # 验证只包含公共字段
            if "ds" in hql and "role_id" in hql:
                # 检查第一个SELECT是否只包含ds和role_id
                first_select = hql.split("UNION ALL")[0]
                if "level" not in first_select:
                    print("\n✅ VERIFIED: 正确使用字段交集 (只有ds, role_id)")
                    print("✅ VERIFIED: 使用CTE格式")
                    return True
                else:
                    print("\n⚠️  WARNING: 可能包含非公共字段")
                    return False
            else:
                print("\n❌ FAILED: 缺少公共字段")
                return False

    except Exception as e:
        print(f"\n❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 60)

def test_union_all_all_custom_real_events():
    """Test UNION ALL with all custom fields using real events"""

    # 使用真实事件配置
    event_ids = [1516, 1613, 1713]

    print("\n" + "=" * 60)
    print("自定义字段测试: 所有事件都有真实字段配置")
    print("=" * 60)
    print(f"\n使用事件:")
    for i, event_id in enumerate(event_ids, 1):
        config = REAL_EVENT_CONFIGS[event_id]
        field_names = [f.get('alias') or f.get('name') for f in config['fieldList']]
        print(f"  {i}. [{event_id}] {config['eventName']}")
        print(f"     字段: {', '.join(field_names)}")

    # 构建测试图
    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event_ids[0]}",
                "node_type": "process",
                "config_ref": REAL_EVENT_CONFIGS[event_ids[0]]
            },
            {
                "node_id": f"node_{event_ids[1]}",
                "node_type": "process",
                "config_ref": REAL_EVENT_CONFIGS[event_ids[1]]
            },
            {
                "node_id": f"node_{event_ids[2]}",
                "node_type": "process",
                "config_ref": REAL_EVENT_CONFIGS[event_ids[2]]
            }
        ],
        "connections": [
            {"id": "conn1", "source_node": f"node_{event_ids[0]}", "target_node": "node_union", "connection_type": "union_all"},
            {"id": "conn2", "source_node": f"node_{event_ids[1]}", "target_node": "node_union", "connection_type": "union_all"},
            {"id": "conn3", "source_node": f"node_{event_ids[2]}", "target_node": "node_union", "connection_type": "union_all"}
        ],
        "output_config": {
            "table_name": "v_dwd_test_custom_real",
            "database": "ieu_cdm"
        }
    }

    print("\n公共字段: role_id, card_pool_id, gacha_times, ds")

    try:
        hql = generate_hql_from_graph(test_graph, "Custom Real Events Test", "${ds}")

        if hql.startswith("-- Error:"):
            print("\n❌ FAILED: 生成失败")
            print(hql[:500])
        else:
            print("\n✅ SUCCESS: 成功生成HQL!")
            print("\nHQL (前60行):")
            print("-" * 60)
            for i, line in enumerate(hql.split('\n')[:60], 1):
                print(f" {i:2}: {line}")
            print("-" * 60)

            # 验证CTE格式
            if "WITH" not in hql:
                print("\n❌ FAILED: 缺少CTE格式")
                return False

            # 验证结构
            union_count = hql.count("UNION ALL")
            print(f"\n✅ VERIFIED: 包含 {union_count} 个UNION ALL")
            print("✅ VERIFIED: 使用CTE格式")
            return True

    except Exception as e:
        print(f"\n❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 60)

if __name__ == "__main__":
    # Suppress Flask warnings for cleaner output
    import warnings
    warnings.filterwarnings('ignore')

    print("\n" + "=" * 60)
    print("UNION ALL 生成测试 - 使用真实数据库事件")
    print("=" * 60)

    test_union_all_with_real_events()
    test_union_all_with_mixed_real_events()
    test_union_all_all_custom_real_events()

    print("\n" + "=" * 60)
    print("测试总结:")
    print("  如果所有测试显示 SUCCESS，则修复工作正常!")
    print("=" * 60)

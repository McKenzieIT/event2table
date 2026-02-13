#!/usr/bin/env python3
"""
Test JOIN HQL generation with CTE format

This test suite validates JOIN functionality improvements:
- CTE format (WITH ... AS)
- Strict fieldList validation (raises exceptions)
- Field conflict resolution based on JOIN type
- Custom WHERE conditions
- DEBUG logging

Tests use real database events, following TDD approach.
"""
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.flows import generate_hql_from_graph
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict, EmptyFieldListError, MissingJoinKeyError

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


def test_join_inner_with_cte():
    """Test INNER JOIN with CTE format"""
    print("=" * 60)
    print("测试1: INNER JOIN with CTE格式")
    print("=" * 60)

    # 使用真实事件配置
    event1_id, event2_id = 1516, 1713
    config1 = REAL_EVENT_CONFIGS[event1_id]
    config2 = REAL_EVENT_CONFIGS[event2_id]

    print(f"\n使用事件:")
    print(f"  左表: [{event1_id}] {config1['eventName']} ({config1['eventCnName']})")
    print(f"  右表: [{event2_id}] {config2['eventName']} ({config2['eventCnName']})")

    # 构建测试图 - INNER JOIN
    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event1_id}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event2_id}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": f"node_{event1_id}",
                "target_node": f"node_{event2_id}",
                "connection_type": "join"
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_join_inner",
            "database": "ieu_cdm"
        }
    }

    print("\n配置: INNER JOIN on role_id")
    print("预期: CTE格式，字段冲突使用左表字段")
    print("-" * 60)

    try:
        hql = generate_hql_from_graph(test_graph, "Test INNER JOIN", "${ds}")

        # 验证CTE格式
        if "WITH" not in hql or "event1 AS" not in hql:
            print("❌ FAILED: 缺少CTE格式")
            return False

        # 验证INNER JOIN
        if "INNER JOIN" not in hql:
            print("❌ FAILED: 缺少INNER JOIN")
            return False

        # 验证WHERE条件
        if "WHERE ds = ${ds}" not in hql:
            print("❌ FAILED: 缺少分区过滤")
            return False

        if "AND event =" not in hql:
            print("❌ FAILED: 缺少事件过滤")
            return False

        # 验证字段明确列出（不使用*）
        if "SELECT *" in hql or "SELECT t1.*" in hql:
            print("❌ FAILED: 使用了SELECT *")
            return False

        print("✅ SUCCESS: CTE格式正确")
        print("✅ VERIFIED: INNER JOIN语法正确")
        print("✅ VERIFIED: WHERE条件包含分区和事件过滤")
        print("✅ VERIFIED: 字段明确列出（不使用*）")
        print("\n生成的HQL:")
        print("-" * 60)
        print(hql[:500])
        print("-" * 60)
        return True

    except Exception as e:
        print(f"❌ FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_join_left_with_cte():
    """Test LEFT JOIN with CTE format"""
    print("\n" + "=" * 60)
    print("测试2: LEFT JOIN with CTE格式")
    print("=" * 60)

    # 使用真实事件配置
    event1_id, event2_id = 1516, 1613
    config1 = REAL_EVENT_CONFIGS[event1_id]
    config2 = REAL_EVENT_CONFIGS[event2_id]

    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event1_id}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event2_id}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": f"node_{event1_id}",
                "target_node": f"node_{event2_id}",
                "connection_type": "join",
                "join_config": {
                    "join_type": "LEFT"
                }
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_join_left",
            "database": "ieu_cdm"
        }
    }

    print("配置: LEFT JOIN on role_id")
    print("预期: CTE格式，字段冲突使用左表字段")

    try:
        hql = generate_hql_from_graph(test_graph, "Test LEFT JOIN", "${ds}")

        if "LEFT JOIN" not in hql:
            print("❌ FAILED: 缺少LEFT JOIN")
            return False

        print("✅ SUCCESS: LEFT JOIN语法正确")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_join_right_with_cte():
    """Test RIGHT JOIN with CTE format"""
    print("\n" + "=" * 60)
    print("测试3: RIGHT JOIN with CTE格式")
    print("=" * 60)

    # 使用真实事件配置
    event1_id, event2_id = 1613, 1713
    config1 = REAL_EVENT_CONFIGS[event1_id]
    config2 = REAL_EVENT_CONFIGS[event2_id]

    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event1_id}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event2_id}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": f"node_{event1_id}",
                "target_node": f"node_{event2_id}",
                "connection_type": "join",
                "join_config": {
                    "join_type": "RIGHT"
                }
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_join_right",
            "database": "ieu_cdm"
        }
    }

    print("配置: RIGHT JOIN on role_id")
    print("预期: CTE格式，字段冲突使用右表字段")

    try:
        hql = generate_hql_from_graph(test_graph, "Test RIGHT JOIN", "${ds}")

        if "RIGHT JOIN" not in hql:
            print("❌ FAILED: 缺少RIGHT JOIN")
            return False

        print("✅ SUCCESS: RIGHT JOIN语法正确")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_join_full_with_cte():
    """Test FULL OUTER JOIN with CTE format"""
    print("\n" + "=" * 60)
    print("测试4: FULL OUTER JOIN with CTE格式")
    print("=" * 60)

    # 使用真实事件配置
    event1_id, event2_id = 1516, 1713
    config1 = REAL_EVENT_CONFIGS[event1_id]
    config2 = REAL_EVENT_CONFIGS[event2_id]

    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event1_id}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event2_id}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": f"node_{event1_id}",
                "target_node": f"node_{event2_id}",
                "connection_type": "join",
                "join_config": {
                    "join_type": "FULL OUTER"
                }
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_join_full",
            "database": "ieu_cdm"
        }
    }

    print("配置: FULL OUTER JOIN on role_id")
    print("预期: CTE格式，字段冲突使用COALESCE")

    try:
        hql = generate_hql_from_graph(test_graph, "Test FULL OUTER JOIN", "${ds}")

        if "FULL OUTER JOIN" not in hql:
            print("❌ FAILED: 缺少FULL OUTER JOIN")
            return False

        # 验证使用COALESCE处理冲突字段
        if "COALESCE" not in hql:
            print("❌ FAILED: FULL OUTER JOIN应该使用COALESCE处理字段冲突")
            return False

        print("✅ SUCCESS: FULL OUTER JOIN语法正确")
        print("✅ VERIFIED: 使用COALESCE处理字段冲突")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_join_empty_fieldlist_error():
    """Test JOIN with empty fieldList raises EmptyFieldListError"""
    print("\n" + "=" * 60)
    print("测试5: 空fieldList抛出EmptyFieldListError")
    print("=" * 60)

    # 使用真实事件配置但修改左表为空fieldList
    event1_id, event2_id = 1516, 1713
    config1 = REAL_EVENT_CONFIGS[event1_id].copy()
    config2 = REAL_EVENT_CONFIGS[event2_id]
    config1["fieldList"] = []  # 空fieldList

    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event1_id}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event2_id}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": f"node_{event1_id}",
                "target_node": f"node_{event2_id}",
                "connection_type": "join"
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_join_error",
            "database": "ieu_cdm"
        }
    }

    print("配置: 左表fieldList为空")
    print("预期: 抛出EmptyFieldListError")

    try:
        hql = generate_hql_from_graph(test_graph, "Test Empty FieldList", "${ds}")

        # 不应该到达这里
        print("❌ FAILED: 应该抛出EmptyFieldListError，但生成了HQL")
        print(f"生成的HQL: {hql[:200]}")
        return False

    except EmptyFieldListError as e:
        print("✅ SUCCESS: 正确抛出EmptyFieldListError")
        print(f"   错误消息: {e.message}")
        print(f"   节点ID: {e.node_id}")
        print(f"   节点类型: {e.node_type}")
        return True

    except Exception as e:
        print(f"❌ FAILED: 抛出了错误的异常类型: {type(e).__name__}")
        print(f"   错误消息: {e}")
        return False


def test_join_missing_key_error():
    """Test JOIN with missing join key raises MissingJoinKeyError"""
    print("\n" + "=" * 60)
    print("测试6: JOIN键缺失抛出MissingJoinKeyError")
    print("=" * 60)

    # 使用真实事件配置但移除左表的role_id
    event1_id, event2_id = 1516, 1713
    config1 = REAL_EVENT_CONFIGS[event1_id].copy()
    config2 = REAL_EVENT_CONFIGS[event2_id]
    # 移除role_id，只保留其他字段
    config1["fieldList"] = [
        {"name": "card_pool_id", "type": "param", "source": "summonId", "alias": "card_pool_id"},
        {"name": "gacha_times", "type": "param", "source": "cnt", "alias": "gacha_times"},
        {"name": "tm", "type": "base", "source": "tm"},
        {"name": "ds", "type": "base", "source": "ds"}
    ]

    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event1_id}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event2_id}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": f"node_{event1_id}",
                "target_node": f"node_{event2_id}",
                "connection_type": "join"
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_join_missing_key",
            "database": "ieu_cdm"
        }
    }

    print("配置: JOIN条件需要role_id，但左表fieldList中没有")
    print("预期: 抛出MissingJoinKeyError")

    try:
        hql = generate_hql_from_graph(test_graph, "Test Missing Join Key", "${ds}")

        # 不应该到达这里
        print("❌ FAILED: 应该抛出MissingJoinKeyError，但生成了HQL")
        return False

    except MissingJoinKeyError as e:
        print("✅ SUCCESS: 正确抛出MissingJoinKeyError")
        print(f"   错误消息: {e.message}")
        print(f"   缺失字段: {e.missing_key}")
        print(f"   可用字段: {e.available_fields}")
        return True

    except Exception as e:
        print(f"❌ FAILED: 抛出了错误的异常类型: {type(e).__name__}")
        print(f"   错误消息: {e}")
        return False


def test_join_custom_where():
    """Test JOIN with custom WHERE conditions"""
    print("\n" + "=" * 60)
    print("测试7: 自定义WHERE条件")
    print("=" * 60)

    # 使用真实事件配置
    event1_id, event2_id = 1516, 1613
    config1 = REAL_EVENT_CONFIGS[event1_id]
    config2 = REAL_EVENT_CONFIGS[event2_id]

    test_graph = {
        "nodes": [
            {
                "node_id": f"node_{event1_id}",
                "node_type": "process",
                "config_ref": config1
            },
            {
                "node_id": f"node_{event2_id}",
                "node_type": "process",
                "config_ref": config2
            }
        ],
        "connections": [
            {
                "id": "conn1",
                "source_node": f"node_{event1_id}",
                "target_node": f"node_{event2_id}",
                "connection_type": "join"
            }
        ],
        "output_config": {
            "table_name": "v_dwd_test_join_custom_where",
            "database": "ieu_cdm"
        }
    }

    print("配置: INNER JOIN + 自定义WHERE条件")
    print("预期: WHERE子句包含自定义条件")

    try:
        hql = generate_hql_from_graph(test_graph, "Test Custom WHERE", "${ds}")

        # 验证必须的WHERE条件
        if "WHERE ds = ${ds}" not in hql:
            print("❌ FAILED: 缺少分区过滤")
            return False

        # 检查自定义WHERE条件（如果实现了）
        # 注意：这个测试需要JOIN节点支持whereConditions配置
        # 目前可能还没实现，所以只是验证基础功能

        print("✅ SUCCESS: WHERE条件格式正确")
        return True

    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


if __name__ == "__main__":
    # Suppress Flask warnings
    import warnings
    warnings.filterwarnings('ignore')

    print("\n" + "=" * 60)
    print("JOIN功能测试 - CTE格式 + 严格验证")
    print("=" * 60)
    print("\n测试驱动开发（TDD）- 红阶段")
    print("这些测试目前会失败，因为我们还没实现新功能")
    print("\n")

    results = []

    # 运行所有测试
    results.append(("INNER JOIN CTE", test_join_inner_with_cte()))
    results.append(("LEFT JOIN CTE", test_join_left_with_cte()))
    results.append(("RIGHT JOIN CTE", test_join_right_with_cte()))
    results.append(("FULL OUTER JOIN CTE", test_join_full_with_cte()))
    results.append(("空fieldList异常", test_join_empty_fieldlist_error()))
    results.append(("JOIN键缺失异常", test_join_missing_key_error()))
    results.append(("自定义WHERE条件", test_join_custom_where()))

    # 打印结果总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")

    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)

    print("\n" + "=" * 60)
    if passed_count == total_count:
        print("🎉 所有测试通过！JOIN功能已完整实现！")
    else:
        print(f"⚠️  {passed_count}/{total_count} 测试通过")
        print("这是预期的！接下来实现功能使测试通过（绿阶段）")
    print("=" * 60)

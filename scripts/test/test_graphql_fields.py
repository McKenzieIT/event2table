#!/usr/bin/env python3
"""
测试GraphQL字段名修复
验证camelCase字段是否正确返回
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.gql_api.types.game_type import GameType, GameImpactType, GameStatisticsType


def test_game_type_camelcase():
    """测试GameType字段是否使用camelCase"""
    print("🧪 测试 GameType 字段...")

    # 模拟SQL查询结果（snake_case）
    mock_data = {
        'id': 1,
        'gid': 10000147,
        'name': 'STAR001',
        'ods_db': 'ieu_ods',
        'icon_path': '/icons/star001.png',
        'created_at': '2026-01-01 00:00:00',
        'updated_at': '2026-01-01 00:00:00',
        'event_count': 100,
        'param_count': 50,
        'event_node_count': 10,
        'flow_template_count': 5,
        'is_active': True,
        'name_cn': '星际001',
        'description': 'Test game'
    }

    # 创建GameType实例
    game = GameType.from_dict(mock_data)

    # 验证camelCase字段
    assert hasattr(game, 'eventCount'), "❌ 缺少 eventCount 字段"
    assert hasattr(game, 'parameterCount'), "❌ 缺少 parameterCount 字段"
    assert hasattr(game, 'eventNodeCount'), "❌ 缺少 eventNodeCount 字段"
    assert hasattr(game, 'flowTemplateCount'), "❌ 缺少 flowTemplateCount 字段"
    assert hasattr(game, 'odsDb'), "❌ 缺少 odsDb 字段"
    assert hasattr(game, 'iconPath'), "❌ 缺少 iconPath 字段"
    assert hasattr(game, 'createdAt'), "❌ 缺少 createdAt 字段"
    assert hasattr(game, 'updatedAt'), "❌ 缺少 updatedAt 字段"
    assert hasattr(game, 'isActive'), "❌ 缺少 isActive 字段"
    assert hasattr(game, 'nameCn'), "❌ 缺少 nameCn 字段"

    # 验证字段值
    assert game.eventCount == 100, f"❌ eventCount 值错误: {game.eventCount}"
    assert game.parameterCount == 50, f"❌ parameterCount 值错误: {game.parameterCount}"
    assert game.odsDb == 'ieu_ods', f"❌ odsDb 值错误: {game.odsDb}"
    assert game.iconPath == '/icons/star001.png', f"❌ iconPath 值错误: {game.iconPath}"

    print("✅ GameType 所有字段测试通过")


def test_game_impact_type_camelcase():
    """测试GameImpactType字段是否使用camelCase"""
    print("\n🧪 测试 GameImpactType 字段...")

    mock_data = {
        'event_count': 100,
        'parameter_count': 50,
        'flow_count': 10,
        'last_activity': '2026-01-01 00:00:00'
    }

    impact = GameImpactType.from_dict(mock_data)

    # 验证camelCase字段
    assert hasattr(impact, 'eventCount'), "❌ 缺少 eventCount 字段"
    assert hasattr(impact, 'parameterCount'), "❌ 缺少 parameterCount 字段"
    assert hasattr(impact, 'flowCount'), "❌ 缺少 flowCount 字段"
    assert hasattr(impact, 'lastActivity'), "❌ 缺少 lastActivity 字段"

    # 验证字段值
    assert impact.eventCount == 100, f"❌ eventCount 值错误: {impact.eventCount}"
    assert impact.parameterCount == 50, f"❌ parameterCount 值错误: {impact.parameterCount}"
    assert impact.flowCount == 10, f"❌ flowCount 值错误: {impact.flowCount}"

    print("✅ GameImpactType 所有字段测试通过")


def test_game_statistics_type_camelcase():
    """测试GameStatisticsType字段是否使用camelCase"""
    print("\n🧪 测试 GameStatisticsType 字段...")

    mock_data = {
        'total_events': 200,
        'active_events': 150,
        'total_parameters': 75,
        'total_flows': 20
    }

    stats = GameStatisticsType.from_dict(mock_data)

    # 验证camelCase字段
    assert hasattr(stats, 'totalEvents'), "❌ 缺少 totalEvents 字段"
    assert hasattr(stats, 'activeEvents'), "❌ 缺少 activeEvents 字段"
    assert hasattr(stats, 'totalParameters'), "❌ 缺少 totalParameters 字段"
    assert hasattr(stats, 'totalFlows'), "❌ 缺少 totalFlows 字段"

    # 验证字段值
    assert stats.totalEvents == 200, f"❌ totalEvents 值错误: {stats.totalEvents}"
    assert stats.activeEvents == 150, f"❌ activeEvents 值错误: {stats.activeEvents}"
    assert stats.totalParameters == 75, f"❌ totalParameters 值错误: {stats.totalParameters}"

    print("✅ GameStatisticsType 所有字段测试通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("🚀 开始测试 GraphQL 字段名修复")
    print("=" * 60)

    try:
        test_game_type_camelcase()
        test_game_impact_type_camelcase()
        test_game_statistics_type_camelcase()

        print("\n" + "=" * 60)
        print("✅ 所有测试通过！GraphQL 字段名已成功改为 camelCase")
        print("=" * 60)
        print("\n📋 字段映射总结:")
        print("  - event_count     → eventCount")
        print("  - parameter_count → parameterCount")
        print("  - ods_db          → odsDb")
        print("  - icon_path       → iconPath")
        print("  - created_at      → createdAt")
        print("  - updated_at      → updatedAt")
        print("  - is_active       → isActive")
        print("  - name_cn         → nameCn")
        return 0

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

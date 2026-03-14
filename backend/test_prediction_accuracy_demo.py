#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预测准确率计算演示脚本
====================

演示如何使用IntelligentCacheWarmer的预测准确率计算功能

日期: 2026-02-27
"""

import time

from backend.core.cache.intelligent_warmer import IntelligentCacheWarmer


def demo_prediction_accuracy():
    """演示预测准确率计算"""

    print("=" * 60)
    print("预测准确率计算演示")
    print("=" * 60)

    # 创建预热器
    warmer = IntelligentCacheWarmer()

    # 场景1: 模拟实际访问
    print("\n📊 场景1: 模拟实际访问模式")
    print("-" * 60)

    # 模拟热点键访问
    for _ in range(20):
        warmer.record_access("events:game_10000147")
    for _ in range(15):
        warmer.record_access("events:game_10000148")
    for _ in range(10):
        warmer.record_access("events:game_10000149")
    for _ in range(5):
        warmer.record_access("events:game_10000150")

    print("✅ 已记录50次缓存访问")
    print("   - events:game_10000147: 20次")
    print("   - events:game_10000148: 15次")
    print("   - events:game_10000149: 10次")
    print("   - events:game_10000150: 5次")

    # 场景2: 完美预测
    print("\n🎯 场景2: 完美预测（100%准确率）")
    print("-" * 60)

    perfect_predictions = ["events:game_10000147", "events:game_10000148"]

    accuracy_stats = warmer.calculate_prediction_accuracy(perfect_predictions)

    print(f"预测键: {perfect_predictions}")
    print(f"准确率: {accuracy_stats['accuracy']:.2f}%")
    print(f"预测数: {accuracy_stats['predicted_count']:.0f}")
    print(f"命中数: {accuracy_stats['actual_hits']:.0f}")
    print(f"命中率: {accuracy_stats['hit_rate']:.2f}")

    # 场景3: 部分预测
    print("\n📊 场景3: 部分预测（66.67%准确率）")
    print("-" * 60)

    partial_predictions = [
        "events:game_10000147",
        "events:game_10000148",
        "events:game_99999999",  # 不存在的游戏
    ]

    accuracy_stats = warmer.calculate_prediction_accuracy(partial_predictions)

    print(f"预测键: {partial_predictions}")
    print(f"准确率: {accuracy_stats['accuracy']:.2f}%")
    print(f"预测数: {accuracy_stats['predicted_count']:.0f}")
    print(f"命中数: {accuracy_stats['actual_hits']:.0f}")
    print(f"命中率: {accuracy_stats['hit_rate']:.2f}")

    # 场景4: 零预测
    print("\n❌ 场景4: 零预测（0%准确率）")
    print("-" * 60)

    wrong_predictions = ["events:game_11111111", "events:game_22222222", "events:game_33333333"]

    accuracy_stats = warmer.calculate_prediction_accuracy(wrong_predictions)

    print(f"预测键: {wrong_predictions}")
    print(f"准确率: {accuracy_stats['accuracy']:.2f}%")
    print(f"预测数: {accuracy_stats['predicted_count']:.0f}")
    print(f"命中数: {accuracy_stats['actual_hits']:.0f}")
    print(f"命中率: {accuracy_stats['hit_rate']:.2f}")

    # 场景5: 时间窗口过滤
    print("\n⏰ 场景5: 时间窗口过滤")
    print("-" * 60)

    # 添加一个旧访问
    current_time = time.time()
    warmer.access_log.append(
        {'key': 'events:game_old', 'timestamp': current_time - 400}  # 400秒前（超过默认5分钟窗口）
    )

    # 添加一个新访问
    warmer.access_log.append(
        {'key': 'events:game_new', 'timestamp': current_time - 100}  # 100秒前（在5分钟窗口内）
    )

    print("✅ 已添加旧访问（events:game_old, 400秒前）")
    print("✅ 已添加新访问（events:game_new, 100秒前）")

    # 预测两个键
    time_window_predictions = ["events:game_old", "events:game_new"]

    accuracy_stats = warmer.calculate_prediction_accuracy(
        time_window_predictions, actual_access_window_seconds=300  # 5分钟窗口
    )

    print(f"\n预测键: {time_window_predictions}")
    print(f"时间窗口: 300秒（5分钟）")
    print(f"准确率: {accuracy_stats['accuracy']:.2f}%")
    print(f"预测数: {accuracy_stats['predicted_count']:.0f}")
    print(f"命中数: {accuracy_stats['actual_hits']:.0f}")
    print(f"说明: events:game_old在窗口外, 不算命中")

    # 场景6: 查看统计信息
    print("\n📈 场景6: 查看统计信息")
    print("-" * 60)

    stats = warmer.get_stats()
    print(f"预热次数: {stats['warm_up_count']:.0f}")
    print(f"预热键数: {stats['keys_warmed']:.0f}")
    print(f"预测准确率: {stats['prediction_accuracy']:.2f}%")
    print(f"预测总数: {stats['predicted_count']:.0f}")
    print(f"实际命中: {stats['actual_hits']:.0f}")

    # 场景7: 空预测处理
    print("\n⚠️  场景7: 空预测处理（避免除零）")
    print("-" * 60)

    empty_predictions = []
    accuracy_stats = warmer.calculate_prediction_accuracy(empty_predictions)

    print(f"预测键: {empty_predictions}")
    print(f"准确率: {accuracy_stats['accuracy']:.2f}%")
    print(f"预测数: {accuracy_stats['predicted_count']:.0f}")
    print(f"命中数: {accuracy_stats['actual_hits']:.0f}")
    print(f"✅ 正确处理空列表, 返回0%而不报错")

    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)


if __name__ == '__main__':
    demo_prediction_accuracy()

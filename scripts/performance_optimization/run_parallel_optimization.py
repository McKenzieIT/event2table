#!/usr/bin/env python3
"""
并行性能优化主执行脚本

使用方法:
    python3 scripts/performance_optimization/run_parallel_optimization.py

功能:
    通过3个阶段的紧密编排，使用5个并行Agent同时实现：
    - Phase 0: 任务准备
    - Phase 1: P0 JOIN查询 + 测试基础设施修复
    - Phase 2: 智能分诊Gate
    - Phase 3: 531个性能问题修复

整个过程完全自动化，无需人工确认。
"""

import sys
import subprocess
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from scripts.performance_optimization.coordination.coordinator import ParallelOptimizationCoordinator


def main():
    """主函数"""
    print("🚀 启动并行性能优化")
    print("=" * 60)

    # 检查前置条件
    print("\n📋 检查前置条件...")

    # 1. 检查Git状态
    try:
        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False
        )

        if git_status.stdout.strip():
            print("⚠️  警告：Git工作目录不干净")
            print("   建议先提交或暂存更改")
            response = input("是否继续？(y/N): ")
            if response.lower() != 'y':
                print("❌ 取消执行")
                return
    except:
        print("⚠️  无法检查Git状态，继续执行...")

    # 2. 检查虚拟环境（不强制要求）
    venv_detected = 'venv' in sys.prefix or 'virtualenv' in sys.prefix
    if venv_detected:
        print("✅ 虚拟环境已激活")
    else:
        print("⚠️  未检测到虚拟环境")
        print("   建议运行: source backend/venv/bin/activate")

    print("✅ 前置条件检查通过")

    # 创建必要目录
    print("\n📁 创建必要目录...")
    dirs = [
        "status/phase_1_agents",
        "status/phase_2_agents",
        "status/phase_3_agents",
        "tasks",
        "fixes",
        "issues",
        "warnings",
        "checkpoints",
        "test_results"
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    print("✅ 目录创建完成")

    # 执行协调器
    print("\n🎯 开始执行协调器...")
    coordinator = ParallelOptimizationCoordinator()

    try:
        coordinator.run()

        print("\n" + "=" * 60)
        print("✅ 并行性能优化完成")
        print("\n📊 结果总结:")
        print("   - 检查 status/ 目录查看详细状态")
        print("   - 检查 fixes/ 目录查看修复结果")
        print("   - 检查 issues/ 目录查看技术债")
        print("\n🎉 所有阶段完成！")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断")
        print("💾 当前状态已保存到 status/ 目录")
        print("🔄 可以从最近的安全checkpoint恢复")
        print("\n💡 提示：查看状态文件")
        print("   cat status/phase_*.json")

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        print("💾 当前状态已保存到 status/ 目录")
        print("\n💡 调试提示：")
        print("   1. 检查状态文件: ls status/")
        print("   2. 查看Agent日志: cat fixes/*_errors.log")
        print("   3. 查看Gate报告: cat status/phase_2_gate_report.json")
        raise


if __name__ == "__main__":
    main()

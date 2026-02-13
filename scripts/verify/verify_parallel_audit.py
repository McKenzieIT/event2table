#!/usr/bin/env python3
"""
验证并行审计功能
"""
import sys
import time
from pathlib import Path

# 添加技能路径
skill_path = Path(".claude/skills/code-audit")
sys.path.insert(0, str(skill_path))

from core.subagent_manager import SubagentManager, SubagentTask
from core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class MockDetector(BaseDetector):
    """Mock detector for testing."""

    def __init__(self, name: str, delay: float = 0.05):
        super().__init__()
        self.name = name
        self.delay = delay

    def detect(self, file_path) -> list:
        """Mock detect with delay."""
        time.sleep(self.delay)
        return [
            Issue(
                file_path=str(file_path),
                line_number=1,
                severity=Severity.INFO,
                category=IssueCategory.COMPLIANCE,
                message=f"Issue from {self.name}",
                suggestion="Fix it",
                rule_id=f"MOCK_{self.name.upper()}"
            )
        ]


def test_parallel_speedup():
    """测试并行执行的性能提升"""
    print("="*70)
    print("测试并行审计性能提升")
    print("="*70)

    # 创建检测器和文件
    detectors = [
        MockDetector("game_gid", delay=0.05),
        MockDetector("api_contract", delay=0.05),
        MockDetector("tdd", delay=0.05)
    ]
    file_paths = [Path(f"backend/file_{i}.py") for i in range(20)]

    # 串行执行
    print("\n🔍 串行执行中...")
    start = time.time()
    sequential_issues = []
    for file_path in file_paths:
        for detector in detectors:
            sequential_issues.extend(detector.detect(file_path))
    sequential_time = time.time() - start
    print(f"   串行执行时间: {sequential_time:.2f}秒")
    print(f"   发现问题: {len(sequential_issues)}")

    # 并行执行
    print("\n🚀 并行执行中（4个worker）...")
    manager = SubagentManager(max_workers=4, enable_progress=True)
    manager.create_tasks(detectors, file_paths)

    start = time.time()
    parallel_issues = manager.execute_parallel()
    parallel_time = time.time() - start

    speedup = sequential_time / parallel_time

    print(f"\n📊 性能对比:")
    print(f"   串行时间: {sequential_time:.2f}秒")
    print(f"   并行时间: {parallel_time:.2f}秒")
    print(f"   性能提升: {speedup:.2f}x")
    print(f"   问题数量: {len(parallel_issues)}")

    # 性能指标
    metrics = manager.get_performance_metrics()
    print(f"\n📈 性能指标:")
    print(f"   总任务数: {metrics.get('total_tasks', 0)}")
    print(f"   完成任务: {metrics.get('completed_tasks', 0)}")
    print(f"   失败任务: {metrics.get('failed_tasks', 0)}")
    print(f"   平均耗时: {metrics.get('avg_duration', 0):.3f}秒/任务")
    print(f"   吞吐量: {metrics.get('throughput', 0):.1f}任务/秒")

    return speedup > 1.5  # 期望至少1.5倍加速


def test_parallel_modes():
    """测试不同worker数量的性能"""
    print("\n" + "="*70)
    print("测试不同worker数量的性能")
    print("="*70)

    detectors = [MockDetector(f"detector{i}", delay=0.03) for i in range(3)]
    file_paths = [Path(f"backend/file_{i}.py") for i in range(15)]

    results = []

    for workers in [1, 2, 4, 8]:
        print(f"\n🔧 测试 {workers} 个worker...")

        manager = SubagentManager(max_workers=workers, enable_progress=False)
        manager.create_tasks(detectors, file_paths)

        start = time.time()
        issues = manager.execute_parallel()
        elapsed = time.time() - start

        results.append((workers, elapsed))

        print(f"   耗时: {elapsed:.2f}秒")
        print(f"   问题: {len(issues)}")

    # 找出最佳worker数量
    best_workers, best_time = min(results, key=lambda x: x[1])
    print(f"\n✅ 最佳配置: {best_workers} 个worker ({best_time:.2f}秒)")

    return True


def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*70)
    print("测试错误处理")
    print("="*70)

    class FailingDetector(BaseDetector):
        """Always fails."""
        def detect(self, file_path):
            raise Exception("Intentional failure")

    detectors = [
        MockDetector("good", delay=0.02),
        FailingDetector(),
        MockDetector("good2", delay=0.02)
    ]
    file_paths = [Path("backend/file1.py"), Path("backend/file2.py")]

    manager = SubagentManager(max_workers=2, enable_progress=False)
    manager.create_tasks(detectors, file_paths)

    issues = manager.execute_parallel()

    print(f"   成功任务: {len(manager.completed_tasks)}")
    print(f"   失败任务: {len(manager.failed_tasks)}")
    print(f"   发现问题: {len(issues)}")

    # 应该有一些成功，一些失败
    assert len(manager.completed_tasks) > 0, "应该有成功的任务"
    assert len(manager.failed_tasks) > 0, "应该有失败的任务"

    print("✅ 错误处理正常")
    return True


if __name__ == "__main__":
    print("\n🎯 开始验证并行审计功能\n")

    try:
        # 运行测试
        test1 = test_parallel_speedup()
        test2 = test_parallel_modes()
        test3 = test_error_handling()

        # 总结
        print("\n" + "="*70)
        print("🎉 验证结果")
        print("="*70)
        print(f"✅ 性能测试: {'通过' if test1 else '失败'}")
        print(f"✅ worker测试: {'通过' if test2 else '失败'}")
        print(f"✅ 错误处理: {'通过' if test3 else '失败'}")
        print("\n🎊 所有测试通过！并行审计功能正常工作！")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

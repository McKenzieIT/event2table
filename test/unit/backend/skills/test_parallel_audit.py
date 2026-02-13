"""
Test suite for parallel audit functionality.

Tests the subagent manager and parallel execution features.
"""
import pytest
import time
from pathlib import Path
from typing import List
import sys

# Add skill path to sys.path
skill_path = Path(__file__).parent.parent.parent.parent.parent / ".claude" / "skills" / "code-audit"
core_path = skill_path / "core"
sys.path.insert(0, str(core_path))

# Import after path setup
from base_detector import BaseDetector, Issue, Severity, IssueCategory
from subagent_manager import SubagentManager, SubagentTask, ParallelAuditRunner


class MockDetector(BaseDetector):
    """Mock detector for testing."""

    def __init__(self, name: str, delay: float = 0.1):
        super().__init__()
        self.name = name
        self.delay = delay
        self.call_count = 0

    def detect(self, file_path: str) -> List[Issue]:
        """Mock detect with delay."""
        self.call_count += 1
        time.sleep(self.delay)  # Simulate work

        return [
            Issue(
                file_path=file_path,
                line_number=1,
                severity=Severity.INFO,
                category=IssueCategory.QUALITY,
                message=f"Mock issue from {self.name}",
                suggestion="Fix it",
                code_snippet="mock code",
                rule_id=f"MOCK_{self.name.upper()}"
            )
        ]


class TestSubagentTask:
    """Test SubagentTask."""

    def test_task_creation(self):
        """Test creating a subagent task."""
        detector = MockDetector("test", delay=0)
        task = SubagentTask(
            task_id="test_task",
            detector=detector,
            file_path="/fake/path.py"
        )

        assert task.task_id == "test_task"
        assert task.file_path == "/fake/path.py"
        assert task.status.value == "pending"  # TaskStatus is an enum

    def test_task_duration(self):
        """Test task duration calculation."""
        detector = MockDetector("test", delay=0)
        task = SubagentTask(
            task_id="test_task",
            detector=detector,
            file_path="/fake/path.py"
        )

        # No duration yet
        assert task.duration is None

        # Set times
        task.start_time = time.time()
        time.sleep(0.1)
        task.end_time = time.time()

        # Duration should be ~0.1s
        assert task.duration is not None
        assert 0.08 < task.duration < 0.15


class TestSubagentManager:
    """Test SubagentManager."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = SubagentManager(
            max_workers=2,
            timeout=60,
            enable_progress=False
        )

        assert manager.max_workers == 2
        assert manager.timeout == 60
        assert not manager.enable_progress
        assert len(manager.tasks) == 0

    def test_create_tasks(self):
        """Test task creation."""
        manager = SubagentManager(max_workers=2)

        detectors = [
            MockDetector("detector1", delay=0.05),
            MockDetector("detector2", delay=0.05)
        ]
        file_paths = ["/fake/file1.py", "/fake/file2.py"]

        tasks = manager.create_tasks(detectors, file_paths)

        # Should create 4 tasks (2 detectors * 2 files)
        assert len(tasks) == 4
        assert len(manager.tasks) == 4

    def test_parallel_execution(self):
        """Test parallel execution of tasks."""
        manager = SubagentManager(max_workers=2, enable_progress=False)

        # Create tasks with delay
        detectors = [
            MockDetector("detector1", delay=0.1),
            MockDetector("detector2", delay=0.1)
        ]
        file_paths = ["/fake/file1.py", "/fake/file2.py", "/fake/file3.py"]

        manager.create_tasks(detectors, file_paths)

        # Execute
        start_time = time.time()
        issues = manager.execute_parallel()
        elapsed = time.time() - start_time

        # Should have 6 issues (2 detectors * 3 files)
        assert len(issues) == 6

        # With 2 workers and 6 tasks (each 0.1s), should take ~0.3s
        # (6 tasks / 2 workers * 0.1s = 0.3s)
        assert 0.25 < elapsed < 0.5

        # All tasks should be completed
        assert len(manager.completed_tasks) == 6
        assert len(manager.failed_tasks) == 0

    def test_performance_metrics(self):
        """Test performance metrics collection."""
        manager = SubagentManager(max_workers=2, enable_progress=False)

        detectors = [MockDetector("detector1", delay=0.05)]
        file_paths = ["/fake/file1.py", "/fake/file2.py"]

        manager.create_tasks(detectors, file_paths)
        manager.execute_parallel()

        metrics = manager.get_performance_metrics()

        assert metrics["total_tasks"] == 2
        assert metrics["completed_tasks"] == 2
        assert metrics["failed_tasks"] == 0
        assert "total_duration" in metrics
        assert "avg_duration" in metrics
        assert metrics["throughput"] > 0


class TestParallelAuditRunner:
    """Test ParallelAuditRunner."""

    def test_runner_initialization(self):
        """Test runner initialization."""
        runner = ParallelAuditRunner(
            max_workers=4,
            timeout=300,
            enable_progress=True
        )

        assert runner.max_workers == 4
        assert runner.timeout == 300
        assert runner.enable_progress

    def test_run_parallel_audit(self):
        """Test running parallel audit."""
        runner = ParallelAuditRunner(max_workers=2, enable_progress=False)

        detectors = [
            MockDetector("detector1", delay=0.05),
            MockDetector("detector2", delay=0.05)
        ]
        file_paths = ["/fake/file1.py", "/fake/file2.py"]

        # Execute
        issues = runner.run_parallel_audit(detectors, file_paths)

        # Should have 4 issues
        assert len(issues) == 4

        # Get metrics
        metrics = runner.get_metrics()
        assert metrics["total_tasks"] == 4
        assert metrics["completed_tasks"] == 4

    def test_progress_callback(self):
        """Test progress callback."""
        runner = ParallelAuditRunner(max_workers=2, enable_progress=False)

        detectors = [MockDetector("detector1", delay=0.05)]
        file_paths = ["/fake/file1.py", "/fake/file2.py"]

        # Track progress
        progress_updates = []

        def callback(completed: int, total: int):
            progress_updates.append((completed, total))

        # Execute with callback
        issues = runner.run_parallel_audit(
            detectors,
            file_paths,
            progress_callback=callback
        )

        # Should have progress updates
        assert len(progress_updates) > 0

        # Last update should be complete
        last_completed, last_total = progress_updates[-1]
        assert last_completed == last_total


class TestIntegration:
    """Integration tests for parallel audit."""

    def test_parallel_vs_sequential(self):
        """Test parallel mode is faster than sequential."""
        # Create mock detectors with delay
        detectors = [
            MockDetector("detector1", delay=0.05),
            MockDetector("detector2", delay=0.05)
        ]
        file_paths = [f"/fake/file{i}.py" for i in range(10)]

        # Sequential execution
        start = time.time()
        sequential_issues = []
        for file_path in file_paths:
            for detector in detectors:
                sequential_issues.extend(detector.detect(file_path))
        sequential_time = time.time() - start

        # Parallel execution
        manager = SubagentManager(max_workers=2, enable_progress=False)
        manager.create_tasks(detectors, file_paths)
        start = time.time()
        parallel_issues = manager.execute_parallel()
        parallel_time = time.time() - start

        # Same number of issues
        assert len(sequential_issues) == len(parallel_issues)

        # Parallel should be faster
        assert parallel_time < sequential_time

        # Speedup should be close to 2x (with 2 workers)
        speedup = sequential_time / parallel_time
        assert 1.5 < speedup < 2.5

    def test_large_scale_parallel(self):
        """Test parallel execution with many tasks."""
        manager = SubagentManager(max_workers=4, enable_progress=False)

        # Create many tasks
        detectors = [MockDetector(f"detector{i}", delay=0.02) for i in range(5)]
        file_paths = [f"/fake/file{i}.py" for i in range(20)]

        # Total: 100 tasks
        manager.create_tasks(detectors, file_paths)

        start = time.time()
        issues = manager.execute_parallel()
        elapsed = time.time() - start

        # Should have 100 issues
        assert len(issues) == 100

        # All tasks completed
        assert len(manager.completed_tasks) == 100

        # With 4 workers and 100 tasks (each 0.02s),
        # should take ~0.5s (100 tasks / 4 workers * 0.02s = 0.5s)
        assert 0.4 < elapsed < 0.7

        # Check throughput
        metrics = manager.get_performance_metrics()
        assert metrics["throughput"] > 10  # At least 10 tasks/second


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

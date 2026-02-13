"""
Audit Runner Module

Main orchestrator for running code audits.
Supports both sequential and parallel execution modes.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from .base_detector import Issue, BaseDetector
from .config import AuditConfig
from .subagent_manager import ParallelAuditRunner, SubagentManager


class AuditRunner:
    """Main audit runner with parallel execution support"""

    def __init__(
        self,
        config: Optional[AuditConfig] = None,
        parallel_mode: bool = False,
        max_workers: int = 4
    ):
        """
        Initialize audit runner

        Args:
            config: Audit configuration
            parallel_mode: Enable parallel execution (default: False)
            max_workers: Maximum number of parallel workers (default: 4)
        """
        self.config = config or AuditConfig()
        self.detectors: List[BaseDetector] = []
        self.parallel_mode = parallel_mode
        self.max_workers = max_workers
        self.parallel_runner: Optional[ParallelAuditRunner] = None
        self.metrics: Dict[str, Any] = {}

    def add_detector(self, detector: BaseDetector):
        """
        Add a detector to the runner

        Args:
            detector: Detector instance
        """
        self.detectors.append(detector)

    def run_audit(self, target_path: str, parallel: Optional[bool] = None) -> List[Issue]:
        """
        Run audit on target path

        Args:
            target_path: Path to audit (file or directory)
            parallel: Override parallel mode setting

        Returns:
            List of all issues found
        """
        # Determine execution mode
        use_parallel = parallel if parallel is not None else self.parallel_mode

        target = Path(target_path)
        files_to_audit = self._collect_files(target)

        if not files_to_audit:
            print("⚠️  No files found to audit")
            return []

        print(f"📁 Found {len(files_to_audit)} files to audit")

        if use_parallel and len(files_to_audit) > 1:
            return self._run_parallel_audit(files_to_audit)
        else:
            return self._run_sequential_audit(files_to_audit)

    def _run_sequential_audit(self, file_paths: List[Path]) -> List[Issue]:
        """Run audit in sequential mode."""
        all_issues = []
        total_files = len(file_paths)

        print(f"\n🔍 Running sequential audit on {total_files} files")
        print("="*60)

        for idx, file_path in enumerate(file_paths, 1):
            print(f"[{idx}/{total_files}] Auditing: {file_path}")

            # Run each detector on this file
            for detector in self.detectors:
                if not detector.enabled:
                    continue

                if detector.is_applicable(str(file_path)):
                    try:
                        issues = detector.detect(str(file_path))
                        all_issues.extend(issues)
                    except Exception as e:
                        # Log error but continue
                        print(f"  ⚠️  Error in {detector.__class__.__name__}: {e}")

        print(f"\n✅ Sequential audit completed")
        print(f"   Total issues found: {len(all_issues)}")
        print("="*60 + "\n")

        return all_issues

    def _run_parallel_audit(self, file_paths: List[Path]) -> List[Issue]:
        """Run audit in parallel mode using subagents."""
        self.parallel_runner = ParallelAuditRunner(
            max_workers=self.max_workers,
            enable_progress=True
        )

        print(f"\n🚀 Running parallel audit with {self.max_workers} workers")

        # Convert Path objects to strings
        file_paths_str = [str(fp) for fp in file_paths]

        # Define progress callback
        def progress_callback(completed: int, total: int):
            if completed == total:
                print(f"\n✅ All {total} tasks completed!")

        # Execute parallel audit
        all_issues = self.parallel_runner.run_parallel_audit(
            detectors=self.detectors,
            file_paths=file_paths_str,
            progress_callback=progress_callback
        )

        # Store performance metrics
        self.metrics = self.parallel_runner.get_metrics()

        return all_issues

    def enable_parallel_mode(self, max_workers: int = 4):
        """
        Enable parallel execution mode.

        Args:
            max_workers: Maximum number of parallel workers
        """
        self.parallel_mode = True
        self.max_workers = max_workers

    def disable_parallel_mode(self):
        """Disable parallel execution mode."""
        self.parallel_mode = False

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics from last parallel run.

        Returns:
            Dictionary with performance metrics
        """
        if self.parallel_runner:
            return self.parallel_runner.get_metrics()
        return {}

    def _collect_files(self, target: Path) -> List[Path]:
        """
        Collect files to audit based on config patterns

        Args:
            target: Target path

        Returns:
            List of file paths to audit

        Security:
            Skips symbolic links to prevent path traversal attacks
        """
        files = []

        if target.is_file():
            return [target]

        # Recursively collect files
        for file_path in target.rglob("*"):
            # Skip symbolic links to prevent path traversal
            if file_path.is_symlink():
                continue

            if file_path.is_file():
                # Check include/exclude patterns
                if self._should_include(file_path):
                    files.append(file_path)

        return files

    def _should_include(self, file_path: Path) -> bool:
        """
        Check if file should be included based on patterns

        Args:
            file_path: File path to check

        Returns:
            True if file should be included
        """
        file_str = str(file_path)

        # Check exclude patterns
        for pattern in self.config.exclude_patterns:
            if file_path.match(pattern):
                return False

        # Check include patterns
        for pattern in self.config.include_patterns:
            if file_path.match(pattern):
                return True

        return False

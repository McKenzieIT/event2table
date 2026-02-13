#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Audit Skill Setup Script

Generates all files for the code-audit skill.
"""

import os
from pathlib import Path
from typing import List, Dict

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills" / "code-audit"

# File templates
FILES_TO_CREATE: Dict[str, str] = {
    # Core module
    "core/__init__.py": "",
    "core/base_detector.py": '''"""
Base Detector Module

Defines the abstract base class for all code audit detectors.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


class IssueCategory(Enum):
    """Issue categories"""
    COMPLIANCE = "compliance"
    SECURITY = "security"
    QUALITY = "quality"
    ARCHITECTURE = "architecture"
    TESTING = "testing"


@dataclass
class Issue:
    """Represents a code issue found by a detector"""

    file_path: str
    line_number: int
    severity: Severity
    category: IssueCategory
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    rule_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary for serialization"""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "severity": self.severity.name,
            "category": self.category.value,
            "message": self.message,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "rule_id": self.rule_id,
            "metadata": self.metadata
        }

    def __str__(self) -> str:
        """String representation of the issue"""
        return f"{self.file_path}:{self.line_number} [{self.severity.name}] {self.message}"


class BaseDetector(ABC):
    """Abstract base class for all code audit detectors"""

    def __init__(self):
        """Initialize detector with default configuration"""
        self.enabled = True
        self.config = {}

    @abstractmethod
    def detect(self, file_path: Path) -> List[Issue]:
        """
        Detect issues in the given file

        Args:
            file_path: Path to the file to analyze

        Returns:
            List of issues found
        """
        raise NotImplementedError("Detector must implement detect() method")

    def is_applicable(self, file_path: Path) -> bool:
        """
        Check if this detector is applicable to the given file

        Args:
            file_path: Path to check

        Returns:
            True if detector should analyze this file
        """
        return True

    def get_rule_id(self) -> str:
        """Get the unique rule ID for this detector"""
        return self.__class__.__name__

    def configure(self, **kwargs):
        """
        Configure detector with custom settings

        Args:
            **kwargs: Configuration options
        """
        self.config.update(kwargs)
''',
    "core/config.py": '''"""
Configuration Module

Manages code audit configuration.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import json


@dataclass
class AuditConfig:
    """Configuration for code audit"""

    # Project settings
    project_root: Path = field(default_factory=lambda: Path.cwd())

    # Detector enable/disable flags
    enable_game_gid_check: bool = True
    enable_api_contract_check: bool = True
    enable_tdd_check: bool = True
    enable_security_checks: bool = True
    enable_quality_checks: bool = True
    enable_architecture_checks: bool = True
    enable_testing_checks: bool = True

    # Quality thresholds
    max_complexity: int = 10
    max_duplication_lines: int = 100
    min_test_coverage: float = 80.0

    # File patterns to include/exclude
    include_patterns: List[str] = field(default_factory=lambda: ["**/*.py", "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["**/node_modules/**", "**/venv/**", "**/.venv/**", "**/dist/**", "**/build/**"])

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path(".claude/skills/code-audit/output/reports"))
    cache_dir: Path = field(default_factory=lambda: Path(".claude/skills/code-audit/output/cache"))

    # Report formats
    enable_markdown_report: bool = True
    enable_json_report: bool = True
    enable_console_report: bool = True


class ConfigManager:
    """Manages audit configuration"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager

        Args:
            config_path: Path to config file (default: .audit-config.json)
        """
        self.config_path = config_path or Path(".audit-config.json")
        self._config = None

    def get_config(self) -> AuditConfig:
        """
        Get configuration (load from file or create default)

        Returns:
            AuditConfig instance
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def load_config(self) -> AuditConfig:
        """
        Load configuration from file

        Returns:
            AuditConfig instance
        """
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                # Convert project_root to Path
                if 'project_root' in data:
                    data['project_root'] = Path(data['project_root'])
                if 'output_dir' in data:
                    data['output_dir'] = Path(data['output_dir'])
                if 'cache_dir' in data:
                    data['cache_dir'] = Path(data['cache_dir'])
                return AuditConfig(**data)
        return AuditConfig()

    def save_config(self, config: AuditConfig):
        """
        Save configuration to file

        Args:
            config: Configuration to save
        """
        data = {
            'project_root': str(config.project_root),
            'enable_game_gid_check': config.enable_game_gid_check,
            'enable_api_contract_check': config.enable_api_contract_check,
            'enable_tdd_check': config.enable_tdd_check,
            'enable_security_checks': config.enable_security_checks,
            'enable_quality_checks': config.enable_quality_checks,
            'enable_architecture_checks': config.enable_architecture_checks,
            'enable_testing_checks': config.enable_testing_checks,
            'max_complexity': config.max_complexity,
            'max_duplication_lines': config.max_duplication_lines,
            'min_test_coverage': config.min_test_coverage,
            'include_patterns': config.include_patterns,
            'exclude_patterns': config.exclude_patterns,
            'output_dir': str(config.output_dir),
            'cache_dir': str(config.cache_dir),
            'enable_markdown_report': config.enable_markdown_report,
            'enable_json_report': config.enable_json_report,
            'enable_console_report': config.enable_console_report
        }

        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)

    def reset_config(self):
        """Reset configuration to defaults"""
        if self.config_path.exists():
            self.config_path.unlink()
        self._config = AuditConfig()
''',
    "core/runner.py": '''"""
Audit Runner Module

Main orchestrator for running code audits.
"""

from pathlib import Path
from typing import List, Optional
from .base_detector import Issue, BaseDetector
from .config import AuditConfig


class AuditRunner:
    """Main audit runner"""

    def __init__(self, config: Optional[AuditConfig] = None):
        """
        Initialize audit runner

        Args:
            config: Audit configuration
        """
        self.config = config or AuditConfig()
        self.detectors: List[BaseDetector] = []

    def add_detector(self, detector: BaseDetector):
        """
        Add a detector to the runner

        Args:
            detector: Detector instance
        """
        self.detectors.append(detector)

    def run_audit(self, target_path: str) -> List[Issue]:
        """
        Run audit on target path

        Args:
            target_path: Path to audit (file or directory)

        Returns:
            List of all issues found
        """
        target = Path(target_path)
        all_issues = []

        # Collect files to audit
        files_to_audit = self._collect_files(target)

        # Run each detector on each file
        for detector in self.detectors:
            if not detector.enabled:
                continue

            for file_path in files_to_audit:
                if detector.is_applicable(file_path):
                    try:
                        issues = detector.detect(file_path)
                        all_issues.extend(issues)
                    except Exception as e:
                        # Log error but continue
                        print(f"Error running {detector.__class__.__name__} on {file_path}: {e}")

        return all_issues

    def _collect_files(self, target: Path) -> List[Path]:
        """
        Collect files to audit based on config patterns

        Args:
            target: Target path

        Returns:
            List of file paths to audit
        """
        files = []

        if target.is_file():
            return [target]

        # Recursively collect files
        for file_path in target.rglob("*"):
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
''',
}


def create_files():
    """Create all files for code-audit skill"""
    print(f"Creating code-audit skill files in: {BASE_DIR}")

    for file_path, content in FILES_TO_CREATE.items():
        full_path = BASE_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w') as f:
            f.write(content)

        print(f"✓ Created: {file_path}")

    print(f"\n✅ Successfully created {len(FILES_TO_CREATE)} files")


if __name__ == "__main__":
    create_files()

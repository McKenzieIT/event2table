"""
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

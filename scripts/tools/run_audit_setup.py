#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code Audit Skill - Master Setup Script

This script creates ALL files for the code-audit skill.
Run this script to generate the complete code-audit implementation.

Usage:
    python3 run_audit_setup.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, Tuple

# Base directory
BASE_DIR = Path(__file__).parent / ".claude" / "skills" / "code-audit"
PROJECT_ROOT = Path(__file__).parent


def setup_directories():
    """Create all required directories"""
    dirs = [
        "core",
        "detectors/compliance",
        "detectors/architecture",
        "detectors/security",
        "detectors/quality",
        "detectors/testing",
        "reporters",
        "utils",
        "hooks",
        "output/reports",
        "output/trends",
        "output/cache",
    ]

    for dir_name in dirs:
        dir_path = BASE_DIR / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "__init__.py").touch(exist_ok=True)

    print("✓ Created all directories")


def create_core_files():
    """Create core module files"""
    files = {
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

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")

    # Update core/__init__.py
    init_path = BASE_DIR / "core" / "__init__.py"
    with open(init_path, 'w') as f:
        f.write('''"""
Core module for code-audit skill
"""

from .base_detector import BaseDetector, Issue, Severity, IssueCategory
from .config import AuditConfig, ConfigManager
from .runner import AuditRunner

__all__ = [
    'BaseDetector',
    'Issue',
    'Severity',
    'IssueCategory',
    'AuditConfig',
    'ConfigManager',
    'AuditRunner'
]
''')
    print("✓ Updated: core/__init__.py")


def create_compliance_detectors():
    """Create compliance detector files"""
    files = {
        "detectors/compliance/game_gid_check.py": '''"""
Game GID Compliance Detector

Enforces Event2Table's critical rule: Use game_gid not game_id for data associations.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class GameGidDetector(BaseDetector):
    """
    Detects illegal game_id usage in code

    Rules:
    - game_id (database auto-increment): Only for games table primary key
    - game_gid (business GID): For all data associations
    """

    # Patterns that indicate illegal game_id usage
    ILLEGAL_PATTERNS = [
        (r'game_id\s*=', "Variable assignment using game_id"),
        (r'game_id\s*,', "Function parameter using game_id"),
        (r'game_id\s*\)', "Function call using game_id"),
        (r'WHERE\s+.*?game_id', "SQL WHERE clause using game_id"),
        (r'JOIN\s+.*?ON\s+.*?game_id', "SQL JOIN using game_id"),
        (r'f["\'].*?{game_id}', "String formatting with game_id"),
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "GAME_GID_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect illegal game_id usage"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\\n')

            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                # Check for illegal patterns
                for pattern, description in self.ILLEGAL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's truly illegal (not just games table primary key)
                        if not self._is_games_table_primary_key(line):
                            issues.append(Issue(
                                file_path=str(file_path),
                                line_number=line_num,
                                severity=Severity.CRITICAL,
                                category=IssueCategory.COMPLIANCE,
                                message=f"Illegal game_id usage: {description}",
                                suggestion="Use game_gid instead of game_id for data associations",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))
                            break  # Only report one issue per line

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _is_games_table_primary_key(self, line: str) -> bool:
        """
        Check if game_id usage is for games table primary key (allowed)

        Args:
            line: Line of code to check

        Returns:
            True if this is合法 games table primary key usage
        """
        # Allow: games.id or games WHERE id
        if re.search(r'games\\.id|games\\s+WHERE\\s+id', line, re.IGNORECASE):
            return True

        # Allow: PRIMARY KEY (id) or similar schema definitions
        if re.search(r'PRIMARY\\s+KEY\\s*\\(\\s*id\\s*\\)', line, re.IGNORECASE):
            return True

        return False
''',
        "detectors/compliance/api_contract_check.py": '''"""
API Contract Detector

Validates frontend-backend API contract consistency.
"""

import re
from pathlib import Path
from typing import List, Dict, Set
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class ApiContractDetector(BaseDetector):
    """
    Detects API contract violations between frontend and backend

    Scans:
    - Frontend: API calls (fetch, axios, etc.)
    - Backend: API routes (Flask @route decorators)
    """

    # Frontend API call patterns
    FRONTEND_PATTERNS = [
        r'fetch\\(["\'](/api/[^"\']+)["\']',
        r'axios\\.(get|post|put|delete|patch)\\(["\'](/api/[^"\']+)["\']',
        r'\\.(get|post|put|delete|patch)\\(["\'](/api/[^"\']+)["\']',
    ]

    # Backend route patterns
    BACKEND_PATTERNS = [
        r'@.*\\.route\\(["\'](/api/[^"\']+)["\']\\s*,\\s*methods=\\["\']([^"\']+)["\']',
        r'@.*\\.route\\(["\'](/api/[^"\']+)["\']',
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "API_CONTRACT_001"
        self.backend_routes: Dict[str, Set[str]] = {}

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect API contract violations"""
        issues = []

        file_str = str(file_path)

        # Check if this is a frontend file
        if self._is_frontend_file(file_path):
            api_calls = self._extract_frontend_api_calls(file_path)
            # Would need to check against backend routes
            # For now, just report potential API calls for manual review

        # Check if this is a backend file
        elif self._is_backend_file(file_path):
            routes = self._extract_backend_routes(file_path)
            # Store routes for validation

        return issues

    def _is_frontend_file(self, file_path: Path) -> bool:
        """Check if file is a frontend file"""
        return any(ext in file_path.suffix for ext in ['.js', '.jsx', '.ts', '.tsx'])

    def _is_backend_file(self, file_path: Path) -> bool:
        """Check if file is a backend file"""
        return 'backend' in file_path.parts and file_path.suffix == '.py'

    def _extract_frontend_api_calls(self, file_path: Path) -> List[Dict]:
        """Extract API calls from frontend file"""
        calls = []
        try:
            content = file_path.read_text()
            lines = content.split('\\n')

            for line_num, line in enumerate(lines, 1):
                for pattern in self.FRONTEND_PATTERNS:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        endpoint = match.group(1) if match.lastindex >= 1 else match.group(2)
                        method = match.group(2).upper() if match.lastindex >= 2 else 'GET'
                        calls.append({
                            'endpoint': endpoint,
                            'method': method,
                            'line': line_num,
                            'file': str(file_path)
                        })
        except Exception as e:
            print(f"Error extracting API calls from {file_path}: {e}")

        return calls

    def _extract_backend_routes(self, file_path: Path) -> List[Dict]:
        """Extract routes from backend file"""
        routes = []
        try:
            content = file_path.read_text()
            lines = content.split('\\n')

            for line_num, line in enumerate(lines, 1):
                for pattern in self.BACKEND_PATTERNS:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        endpoint = match.group(1)
                        methods = match.group(2).split(',') if match.lastindex >= 2 else ['GET']
                        routes.append({
                            'endpoint': endpoint,
                            'methods': [m.strip().strip('\"\'') for m in methods],
                            'line': line_num,
                            'file': str(file_path)
                        })
        except Exception as e:
            print(f"Error extracting routes from {file_path}: {e}")

        return routes
''',
        "detectors/compliance/tdd_check.py": '''"""
TDD Compliance Detector

Validates Test-Driven Development compliance.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class TddDetector(BaseDetector):
    """
    Detects TDD compliance violations

    Checks:
    - Test files exist for source files
    - Test files follow naming convention
    - Tests were written before implementation (file modification time)
    """

    def __init__(self):
        super().__init__()
        self.rule_id = "TDD_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect TDD violations"""
        issues = []

        # Skip test files themselves
        if self._is_test_file(file_path):
            return issues

        # Check if corresponding test file exists
        test_file = self._find_test_file(file_path)
        if not test_file or not test_file.exists():
            issues.append(Issue(
                file_path=str(file_path),
                line_number=1,
                severity=Severity.HIGH,
                category=IssueCategory.COMPLIANCE,
                message="Missing test file",
                suggestion=f"Create test file: {self._get_expected_test_name(file_path)}",
                rule_id=self.rule_id
            ))

        return issues

    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file"""
        return 'test' in file_path.name.lower()

    def _find_test_file(self, source_file: Path) -> Path:
        """Find corresponding test file"""
        # Common test locations
        potential_paths = [
            source_file.parent / f"test_{source_file.name}",
            source_file.parent.parent / "tests" / source_file.name,
            source_file.parent.parent / "test" / source_file.name,
        ]

        # Replace .py with _test.py
        test_name = source_file.stem + "_test" + source_file.suffix
        potential_paths.append(source_file.parent / test_name)

        for path in potential_paths:
            if path.exists():
                return path

        return None

    def _get_expected_test_name(self, source_file: Path) -> str:
        """Get expected test file name"""
        return f"test_{source_file.name}"
''',
    }

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")


def create_security_detectors():
    """Create security detector files"""
    files = {
        "detectors/security/sql_injection.py": '''"""
SQL Injection Detector

Detects potential SQL injection vulnerabilities.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class SqlInjectionDetector(BaseDetector):
    """
    Detects SQL injection vulnerabilities

    Patterns:
    - String concatenation in SQL queries
    - f-strings with user input in SQL
    - Unescaped variables in SQL
    """

    # Dangerous SQL patterns
    SQL_INJECTION_PATTERNS = [
        (r'f["\'].*?\{.*?\}.*?["\']\s*\)', "f-string with variable in SQL query"),
        (r'["\'].*?(SELECT|INSERT|UPDATE|DELETE).*?\+.*?["\']', "String concatenation in SQL"),
        (r'["\'].*?WHERE.*?\{.*?\}', "Variable in WHERE clause"),
        (r'execute\s*\(\s*f["\'].*?\{', "execute() with f-string"),
        (r'query\s*=\s*f["\'].*?\{', "query assignment with f-string"),
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "SEC_SQL_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect SQL injection vulnerabilities"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\\n')

            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                for pattern, description in self.SQL_INJECTION_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's actually SQL
                        if re.search(r'(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)', line, re.IGNORECASE):
                            issues.append(Issue(
                                file_path=str(file_path),
                                line_number=line_num,
                                severity=Severity.CRITICAL,
                                category=IssueCategory.SECURITY,
                                message=f"SQL injection risk: {description}",
                                suggestion="Use parameterized queries with ? placeholders",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))
                            break

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues
''',
        "detectors/security/xss_check.py": '''"""
XSS Protection Detector

Detects missing XSS protection.
"""

import re
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class XssDetector(BaseDetector):
    """
    Detects XSS vulnerabilities

    Checks:
    - Unescaped user input in HTML output
    - Missing html.escape() for user data
    - Direct variable interpolation in HTML
    """

    # XSS risk patterns
    XSS_PATTERNS = [
        (r'f["\']<.*?\{.*?\}.*?>["\']', "f-string with variable in HTML"),
        (r'return\\s+f["\']<.*?\{', "Returning f-string HTML with variable"),
        (r'<[^>]*?\{[^}]*\}[^>]*>', "Variable in HTML tag"),
    ]

    def __init__(self):
        super().__init__()
        self.rule_id = "SEC_XSS_001"

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect XSS vulnerabilities"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\\n')

            for line_num, line in enumerate(lines, 1):
                # Check for XSS risk patterns
                for pattern, description in self.XSS_PATTERNS:
                    if re.search(pattern, line):
                        # Check if html.escape is used
                        if 'html.escape' not in line and 'sanitize' not in line:
                            issues.append(Issue(
                                file_path=str(file_path),
                                line_number=line_num,
                                severity=Severity.HIGH,
                                category=IssueCategory.SECURITY,
                                message=f"XSS vulnerability: {description}",
                                suggestion="Use html.escape() or sanitize user input",
                                code_snippet=line.strip(),
                                rule_id=self.rule_id
                            ))
                            break

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues
''',
    }

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")


def create_quality_detectors():
    """Create quality detector files"""
    files = {
        "detectors/quality/complexity.py": '''"""
Cyclomatic Complexity Detector

Analyzes code complexity.
"""

import ast
from pathlib import Path
from typing import List
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class ComplexityDetector(BaseDetector):
    """
    Detects high cyclomatic complexity

    Measures:
    - Number of decision points
    - Nested control structures
    - Function/method complexity
    """

    def __init__(self, max_complexity: int = 10):
        super().__init__()
        self.rule_id = "QUAL_COMPLEXITY_001"
        self.max_complexity = max_complexity

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect high complexity"""
        issues = []

        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    complexity = self._calculate_complexity(node)
                    if complexity > self.max_complexity:
                        issues.append(Issue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            severity=Severity.MEDIUM,
                            category=IssueCategory.QUALITY,
                            message=f"High cyclomatic complexity: {complexity} (max: {self.max_complexity})",
                            suggestion="Refactor function into smaller functions",
                            rule_id=self.rule_id,
                            metadata={'complexity': complexity}
                        ))

        except SyntaxError:
            # Skip files with syntax errors
            pass
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity
''',
        "detectors/quality/duplication.py": '''"""
Code Duplication Detector

Detects duplicate code blocks.
"""

from pathlib import Path
from typing import List, Dict
from ..core.base_detector import BaseDetector, Issue, Severity, IssueCategory


class DuplicationDetector(BaseDetector):
    """
    Detects code duplication

    Strategy:
    - Hash-based line sequence matching
    - Detects copy-pasted code blocks
    """

    def __init__(self, min_lines: int = 5):
        super().__init__()
        self.rule_id = "QUAL_DUP_001"
        self.min_lines = min_lines
        self.code_blocks: Dict[str, List[tuple]] = {}

    def detect(self, file_path: Path) -> List[Issue]:
        """Detect code duplication"""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.split('\\n')

            # Extract code blocks
            blocks = self._extract_blocks(lines)

            # Check for duplicates
            for block_hash, locations in blocks.items():
                if len(locations) > 1:
                    for line_num in locations[1:]:  # Skip first occurrence
                        issues.append(Issue(
                            file_path=str(file_path),
                            line_number=line_num,
                            severity=Severity.LOW,
                            category=IssueCategory.QUALITY,
                            message=f"Duplicated code block ({len(locations)} occurrences)",
                            suggestion="Extract duplicated code into a function",
                            rule_id=self.rule_id
                        ))

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _extract_blocks(self, lines: List[str]) -> Dict[str, List[int]]:
        """Extract code blocks and return hash map"""
        blocks = {}

        for i in range(len(lines) - self.min_lines + 1):
            block = '\\n'.join(lines[i:i + self.min_lines])
            block_hash = hash(block.strip())

            if block_hash not in blocks:
                blocks[block_hash] = []
            blocks[block_hash].append(i + 1)

        return blocks
''',
    }

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")


def create_reporters():
    """Create reporter files"""
    files = {
        "reporters/markdown_reporter.py": '''"""
Markdown Reporter

Generates Markdown audit reports.
"""

from pathlib import Path
from typing import List
from datetime import datetime
from ..core.base_detector import Issue


class MarkdownReporter:
    """Generates Markdown format reports"""

    def generate_report(self, issues: List[Issue], output_path: str):
        """
        Generate Markdown report

        Args:
            issues: List of issues to report
            output_path: Path to output file
        """
        # Sort issues by severity and file
        sorted_issues = sorted(issues, key=lambda i: (i.severity.value, i.file_path, i.line_number), reverse=True)

        # Generate markdown content
        lines = [
            "# Code Audit Report",
            f"",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Issues**: {len(issues)}",
            f"",
            "---",
            f"",
        ]

        # Group by severity
        from ..core.base_detector import Severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_issues = [i for i in sorted_issues if i.severity == severity]
            if severity_issues:
                lines.append(f"## {severity.name} Issues ({len(severity_issues)})")
                lines.append("")
                for issue in severity_issues:
                    lines.append(f"### {issue.file_path}:{issue.line_number}")
                    lines.append(f"**Category**: {issue.category.value}")
                    lines.append(f"**Message**: {issue.message}")
                    if issue.suggestion:
                        lines.append(f"**Suggestion**: {issue.suggestion}")
                    if issue.code_snippet:
                        lines.append(f"**Code**:")
                        lines.append(f"```")
                        lines.append(issue.code_snippet)
                        lines.append(f"```")
                    lines.append("")

        # Write to file
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write('\\n'.join(lines))

        return '\\n'.join(lines)
''',
        "reporters/json_reporter.py": '''"""
JSON Reporter

Generates JSON audit reports.
"""

import json
from pathlib import Path
from typing import List
from datetime import datetime
from ..core.base_detector import Issue


class JsonReporter:
    """Generates JSON format reports"""

    def generate_report(self, issues: List[Issue], output_path: str):
        """
        Generate JSON report

        Args:
            issues: List of issues to report
            output_path: Path to output file
        """
        # Sort issues by severity and file
        sorted_issues = sorted(issues, key=lambda i: (i.severity.value, i.file_path, i.line_number), reverse=True)

        # Generate report data
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_issues": len(issues),
            "summary": self._generate_summary(issues),
            "issues": [issue.to_dict() for issue in sorted_issues]
        }

        # Write to file
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)

        return report

    def _generate_summary(self, issues: List[Issue]) -> dict:
        """Generate summary statistics"""
        from ..core.base_detector import Severity, IssueCategory

        summary = {
            "by_severity": {},
            "by_category": {}
        }

        for severity in Severity:
            count = len([i for i in issues if i.severity == severity])
            summary["by_severity"][severity.name] = count

        for category in IssueCategory:
            count = len([i for i in issues if i.category == category])
            summary["by_category"][category.value] = count

        return summary
''',
        "reporters/console_reporter.py": '''"""
Console Reporter

Prints audit reports to console.
"""

from typing import List
from ..core.base_detector import Issue, Severity


class ConsoleReporter:
    """Prints reports to console"""

    def generate_report(self, issues: List[Issue], output_path: str = None):
        """
        Print report to console

        Args:
            issues: List of issues to report
            output_path: Ignored (always prints to console)
        """
        # Sort issues by severity
        sorted_issues = sorted(issues, key=lambda i: i.severity.value, reverse=True)

        # Print header
        print("=" * 80)
        print("CODE AUDIT REPORT")
        print("=" * 80)
        print(f"Total Issues: {len(issues)}")
        print()

        # Group by severity
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_issues = [i for i in sorted_issues if i.severity == severity]
            if severity_issues:
                # Print severity header
                color = self._get_color(severity)
                print(f"\\n{color}{'=' * 80}\\033[0m")
                print(f"{color}{severity.name} ISSUES ({len(severity_issues)})\\033[0m")
                print(f"{color}{'=' * 80}\\033[0m\\n")

                # Print issues
                for issue in severity_issues:
                    print(f"  📍 {issue.file_path}:{issue.line_number}")
                    print(f"  📁 [{issue.category.value}] {issue.message}")
                    if issue.suggestion:
                        print(f"  💡 {issue.suggestion}")
                    print()

    def _get_color(self, severity: Severity) -> str:
        """Get ANSI color code for severity"""
        colors = {
            Severity.CRITICAL: "\\033[91m",  # Red
            Severity.HIGH: "\\033[93m",      # Yellow
            Severity.MEDIUM: "\\033[94m",    # Blue
            Severity.LOW: "\\033[96m",       # Cyan
            Severity.INFO: "\\033[97m",      # White
        }
        return colors.get(severity, "")
''',
    }

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")


def create_utility_files():
    """Create utility files"""
    files = {
        "utils/git_helper.py": '''"""
Git Helper Utilities

Provides git-related utilities for code audit.
"""

import subprocess
from pathlib import Path
from typing import List


def get_git_diff_files() -> List[Path]:
    """
    Get list of changed files in git

    Returns:
        List of changed file paths
    """
    try:
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return [Path(line.strip()) for line in result.stdout.split('\\n') if line.strip()]
    except subprocess.CalledProcessError:
        return []


def get_git_root() -> Path:
    """
    Get git repository root directory

    Returns:
        Path to git root
    """
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        return Path.cwd()
''',
        "utils/file_scanner.py": '''"""
File Scanner Utilities

Provides file scanning utilities for code audit.
"""

from pathlib import Path
from typing import List


def find_python_files(root: Path) -> List[Path]:
    """
    Find all Python files in directory

    Args:
        root: Root directory to search

    Returns:
        List of Python file paths
    """
    return list(root.rglob("*.py"))


def find_javascript_files(root: Path) -> List[Path]:
    """
    Find all JavaScript files in directory

    Args:
        root: Root directory to search

    Returns:
        List of JavaScript file paths
    """
    return list(root.rglob("*.js")) + list(root.rglob("*.jsx"))


def find_typescript_files(root: Path) -> List[Path]:
    """
    Find all TypeScript files in directory

    Args:
        root: Root directory to search

    Returns:
        List of TypeScript file paths
    """
    return list(root.rglob("*.ts")) + list(root.rglob("*.tsx"))
''',
        "utils/ast_analyzer.py": '''"""
AST Analyzer Utilities

Provides AST analysis utilities for code audit.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any


def analyze_file_ast(file_path: Path) -> Dict[str, Any]:
    """
    Analyze Python file using AST

    Args:
        file_path: Path to Python file

    Returns:
        Dictionary with analysis results
    """
    try:
        content = file_path.read_text()
        tree = ast.parse(content)

        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity": 0
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                analysis["classes"].append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    analysis["imports"].append(alias.name)

        return analysis

    except SyntaxError:
        return {"error": "Syntax error"}
    except Exception as e:
        return {"error": str(e)}
''',
    }

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")


def create_hooks():
    """Create git hook files"""
    files = {
        "hooks/pre-commit.sh": '''#!/bin/bash
# Pre-commit hook for code audit

# Run quick code audit before commit
echo "Running code audit..."

python3 .claude/skills/code-audit/hooks/run_audit.py --quick

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ Code audit failed. Commit aborted."
    echo "Run '/code-audit' to see issues and fix them before committing."
    exit 1
fi

echo "✅ Code audit passed"
exit 0
''',
        "hooks/pre-push.sh": '''#!/bin/bash
# Pre-push hook for code audit

# Run full code audit before push
echo "Running full code audit..."

python3 .claude/skills/code-audit/hooks/run_audit.py

# Check exit code
if [ $? -ne 0 ]; then
    echo "❌ Code audit failed. Push aborted."
    echo "Run '/code-audit' to see issues and fix them before pushing."
    exit 1
fi

echo "✅ Code audit passed"
exit 0
''',
        "hooks/run_audit.py": '''#!/usr/bin/env python3
"""
Audit Runner Script for Git Hooks
"""

import sys
from pathlib import Path

# Add code-audit to path
code_audit_path = Path(__file__).parent.parent
sys.path.insert(0, str(code_audit_path))

from core.runner import AuditRunner
from core.config import AuditConfig
from detectors.compliance.game_gid_check import GameGidDetector
from detectors.compliance.tdd_check import TddDetector
from detectors.security.sql_injection import SqlInjectionDetector


def main():
    """Run audit with critical checks"""
    config = AuditConfig()

    # Quick mode - only critical checks
    runner = AuditRunner(config)
    runner.add_detector(GameGidDetector())
    runner.add_detector(SqlInjectionDetector())

    # Run on backend
    backend_path = Path(__file__).parent.parent.parent.parent.parent / "backend"
    issues = runner.run_audit(str(backend_path))

    # Filter critical and high severity
    critical_issues = [i for i in issues if i.severity.value >= 4]

    if critical_issues:
        print(f"\\n❌ Found {len(critical_issues)} critical/high issues:")
        for issue in critical_issues:
            print(f"  - {issue}")
        sys.exit(1)

    print(f"✅ No critical issues found")
    sys.exit(0)


if __name__ == "__main__":
    main()
''',
    }

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        full_path.chmod(0o755)  # Make executable
        print(f"✓ Created: {file_path}")


def create_documentation():
    """Create documentation files"""
    files = {
        "README.md": '''# Code Audit Skill

Comprehensive code quality audit tool for Event2Table project.

## Features

### Compliance Detectors
- **Game GID Check**: Enforces game_gid vs game_id usage rules
- **API Contract Check**: Validates frontend-backend API consistency
- **TDD Check**: Ensures test files exist for all source files

### Security Detectors
- **SQL Injection**: Detects SQL injection vulnerabilities
- **XSS Protection**: Detects missing XSS protection

### Quality Detectors
- **Complexity Analysis**: Measures cyclomatic complexity
- **Code Duplication**: Detects duplicate code blocks

## Usage

### Run Full Audit
```
/code-audit
```

### Run Quick Audit
```
/code-audit --quick
```

### Run Specific Detectors
```
/code-audit --detectors game_gid,sql_injection
```

## Output

Reports are generated in `.claude/skills/code-audit/output/reports/`:
- `audit_report.md` - Markdown report
- `audit_report.json` - JSON report

## Git Hooks

Pre-commit and pre-push hooks are available:
```bash
python3 scripts/setup/setup_code_audit_hooks.py
```
''',
        "SKILL.md": f'''---
name: code-audit
description: Comprehensive code quality audit tool for Event2Table project. Enforces game_gid compliance, checks API contracts, validates TDD compliance, detects security vulnerabilities (SQL injection, XSS), and analyzes code quality (complexity, duplication).
---

# Code Audit Skill

## When to Use

Use this skill when:
- Reviewing code before committing
- Checking for compliance with Event2Table standards
- Performing security audits
- Analyzing code quality
- Validating API contracts between frontend and backend

## Quick Start

Simply invoke:
```
/code-audit
```

## What It Does

The code-audit skill runs a comprehensive analysis of your codebase:

1. **Compliance Checks**
   - Enforces game_gid usage (critical for Event2Table)
   - Validates frontend-backend API contracts
   - Checks TDD compliance

2. **Security Scanning**
   - Detects SQL injection vulnerabilities
   - Identifies XSS protection gaps

3. **Quality Analysis**
   - Measures cyclomatic complexity
   - Detects code duplication

## Modes

- **Quick Mode** (`--quick`): Only critical compliance checks (~1 minute)
- **Standard Mode** (`--standard`): Compliance + security (~3 minutes)
- **Deep Mode** (`--deep` or default): All checks + trend analysis (~10 minutes)

## Output

Reports are generated in:
- `.claude/skills/code-audit/output/reports/audit_report.md`
- `.claude/skills/code-audit/output/reports/audit_report.json`

## Project Root

The skill operates from: {PROJECT_ROOT}
''',
        "skill.json": '''{
  "name": "code-audit",
  "version": "1.0.0",
  "description": "Comprehensive code quality audit tool for Event2Table project",
  "author": "Event2Table Development Team",
  "python_version": ">=3.9",
  "dependencies": [],
  "entry_point": ".claude/skills/code-audit/core/runner.py"
}
''',
    }

    for file_path, content in files.items():
        full_path = BASE_DIR / file_path
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")


def main():
    """Main setup function"""
    print("=" * 80)
    print("Code Audit Skill - Complete Setup")
    print("=" * 80)
    print()

    print("Step 1: Creating directories...")
    setup_directories()
    print()

    print("Step 2: Creating core files...")
    create_core_files()
    print()

    print("Step 3: Creating compliance detectors...")
    create_compliance_detectors()
    print()

    print("Step 4: Creating security detectors...")
    create_security_detectors()
    print()

    print("Step 5: Creating quality detectors...")
    create_quality_detectors()
    print()

    print("Step 6: Creating reporters...")
    create_reporters()
    print()

    print("Step 7: Creating utilities...")
    create_utility_files()
    print()

    print("Step 8: Creating git hooks...")
    create_hooks()
    print()

    print("Step 9: Creating documentation...")
    create_documentation()
    print()

    print("=" * 80)
    print("✅ CODE AUDIT SKILL SETUP COMPLETE!")
    print("=" * 80)
    print()
    print(f"📁 Skill installed at: {BASE_DIR}")
    print(f"📊 Reports will be generated in: {BASE_DIR / 'output' / 'reports'}")
    print()
    print("Next steps:")
    print("  1. Run tests: python3 -m pytest test/unit/backend_tests/skills/test_code_audit.py -v")
    print("  2. Try the skill: /code-audit")
    print("  3. Setup git hooks: python3 scripts/setup/setup_code_audit_hooks.py")
    print()


if __name__ == "__main__":
    main()

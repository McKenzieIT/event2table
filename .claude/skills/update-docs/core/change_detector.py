"""
Change Detection Engine.

Detects and categorizes code changes in the project.

Refactored to use Strategy Pattern for extensibility.
"""
from typing import List, Dict, Any, Optional, Protocol
from pathlib import Path
from enum import Enum


class ChangeType(Enum):
    """Types of code changes."""
    API_CHANGE = "api_change"
    SERVICE_CHANGE = "service_change"
    REPOSITORY_CHANGE = "repository_change"
    FRONTEND_FEATURE = "frontend_feature"
    SCHEMA_CHANGE = "schema_change"
    CONFIG_CHANGE = "config_change"
    TEST_CHANGE = "test_change"
    OTHER = "other"


class Change:
    """Represents a single code change."""

    def __init__(
        self,
        file_path: str,
        change_type: ChangeType,
        details: Optional[Dict[str, Any]] = None
    ):
        self.file_path = file_path
        self.change_type = change_type
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "change_type": self.change_type.value,
            "details": self.details
        }


class ChangeRule(Protocol):
    """Protocol for change detection rules."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        """
        Check if this rule matches the file path.
        
        Args:
            file_path: The file path to check
            
        Returns:
            The ChangeType if matched, None otherwise
        """
        ...

    def priority(self) -> int:
        """
        Return priority for rule matching (higher = checked first).
        
        Returns:
            Priority value (default: 0)
        """
        return 0


class APIChangeRule:
    """Detects API route changes."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        if "backend/api/routes/" in file_path:
            return ChangeType.API_CHANGE
        return None
    
    def priority(self) -> int:
        return 10  # High priority: specific path


class ServiceChangeRule:
    """Detects service layer changes."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        if "backend/services/" in file_path:
            return ChangeType.SERVICE_CHANGE
        return None
    
    def priority(self) -> int:
        return 9


class RepositoryChangeRule:
    """Detects repository layer changes."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        if "backend/models/repositories/" in file_path:
            return ChangeType.REPOSITORY_CHANGE
        return None
    
    def priority(self) -> int:
        return 8


class FrontendFeatureRule:
    """Detects frontend feature changes."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        if ("frontend/src/features/" in file_path or 
            "frontend/src/analytics/pages/" in file_path):
            return ChangeType.FRONTEND_FEATURE
        return None
    
    def priority(self) -> int:
        return 7


class SchemaChangeRule:
    """Detects schema changes."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        if "backend/models/schemas.py" in file_path or "schemas" in file_path:
            return ChangeType.SCHEMA_CHANGE
        return None
    
    def priority(self) -> int:
        return 6


class ConfigChangeRule:
    """Detects configuration changes."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        if "config/" in file_path:
            return ChangeType.CONFIG_CHANGE
        return None
    
    def priority(self) -> int:
        return 5


class TestChangeRule:
    """Detects test changes."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        if "test/" in file_path:
            return ChangeType.TEST_CHANGE
        return None
    
    def priority(self) -> int:
        return 4


class DefaultChangeRule:
    """Default rule for unmatched files."""
    
    def matches(self, file_path: str) -> Optional[ChangeType]:
        return ChangeType.OTHER
    
    def priority(self) -> int:
        return 0  # Lowest priority: always matches


class ChangeDetector:
    """Detects code changes using strategy pattern."""

    def __init__(
        self, 
        project_root: Optional[Path] = None,
        rules: Optional[List[ChangeRule]] = None
    ):
        """
        Initialize change detector.
        
        Args:
            project_root: Project root path
            rules: Optional list of ChangeRule objects (dependency injection)
        """
        self.project_root = project_root or Path.cwd()
        self.changes: List[Change] = []
        
        # Use injected rules or default rules
        if rules is None:
            self.rules = self._get_default_rules()
        else:
            # Sort by priority (highest first)
            self.rules = sorted(rules, key=lambda r: r.priority(), reverse=True)

    def _get_default_rules(self) -> List[ChangeRule]:
        """Get default change detection rules."""
        return [
            APIChangeRule(),
            ServiceChangeRule(),
            RepositoryChangeRule(),
            FrontendFeatureRule(),
            SchemaChangeRule(),
            ConfigChangeRule(),
            TestChangeRule(),
            DefaultChangeRule(),  # Must be last (lowest priority)
        ]

    def add_change(self, change: Change):
        """Add a change to the list."""
        self.changes.append(change)

    def categorize_change(self, file_path: str) -> ChangeType:
        """
        Categorize a file change by path using strategy pattern.
        
        Rules are checked in priority order (highest first).
        The first matching rule determines the change type.
        """
        for rule in self.rules:
            result = rule.matches(file_path)
            if result is not None:
                return result
        
        # Fallback (should never happen if DefaultChangeRule is present)
        return ChangeType.OTHER

    def detect_changes_from_files(self, files: List[str]) -> List[Change]:
        """Detect changes from a list of files."""
        changes = []
        for file_path in files:
            change_type = self.categorize_change(file_path)
            change = Change(
                file_path=file_path,
                change_type=change_type,
                details={"detected_at": str(Path.cwd())}
            )
            changes.append(change)
            self.add_change(change)
        return changes

    def get_summary(self) -> Dict[str, int]:
        """Get summary of changes."""
        summary = {}
        for change in self.changes:
            type_name = change.change_type.value
            summary[type_name] = summary.get(type_name, 0) + 1
        return summary

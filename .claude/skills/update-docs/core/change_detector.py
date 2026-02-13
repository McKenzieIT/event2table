"""
Change Detection Engine.

Detects and categorizes code changes in the project.
"""
from typing import List, Dict, Any, Optional
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


class ChangeDetector:
    """Detects code changes."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize change detector."""
        self.project_root = project_root or Path.cwd()
        self.changes: List[Change] = []

    def add_change(self, change: Change):
        """Add a change to the list."""
        self.changes.append(change)

    def categorize_change(self, file_path: str) -> ChangeType:
        """Categorize a file change by path."""
        # API changes
        if "backend/api/routes/" in file_path:
            return ChangeType.API_CHANGE

        # Service changes
        if "backend/services/" in file_path:
            return ChangeType.SERVICE_CHANGE

        # Repository changes
        if "backend/models/repositories/" in file_path:
            return ChangeType.REPOSITORY_CHANGE

        # Frontend features
        if "frontend/src/features/" in file_path or "frontend/src/analytics/pages/" in file_path:
            return ChangeType.FRONTEND_FEATURE

        # Schema changes
        if "backend/models/schemas.py" in file_path or "schemas" in file_path:
            return ChangeType.SCHEMA_CHANGE

        # Config changes
        if "config/" in file_path:
            return ChangeType.CONFIG_CHANGE

        # Test changes
        if "test/" in file_path:
            return ChangeType.TEST_CHANGE

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

"""
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
    def detect(self, file_path: str) -> List[Issue]:
        """
        Detect issues in the given file

        Args:
            file_path: Path to the file to analyze

        Returns:
            List of issues found
        """
        raise NotImplementedError("Detector must implement detect() method")

    def is_applicable(self, file_path: str) -> bool:
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

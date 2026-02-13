"""
Document Mapper.

Maps code changes to documentation files.
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class MappingRule:
    """Represents a mapping rule."""
    pattern: str
    target: str
    action: str
    doc_type: str = "guide"


class DocMapper:
    """Maps code changes to documentation."""

    def __init__(self):
        """Initialize document mapper."""
        self.rules: List[MappingRule] = []

    def add_rule(self, rule: MappingRule):
        """Add a mapping rule."""
        self.rules.append(rule)

    def load_default_rules(self):
        """Load default mapping rules."""
        default_rules = [
            MappingRule(
                pattern="backend/api/routes/",
                target="docs/api/",
                action="update_endpoint",
                doc_type="api"
            ),
            MappingRule(
                pattern="backend/services/",
                target="docs/development/backend-development.md",
                action="update_service",
                doc_type="guide"
            ),
            MappingRule(
                pattern="backend/models/repositories/",
                target="docs/development/backend-development.md",
                action="update_repository",
                doc_type="guide"
            ),
            MappingRule(
                pattern="frontend/src/features/",
                target="docs/development/frontend-development.md",
                action="update_feature",
                doc_type="guide"
            ),
            MappingRule(
                pattern="frontend/src/analytics/pages/",
                target="docs/development/frontend-development.md",
                action="update_page",
                doc_type="guide"
            ),
            MappingRule(
                pattern="backend/services/hql/",
                target="docs/hql/",
                action="update_hql",
                doc_type="technical"
            ),
        ]

        for rule in default_rules:
            self.add_rule(rule)

    def map(self, file_path: str) -> List[Dict[str, Any]]:
        """Map a file path to target documentation."""
        normalized_path = file_path.replace("\\", "/")
        results = []

        for rule in self.rules:
            if rule.pattern in normalized_path:
                result = {
                    "target": rule.target,
                    "action": rule.action,
                    "doc_type": rule.doc_type,
                    "source": file_path
                }
                results.append(result)

        return results

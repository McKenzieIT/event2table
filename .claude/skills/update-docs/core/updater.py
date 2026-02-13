"""
Document Updater.

Updates documentation based on code changes.
"""
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

from .change_detector import Change, ChangeDetector
from .doc_mapper import DocMapper


class DocumentUpdater:
    """Updates documentation."""

    def __init__(self, project_root: Path = None):
        """Initialize document updater."""
        self.project_root = project_root or Path.cwd()
        self.mapper = DocMapper()
        self.mapper.load_default_rules()

    def generate_update_summary(self, changes: List[Change]) -> Dict[str, Any]:
        """Generate update summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "changes_detected": len(changes),
            "changes_by_type": {},
            "docs_to_update": 0
        }

        for change in changes:
            type_name = change.change_type.value
            summary["changes_by_type"][type_name] = \
                summary["changes_by_type"].get(type_name, 0) + 1

        return summary

    def map_changes_to_docs(self, changes: List[Change]) -> List[Dict[str, Any]]:
        """Map changes to documentation."""
        mappings = []

        for change in changes:
            file_mappings = self.mapper.map(change.file_path)
            for mapping in file_mappings:
                mapping["change_type"] = change.change_type.value
                mappings.append(mapping)

        return mappings

    def create_update_plan(
        self,
        changes: List[Change]
    ) -> Dict[str, Any]:
        """Create document update plan."""
        mappings = self.map_changes_to_docs(changes)
        summary = self.generate_update_summary(changes)

        # Group by target document
        by_target = {}
        for mapping in mappings:
            target = mapping["target"]
            if target not in by_target:
                by_target[target] = []
            by_target[target].append(mapping)

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "update_plans": [
                {
                    "target": target,
                    "actions": [m["action"] for m in mappings],
                    "sources": [m["source"] for m in mappings],
                    "priority": 1
                }
                for target, mappings in by_target.items()
            ]
        }

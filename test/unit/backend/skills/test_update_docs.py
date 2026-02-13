"""
Test suite for update-docs skill.

Tests follow TDD principles:
1. RED: Write failing tests first
2. GREEN: Implement minimal code to pass
3. REFACTOR: Improve while keeping tests green
"""

import pytest
from pathlib import Path
import sys
from typing import Dict, List, Any

# Add skill path to sys.path
skill_path = Path(__file__).parent.parent.parent.parent / ".claude" / "skills" / "update-docs"
sys.path.insert(0, str(skill_path))

from core.change_detector import ChangeDetector, ChangeType, Change
from core.doc_mapper import DocMapper, MappingRule
from core.updater import DocumentUpdater


class TestChangeDetector:
    """Test change detection functionality."""

    def test_init_change_detector(self):
        """Test ChangeDetector initialization."""
        detector = ChangeDetector()
        assert detector is not None
        assert detector.changes == []

    def test_add_change(self):
        """Test adding a change."""
        detector = ChangeDetector()
        change = Change(
            file_path="backend/api/routes/games.py",
            change_type=ChangeType.MODIFY,
            details={"lines_added": 10, "lines_removed": 5}
        )
        detector.add_change(change)
        assert len(detector.changes) == 1
        assert detector.changes[0].file_path == "backend/api/routes/games.py"

    def test_categorize_api_change(self):
        """Test categorizing API route changes."""
        detector = ChangeDetector()
        change_type = detector.categorize_change("backend/api/routes/games.py")
        assert change_type == ChangeType.API_CHANGE

    def test_categorize_service_change(self):
        """Test categorizing service changes."""
        detector = ChangeDetector()
        change_type = detector.categorize_change("backend/services/games/game_service.py")
        assert change_type == ChangeType.SERVICE_CHANGE

    def test_categorize_feature_change(self):
        """Test categorizing frontend feature changes."""
        detector = ChangeDetector()
        change_type = detector.categorize_change("frontend/src/features/games/GamesList.jsx")
        assert change_type == ChangeType.FRONTEND_FEATURE

    def test_categorize_unknown_change(self):
        """Test categorizing unknown file types."""
        detector = ChangeDetector()
        change_type = detector.categorize_change("unknown/file.txt")
        assert change_type == ChangeType.OTHER


class TestDocMapper:
    """Test document mapping functionality."""

    def test_init_mapper(self):
        """Test DocMapper initialization."""
        mapper = DocMapper()
        assert mapper is not None
        assert mapper.rules == []

    def test_add_mapping_rule(self):
        """Test adding mapping rules."""
        mapper = DocMapper()
        rule = MappingRule(
            pattern="backend/api/routes/",
            target="docs/api/",
            action="update_endpoint"
        )
        mapper.add_rule(rule)
        assert len(mapper.rules) == 1

    def test_map_api_route(self):
        """Test mapping API route files."""
        mapper = DocMapper()
        mapper.load_default_rules()
        mappings = mapper.map("backend/api/routes/dwd_generator/games.py")
        assert len(mappings) > 0
        assert any(m.target == "docs/api/" for m in mappings)

    def test_map_service_file(self):
        """Test mapping service files."""
        mapper = DocMapper()
        mapper.load_default_rules()
        mappings = mapper.map("backend/services/games/game_service.py")
        assert len(mappings) > 0
        assert any(m.target == "docs/development/backend-development.md" for m in mappings)

    def test_map_frontend_component(self):
        """Test mapping frontend components."""
        mapper = DocMapper()
        mapper.load_default_rules()
        mappings = mapper.map("frontend/src/features/games/GamesList.jsx")
        assert len(mappings) > 0

    def test_map_unknown_file(self):
        """Test mapping unknown files returns empty list."""
        mapper = DocMapper()
        mapper.load_default_rules()
        mappings = mapper.map("unknown/file.txt")
        assert len(mappings) == 0


class TestDocumentUpdater:
    """Test document update functionality."""

    def test_init_updater(self):
        """Test DocumentUpdater initialization."""
        updater = DocumentUpdater()
        assert updater is not None
        assert updater.project_root == Path.cwd()

    def test_set_project_root(self):
        """Test setting custom project root."""
        updater = DocumentUpdater(project_root=Path("/tmp/test"))
        assert updater.project_root == Path("/tmp/test")

    def test_generate_update_summary(self):
        """Test generating update summary."""
        updater = DocumentUpdater()
        changes = [
            Change(
                file_path="backend/api/routes/games.py",
                change_type=ChangeType.API_CHANGE,
                details={"endpoint": "/api/games"}
            )
        ]
        summary = updater.generate_update_summary(changes)
        assert summary is not None
        assert "changes_detected" in summary
        assert summary["changes_detected"] == 1

    def test_map_changes_to_docs(self):
        """Test mapping changes to documents."""
        updater = DocumentUpdater()
        changes = [
            Change(
                file_path="backend/api/routes/games.py",
                change_type=ChangeType.API_CHANGE,
                details={}
            )
        ]
        mappings = updater.map_changes_to_docs(changes)
        assert mappings is not None
        assert len(mappings) > 0


class TestIntegration:
    """Integration tests for the full workflow."""

    def test_full_workflow(self):
        """Test the complete change detection → mapping → update workflow."""
        # Step 1: Detect changes
        detector = ChangeDetector()
        detector.add_change(Change(
            file_path="backend/api/routes/dwd_generator/games.py",
            change_type=ChangeType.API_CHANGE,
            details={"endpoint": "POST /api/games"}
        ))

        # Step 2: Map to documents
        mapper = DocMapper()
        mapper.load_default_rules()
        mappings = mapper.map(detector.changes[0].file_path)

        # Step 3: Generate update plan
        updater = DocumentUpdater()
        update_plan = updater.map_changes_to_docs(detector.changes)

        assert len(detector.changes) == 1
        assert len(mappings) > 0
        assert len(update_plan) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

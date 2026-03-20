"""
Test suite for code duplication refactoring
Tests to verify that refactored code uses shared utilities instead of duplicated patterns
"""

import pytest
import ast
import os
from pathlib import Path


class TestBackendCodeDuplication:
    """Test backend code uses shared utilities instead of duplicating error handling"""

    def setup_method(self):
        """Setup test paths"""
        self.backend_root = Path(__file__).parent.parent.parent.parent / "backend"
        self.api_routes_dir = self.backend_root / "api" / "routes"

    def _count_pattern_in_file(self, file_path: Path, pattern: str) -> int:
        """Count occurrences of a pattern string in a file"""
        if not file_path.exists():
            return 0

        content = file_path.read_text()
        return content.count(pattern)

    def _check_decorator_usage(self, file_path: Path) -> dict:
        """Check if file uses @handle_api_errors decorator"""
        if not file_path.exists():
            return {"uses_decorator": False, "has_try_except": 0}

        content = file_path.read_text()
        uses_decorator = "@handle_api_errors" in content
        has_try_except = content.count("try:")
        has_json_success = content.count("json_success_response")
        has_json_error = content.count("json_error_response")

        return {
            "uses_decorator": uses_decorator,
            "has_try_except": has_try_except,
            "has_json_success": has_json_success,
            "has_json_error": has_json_error
        }

    def test_events_py_uses_decorator(self):
        """Test events.py uses @handle_api_errors decorator"""
        events_file = self.api_routes_dir / "events.py"
        result = self._check_decorator_usage(events_file)

        # After refactoring, should use decorator
        assert result["uses_decorator"], "events.py should use @handle_api_errors decorator"

        # Should have reduced try-except blocks (ideally 0 for simple endpoints)
        # Allow some try-except for complex logic, but much fewer than before
        assert result["has_try_except"] <= 2, "events.py should minimize try-except blocks"

    def test_games_py_uses_decorator(self):
        """Test games.py uses @handle_api_errors decorator"""
        games_file = self.api_routes_dir / "games.py"
        result = self._check_decorator_usage(games_file)

        assert result["uses_decorator"], "games.py should use @handle_api_errors decorator"
        assert result["has_try_except"] <= 2, "games.py should minimize try-except blocks"

    def test_categories_py_uses_decorator(self):
        """Test categories.py uses @handle_api_errors decorator"""
        categories_file = self.api_routes_dir / "categories.py"
        result = self._check_decorator_usage(categories_file)

        assert result["uses_decorator"], "categories.py should use @handle_api_errors decorator"
        assert result["has_try_except"] <= 2, "categories.py should minimize try-except blocks"

    def test_parameters_py_uses_decorator(self):
        """Test parameters.py uses @handle_api_errors decorator"""
        parameters_file = self.api_routes_dir / "parameters.py"
        result = self._check_decorator_usage(parameters_file)

        assert result["uses_decorator"], "parameters.py should use @handle_api_errors decorator"
        assert result["has_try_except"] <= 2, "parameters.py should minimize try-except blocks"

    def test_flows_py_uses_decorator(self):
        """Test flows.py uses @handle_api_errors decorator"""
        flows_file = self.api_routes_dir / "flows.py"
        result = self._check_decorator_usage(flows_file)

        assert result["uses_decorator"], "flows.py should use @handle_api_errors decorator"
        assert result["has_try_except"] <= 2, "flows.py should minimize try-except blocks"

    def test_import_shared_utils(self):
        """Test files import from backend.core.utils.common"""
        files_to_check = [
            "events.py",
            "games.py",
            "categories.py",
            "parameters.py",
            "flows.py"
        ]

        for filename in files_to_check:
            file_path = self.api_routes_dir / filename
            if file_path.exists():
                content = file_path.read_text()
                # Should import from shared utilities
                assert "from backend.core.utils.common import" in content or \
                       "from backend.core.utils import common" in content, \
                       f"{filename} should import from backend.core.utils.common"


class TestBackendDateFormatting:
    """Test backend code uses shared date formatting utilities"""

    def setup_method(self):
        """Setup test paths"""
        self.backend_root = Path(__file__).parent.parent.parent.parent / "backend"
        self.api_routes_dir = self.backend_root / "api" / "routes"

    def test_no_manual_strftime_in_routes(self):
        """Test routes don't manually format dates with strftime"""
        # Allow some strftime usage but it should be minimal
        # Most date formatting should use format_datetime() from common.py

        files_to_check = [
            "events.py",
            "games.py",
            "categories.py",
            "parameters.py",
            "flows.py"
        ]

        for filename in files_to_check:
            file_path = self.api_routes_dir / filename
            if file_path.exists():
                content = file_path.read_text()
                strftime_count = content.count(".strftime(")

                # Should use format_datetime() instead of manual strftime
                # Allow some strftime for special cases
                assert strftime_count <= 2, \
                    f"{filename} should use format_datetime() from common.py instead of manual strftime"


class TestBackendStringSanitization:
    """Test backend code uses shared string sanitization utilities"""

    def setup_method(self):
        """Setup test paths"""
        self.backend_root = Path(__file__).parent.parent.parent.parent / "backend"
        self.api_routes_dir = self.backend_root / "api" / "routes"

    def test_no_manual_html_escape_in_routes(self):
        """Test routes don't manually escape HTML"""
        files_to_check = [
            "events.py",
            "games.py",
            "categories.py",
            "parameters.py",
            "flows.py"
        ]

        for filename in files_to_check:
            file_path = self.api_routes_dir / filename
            if file_path.exists():
                content = file_path.read_text()

                # Should not manually import and use html.escape
                # Should use sanitize_string() from common.py instead
                assert not ("import html" in content and "html.escape" in content), \
                    f"{filename} should use sanitize_string() from common.py instead of html.escape"


class TestBackendPagination:
    """Test backend code uses shared pagination utilities"""

    def setup_method(self):
        """Setup test paths"""
        self.backend_root = Path(__file__).parent.parent.parent.parent / "backend"
        self.api_routes_dir = self.backend_root / "api" / "routes"

    def test_uses_get_pagination_params(self):
        """Test routes use get_pagination_params() from common.py"""
        files_to_check = [
            "events.py",
            "games.py",
            "categories.py",
            "parameters.py"
        ]

        for filename in files_to_check:
            file_path = self.api_routes_dir / filename
            if file_path.exists():
                content = file_path.read_text()

                # Check for manual pagination calculation
                has_manual_pagination = (
                    "request.args.get('page'" in content or
                    "request.args.get(\"page\"" in content
                )

                if has_manual_pagination:
                    # Should use get_pagination_params()
                    assert "get_pagination_params" in content, \
                        f"{filename} should use get_pagination_params() from common.py for pagination"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

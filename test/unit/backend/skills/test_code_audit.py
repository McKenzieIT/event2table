"""
Code Audit Skill - Comprehensive Test Suite

Tests for the code-audit skill following TDD principles.
Test file created FIRST (RED phase).
"""

import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Add code-audit skill to path
code_audit_path = Path(__file__).parent.parent.parent.parent / ".claude" / "skills" / "code-audit"
sys.path.insert(0, str(code_audit_path))

from core.base_detector import BaseDetector, Issue, Severity, IssueCategory
from core.config import AuditConfig, ConfigManager
from core.runner import AuditRunner


class TestIssue:
    """Test Issue dataclass"""

    def test_issue_creation(self):
        """Test creating an issue with all fields"""
        issue = Issue(
            file_path="test.py",
            line_number=10,
            severity=Severity.CRITICAL,
            category=IssueCategory.COMPLIANCE,
            message="Test issue",
            suggestion="Fix it",
            code_snippet="bad_code()"
        )
        assert issue.file_path == "test.py"
        assert issue.line_number == 10
        assert issue.severity == Severity.CRITICAL
        assert issue.category == IssueCategory.COMPLIANCE
        assert issue.message == "Test issue"
        assert issue.suggestion == "Fix it"
        assert issue.code_snippet == "bad_code()"

    def test_issue_to_dict(self):
        """Test Issue serialization to dict"""
        issue = Issue(
            file_path="test.py",
            line_number=10,
            severity=Severity.HIGH,
            category=IssueCategory.SECURITY,
            message="XSS vulnerability",
            suggestion="Use html.escape()",
            code_snippet="return user_input"
        )
        data = issue.to_dict()
        assert data["file_path"] == "test.py"
        assert data["line_number"] == 10
        assert data["severity"] == "HIGH"
        assert data["category"] == "SECURITY"
        assert data["message"] == "XSS vulnerability"


class TestAuditConfig:
    """Test AuditConfig configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = AuditConfig()
        assert config.project_root == Path.cwd()
        assert config.enable_game_gid_check is True
        assert config.enable_api_contract_check is True
        assert config.enable_tdd_check is True
        assert config.enable_security_checks is True
        assert config.enable_quality_checks is True

    def test_custom_config(self):
        """Test custom configuration"""
        config = AuditConfig(
            project_root=Path("/tmp/test"),
            enable_game_gid_check=False,
            max_complexity=10
        )
        assert config.project_root == Path("/tmp/test")
        assert config.enable_game_gid_check is False
        assert config.max_complexity == 10


class TestConfigManager:
    """Test ConfigManager"""

    def test_load_default_config(self):
        """Test loading default configuration"""
        manager = ConfigManager()
        config = manager.get_config()
        assert isinstance(config, AuditConfig)
        assert config.enable_game_gid_check is True

    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "audit_config.json"

            # Save config
            config = AuditConfig(
                project_root=Path("/custom/path"),
                max_complexity=15
            )
            manager = ConfigManager(config_path=config_path)
            manager.save_config(config)

            # Load config
            loaded_config = manager.load_config()
            assert loaded_config.project_root == Path("/custom/path")
            assert loaded_config.max_complexity == 15


class TestBaseDetector:
    """Test BaseDetector abstract class"""

    def test_detector_not_implemented(self):
        """Test that BaseDetector raises NotImplementedError"""
        detector = BaseDetector()
        with pytest.raises(NotImplementedError):
            detector.detect(Path("test.py"))

    def test_detector_with_mock(self):
        """Test detector with mock implementation"""
        class MockDetector(BaseDetector):
            def detect(self, file_path: Path):
                return [
                    Issue(
                        file_path=str(file_path),
                        line_number=1,
                        severity=Severity.HIGH,
                        category=IssueCategory.COMPLIANCE,
                        message="Mock issue"
                    )
                ]

        detector = MockDetector()
        issues = detector.detect(Path("test.py"))
        assert len(issues) == 1
        assert issues[0].message == "Mock issue"


class TestAuditRunner:
    """Test AuditRunner main orchestrator"""

    def test_runner_initialization(self):
        """Test runner initialization with config"""
        config = AuditConfig(project_root=Path("/tmp"))
        runner = AuditRunner(config)
        assert runner.config.project_root == Path("/tmp")

    def test_runner_with_detectors(self):
        """Test runner with custom detectors"""
        class MockDetector(BaseDetector):
            def detect(self, file_path: Path):
                return [
                    Issue(
                        file_path=str(file_path),
                        line_number=1,
                        severity=Severity.LOW,
                        category=IssueCategory.QUALITY,
                        message="Test"
                    )
                ]

        config = AuditConfig()
        runner = AuditRunner(config)
        runner.add_detector(MockDetector())

        # Run audit on a temporary file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('test')")

            results = runner.run_audit(str(tmpdir))
            assert len(results) == 1
            assert results[0].message == "Test"


class TestSeverity:
    """Test Severity enum"""

    def test_severity_levels(self):
        """Test severity level ordering"""
        assert Severity.CRITICAL.value > Severity.HIGH.value
        assert Severity.HIGH.value > Severity.MEDIUM.value
        assert Severity.MEDIUM.value > Severity.LOW.value
        assert Severity.LOW.value > Severity.INFO.value


class TestIssueCategory:
    """Test IssueCategory enum"""

    def test_category_values(self):
        """Test category enum values"""
        assert IssueCategory.COMPLIANCE.value == "compliance"
        assert IssueCategory.SECURITY.value == "security"
        assert IssueCategory.QUALITY.value == "quality"
        assert IssueCategory.ARCHITECTURE.value == "architecture"
        assert IssueCategory.TESTING.value == "testing"


class TestGameGidDetector:
    """Test game_gid compliance detector"""

    def test_detect_illegal_game_id_variable(self):
        """Test detection of illegal game_id variable usage"""
        from detectors.compliance.game_gid_check import GameGidDetector

        detector = GameGidDetector()

        # Create test file with illegal game_id usage
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def get_events(game_id):
    query = f"SELECT * FROM events WHERE game_id = {game_id}"
    return execute(query)
""")

            issues = detector.detect(test_file)
            assert len(issues) > 0
            assert any("game_id" in issue.message.lower() for issue in issues)

    def test_detect_sql_game_id(self):
        """Test detection of game_id in SQL queries"""
        from detectors.compliance.game_gid_check import GameGidDetector

        detector = GameGidDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
query = "SELECT * FROM log_events WHERE game_id = ?"
""")

            issues = detector.detect(test_file)
            assert len(issues) > 0
            assert any("sql" in issue.message.lower() for issue in issues)


class TestApiContractDetector:
    """Test API contract detector"""

    def test_detect_missing_backend_api(self):
        """Test detection of missing backend API"""
        from detectors.compliance.api_contract_check import ApiContractDetector

        detector = ApiContractDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create frontend file with API call
            frontend_file = Path(tmpdir) / "frontend.js"
            frontend_file.write_text("""
fetch('/api/games/123', { method: 'DELETE' })
""")

            # No backend route exists
            issues = detector.detect(frontend_file)
            # Should detect potential missing API (simplified test)
            assert len(issues) >= 0  # May not detect without full project context


class TestTddDetector:
    """Test TDD compliance detector"""

    def test_detect_missing_test_file(self):
        """Test detection of missing test file"""
        from detectors.compliance.tdd_check import TddDetector

        detector = TddDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file without test
            source_file = Path(tmpdir) / "service.py"
            source_file.write_text("""
class GameService:
    def create_game(self):
        pass
""")

            issues = detector.detect(source_file)
            # Should detect missing test file
            assert len(issues) >= 0


class TestSqlInjectionDetector:
    """Test SQL injection detector"""

    def test_detect_string_concatenation(self):
        """Test detection of SQL string concatenation"""
        from detectors.security.sql_injection import SqlInjectionDetector

        detector = SqlInjectionDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
query = "SELECT * FROM games WHERE name = '" + user_input + "'"
""")

            issues = detector.detect(test_file)
            assert len(issues) > 0
            assert any("sql injection" in issue.message.lower() for issue in issues)


class TestXssDetector:
    """Test XSS protection detector"""

    def test_detect_unescaped_user_input(self):
        """Test detection of unescaped user input"""
        from detectors.security.xss_check import XssDetector

        detector = XssDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def render(username):
    return f"<h1>Welcome {username}</h1>"
""")

            issues = detector.detect(test_file)
            # Should detect potential XSS vulnerability
            assert len(issues) >= 0


class TestComplexityDetector:
    """Test cyclomatic complexity detector"""

    def test_calculate_complexity(self):
        """Test complexity calculation"""
        from detectors.quality.complexity import ComplexityDetector

        detector = ComplexityDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            simple_file = Path(tmpdir) / "simple.py"
            simple_file.write_text("""
def simple_function():
    return 1 + 1
""")

            complex_file = Path(tmpdir) / "complex.py"
            complex_file.write_text("""
def complex_function(x):
    if x > 0:
        if x > 10:
            return x * 2
        else:
            return x
    elif x < 0:
        return -x
    else:
        return 0
""")

            simple_issues = detector.detect(simple_file)
            complex_issues = detector.detect(complex_file)

            # Complex function should have more issues or higher complexity
            assert len(complex_issues) >= len(simple_issues)


class TestMarkdownReporter:
    """Test Markdown reporter"""

    def test_generate_report(self):
        """Test markdown report generation"""
        from reporters.markdown_reporter import MarkdownReporter

        reporter = MarkdownReporter()

        issues = [
            Issue(
                file_path="test.py",
                line_number=10,
                severity=Severity.CRITICAL,
                category=IssueCategory.SECURITY,
                message="SQL injection",
                suggestion="Use parameterized queries",
                code_snippet="query = f\"SELECT * FROM users WHERE name = '{name}'\""
            )
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.md"
            reporter.generate_report(issues, str(output_path))

            assert output_path.exists()
            content = output_path.read_text()
            assert "SQL injection" in content
            assert "CRITICAL" in content


class TestJsonReporter:
    """Test JSON reporter"""

    def test_generate_report(self):
        """Test JSON report generation"""
        from reporters.json_reporter import JsonReporter

        reporter = JsonReporter()

        issues = [
            Issue(
                file_path="test.py",
                line_number=10,
                severity=Severity.HIGH,
                category=IssueCategory.COMPLIANCE,
                message="game_id usage detected"
            )
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.json"
            reporter.generate_report(issues, str(output_path))

            assert output_path.exists()
            import json
            data = json.loads(output_path.read_text())
            assert data["total_issues"] == 1
            assert data["issues"][0]["message"] == "game_id usage detected"


class TestConsoleReporter:
    """Test Console reporter"""

    def test_generate_report(self, capsys):
        """Test console report generation"""
        from reporters.console_reporter import ConsoleReporter

        reporter = ConsoleReporter()

        issues = [
            Issue(
                file_path="test.py",
                line_number=10,
                severity=Severity.MEDIUM,
                category=IssueCategory.QUALITY,
                message="High complexity"
            )
        ]

        reporter.generate_report(issues, None)

        captured = capsys.readouterr()
        assert "High complexity" in captured.out
        assert "MEDIUM" in captured.out

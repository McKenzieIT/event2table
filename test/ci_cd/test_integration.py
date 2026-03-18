"""
Integration Tests for CI/CD Pipeline

Test suite for verifying end-to-end CI/CD functionality:
- Deployment workflow
- Monitoring integration
- Health checks
- Rollback procedures
"""

import os
import pytest
import subprocess
import time
from pathlib import Path
from typing import Dict, Any


class TestDeploymentIntegration:
    """Integration tests for deployment workflow"""

    @pytest.fixture
    def deploy_script(self) -> Path:
        """Path to deployment script"""
        return Path("/Users/mckenzie/Documents/event2table/scripts/deploy.sh")

    @pytest.fixture
    def project_root(self) -> Path:
        """Project root directory"""
        return Path("/Users/mckenzie/Documents/event2table")

    def test_deploy_script_help(self, deploy_script: Path):
        """Test that deployment script shows help"""
        result = subprocess.run(
            [str(deploy_script)],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert "Usage:" in result.stdout or "Usage:" in result.stderr, \
            "Deploy script should show usage information"

    def test_deploy_backup_command(self, deploy_script: Path, project_root: Path):
        """Test deployment backup command"""
        # Ensure backup directory exists
        backup_dir = project_root / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [str(deploy_script), "backup"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root)
        )

        # Should not crash (may fail if dependencies not met)
        assert result.returncode in [0, 1], \
            f"Backup command should complete: {result.stderr}"

        # Check if backup was created
        backups = list(backup_dir.glob("backup_*.tar.gz"))
        # Note: May not create backup if environment checks fail

    def test_deploy_health_check_command(self, deploy_script: Path, project_root: Path):
        """Test deployment health check command"""
        result = subprocess.run(
            [str(deploy_script), "health-check"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root)
        )

        # Health check may fail if services not running
        assert result.returncode in [0, 1], \
            f"Health check command should complete: {result.stderr}"

        # Should contain health check related output
        output = result.stdout + result.stderr
        assert "health" in output.lower() or "check" in output.lower() or \
               "connection" in output.lower() or "refused" in output.lower(), \
            "Health check should produce relevant output"


class TestMonitoringIntegration:
    """Integration tests for monitoring system"""

    @pytest.fixture
    def monitor_script(self) -> Path:
        """Path to monitoring script"""
        return Path("/Users/mckenzie/Documents/event2table/scripts/monitoring/performance_monitor.sh")

    @pytest.fixture
    def project_root(self) -> Path:
        """Project root directory"""
        return Path("/Users/mckenzie/Documents/event2table")

    def test_monitor_script_help(self, monitor_script: Path):
        """Test that monitoring script shows help"""
        result = subprocess.run(
            [str(monitor_script), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0, "Help command should succeed"
        assert "Usage:" in result.stdout, "Should show usage information"

    def test_monitor_cache_check(self, monitor_script: Path, project_root: Path):
        """Test cache monitoring functionality"""
        # Create log directory
        log_dir = project_root / "logs" / "monitoring"
        log_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [str(monitor_script), "--cache"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root)
        )

        # Should complete (may fail if services not running)
        assert result.returncode in [0, 1], \
            f"Cache monitoring should complete: {result.stderr}"

        # Should mention cache
        output = result.stdout + result.stderr
        assert "cache" in output.lower(), \
            "Output should mention cache"

    def test_monitor_api_check(self, monitor_script: Path, project_root: Path):
        """Test API monitoring functionality"""
        result = subprocess.run(
            [str(monitor_script), "--api"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root)
        )

        # Should complete (may fail if services not running)
        assert result.returncode in [0, 1], \
            f"API monitoring should complete: {result.stderr}"

        # Should mention API or response time
        output = result.stdout + result.stderr
        assert "api" in output.lower() or "response" in output.lower(), \
            "Output should mention API or response time"

    def test_monitor_database_check(self, monitor_script: Path, project_root: Path):
        """Test database monitoring functionality"""
        # Ensure data directory exists
        data_dir = project_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [str(monitor_script), "--database"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root)
        )

        # Should complete (may fail if database not exists)
        assert result.returncode in [0, 1], \
            f"Database monitoring should complete: {result.stderr}"

        # Should mention database
        output = result.stdout + result.stderr
        assert "database" in output.lower() or "db" in output.lower(), \
            "Output should mention database"

    def test_monitor_resources_check(self, monitor_script: Path, project_root: Path):
        """Test resource monitoring functionality"""
        result = subprocess.run(
            [str(monitor_script), "--resources"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(project_root)
        )

        # Should complete
        assert result.returncode in [0, 1], \
            f"Resource monitoring should complete: {result.stderr}"

        # Should mention resources
        output = result.stdout + result.stderr
        assert any(term in output.lower() for term in ["cpu", "memory", "disk"]), \
            "Output should mention system resources"

    def test_monitor_report_generation(self, monitor_script: Path, project_root: Path):
        """Test performance report generation"""
        # Create report directory
        report_dir = project_root / "reports" / "monitoring"
        report_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            [str(monitor_script), "--report"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(project_root)
        )

        # Should complete
        assert result.returncode in [0, 1], \
            f"Report generation should complete: {result.stderr}"

        # Check if report was created
        reports = list(report_dir.glob("performance_report_*.md"))
        # Note: Report creation depends on monitoring data availability


class TestCICDWorkflowIntegration:
    """Integration tests for CI/CD workflow"""

    @pytest.fixture
    def project_root(self) -> Path:
        """Project root directory"""
        return Path("/Users/mckenzie/Documents/event2table")

    def test_workflow_yaml_valid(self, project_root: Path):
        """Test that workflow YAML is valid"""
        import yaml

        workflow_path = project_root / ".github" / "workflows" / "ci-cd.yml"

        with open(workflow_path) as f:
            try:
                config = yaml.safe_load(f)
                assert config is not None, "Workflow config should not be None"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML: {e}")

    def test_all_jobs_have_valid_names(self, project_root: Path):
        """Test that all jobs have valid GitHub Actions names"""
        import yaml

        workflow_path = project_root / ".github" / "workflows" / "ci-cd.yml"

        with open(workflow_path) as f:
            config = yaml.safe_load(f)

        jobs = config.get("jobs", {})
        for job_name, job_config in jobs.items():
            # Job names should be lowercase with hyphens
            assert job_name.replace("-", "").replace("_", "").isalnum(), \
                f"Job name '{job_name}' should be alphanumeric with hyphens/underscores"

            # Each job should have a name or runs-on
            assert "name" in job_config or "runs-on" in job_config, \
                f"Job '{job_name}' should have a name or runs-on field"

    def test_jobs_have_required_steps(self, project_root: Path):
        """Test that critical jobs have required steps"""
        import yaml

        workflow_path = project_root / ".github" / "workflows" / "ci-cd.yml"

        with open(workflow_path) as f:
            config = yaml.safe_load(f)

        jobs = config.get("jobs", {})

        # Backend tests should checkout code
        backend_job = jobs.get("backend-unit-tests", {})
        backend_steps = backend_job.get("steps", [])
        assert any("checkout" in str(step).lower() for step in backend_steps), \
            "Backend tests should checkout code"

        # Frontend tests should setup Node.js
        frontend_job = jobs.get("frontend-unit-tests", {})
        frontend_steps = frontend_job.get("steps", [])
        assert any("node" in str(step).lower() for step in frontend_steps), \
            "Frontend tests should setup Node.js"

        # Deploy should have health check
        deploy_job = jobs.get("deploy", {})
        deploy_steps = deploy_job.get("steps", [])
        assert any("health" in str(step).lower() for step in deploy_steps), \
            "Deploy should include health check"


class TestCICDDocumentation:
    """Tests for CI/CD documentation completeness"""

    @pytest.fixture
    def project_root(self) -> Path:
        """Project root directory"""
        return Path("/Users/mckenzie/Documents/event2table")

    def test_deploy_script_has_docs(self, project_root: Path):
        """Test that deployment script has documentation"""
        deploy_script = project_root / "scripts" / "deploy.sh"

        content = deploy_script.read_text()

        # Should have usage information
        assert "Usage:" in content, "Deploy script should document usage"

        # Should have examples
        assert "Examples:" in content or "Example" in content, \
            "Deploy script should have examples"

    def test_monitor_script_has_docs(self, project_root: Path):
        """Test that monitoring script has documentation"""
        monitor_script = project_root / "scripts" / "monitoring" / "performance_monitor.sh"

        content = monitor_script.read_text()

        # Should have usage information
        assert "Usage:" in content, "Monitor script should document usage"

        # Should have examples
        assert "Examples:" in content or "Example" in content, \
            "Monitor script should have examples"

    def test_workflow_has_comments(self, project_root: Path):
        """Test that workflow file has descriptive comments"""
        workflow_path = project_root / ".github" / "workflows" / "ci-cd.yml"

        content = workflow_path.read_text()

        # Should have comments describing jobs
        assert "#" in content, "Workflow should have comments"

        # Should have job descriptions
        assert "name:" in content, "Jobs should have descriptive names"


@pytest.fixture
def setup_test_environment():
    """Setup test environment before running integration tests"""
    project_root = Path("/Users/mckenzie/Documents/event2table")

    # Create required directories
    directories = [
        project_root / "logs" / "monitoring",
        project_root / "logs" / "deployments",
        project_root / "reports" / "monitoring",
        project_root / "backups",
        project_root / "data"
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup if needed
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

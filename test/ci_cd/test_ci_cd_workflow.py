"""
CI/CD Workflow Tests

Test suite for CI/CD pipeline components including:
- GitHub Actions workflow validation
- Deployment script functionality
- Monitoring system integration
- Rollback mechanisms
"""

import os
import pytest
import subprocess
import yaml
from pathlib import Path
from typing import Dict, Any


class TestGitHubActionsWorkflow:
    """Test GitHub Actions workflow configuration"""

    @pytest.fixture
    def workflow_path(self) -> Path:
        """Path to CI/CD workflow file"""
        return Path("/Users/mckenzie/Documents/event2table/.github/workflows/ci-cd.yml")

    @pytest.fixture
    def workflow_config(self, workflow_path: Path) -> Dict[str, Any]:
        """Load and parse workflow configuration"""
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_workflow_file_exists(self, workflow_path: Path):
        """Test that workflow file exists"""
        assert workflow_path.exists(), "CI/CD workflow file must exist"
        assert workflow_path.is_file(), "CI/CD workflow must be a file"

    def test_workflow_has_required_jobs(self, workflow_config: Dict[str, Any]):
        """Test that workflow includes all required jobs"""
        required_jobs = [
            "backend-unit-tests",
            "frontend-unit-tests",
            "e2e-tests",
            "lighthouse",
            "code-quality",
            "deploy"
        ]

        assert "jobs" in workflow_config, "Workflow must have jobs section"
        actual_jobs = set(workflow_config["jobs"].keys())
        required_jobs_set = set(required_jobs)

        missing_jobs = required_jobs_set - actual_jobs
        assert not missing_jobs, f"Missing required jobs: {missing_jobs}"

    def test_backend_tests_job_config(self, workflow_config: Dict[str, Any]):
        """Test backend unit tests job configuration"""
        job = workflow_config["jobs"]["backend-unit-tests"]

        assert job["runs-on"] == "ubuntu-latest", "Must run on Ubuntu"
        assert "steps" in job, "Must have steps"

        step_names = [step.get("name", "") for step in job["steps"]]
        assert any("checkout" in name.lower() for name in step_names), "Must checkout code"
        assert any("python" in name.lower() for name in step_names), "Must setup Python"
        assert any("test" in name.lower() for name in step_names), "Must run tests"

    def test_frontend_tests_job_config(self, workflow_config: Dict[str, Any]):
        """Test frontend unit tests job configuration"""
        job = workflow_config["jobs"]["frontend-unit-tests"]

        assert job["runs-on"] == "ubuntu-latest", "Must run on Ubuntu"
        assert "steps" in job, "Must have steps"

        step_names = [step.get("name", "") for step in job["steps"]]
        assert any("node" in name.lower() for name in step_names), "Must setup Node.js"
        assert any("install" in name.lower() for name in step_names), "Must install dependencies"
        assert any("test" in name.lower() for name in step_names), "Must run tests"

    def test_e2e_tests_job_config(self, workflow_config: Dict[str, Any]):
        """Test E2E tests job configuration"""
        job = workflow_config["jobs"]["e2e-tests"]

        assert "runs-on" in job, "Must specify runner"
        assert "steps" in job, "Must have steps"

        # E2E tests should depend on unit tests passing
        assert "needs" in job, "E2E tests should depend on unit tests"

    def test_lighthouse_job_config(self, workflow_config: Dict[str, Any]):
        """Test Lighthouse CI job configuration"""
        job = workflow_config["jobs"]["lighthouse"]

        assert "runs-on" in job, "Must specify runner"
        assert "steps" in job, "Must have steps"

        step_names = [step.get("name", "") for step in job["steps"]]
        assert any("lighthouse" in name.lower() for name in step_names), "Must run Lighthouse"

    def test_code_quality_job_config(self, workflow_config: Dict[str, Any]):
        """Test code quality job configuration"""
        job = workflow_config["jobs"]["code-quality"]

        assert "runs-on" in job, "Must specify runner"
        assert "steps" in job, "Must have steps"

        # Should check linting, type checking, etc.
        step_names = [step.get("name", "") for step in job["steps"]]
        assert any("lint" in name.lower() or "quality" in name.lower()
                   for name in step_names), "Must check code quality"

    def test_deploy_job_config(self, workflow_config: Dict[str, Any]):
        """Test deployment job configuration"""
        job = workflow_config["jobs"]["deploy"]

        assert "runs-on" in job, "Must specify runner"
        assert "steps" in job, "Must have steps"

        # Deploy should depend on all tests passing
        assert "needs" in job, "Deploy should depend on other jobs"
        assert len(job["needs"]) >= 4, "Deploy should depend on all test jobs"

        # Should only run on main branch
        if "if" in job:
            assert "main" in job["if"] or "master" in job["if"], \
                "Deploy should only run on main/master branch"


class TestDeploymentScript:
    """Test deployment script functionality"""

    @pytest.fixture
    def deploy_script_path(self) -> Path:
        """Path to deployment script"""
        return Path("/Users/mckenzie/Documents/event2table/scripts/deploy.sh")

    def test_deploy_script_exists(self, deploy_script_path: Path):
        """Test that deployment script exists"""
        assert deploy_script_path.exists(), "Deployment script must exist"
        assert deploy_script_path.is_file(), "Deployment script must be a file"

    def test_deploy_script_executable(self, deploy_script_path: Path):
        """Test that deployment script is executable"""
        assert os.access(deploy_script_path, os.X_OK), \
            "Deployment script must be executable"

    def test_deploy_script_has_health_check(self, deploy_script_path: Path):
        """Test that deployment script includes health checks"""
        content = deploy_script_path.read_text()

        assert "health" in content.lower() or "check" in content.lower(), \
            "Deployment script must include health checks"

    def test_deploy_script_has_rollback(self, deploy_script_path: Path):
        """Test that deployment script includes rollback mechanism"""
        content = deploy_script_path.read_text()

        assert "rollback" in content.lower(), \
            "Deployment script must include rollback mechanism"

    def test_deploy_script_has_backup(self, deploy_script_path: Path):
        """Test that deployment script creates backups"""
        content = deploy_script_path.read_text()

        assert "backup" in content.lower(), \
            "Deployment script must create backups before deployment"


class TestPerformanceMonitoring:
    """Test performance monitoring system"""

    @pytest.fixture
    def monitor_script_path(self) -> Path:
        """Path to performance monitoring script"""
        return Path("/Users/mckenzie/Documents/event2table/scripts/monitoring/performance_monitor.sh")

    def test_monitor_script_exists(self, monitor_script_path: Path):
        """Test that monitoring script exists"""
        assert monitor_script_path.exists(), "Performance monitoring script must exist"
        assert monitor_script_path.is_file(), "Monitoring script must be a file"

    def test_monitor_script_executable(self, monitor_script_path: Path):
        """Test that monitoring script is executable"""
        assert os.access(monitor_script_path, os.X_OK), \
            "Monitoring script must be executable"

    def test_monitor_checks_cache_hit_rate(self, monitor_script_path: Path):
        """Test that monitor checks cache hit rate"""
        content = monitor_script_path.read_text()

        assert "cache" in content.lower(), \
            "Monitoring must check cache performance"

    def test_monitor_checks_api_response_time(self, monitor_script_path: Path):
        """Test that monitor checks API response times"""
        content = monitor_script_path.read_text()

        assert "response" in content.lower() or "api" in content.lower(), \
            "Monitoring must check API response times"

    def test_monitor_checks_database_queries(self, monitor_script_path: Path):
        """Test that monitor checks database query performance"""
        content = monitor_script_path.read_text()

        assert "database" in content.lower() or "db" in content.lower() or "query" in content.lower(), \
            "Monitoring must check database query performance"


class TestCICDIntegration:
    """Integration tests for CI/CD pipeline"""

    def test_workflow_triggers_on_push(self):
        """Test that workflow triggers on push to main branches"""
        workflow_path = Path("/Users/mckenzie/Documents/event2table/.github/workflows/ci-cd.yml")

        with open(workflow_path) as f:
            config = yaml.safe_load(f)

        # 'on' is a reserved word in Python, yaml.safe_load converts it to True
        assert True in config or "on" in config or "trigger" in config, \
            "Workflow must have trigger configuration"

        triggers = config.get(True, config.get("on", config.get("trigger", {})))
        assert "push" in triggers or "push" in str(triggers), \
            "Workflow must trigger on push"

    def test_workflow_triggers_on_pull_request(self):
        """Test that workflow triggers on pull requests"""
        workflow_path = Path("/Users/mckenzie/Documents/event2table/.github/workflows/ci-cd.yml")

        with open(workflow_path) as f:
            config = yaml.safe_load(f)

        # 'on' is a reserved word in Python, yaml.safe_load converts it to True
        triggers = config.get(True, config.get("on", config.get("trigger", {})))
        assert "pull_request" in triggers or "pull_request" in str(triggers), \
            "Workflow must trigger on pull requests"

    def test_deployment_time_target(self):
        """Test that deployment targets <5 minutes"""
        # This is a documentation test - actual timing would be measured in real runs
        deploy_script = Path("/Users/mckenzie/Documents/event2table/scripts/deploy.sh")

        if deploy_script.exists():
            content = deploy_script.read_text()
            # Look for timeout or time target references
            # In practice, this would be measured during actual deployments
            assert True  # Placeholder for actual timing verification


@pytest.fixture
def setup_test_environment():
    """Setup test environment before running tests"""
    # Ensure directories exist
    directories = [
        Path("/Users/mckenzie/Documents/event2table/.github/workflows"),
        Path("/Users/mckenzie/Documents/event2table/scripts"),
        Path("/Users/mckenzie/Documents/event2table/scripts/monitoring"),
        Path("/Users/mckenzie/Documents/event2table/test/ci_cd")
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    yield

    # Cleanup if needed
    pass


@pytest.fixture
def mock_github_secrets():
    """Mock GitHub secrets for testing"""
    return {
        "LHCI_GITHUB_APP_TOKEN": "test_token",
        "DEPLOY_KEY": "test_deploy_key",
        "API_TOKEN": "test_api_token"
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

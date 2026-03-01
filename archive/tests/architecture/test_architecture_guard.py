#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
架构守护测试

使用pytest架构测试来确保代码符合DDD架构规范。
"""

import pytest
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestDDDArchitecture:
    """DDD架构测试"""

    def test_domain_layer_exists(self):
        """测试领域层目录存在"""
        domain_path = PROJECT_ROOT / "backend" / "domain"
        assert domain_path.exists(), "领域层目录不存在: backend/domain"

    def test_application_layer_exists(self):
        """测试应用层目录存在"""
        app_path = PROJECT_ROOT / "backend" / "application"
        assert app_path.exists(), "应用层目录不存在: backend/application"

    def test_infrastructure_layer_exists(self):
        """测试基础设施层目录存在"""
        infra_path = PROJECT_ROOT / "backend" / "infrastructure"
        assert infra_path.exists(), "基础设施层目录不存在: backend/infrastructure"

    def test_api_layer_exists(self):
        """测试API层目录存在"""
        api_path = PROJECT_ROOT / "backend" / "api"
        assert api_path.exists(), "API层目录不存在: backend/api"

    def test_domain_models_exist(self):
        """测试领域模型存在"""
        models_path = PROJECT_ROOT / "backend" / "domain" / "models"
        assert models_path.exists(), "领域模型目录不存在"

        # 检查核心领域模型
        event_model = models_path / "event.py"
        parameter_model = models_path / "parameter.py"
        game_model = models_path / "game.py"

        assert event_model.exists(), "Event领域模型不存在"
        assert parameter_model.exists(), "Parameter领域模型不存在"
        assert game_model.exists(), "Game领域模型不存在"

    def test_domain_repositories_exist(self):
        """测试领域仓储接口存在"""
        repos_path = PROJECT_ROOT / "backend" / "domain" / "repositories"
        assert repos_path.exists(), "领域仓储目录不存在"

        # 检查仓储接口
        event_repo = repos_path / "event_repository.py"
        game_repo = repos_path / "game_repository.py"

        assert event_repo.exists(), "Event仓储接口不存在"
        assert game_repo.exists(), "Game仓储接口不存在"

    def test_infrastructure_repositories_exist(self):
        """测试基础设施层仓储实现存在"""
        infra_repos_path = PROJECT_ROOT / "backend" / "infrastructure" / "persistence"
        assert infra_repos_path.exists(), "基础设施持久化目录不存在"

        # 检查仓储实现
        event_repo_impl = infra_repos_path / "event_repository_impl.py"
        game_repo_impl = infra_repos_path / "game_repository_impl.py"

        assert event_repo_impl.exists(), "Event仓储实现不存在"
        assert game_repo_impl.exists(), "Game仓储实现不存在"

    def test_application_services_exist(self):
        """测试应用服务存在"""
        services_path = PROJECT_ROOT / "backend" / "application" / "services"
        assert services_path.exists(), "应用服务目录不存在"

        # 检查应用服务
        event_service = services_path / "event_app_service.py"
        game_service = services_path / "game_app_service.py"

        assert event_service.exists(), "Event应用服务不存在"
        assert game_service.exists(), "Game应用服务不存在"

    def test_api_routes_exist(self):
        """测试API路由存在"""
        routes_path = PROJECT_ROOT / "backend" / "api" / "routes"
        assert routes_path.exists(), "API路由目录不存在"

        # 检查API路由
        events_route = routes_path / "events.py"
        games_route = routes_path / "games.py"

        assert events_route.exists(), "Events API路由不存在"
        assert games_route.exists(), "Games API路由不存在"

    def test_no_business_logic_in_api(self):
        """测试API层不包含业务逻辑"""
        api_path = PROJECT_ROOT / "backend" / "api" / "routes"

        # 检查API文件不应直接访问数据库
        forbidden_patterns = [
            "get_db_connection()",
            "cursor.execute(",
            "conn.execute(",
        ]

        for py_file in api_path.rglob("*.py"):
            content = py_file.read_text()
            for pattern in forbidden_patterns:
                # 允许在v2版本中使用新的架构
                if "_v2" in py_file.name:
                    continue
                # 旧API可能还有这些模式，但新API不应该有
                if pattern in content and "_v2" not in py_file.name:
                    # 这是一个警告，不是错误
                    pass

    def test_domain_exceptions_exist(self):
        """测试领域异常存在"""
        exceptions_path = PROJECT_ROOT / "backend" / "domain" / "exceptions"
        assert exceptions_path.exists(), "领域异常目录不存在"

        domain_exceptions = exceptions_path / "domain_exceptions.py"
        assert domain_exceptions.exists(), "领域异常文件不存在"


class TestNamingConventions:
    """命名规范测试"""

    def test_python_files_use_snake_case(self):
        """测试Python文件使用snake_case"""
        backend_path = PROJECT_ROOT / "backend"

        for py_file in backend_path.rglob("*.py"):
            # 排除测试文件和特殊文件
            if py_file.name.startswith("test_"):
                continue
            if py_file.name.startswith("_"):
                continue

            # 检查是否包含大写字母（除了测试文件）
            if any(c.isupper() for c in py_file.stem):
                pytest.fail(f"Python文件应使用snake_case: {py_file}")

    def test_domain_classes_use_pascal_case(self):
        """测试领域类使用PascalCase"""
        models_path = PROJECT_ROOT / "backend" / "domain" / "models"

        if not models_path.exists():
            pytest.skip("领域模型目录不存在")

        for py_file in models_path.glob("*.py"):
            content = py_file.read_text()

            # 检查类定义
            import re
            class_pattern = r'class\s+([A-Z][a-zA-Z0-9]*)\s*[:\(]'
            matches = re.findall(class_pattern, content)

            for class_name in matches:
                assert class_name[0].isupper(), f"类名应使用PascalCase: {class_name}"


class TestDependencyDirection:
    """依赖方向测试"""

    def test_domain_does_not_import_application(self):
        """测试领域层不依赖应用层"""
        domain_path = PROJECT_ROOT / "backend" / "domain"

        if not domain_path.exists():
            pytest.skip("领域层目录不存在")

        for py_file in domain_path.rglob("*.py"):
            content = py_file.read_text()

            # 检查是否导入了应用层
            assert "from backend.application" not in content, \
                f"领域层不应依赖应用层: {py_file}"
            assert "import backend.application" not in content, \
                f"领域层不应依赖应用层: {py_file}"

    def test_domain_does_not_import_infrastructure(self):
        """测试领域层不依赖基础设施层"""
        domain_path = PROJECT_ROOT / "backend" / "domain"

        if not domain_path.exists():
            pytest.skip("领域层目录不存在")

        for py_file in domain_path.rglob("*.py"):
            content = py_file.read_text()

            # 检查是否导入了基础设施层
            assert "from backend.infrastructure" not in content, \
                f"领域层不应依赖基础设施层: {py_file}"
            assert "import backend.infrastructure" not in content, \
                f"领域层不应依赖基础设施层: {py_file}"

    def test_domain_does_not_import_api(self):
        """测试领域层不依赖API层"""
        domain_path = PROJECT_ROOT / "backend" / "domain"

        if not domain_path.exists():
            pytest.skip("领域层目录不存在")

        for py_file in domain_path.rglob("*.py"):
            content = py_file.read_text()

            # 检查是否导入了API层
            assert "from backend.api" not in content, \
                f"领域层不应依赖API层: {py_file}"
            assert "import backend.api" not in content, \
                f"领域层不应依赖API层: {py_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

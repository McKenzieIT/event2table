"""
权限和认证测试 - P0-11

测试GraphQL mutations的身份验证和授权检查. 

当前状态: 所有测试应该失败（RED阶段）
目标状态: 添加权限检查后, 所有测试通过（GREEN阶段）

测试覆盖:
- 事件mutations (CreateEvent, UpdateEvent, DeleteEvent, BatchDeleteEvents)
- 游戏mutations (CreateGame, UpdateGame, DeleteGame)
- 参数mutations (CreateParameter, UpdateParameter, DeleteParameter)
- 批量mutations (BatchCreateGames, BatchUpdateGames, BatchDeleteGames)
- 其他mutations (Category, JoinConfig, Node, Flow, HQL, Template)
"""

import pytest
import ast
import os
from unittest.mock import Mock, MagicMock, patch


class TestEventMutationsAuth:
    """测试事件mutations的权限检查"""

    def test_create_event_requires_authentication(self):
        """
        测试创建事件需要身份验证

        应该:
        - 检查用户是否已登录
        - 未登录时抛出认证错误
        """
        from backend.gql_api.mutations.event_mutations import CreateEvent

        info = Mock()
        # 模拟未登录用户(context中没有user)
        info.context = Mock(user=None)

        mutation = CreateEvent()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(
                info,
                game_gid=90000001,
                event_name="Test Event",
                event_name_cn="测试事件",
                category_id=None,
            )

        # 应该返回认证错误
        error_msg = str(exc_info.value).lower()
        assert (
            "authentication" in error_msg
            or "unauthorized" in error_msg
            or "login" in error_msg
            or "未登录" in error_msg
            or "认证" in error_msg
        ), f"Expected authentication error, got: {exc_info.value}"

    def test_update_event_requires_permission(self):
        """
        测试更新事件需要相应权限

        应该:
        - 检查用户是否有event:write权限
        - 无权限时抛出授权错误
        """
        from backend.gql_api.mutations.event_mutations import UpdateEvent

        info = Mock()
        # 模拟已登录但无权限的用户
        mock_user = Mock(id=1, username="testuser")
        mock_user.permissions = []  # 无event:write权限
        info.context = Mock(user=mock_user)

        mutation = UpdateEvent()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, event_id=1, event_name="Updated Event", event_name_cn="更新事件")

        # 应该返回授权错误
        error_msg = str(exc_info.value).lower()
        assert (
            "permission" in error_msg
            or "authorized" in error_msg
            or "forbidden" in error_msg
            or "权限" in error_msg
        ), f"Expected permission error, got: {exc_info.value}"

    def test_delete_event_requires_permission(self):
        """
        测试删除事件需要相应权限

        应该:
        - 检查用户是否有event:delete权限
        - 无权限时抛出授权错误
        """
        from backend.gql_api.mutations.event_mutations import DeleteEvent

        info = Mock()
        # 模拟已登录但无删除权限的用户
        mock_user = Mock(id=1, username="testuser")
        mock_user.permissions = []  # 无event:delete权限
        info.context = Mock(user=mock_user)

        mutation = DeleteEvent()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, event_id=1)

        # 应该返回授权错误
        error_msg = str(exc_info.value).lower()
        assert (
            "permission" in error_msg
            or "authorized" in error_msg
            or "forbidden" in error_msg
            or "权限" in error_msg
        ), f"Expected permission error, got: {exc_info.value}"

    def test_batch_delete_events_has_limit(self):
        """
        测试批量删除事件有大小限制

        应该:
        - 限制批量操作的大小
        - 防止资源耗尽攻击
        """
        from backend.gql_api.mutations.event_mutations import BatchDeleteEvents

        info = Mock()
        info.context = Mock(user=Mock(id=1, username="testuser"))

        mutation = BatchDeleteEvents()

        # 尝试批量删除1000个事件(应该被限制)
        event_ids = list(range(1, 1001))

        # 应该抛出批量大小限制错误
        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, ids=event_ids)

        error_msg = str(exc_info.value).lower()
        assert (
            "too many" in error_msg
            or "limit" in error_msg
            or "exceed" in error_msg
            or "maximum" in error_msg
            or "限制" in error_msg
        ), f"Expected batch size limit error, got: {exc_info.value}"


class TestGameMutationsAuth:
    """测试游戏mutations的权限检查"""

    def test_create_game_requires_authentication(self):
        """
        测试创建游戏需要身份验证

        应该:
        - 检查用户是否已登录
        - 未登录时抛出认证错误
        """
        from backend.gql_api.mutations.game_mutations import CreateGame

        info = Mock()
        info.context = Mock(user=None)

        mutation = CreateGame()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, gid=90000001, name="Test Game", ods_db="ieu_ods")

        error_msg = str(exc_info.value).lower()
        assert (
            "authentication" in error_msg
            or "unauthorized" in error_msg
            or "login" in error_msg
            or "未登录" in error_msg
            or "认证" in error_msg
        ), f"Expected authentication error, got: {exc_info.value}"

    def test_create_game_requires_permission(self):
        """
        测试创建游戏需要相应权限

        应该:
        - 检查用户是否有game:write权限
        - 无权限时抛出授权错误
        """
        from backend.gql_api.mutations.game_mutations import CreateGame

        info = Mock()
        # 模拟已登录但无权限的用户
        mock_user = Mock(id=1, username="testuser")
        mock_user.permissions = []  # 无game:write权限
        info.context = Mock(user=mock_user)

        mutation = CreateGame()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, gid=90000001, name="Test Game", ods_db="ieu_ods")

        error_msg = str(exc_info.value).lower()
        assert (
            "permission" in error_msg
            or "authorized" in error_msg
            or "forbidden" in error_msg
            or "权限" in error_msg
        ), f"Expected permission error, got: {exc_info.value}"

    def test_update_game_requires_permission(self):
        """
        测试更新游戏需要相应权限
        """
        from backend.gql_api.mutations.game_mutations import UpdateGame

        info = Mock()
        mock_user = Mock(id=1, username="testuser")
        mock_user.permissions = []
        info.context = Mock(user=mock_user)

        mutation = UpdateGame()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, game_gid=90000001, name="Updated Game")

        error_msg = str(exc_info.value).lower()
        assert (
            "permission" in error_msg
            or "authorized" in error_msg
            or "forbidden" in error_msg
            or "权限" in error_msg
        ), f"Expected permission error, got: {exc_info.value}"

    def test_delete_game_requires_permission(self):
        """
        测试删除游戏需要相应权限

        应该:
        - 检查用户是否有game:delete权限
        - 这是高危操作, 需要特殊权限
        """
        from backend.gql_api.mutations.game_mutations import DeleteGame

        info = Mock()

        # 创建一个Mock对象, 其permissions是空列表(不支持'in'操作)
        class MockUser:
            id = 1
            username = "testuser"
            permissions = []  # 空列表, 所以'delete' not in permissions 为True

        mock_user = MockUser()
        # 确保permissions属性真实存在
        info.context = Mock()
        info.context.user = mock_user

        mutation = DeleteGame()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, gid=90000001, confirm=False)

        error_msg = str(exc_info.value).lower()
        assert (
            "permission" in error_msg
            or "authorized" in error_msg
            or "forbidden" in error_msg
            or "权限" in error_msg
        ), f"Expected permission error, got: {exc_info.value}"


class TestParameterMutationsAuth:
    """测试参数mutations的权限检查"""

    def test_create_parameter_requires_authentication(self):
        """
        测试创建参数需要身份验证
        """
        from backend.gql_api.mutations.parameter_mutations import CreateParameter

        info = Mock()
        # 确保user确实是None
        info.context = Mock()
        info.context.user = None

        mutation = CreateParameter()

        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, event_id=1, param_name="test_param", param_name_cn="测试参数")

        error_msg = str(exc_info.value).lower()
        assert (
            "authentication" in error_msg
            or "unauthorized" in error_msg
            or "login" in error_msg
            or "未登录" in error_msg
        ), f"Expected authentication error, got: {exc_info.value}"


class TestBatchMutationsAuth:
    """测试批量mutations的权限检查"""

    def test_batch_create_games_has_limit(self):
        """
        测试批量创建游戏有大小限制

        应该:
        - 限制批量操作的大小
        - 防止资源耗尽攻击
        """
        from backend.gql_api.mutations.batch_mutations import BatchCreateGames

        info = Mock()
        mock_user = Mock(id=1, username="testuser")
        mock_user.permissions = ['game:write']
        info.context = Mock(user=mock_user)

        mutation = BatchCreateGames()

        # 尝试批量创建1000个游戏(应该被限制)
        games_input = [
            {"gid": 90000000 + i, "name": f"Game {i}", "ods_db": "ieu_ods"} for i in range(1000)
        ]

        # 应该抛出批量大小限制错误
        with pytest.raises(Exception) as exc_info:
            mutation.mutate(info, games=games_input)

        error_msg = str(exc_info.value).lower()
        assert (
            "too many" in error_msg
            or "limit" in error_msg
            or "exceed" in error_msg
            or "maximum" in error_msg
            or "限制" in error_msg
        ), f"Expected batch size limit error, got: {exc_info.value}"


class TestMutationAuthDecorators:
    """测试mutations有认证装饰器"""

    def test_all_mutations_have_auth_check(self):
        """
        测试所有mutation类都有认证检查

        这是一个元测试, 检查代码结构. 
        当前应该失败, 因为还没有添加认证检查. 
        """
        mutation_files = [
            'backend/gql_api/mutations/event_mutations.py',
            'backend/gql_api/mutations/game_mutations.py',
            'backend/gql_api/mutations/parameter_mutations.py',
            'backend/gql_api/mutations/batch_mutations.py',
            'backend/gql_api/mutations/category_mutations.py',
            'backend/gql_api/mutations/join_config_mutations.py',
            'backend/gql_api/mutations/node_mutations.py',
            'backend/gql_api/mutations/hql_mutations.py',
            'backend/gql_api/mutations/template_mutations.py',
            'backend/gql_api/mutations/field_builder_mutations.py',
        ]

        mutations_without_auth = []

        for file_path in mutation_files:
            full_path = file_path

            if not os.path.exists(full_path):
                print(f"警告: 文件不存在 {full_path}")
                continue

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找所有mutation类
            try:
                tree = ast.parse(content, file_path)
            except SyntaxError as e:
                print(f"语法错误 {file_path}: {e}")
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 检查是否是Mutation类(类名以Mutation结尾或继承graphene.Mutation)
                    is_mutation = node.name.endswith('Mutation') or any(
                        base.id == 'Mutation' if isinstance(base, ast.Name) else False
                        for base in node.bases
                    )

                    if is_mutation:
                        # 检查是否有mutate方法
                        has_mutate = any(
                            method.name == 'mutate'
                            for method in node.body
                            if isinstance(method, ast.FunctionDef)
                        )

                        if has_mutate:
                            # 检查mutate方法中是否有认证检查
                            mutate_method = next(
                                method
                                for method in node.body
                                if isinstance(method, ast.FunctionDef) and method.name == 'mutate'
                            )

                            # 检查是否有认证装饰器
                            has_auth_check = False

                            # 检查装饰器
                            if hasattr(mutate_method, 'decorator_list'):
                                for decorator in mutate_method.decorator_list:
                                    deco_source = ast.get_source_segment(content, decorator)
                                    if deco_source and any(
                                        keyword in deco_source.lower()
                                        for keyword in [
                                            'authenticated',
                                            'require_permission',
                                            'require_auth',
                                            'login_required',
                                            'permission_required',
                                        ]
                                    ):
                                        has_auth_check = True
                                        break

                            # 如果没有装饰器, 检查方法体内的前10行
                            if not has_auth_check:
                                for stmt in mutate_method.body[:10]:
                                    stmt_source = ast.get_source_segment(content, stmt)
                                    if stmt_source:
                                        if any(
                                            keyword in stmt_source.lower()
                                            for keyword in [
                                                'authenticate',
                                                'authorization',
                                                'permission',
                                                'check_auth',
                                                'require_auth',
                                                'info.context.user',
                                                'context.user',
                                                'get_current_user',
                                                'login_required',
                                            ]
                                        ):
                                            has_auth_check = True
                                            break

                            if not has_auth_check:
                                mutations_without_auth.append(
                                    {'file': file_path, 'class': node.name, 'line': node.lineno}
                                )

        if mutations_without_auth:
            print("\n" + "=" * 70)
            print("缺少认证检查的Mutation类:")
            print("=" * 70)
            for item in mutations_without_auth:
                print(f"  ❌ {item['file']}:{item['line']} - {item['class']}")
            print("=" * 70)
            print(f"\n共发现 {len(mutations_without_auth)} 个mutation缺少认证检查")
            print("这违反了安全原则: 所有写操作必须验证用户身份和权限")

            pytest.fail(
                f"发现 {len(mutations_without_auth)} 个mutation缺少认证检查\n"
                f"这违反了安全原则: 所有写操作必须验证用户身份和权限"
            )
        else:
            print("\n✅ 所有mutations都有认证检查")


class TestSecurityHeaders:
    """测试安全相关配置"""

    def test_api_has_context_validation(self):
        """
        测试API验证GraphQL context

        应该:
        - context包含user信息
        - context包含权限信息
        """
        # TODO: 添加实际的context验证测试
        pytest.skip("需要实际的GraphQL context配置")

    def test_sensitive_operations_require_special_permission(self):
        """
        测试敏感操作需要特殊权限

        敏感操作包括:
        - 删除游戏（game:delete）
        - 批量删除（batch:delete）
        - 修改HQL（hql:write）
        """
        # TODO: 实现敏感操作权限检查
        pytest.skip("需要实现敏感操作权限检查")


class TestRateLimiting:
    """测试速率限制"""

    def test_batch_operations_have_size_limits(self):
        """
        测试批量操作有大小限制

        防止:
        - 内存耗尽
        - 数据库连接耗尽
        - DoS攻击
        """
        # TODO: 实现批量操作大小限制
        pytest.skip("需要实现批量操作大小限制")

    def test_api_has_rate_limiting(self):
        """
        测试API有速率限制

        防止:
        - 暴力攻击
        - API滥用
        """
        # TODO: 实现API速率限制
        pytest.skip("需要实现API速率限制")


class TestInputValidation:
    """测试输入验证安全"""

    def test_mutations_validate_input(self):
        """
        测试所有mutations验证输入

        应该:
        - 使用Pydantic schema验证
        - 检查SQL注入
        - 检查XSS攻击
        """
        # TODO: 实现输入验证测试
        pytest.skip("需要实现输入验证测试")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

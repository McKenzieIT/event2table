"""
TDD测试: 验证JoinConfig使用game_gid而非game_id

这是TDD的RED阶段 - 测试应该失败, 因为当前代码使用了game_id
"""

import pytest
from unittest.mock import Mock, patch


def test_join_config_query_uses_game_gid():
    """
    测试JoinConfig查询使用game_gid而非game_id

    应该:
    - SQL查询使用 game_gid
    - 参数名使用 game_gid

    这个测试会先失败, 因为当前使用了game_id
    """
    from backend.gql_api.queries.join_config_queries import JoinConfigQueries

    info = Mock()
    resolver = JoinConfigQueries()

    # 测试SQL查询应该使用game_gid
    with patch('backend.core.data_access.Repositories') as mock_repos:
        mock_repo = Mock()
        mock_repo.fetch_all.return_value = []
        mock_repos.join_configs.return_value = mock_repo

        # 调用resolver
        result = resolver.resolve_join_configs(info, game_gid=10000147)

        # 验证fetch_all被调用
        assert mock_repo.fetch_all.called, "fetch_all should be called"

        # 获取SQL查询语句
        call_args = mock_repo.fetch_all.call_args
        sql_query = call_args[0][0] if call_args[0] else ""

        # 验证SQL使用game_gid而非game_id
        assert (
            'game_gid' in sql_query.lower()
        ), f"SQL should use 'game_gid', not 'game_id'. Query: {sql_query}"

        assert (
            'game_id' not in sql_query.lower()
        ), f"SQL should NOT use 'game_id'. Query: {sql_query}"

        # 验证参数正确传递
        params = call_args[0][1] if len(call_args[0]) > 1 else []
        assert 10000147 in params, f"game_gid parameter should be in params. Got: {params}"


def test_join_config_type_uses_game_gid():
    """
    测试JoinConfig GraphQL类型使用game_gid
    """
    from backend.gql_api.types.join_config_type import JoinConfigType

    # 验证字段存在且命名正确
    assert hasattr(JoinConfigType, 'game_gid'), "JoinConfigType should have 'game_gid' field"

    # 验证没有game_id字段
    assert not hasattr(JoinConfigType, 'game_id'), "JoinConfigType should NOT have 'game_id' field"


def test_join_config_resolver_parameter_name():
    """
    测试JoinConfig resolver参数名使用game_gid
    """
    from backend.gql_api.queries.join_config_queries import JoinConfigQueries
    import inspect

    # 获取方法签名
    method = JoinConfigQueries.resolve_join_configs
    sig = inspect.signature(method)

    # 验证参数名包含game_gid
    params = list(sig.parameters.keys())
    assert (
        'game_gid' in params
    ), f"Resolver should have 'game_gid' parameter. Current params: {params}"

    # 验证没有game_id参数
    assert (
        'gameId' not in params and 'game_id' not in params
    ), f"Resolver should NOT have 'gameId' or 'game_id' parameter. Current params: {params}"

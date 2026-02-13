"""
Common utilities 模块测试

测试通用业务逻辑函数：
- 表单处理 (validate_form_fields, parse_form_list_fields)
- 缓存管理 (clear_entity_caches)
- 数据获取 (get_reference_data)
- 表名生成 (generate_dwd_table_names)

TDD Phase: Red - 先写测试，验证功能正确性
"""

import pytest
from flask import Flask, request


@pytest.fixture
def app():
    """创建测试Flask应用"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'

    @app.route('/test-form', methods=['POST'])
    def test_form():
        from backend.core.common import validate_form_fields

        field_defs = [
            {'name': 'game_gid', 'required': True, 'alias': '游戏ID'},
            {'name': 'event_name', 'required': True, 'alias': '事件名'},
            {'name': 'optional_field', 'required': False}
        ]

        is_valid, values, error = validate_form_fields(field_defs)

        if is_valid:
            return {'success': True, 'values': values}, 200
        else:
            return {'success': False, 'error': error}, 400

    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestValidateFormFields:
    """测试 validate_form_fields 函数"""

    def test_validate_all_required_fields_present(self, client):
        """测试所有必填字段都存在 - 应该通过"""
        response = client.post('/test-form', data={
            'game_gid': '10000147',
            'event_name': 'login',
            'optional_field': 'optional value'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['values']['game_gid'] == '10000147'
        assert data['values']['event_name'] == 'login'

    def test_validate_missing_required_field(self, client):
        """测试缺少必填字段 - 应该失败"""
        response = client.post('/test-form', data={
            'game_gid': '10000147'
            # 缺少 event_name
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert '事件名' in data['error'] or '必填' in data['error']

    def test_validate_fields_with_stripping(self, client):
        """测试字段值自动去除空白"""
        response = client.post('/test-form', data={
            'game_gid': '  10000147  ',
            'event_name': '  login  '
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['values']['game_gid'] == '10000147'
        assert data['values']['event_name'] == 'login'

    def test_validate_empty_field(self, client):
        """测试空字符串字段验证"""
        response = client.post('/test-form', data={
            'game_gid': '10000147',
            'event_name': '   '  # 只有空白
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_validate_custom_error_message(self, app):
        """测试自定义错误消息"""
        with app.test_request_context('/test', method='POST', data={
            'game_gid': '10000147'
        }):
            from backend.core.common import validate_form_fields

            field_defs = [
                {'name': 'game_gid', 'required': True},
                {'name': 'event_name', 'required': True}
            ]

            is_valid, values, error = validate_form_fields(
                field_defs,
                error_message="自定义错误：请填写所有字段"
            )

            assert not is_valid
            assert "自定义错误" in error

    def test_validate_optional_fields(self, client):
        """测试可选字段可以省略"""
        response = client.post('/test-form', data={
            'game_gid': '10000147',
            'event_name': 'login'
            # optional_field 不提供
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestParseFormListFields:
    """测试 parse_form_list_fields 函数"""

    def test_parse_array_fields(self, app):
        """测试解析数组字段"""
        with app.test_request_context('/test', method='POST', data={
            'param_name[]': ['name1', 'name2', 'name3'],
            'param_type[]': ['1', '2', '3']
        }):
            from backend.core.common import parse_form_list_fields

            fields = parse_form_list_fields(['param_name', 'param_type'])

            assert 'param_name' in fields
            assert 'param_type' in fields
            assert fields['param_name'] == ['name1', 'name2', 'name3']
            assert fields['param_type'] == ['1', '2', '3']

    def test_parse_with_stripping(self, app):
        """测试数组字段值自动去除空白"""
        with app.test_request_context('/test', method='POST', data={
            'param_name[]': ['  name1  ', '  name2  ']
        }):
            from backend.core.common import parse_form_list_fields

            fields = parse_form_list_fields(['param_name'], strip_values=True)

            assert fields['param_name'] == ['name1', 'name2']

    def test_parse_empty_array(self, app):
        """测试空数组字段"""
        with app.test_request_context('/test', method='POST', data={}):
            from backend.core.common import parse_form_list_fields

            fields = parse_form_list_fields(['param_name'])

            assert fields['param_name'] == []

    def test_parse_multiple_fields(self, app):
        """测试解析多个数组字段"""
        with app.test_request_context('/test', method='POST', data={
            'param_name[]': ['name1', 'name2'],
            'param_type[]': ['1', '2'],
            'param_desc[]': ['desc1', 'desc2']
        }):
            from backend.core.common import parse_form_list_fields

            fields = parse_form_list_fields(['param_name', 'param_type', 'param_desc'])

            assert len(fields) == 3
            assert len(fields['param_name']) == 2
            assert len(fields['param_type']) == 2
            assert len(fields['param_desc']) == 2


class TestClearEntityCaches:
    """测试 clear_entity_caches 函数"""

    def test_clear_event_cache(self, app):
        """测试清理事件缓存"""
        with app.app_context():
            from backend.core.common import clear_entity_caches

            # 应该不抛出错误（即使缓存系统不可用）
            clear_entity_caches('event', 123, game_gid=10000147)

    def test_clear_game_cache(self, app):
        """测试清理游戏缓存"""
        with app.app_context():
            from backend.core.common import clear_entity_caches

            clear_entity_caches('game', 456)

    def test_clear_parameter_cache(self, app):
        """测试清理参数缓存"""
        with app.app_context():
            from backend.core.common import clear_entity_caches

            clear_entity_caches('parameter', 789, game_gid=10000147)

    def test_clear_unknown_entity_type(self, app):
        """测试清理未知实体类型 - 应该记录警告但不崩溃"""
        with app.app_context():
            from backend.core.common import clear_entity_caches

            # 未知类型应该记录警告但不抛出异常
            clear_entity_caches('unknown_type', 999)

    def test_clear_cache_with_error_handling(self, app):
        """测试缓存清理的错误处理"""
        with app.app_context():
            from backend.core.common import clear_entity_caches

            # 即使缓存系统出错也不应该抛出异常
            clear_entity_caches('event', 123, game_gid=10000147)


class TestGetReferenceData:
    """测试 get_reference_data 函数"""

    def test_get_games_data(self):
        """测试获取游戏列表"""
        from backend.core.common import get_reference_data

        result = get_reference_data(['games'])

        assert 'games' in result
        assert isinstance(result['games'], list)

    def test_get_event_categories(self):
        """测试获取事件分类"""
        from backend.core.common import get_reference_data

        result = get_reference_data(['event_categories'])

        assert 'event_categories' in result
        assert isinstance(result['event_categories'], list)

    def test_get_multiple_data_types(self):
        """测试获取多种参考数据"""
        from backend.core.common import get_reference_data

        result = get_reference_data(['games', 'event_categories', 'param_types'])

        assert 'games' in result
        assert 'event_categories' in result
        assert 'param_types' in result

    def test_get_unknown_data_type(self):
        """测试获取未知数据类型"""
        from backend.core.common import get_reference_data

        result = get_reference_data(['unknown_type'])

        # 未知类型应该被忽略
        assert 'unknown_type' not in result or result.get('unknown_type') is None


class TestGenerateDWDTableNames:
    """测试 generate_dwd_table_names 函数"""

    def test_generate_table_names_basic(self):
        """测试基本表名生成"""
        from backend.core.common import generate_dwd_table_names

        game = {
            'gid': 10000147,
            'ods_db': 'ieu_ods'
        }

        result = generate_dwd_table_names(game, 'login')

        assert 'source_table' in result
        assert 'target_table' in result
        assert 'dwd_prefix' in result

        assert result['source_table'] == 'ieu_ods.ods_10000147_all_view'
        assert result['target_table'] == 'ieu_cdm.v_dwd_10000147_login_di'
        assert result['dwd_prefix'] == 'ieu_cdm'

    def test_generate_table_names_overwrite_ods_db(self):
        """测试覆盖ODS数据库名"""
        from backend.core.common import generate_dwd_table_names

        game = {
            'gid': 10000147,
            'ods_db': 'ieu_ods'
        }

        result = generate_dwd_table_names(game, 'login', ods_db='custom_db')

        assert result['source_table'] == 'custom_db.ods_10000147_all_view'
        assert result['dwd_prefix'] == 'custom_db'

    def test_generate_table_names_overseas_game(self):
        """测试海外游戏表名生成（非ieu_ods）"""
        from backend.core.common import generate_dwd_table_names

        game = {
            'gid': 20000123,
            'ods_db': 'oversea_ods'
        }

        result = generate_dwd_table_names(game, 'register')

        assert result['source_table'] == 'oversea_ods.ods_20000123_all_view'
        assert result['dwd_prefix'] == 'oversea_ods'  # 海外游戏使用原ods_db
        assert result['target_table'] == 'oversea_ods.v_dwd_20000123_register_di'

    def test_generate_table_names_with_dots_in_event_name(self):
        """测试事件名包含点号的处理"""
        from backend.core.common import generate_dwd_table_names

        game = {
            'gid': 10000147,
            'ods_db': 'ieu_ods'
        }

        result = generate_dwd_table_names(game, 'login.success')

        # 点号应该被替换为下划线
        assert result['target_table'] == 'ieu_cdm.v_dwd_10000147_login_success_di'

    def test_generate_table_names_consistency(self):
        """测试相同输入产生相同表名"""
        from backend.core.common import generate_dwd_table_names

        game = {'gid': 10000147, 'ods_db': 'ieu_ods'}

        result1 = generate_dwd_table_names(game, 'login')
        result2 = generate_dwd_table_names(game, 'login')

        assert result1['source_table'] == result2['source_table']
        assert result1['target_table'] == result2['target_table']

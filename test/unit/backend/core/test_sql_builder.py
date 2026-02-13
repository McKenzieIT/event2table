"""
SQL Builder 模块测试

测试SQL构建通用工具函数：
- 聚合函数构建器 (AggregateFunctionBuilder)
- 字段处理工具 (get_field_name, normalize_field_list)
- JOIN构建器 (JoinBuilder)
- GROUP BY构建器 (GroupByBuilder)

TDD Phase: Red - 先写测试，验证SQL生成正确性
"""

import pytest


class TestAggregateFunctionBuilder:
    """测试 AggregateFunctionBuilder 类"""

    def test_build_count(self):
        """测试COUNT聚合函数"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('COUNT', 'user_id', 'user_count')

        assert sql == 'COUNT(user_id) AS user_count'

    def test_build_count_with_wildcard(self):
        """测试COUNT(*)"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('COUNT', None, 'total_count')

        assert sql == 'COUNT(*) AS total_count'

    def test_build_sum(self):
        """测试SUM聚合函数"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('SUM', 'amount', 'total_amount')

        assert sql == 'SUM(CAST(amount AS DOUBLE)) AS total_amount'

    def test_build_avg(self):
        """测试AVG聚合函数"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('AVG', 'score', 'avg_score')

        assert sql == 'AVG(CAST(score AS DOUBLE)) AS avg_score'

    def test_build_min(self):
        """测试MIN聚合函数"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('MIN', 'price', 'min_price')

        assert sql == 'MIN(price) AS min_price'

    def test_build_max(self):
        """测试MAX聚合函数"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('MAX', 'price', 'max_price')

        assert sql == 'MAX(price) AS max_price'

    def test_build_count_distinct(self):
        """测试COUNT DISTINCT聚合函数"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('COUNT_DISTINCT', 'user_id', 'unique_users')

        assert sql == 'COUNT(DISTINCT user_id) AS unique_users'

    def test_build_case_insensitive(self):
        """测试函数名大小写不敏感"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql1 = AggregateFunctionBuilder.build_aggregate_sql('count', 'id', 'count')
        sql2 = AggregateFunctionBuilder.build_aggregate_sql('Count', 'id', 'count')
        sql3 = AggregateFunctionBuilder.build_aggregate_sql('COUNT', 'id', 'count')

        # 应该都使用COUNT模板
        assert sql1 == sql2 == sql3

    def test_build_unknown_function(self):
        """测试未知函数使用默认格式"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        sql = AggregateFunctionBuilder.build_aggregate_sql('PERCENTILE', 'value', 'p95')

        assert sql == 'PERCENTILE(value) AS p95'

    def test_custom_builder(self):
        """测试自定义构建器"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        def custom_builder(func, field, alias):
            return f'CUSTOM_{func}({field}) AS {alias}'

        sql = AggregateFunctionBuilder.build_aggregate_sql(
            'MYFUNC', 'field', 'alias',
            custom_builder=custom_builder
        )

        assert sql == 'CUSTOM_MYFUNC(field) AS alias'

    def test_register_aggregate_function(self):
        """测试注册自定义聚合函数"""
        from backend.core.sql_builder import AggregateFunctionBuilder

        # 注册自定义函数
        def build_percentile(field, alias):
            return f'PERCENTILE({field}, 0.95) AS {alias}'

        AggregateFunctionBuilder.register_aggregate_function('PERCENTILE', build_percentile)

        sql = AggregateFunctionBuilder.build_aggregate_sql('PERCENTILE', 'value', 'p95')

        assert sql == 'PERCENTILE(value, 0.95) AS p95'


class TestGetFieldName:
    """测试 get_field_name 函数"""

    def test_get_fieldname_key(self):
        """测试使用fieldName键"""
        from backend.core.sql_builder import get_field_name

        field = {'fieldName': 'user_id', 'alias': 'uid'}

        assert get_field_name(field) == 'user_id'

    def test_get_fallback_key(self):
        """测试使用fallback键"""
        from backend.core.sql_builder import get_field_name

        field = {'name': 'user_id', 'alias': 'uid'}

        assert get_field_name(field) == 'user_id'

    def test_get_fieldname_priority(self):
        """测试fieldName优先于name"""
        from backend.core.sql_builder import get_field_name

        field = {'fieldName': 'user_id', 'name': 'uid'}

        # fieldName优先
        assert get_field_name(field) == 'user_id'

    def test_get_custom_fallback(self):
        """测试自定义fallback键"""
        from backend.core.sql_builder import get_field_name

        field = {'custom_key': 'value', 'name': 'fallback'}

        assert get_field_name(field, fallback_key='custom_key') == 'value'

    def test_get_fieldname_empty(self):
        """测试空字段"""
        from backend.core.sql_builder import get_field_name

        field = {}

        assert get_field_name(field) == ''


class TestNormalizeFieldList:
    """测试 normalize_field_list 函数"""

    def test_normalize_simple_fields(self):
        """测试标准化简单字段列表"""
        from backend.core.sql_builder import normalize_field_list

        fields = [
            {'fieldName': 'user_id', 'alias': 'uid', 'type': 'int'}
        ]

        normalized = normalize_field_list(fields)

        assert len(normalized) == 1
        assert normalized[0] == {
            'name': 'user_id',
            'alias': 'uid',
            'type': 'int'
        }

    def test_normalize_with_fieldname_key(self):
        """测试使用fieldName键"""
        from backend.core.sql_builder import normalize_field_list

        fields = [
            {'fieldName': 'x', 'alias': 'y'}
        ]

        normalized = normalize_field_list(fields)

        assert normalized[0]['name'] == 'x'
        assert normalized[0]['alias'] == 'y'

    def test_normalize_with_name_key(self):
        """测试使用name键"""
        from backend.core.sql_builder import normalize_field_list

        fields = [
            {'name': 'field_a', 'alias': 'alias_a'}
        ]

        normalized = normalize_field_list(fields)

        assert normalized[0]['name'] == 'field_a'

    def test_normalize_default_values(self):
        """测试默认值"""
        from backend.core.sql_builder import normalize_field_list

        fields = [{'fieldName': 'field_x'}]

        normalized = normalize_field_list(fields)

        assert normalized[0]['name'] == 'field_x'
        # alias默认为name
        assert normalized[0]['alias'] == 'field_x'
        # type默认为string
        assert normalized[0]['type'] == 'string'

    def test_normalize_with_fieldtype(self):
        """测试使用fieldType键"""
        from backend.core.sql_builder import normalize_field_list

        fields = [
            {'fieldName': 'x', 'fieldType': 'int'}
        ]

        normalized = normalize_field_list(fields)

        assert normalized[0]['type'] == 'int'

    def test_normalize_multiple_fields(self):
        """测试标准化多个字段"""
        from backend.core.sql_builder import normalize_field_list

        fields = [
            {'fieldName': 'a', 'alias': 'alias_a'},
            {'name': 'b', 'type': 'int'},
            {'fieldName': 'c'}
        ]

        normalized = normalize_field_list(fields)

        assert len(normalized) == 3
        assert normalized[0]['name'] == 'a'
        assert normalized[1]['name'] == 'b'
        assert normalized[2]['name'] == 'c'


class TestJoinBuilder:
    """测试 JoinBuilder 类"""

    def test_build_inner_join(self):
        """测试INNER JOIN"""
        from backend.core.sql_builder import JoinBuilder

        sql = JoinBuilder.build_join_clause(
            'INNER', 'events', 'users', 'events.user_id = users.id'
        )

        assert sql == 'INNER JOIN users ON events.user_id = users.id'

    def test_build_left_join(self):
        """测试LEFT JOIN"""
        from backend.core.sql_builder import JoinBuilder

        sql = JoinBuilder.build_join_clause(
            'LEFT', 'events', 'users', 'events.user_id = users.id'
        )

        assert sql == 'LEFT OUTER JOIN users ON events.user_id = users.id'

    def test_build_right_join(self):
        """测试RIGHT JOIN"""
        from backend.core.sql_builder import JoinBuilder

        sql = JoinBuilder.build_join_clause(
            'RIGHT', 'events', 'users', 'events.user_id = users.id'
        )

        assert sql == 'RIGHT OUTER JOIN users ON events.user_id = users.id'

    def test_build_full_join(self):
        """测试FULL JOIN"""
        from backend.core.sql_builder import JoinBuilder

        sql = JoinBuilder.build_join_clause(
            'FULL', 'events', 'users', 'events.user_id = users.id'
        )

        assert sql == 'FULL OUTER JOIN users ON events.user_id = users.id'

    def test_build_cross_join(self):
        """测试CROSS JOIN"""
        from backend.core.sql_builder import JoinBuilder

        sql = JoinBuilder.build_join_clause(
            'CROSS', 'events', 'users', 'events.user_id = users.id'
        )

        assert sql == 'CROSS JOIN users ON events.user_id = users.id'

    def test_build_join_case_insensitive(self):
        """测试JOIN类型大小写不敏感"""
        from backend.core.sql_builder import JoinBuilder

        sql1 = JoinBuilder.build_join_clause('left', 'A', 'B', 'A.id = B.id')
        sql2 = JoinBuilder.build_join_clause('LEFT', 'A', 'B', 'A.id = B.id')

        assert sql1 == sql2

    def test_build_join_default_inner(self):
        """测试默认INNER JOIN"""
        from backend.core.sql_builder import JoinBuilder

        sql = JoinBuilder.build_join_clause(
            'UNKNOWN', 'A', 'B', 'A.id = B.id'
        )

        # 未知类型默认为INNER JOIN
        assert 'INNER JOIN' in sql


class TestGroupByBuilder:
    """测试 GroupByBuilder 类"""

    def test_build_group_by_single_field(self):
        """测试单字段GROUP BY"""
        from backend.core.sql_builder import GroupByBuilder

        fields = [{'fieldName': 'region'}]

        sql = GroupByBuilder.build_group_by_clause(fields)

        assert sql == 'GROUP BY region'

    def test_build_group_by_multiple_fields(self):
        """测试多字段GROUP BY"""
        from backend.core.sql_builder import GroupByBuilder

        fields = [
            {'fieldName': 'region'},
            {'fieldName': 'category'}
        ]

        sql = GroupByBuilder.build_group_by_clause(fields)

        assert sql == 'GROUP BY region, category'

    def test_build_group_by_empty_fields(self):
        """测试空字段列表"""
        from backend.core.sql_builder import GroupByBuilder

        sql = GroupByBuilder.build_group_by_clause([])

        assert sql == ''

    def test_build_group_by_with_name_key(self):
        """测试使用name键"""
        from backend.core.sql_builder import GroupByBuilder

        fields = [{'name': 'user_type'}]

        sql = GroupByBuilder.build_group_by_clause(fields)

        assert sql == 'GROUP BY user_type'

    def test_build_group_by_with_empty_fieldnames(self):
        """测试过滤空字段名"""
        from backend.core.sql_builder import GroupByBuilder

        fields = [
            {'fieldName': 'region'},
            {'fieldName': ''},  # 空字段名应被过滤
            {'fieldName': 'category'}
        ]

        sql = GroupByBuilder.build_group_by_clause(fields)

        assert sql == 'GROUP BY region, category'

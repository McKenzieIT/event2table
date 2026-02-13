"""
PerformanceAnalyzer 扩展单元测试

补充测试以达到90%+覆盖率目标
遵循TDD原则
"""

import pytest
from backend.services.hql.validators.performance_analyzer import HQLPerformanceAnalyzer


class TestPerformanceAnalyzerExtended:
    """PerformanceAnalyzer扩展测试套件"""

    def test_analyze_with_missing_partition_filter(self):
        """测试缺少分区过滤时的性能分析"""
        analyzer = HQLPerformanceAnalyzer()

        hql = """
        SELECT role_id, zone_id
        FROM ods_login
        WHERE zone_id > 1
        """

        report = analyzer.analyze(hql)

        assert report.score < 60  # 应该有低分
        assert any("partition" in issue.message.lower() for issue in report.issues)

    def test_analyze_with_select_star(self):
        """测试使用SELECT *时的性能分析"""
        analyzer = HQLPerformanceAnalyzer()

        hql = "SELECT * FROM ods_login WHERE ds = '${ds}'"

        report = analyzer.analyze(hql)

        assert report.score < 80  # 应该有中等或低分
        assert any("select *" in issue.message.lower() for issue in report.issues)

    def test_analyze_with_multiple_joins(self):
        """测试多JOIN时的性能分析"""
        analyzer = HQLPerformanceAnalyzer()

        # 使用单行HQL以确保正确解析
        hql = "SELECT a.role_id FROM table_a a JOIN table_b b ON a.id = b.id JOIN table_c c ON b.id = c.id JOIN table_d d ON c.id JOIN table_e e ON d.id = e.id WHERE ds = '${ds}'"

        report = analyzer.analyze(hql)

        # 5个JOIN应该触发警告（>3个）
        assert report.score < 85
        assert len(report.issues) > 0
        assert any("join" in issue.message.lower() for issue in report.issues)

    def test_analyze_with_cross_join(self):
        """测试CROSS JOIN时的性能分析"""
        analyzer = HQLPerformanceAnalyzer()

        hql = """
        SELECT a.*, b.*
        FROM table_a a
        CROSS JOIN table_b b
        WHERE ds = '${ds}'
        """

        report = analyzer.analyze(hql)

        # CROSS JOIN应该大幅降低分数
        assert report.score < 60
        assert any("cross join" in issue.message.lower() for issue in report.issues)

    def test_analyze_optimized_hql(self):
        """测试优化后的HQL应该有高分"""
        analyzer = HQLPerformanceAnalyzer()

        hql = """
        SELECT
          role_id,
          zone_id,
          server_id
        FROM ieu_ods.ods_10000147_all_view
        WHERE ds = '${ds}'
          AND event = 'login'
        """

        report = analyzer.analyze(hql)

        # 优化的HQL应该有高分
        assert report.score >= 90
        assert len(report.issues) == 0 or all(issue.type.value == "info" for issue in report.issues)

    def test_score_calculation_with_multiple_issues(self):
        """测试多个问题同时存在时的分数计算"""
        analyzer = HQLPerformanceAnalyzer()

        # 包含多个问题的HQL
        hql = "SELECT * FROM ods_login WHERE zone_id > 1"

        report = analyzer.analyze(hql)

        # 应该有多个问题
        assert len(report.issues) >= 2
        # 分数应该很低
        assert report.score < 50

    def test_issue_type_classification(self):
        """测试问题类型分类"""
        analyzer = HQLPerformanceAnalyzer()

        # 测试error类型问题
        hql_no_partition = "SELECT role_id FROM ods_login"
        report_no_partition = analyzer.analyze(hql_no_partition)

        assert any(issue.type.value in ["error", "warning"] for issue in report_no_partition.issues)

        # 测试warning类型问题
        hql_select_star = "SELECT * FROM ods_login WHERE ds = '${ds}'"
        report_select_star = analyzer.analyze(hql_select_star)

        assert any(issue.type.value == "warning" for issue in report_select_star.issues)

    def test_suggestion_generation(self):
        """测试优化建议生成"""
        analyzer = HQLPerformanceAnalyzer()

        # 测试缺少分区过滤的建议
        hql = "SELECT role_id FROM ods_login"
        report = analyzer.analyze(hql)

        partition_issue = next(
            (issue for issue in report.issues if "partition" in issue.message.lower()), None
        )

        if partition_issue:
            assert partition_issue.suggestion is not None
            assert "ds" in partition_issue.suggestion.lower()

    def test_empty_hql_handling(self):
        """测试空HQL的处理"""
        analyzer = HQLPerformanceAnalyzer()

        report = analyzer.analyze("")

        # 空HQL应该有低分
        assert report.score < 70

    def test_analyze_with_subquery(self):
        """测试包含子查询的HQL分析"""
        analyzer = HQLPerformanceAnalyzer()

        hql = """
        SELECT
          role_id,
          (SELECT COUNT(*) FROM table_b WHERE table_b.role_id = table_a.role_id) as count
        FROM table_a
        WHERE ds = '${ds}'
        """

        report = analyzer.analyze(hql)

        # 应该返回报告，不应该抛出异常
        assert report is not None
        assert isinstance(report.score, int)

    def test_performance_score_bounds(self):
        """测试性能分数边界值"""
        analyzer = HQLPerformanceAnalyzer()

        # 测试最差情况
        bad_hql = "SELECT * FROM table_a CROSS JOIN table_b"
        report_bad = analyzer.analyze(bad_hql)
        assert 0 <= report_bad.score <= 100

        # 测试最好情况
        good_hql = """
        SELECT role_id, zone_id
        FROM ieu_ods.ods_10000147_all_view
        WHERE ds = '${ds}' AND event = 'login'
        """
        report_good = analyzer.analyze(good_hql)
        assert 0 <= report_good.score <= 100

    def test_case_sensitivity_detection(self):
        """测试大小写不敏感的关键词检测"""
        analyzer = HQLPerformanceAnalyzer()

        # 测试SELECT *的不同大小写
        hql_variants = ["SELECT * FROM table", "select * from table", "Select * From table"]

        for hql in hql_variants:
            report = analyzer.analyze(hql)
            # 所有变体都应该检测到SELECT *问题
            assert any("select *" in issue.message.lower() for issue in report.issues)

    def test_udf_detection(self):
        """测试自定义函数检测"""
        analyzer = HQLPerformanceAnalyzer()

        hql = """
        SELECT
          role_id,
          custom_function(role_id) as custom_result
        FROM ods_login
        WHERE ds = '${ds}'
        """

        report = analyzer.analyze(hql)

        # 应该检测到UDF
        assert report.metrics.udf_count > 0

    def test_subquery_count_impact(self):
        """测试子查询数量对分数的影响"""
        analyzer = HQLPerformanceAnalyzer()

        # 单个子查询
        hql_single = "SELECT role_id, (SELECT COUNT(*) FROM table_b) FROM table_a"
        report_single = analyzer.analyze(hql_single)

        # 多个子查询
        hql_multiple = """
        SELECT
          role_id,
          (SELECT COUNT(*) FROM table_b),
          (SELECT MAX(*) FROM table_c),
          (SELECT MIN(*) FROM table_d)
        FROM table_a
        """
        report_multiple = analyzer.analyze(hql_multiple)

        # 多个子查询的分数应该更低
        assert report_multiple.score < report_single.score

    def test_high_complexity_detection(self):
        """测试高复杂度HQL检测 - 触发行184和236-237"""
        analyzer = HQLPerformanceAnalyzer()

        # 创建一个非常复杂的HQL（多个JOIN、子查询、UNION等）
        hql = """
        SELECT 
            a.role_id,
            (SELECT COUNT(*) FROM table_b WHERE table_b.id = a.id) as count1,
            (SELECT MAX(*) FROM table_c WHERE c.id = a.id) as max1,
            (SELECT MIN(*) FROM table_d WHERE d.id = a.id) as min1
        FROM table_a a
        JOIN table_b b ON a.id = b.id
        JOIN table_c c ON b.id = c.id
        JOIN table_d d ON c.id = d.id
        JOIN table_e e ON d.id = e.id
        WHERE a.ds = '${ds}'
        """

        report = analyzer.analyze(hql)

        # 验证复杂度被检测为high
        assert report.metrics.complexity == "high"
        # 验证复杂度高的issue被添加
        assert any("complexity" in issue.message.lower() for issue in report.issues)

    def test_multiple_udfs_detection_over_threshold(self):
        """测试多个UDF检测超过阈值 - 触发行267"""
        analyzer = HQLPerformanceAnalyzer()

        # 创建包含多个UDF的HQL
        hql = """
        SELECT
          role_id,
          custom_func1(role_id) as val1,
          custom_func2(role_id) as val2,
          custom_func3(role_id) as val3,
          custom_func4(role_id) as val4
        FROM ods_login
        WHERE ds = '${ds}'
        """

        report = analyzer.analyze(hql)

        # 验证检测到多个UDF
        assert report.metrics.udf_count >= 4
        # 验证多个UDF的issue被添加
        assert any("multiple udf" in issue.message.lower() for issue in report.issues)

    def test_convenience_function_analyze_hql_performance(self):
        """测试便利函数analyze_hql_performance - 触发行286-287"""
        from backend.services.hql.validators.performance_analyzer import analyze_hql_performance

        hql = "SELECT role_id FROM ods_login WHERE ds = '${ds}'"
        report = analyze_hql_performance(hql)

        # 验证返回PerformanceReport
        assert report is not None
        assert hasattr(report, "score")
        assert hasattr(report, "issues")

    def test_format_report_for_api(self):
        """测试format_report_for_api函数 - 触发行300"""
        from backend.services.hql.validators.performance_analyzer import (
            HQLPerformanceAnalyzer,
            format_report_for_api,
        )

        analyzer = HQLPerformanceAnalyzer()
        hql = "SELECT * FROM ods_login WHERE ds = '${ds}'"
        report = analyzer.analyze(hql)

        # 调用format_report_for_api
        api_response = format_report_for_api(report)

        # 验证API响应格式
        assert isinstance(api_response, dict)
        assert "score" in api_response
        assert "issues" in api_response
        assert isinstance(api_response["issues"], list)

        # 验证issue的格式
        if api_response["issues"]:
            issue = api_response["issues"][0]
            assert "type" in issue
            assert "message" in issue

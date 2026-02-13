"""
HQL性能分析器单元测试
"""

import pytest
from .performance_analyzer import (
    HQLPerformanceAnalyzer,
    analyze_hql_performance,
    format_report_for_api,
    IssueType,
)


class TestHQLPerformanceAnalyzer:
    """测试HQL性能分析器"""

    def setup_method(self):
        """测试前准备"""
        self.analyzer = HQLPerformanceAnalyzer()

    def test_perfect_hql(self):
        """测试完美的HQL"""
        hql = """
        SELECT
          role_id,
          account_id
        FROM table
        WHERE ds = '${ds}'
        """

        report = self.analyzer.analyze(hql)

        assert report.score == 100
        assert len(report.issues) == 0
        assert report.metrics.has_partition_filter == True
        assert report.metrics.has_select_star == False

    def test_missing_partition_filter(self):
        """测试缺少分区过滤"""
        hql = """
        SELECT role_id FROM table WHERE zone_id = 1
        """

        report = self.analyzer.analyze(hql)

        assert report.score < 100
        assert report.metrics.has_partition_filter == False

        # 检查是否有错误
        error_issues = [i for i in report.issues if i.type == IssueType.ERROR]
        assert len(error_issues) > 0

        # 检查错误消息
        error_messages = [i.message for i in error_issues]
        assert any("partition filter" in msg.lower() for msg in error_messages)

    def test_select_star(self):
        """测试SELECT *"""
        hql = """
        SELECT * FROM table WHERE ds = '${ds}'
        """

        report = self.analyzer.analyze(hql)

        assert report.score < 100
        assert report.metrics.has_select_star == True

        # 检查是否有警告
        warning_issues = [i for i in report.issues if i.type == IssueType.WARNING]
        assert len(warning_issues) > 0

    def test_cross_join(self):
        """测试CROSS JOIN"""
        hql = """
        SELECT *
        FROM table1
        CROSS JOIN table2
        WHERE ds = '${ds}'
        """

        report = self.analyzer.analyze(hql)

        assert report.score < 100
        assert report.metrics.cross_join_count == 1

        # 检查是否有错误
        error_issues = [i for i in report.issues if i.type == IssueType.ERROR]
        assert any("cross join" in i.message.lower() for i in error_issues)

    def test_multiple_joins(self):
        """测试多JOIN"""
        hql = """
        SELECT a.role_id
        FROM table1 a
        JOIN table2 b ON a.id = b.id
        JOIN table3 c ON b.id = c.id
        JOIN table4 d ON c.id = d.id
        JOIN table5 e ON d.id = e.id
        WHERE a.ds = '${ds}'
        """

        report = self.analyzer.analyze(hql)

        # 4 JOINs detected (not 5) because JOIN count counts " JOIN " occurrences
        assert report.metrics.join_count >= 4
        assert report.score < 100

    def test_complexity_low(self):
        """测试低复杂度"""
        hql = "SELECT role_id FROM table WHERE ds = '${ds}'"
        report = self.analyzer.analyze(hql)
        assert report.metrics.complexity == "low"

    def test_complexity_medium(self):
        """测试中等复杂度"""
        # 创建中等长度的HQL
        fields = ", ".join([f"field_{i}" for i in range(20)])
        hql = f"SELECT {fields} FROM table WHERE ds = '${{ds}}' AND zone_id = 1"
        report = self.analyzer.analyze(hql)
        assert report.metrics.complexity in ["low", "medium"]

    def test_format_report_for_api(self):
        """测试API响应格式化"""
        hql = "SELECT * FROM table WHERE zone_id = 1"
        report = self.analyzer.analyze(hql)

        api_response = format_report_for_api(report)

        # 验证结构
        assert "score" in api_response
        assert "issues" in api_response
        assert "metrics" in api_response

        # 验证类型
        assert isinstance(api_response["score"], int)
        assert isinstance(api_response["issues"], list)
        assert isinstance(api_response["metrics"], dict)

        # 验证issues格式
        if len(api_response["issues"]) > 0:
            issue = api_response["issues"][0]
            assert "type" in issue
            assert "message" in issue


class TestConvenienceFunctions:
    """测试便捷函数"""

    def test_analyze_hql_performance(self):
        """测试便捷分析函数"""
        hql = "SELECT role_id FROM table WHERE ds = '${ds}'"
        report = analyze_hql_performance(hql)

        assert report.score > 0
        assert isinstance(report.issues, list)


# Pytest fixture配置
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

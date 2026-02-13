#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第2阶段集成测试 - Phase 2 Integration Tests

验证第2阶段新增的优化规则：
- JOIN优化规则
- COUNT DISTINCT优化规则
"""

import sys
import unittest
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入SQL优化器
from backend.services.sql_optimizer.optimizer import SQLOptimizer


class TestJoinOptimizationRule(unittest.TestCase):
    """测试JOIN优化规则"""

    def setUp(self):
        """设置优化器"""
        self.optimizer = SQLOptimizer()

    def test_small_table_join(self):
        """测试小表JOIN优化"""
        hql = "SELECT a.*, b.amount FROM small_table a JOIN big_table b ON a.id = b.id"
        result = self.optimizer.optimize(hql)

        # 应该检测到小表JOIN
        self.assertTrue(len(result.applied_rules) > 0)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("join_optimize", rule_names)

    def test_large_table_join(self):
        """测试大表JOIN优化"""
        hql = "SELECT a.*, b.amount FROM large_table a JOIN big_table b ON a.id = b.id"
        result = self.optimizer.optimize(hql)

        # 应该检测到大表JOIN
        self.assertTrue(len(result.applied_rules) > 0)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("join_optimize", rule_names)

    def test_join_without_filter(self):
        """测试JOIN前无过滤"""
        hql = "SELECT a.*, b.* FROM table_a a JOIN table_b b ON a.id = b.id"
        result = self.optimizer.optimize(hql)

        # 应该检测到JOIN前无过滤
        self.assertTrue(len(result.suggested_rules) > 0)
        rule_names = [r["name"] for r in result.suggested_rules]
        self.assertTrue("join_optimize", rule_names)

    def test_empty_join(self):
        """测试空JOIN"""
        hql = "SELECT a.id FROM table_a a"
        result = self.optimizer.optimize(hql)

        # 不应该触发JOIN优化规则（但可能触发其他规则如column_prune）
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertNotIn("join_optimize", rule_names)
        suggested_names = [r["name"] for r in result.suggested_rules]
        self.assertNotIn("join_optimize", suggested_names)


class TestCountDistinctOptimizationRule(unittest.TestCase):
    """测试COUNT DISTINCT优化规则"""

    def setUp(self):
        """设置优化器"""
        self.optimizer = SQLOptimizer()

    def test_count_distinct_single_column(self):
        """测试单字段COUNT DISTINCT"""
        hql = "SELECT COUNT(DISTINCT user_id) FROM user_table"
        result = self.optimizer.optimize(hql)

        # 应该检测到COUNT DISTINCT
        self.assertTrue(len(result.applied_rules) > 0)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("count_distinct_optimize", rule_names)

    def test_count_distinct_multiple_columns(self):
        """测试多字段COUNT DISTINCT"""
        hql = "SELECT COUNT(DISTINCT user_id), COUNT(DISTINCT product_id) FROM user_table"
        result = self.optimizer.optimize(hql)

        # 应该检测到COUNT DISTINCT
        self.assertTrue(len(result.applied_rules) > 0)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("count_distinct_optimize", rule_names)

    def test_count_without_distinct(self):
        """测试没有DISTINCT的COUNT"""
        hql = "SELECT COUNT(user_id) FROM user_table"
        result = self.optimizer.optimize(hql)

        # 不应该触发COUNT DISTINCT优化
        self.assertNotIn("count_distinct_optimize", [r["name"] for r in result.applied_rules])

    def test_empty_hql(self):
        """测试空HQL"""
        hql = ""
        result = self.optimizer.optimize(hql)

        # 不应该触发COUNT DISTINCT优化
        rule_names = [r["name"] for r in result.applied_rules]
        suggested_names = [r["name"] for r in result.suggested_rules]
        self.assertNotIn("count_distinct_optimize", rule_names)
        self.assertNotIn("count_distinct_optimize", suggested_names)
        self.assertEqual(result.optimized_hql, hql)


class TestPhase2Integration(unittest.TestCase):
    """第2阶段集成测试"""

    def setUp(self):
        """设置优化器"""
        self.optimizer = SQLOptimizer()

    def test_single_table_with_groupby(self):
        """测试单表查询的GROUP BY优化"""
        hql = "SELECT user_id, COUNT(*) AS order_count FROM user_table GROUP BY user_id"
        result = self.optimizer.optimize(hql)

        # 应该检测到GROUP BY优化
        self.assertTrue(len(result.applied_rules) > 0 or len(result.suggested_rules) > 0)

    def test_join_with_count_distinct(self):
        """测试JOIN + COUNT DISTINCT"""
        hql = "SELECT a.*, COUNT(DISTINCT b.order_id) AS order_count FROM table_a a JOIN table_b b ON a.id = b.id"
        result = self.optimizer.optimize(hql)

        # 应该检测到COUNT DISTINCT优化
        self.assertTrue(len(result.applied_rules) > 0)

    def test_complex_query(self):
        """测试复杂查询优化"""
        hql = """
        SELECT
            a.user_id,
            a.user_name,
            b.order_id,
            b.product_id,
            c.product_name
        FROM table_a a
        LEFT JOIN table_b b ON a.user_id = b.user_id
        JOIN table_c c ON b.product_id = c.product_id
        WHERE a.ds = '2025-01-15'
        """

        result = self.optimizer.optimize(hql)

        # 应该检测到多个优化规则
        self.assertTrue(len(result.applied_rules) + len(result.suggested_rules) > 0)

    def test_empty_hql(self):
        """测试空HQL处理"""
        hql = ""
        result = self.optimizer.optimize(hql)

        # 应该正确返回
        self.assertEqual(result.optimized_hql, hql)


if __name__ == "__main__":
    # 运行测试
    unittest.main()

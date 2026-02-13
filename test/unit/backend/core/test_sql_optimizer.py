#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL优化器单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.sql_optimizer.optimizer import SQLOptimizer
from backend.services.sql_optimizer.parser import HQLParser


class TestPartitionPruneRule(unittest.TestCase):
    """测试分区裁剪规则"""

    def setUp(self):
        """设置优化器"""
        self.optimizer = SQLOptimizer()

    def test_partition_with_function(self):
        """分区字段参与函数"""
        hql = "SELECT * FROM t WHERE YEAR(ds) = 2025"
        result = self.optimizer.optimize(hql)

        self.assertTrue(len(result.applied_rules) > 0)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("partition_prune", rule_names)

    def test_partition_direct_use(self):
        """分区字段直接使用"""
        hql = "SELECT * FROM t WHERE ds = '2025-01-15'"
        result = self.optimizer.optimize(hql)

        # 不应该触发分区裁剪规则
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertNotIn("partition_prune", rule_names)

    def test_month_function_on_partition(self):
        """MONTH函数作用于分区字段"""
        hql = "SELECT * FROM t WHERE MONTH(ds) = 12"
        result = self.optimizer.optimize(hql)

        # 应该触发分区裁剪规则
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("partition_prune", rule_names)


class TestColumnPruneRule(unittest.TestCase):
    """测试列裁剪规则"""

    def setUp(self):
        """设置优化器"""
        self.optimizer = SQLOptimizer()

    def test_select_star(self):
        """SELECT * 检测"""
        hql = "SELECT * FROM t"
        result = self.optimizer.optimize(hql)

        self.assertTrue(len(result.applied_rules) > 0)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("column_prune", rule_names)

    def test_select_specific_columns(self):
        """明确列出字段"""
        hql = "SELECT id, name, create_time FROM t"
        result = self.optimizer.optimize(hql)

        # 不应该触发列裁剪规则
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertNotIn("column_prune", rule_names)


class TestPredicatePushdownRule(unittest.TestCase):
    """测试谓词下推规则"""

    def setUp(self):
        """设置优化器"""
        self.optimizer = SQLOptimizer()

    def test_subquery_with_filter(self):
        """子查询外层过滤"""
        hql = "SELECT * FROM (SELECT * FROM t) WHERE a > 10"
        result = self.optimizer.optimize(hql)

        self.assertTrue(len(result.applied_rules) > 0)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("predicate_pushdown", rule_names)

    def test_simple_select(self):
        """简单SELECT语句"""
        hql = "SELECT * FROM t WHERE a > 10"
        result = self.optimizer.optimize(hql)

        # 不应该触发谓词下推规则
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertNotIn("predicate_pushdown", rule_names)


class TestHQLParser(unittest.TestCase):
    """测试HQL解析器"""

    def test_select_star_parsing(self):
        """解析SELECT *"""
        hql = "SELECT * FROM ods_order"
        parser = HQLParser(hql)

        self.assertIn("*", parser.select_columns)

    def test_table_extraction(self):
        """提取表名"""
        hql = "SELECT * FROM ods_order"
        parser = HQLParser(hql)

        self.assertEqual(len(parser.tables), 1)
        self.assertEqual(parser.tables[0].name, "ods_order")

    def test_table_with_alias(self):
        """提取带别名的表名"""
        hql = "SELECT * FROM ods_order o"
        parser = HQLParser(hql)

        self.assertEqual(len(parser.tables), 1)
        self.assertEqual(parser.tables[0].name, "ods_order")
        self.assertEqual(parser.tables[0].alias, "o")


class TestSQLOptimizerIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """设置优化器"""
        self.optimizer = SQLOptimizer()

    def test_simple_single_table(self):
        """简单单表查询优化"""
        hql = "SELECT * FROM ods_order WHERE YEAR(ds) = 2025"
        result = self.optimizer.optimize(hql)

        # 应该应用多个优化规则
        self.assertTrue(len(result.applied_rules) >= 2)
        rule_names = [r["name"] for r in result.applied_rules]
        self.assertIn("partition_prune", rule_names)
        self.assertIn("column_prune", rule_names)

    def test_no_optimization_needed(self):
        """不需要优化的查询"""
        hql = "SELECT id, name FROM ods_order WHERE ds = '2025-01-15'"
        result = self.optimizer.optimize(hql)

        # 不应该应用任何优化规则
        self.assertEqual(len(result.applied_rules), 0)

    def test_empty_hql(self):
        """空HQL"""
        hql = ""
        result = self.optimizer.optimize(hql)

        # 应该返回原始HQL
        self.assertEqual(result.optimized_hql, hql)
        self.assertEqual(len(result.applied_rules), 0)

    def test_multiple_issues(self):
        """多个问题"""
        hql = "SELECT * FROM (SELECT * FROM t) WHERE YEAR(ds) = 2025"
        result = self.optimizer.optimize(hql)

        # 应该应用多个优化规则
        self.assertTrue(len(result.applied_rules) >= 3)


if __name__ == "__main__":
    unittest.main()

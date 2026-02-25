#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存性能测试脚本

测试缓存增强版服务的性能提升效果
"""

import time
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.hql.hql_service_cached import HQLServiceCached
from backend.services.parameters.parameter_service_cached import ParameterServiceCached
from backend.core.cache.cache_system import HierarchicalCache
from backend.core.database import init_db
from backend.core.logging import get_logger

logger = get_logger(__name__)


class CachePerformanceTest:
    """缓存性能测试"""
    
    def __init__(self):
        self.hql_service = HQLServiceCached()
        self.param_service = ParameterServiceCached()
        self.cache = HierarchicalCache()
        
        # 测试数据
        self.test_events = [
            {
                "name": "login",
                "table_name": "dwd_login_di",
                "alias": "e1"
            },
            {
                "name": "purchase",
                "table_name": "dwd_purchase_di",
                "alias": "e2"
            }
        ]
        
        self.test_fields = [
            {
                "name": "role_id",
                "type": "base",
                "json_path": "$.role_id"
            },
            {
                "name": "account_id",
                "type": "base",
                "json_path": "$.account_id"
            }
        ]
        
        self.test_conditions = [
            {
                "field": "ds",
                "operator": "=",
                "value": "${bizdate}",
                "logic": "AND"
            }
        ]
    
    def test_hql_generation_cache(self):
        """测试HQL生成缓存"""
        print("\n" + "=" * 60)
        print("测试1: HQL生成缓存")
        print("=" * 60)
        
        # 第一次生成(无缓存)
        print("\n第一次生成(无缓存)...")
        start_time = time.time()
        hql1 = self.hql_service.generate_hql(
            self.test_events,
            self.test_fields,
            self.test_conditions,
            mode="single",
            use_cache=True
        )
        time1 = time.time() - start_time
        print(f"耗时: {time1:.4f}秒")
        
        # 第二次生成(有缓存)
        print("\n第二次生成(有缓存)...")
        start_time = time.time()
        hql2 = self.hql_service.generate_hql(
            self.test_events,
            self.test_fields,
            self.test_conditions,
            mode="single",
            use_cache=True
        )
        time2 = time.time() - start_time
        print(f"耗时: {time2:.4f}秒")
        
        # 计算性能提升
        improvement = ((time1 - time2) / time1) * 100 if time1 > 0 else 0
        print(f"\n性能提升: {improvement:.2f}%")
        print(f"速度提升: {time1/time2:.2f}x")
        
        # 验证结果一致性
        if hql1 == hql2:
            print("✅ 结果一致性验证通过")
        else:
            print("❌ 结果不一致!")
        
        return {
            'test': 'HQL生成缓存',
            'time_without_cache': time1,
            'time_with_cache': time2,
            'improvement': improvement
        }
    
    def test_hql_validation_cache(self):
        """测试HQL验证缓存"""
        print("\n" + "=" * 60)
        print("测试2: HQL验证缓存")
        print("=" * 60)
        
        test_hql = """
        CREATE OR REPLACE VIEW dwd_test_di AS
        SELECT 
            e1.role_id,
            e1.account_id
        FROM dwd_login_di e1
        WHERE e1.ds = '${bizdate}'
        """
        
        # 第一次验证(无缓存)
        print("\n第一次验证(无缓存)...")
        start_time = time.time()
        result1 = self.hql_service.validate_hql(test_hql, use_cache=True)
        time1 = time.time() - start_time
        print(f"耗时: {time1:.4f}秒")
        
        # 第二次验证(有缓存)
        print("\n第二次验证(有缓存)...")
        start_time = time.time()
        result2 = self.hql_service.validate_hql(test_hql, use_cache=True)
        time2 = time.time() - start_time
        print(f"耗时: {time2:.4f}秒")
        
        # 计算性能提升
        improvement = ((time1 - time2) / time1) * 100 if time1 > 0 else 0
        print(f"\n性能提升: {improvement:.2f}%")
        print(f"速度提升: {time1/time2:.2f}x")
        
        return {
            'test': 'HQL验证缓存',
            'time_without_cache': time1,
            'time_with_cache': time2,
            'improvement': improvement
        }
    
    def test_parameter_query_cache(self):
        """测试参数查询缓存"""
        print("\n" + "=" * 60)
        print("测试3: 参数查询缓存")
        print("=" * 60)
        
        # 注意: 这个测试需要数据库中有实际数据
        # 如果没有数据,会返回空结果
        
        test_event_id = 1  # 假设事件ID为1
        
        # 第一次查询(无缓存)
        print(f"\n第一次查询事件{test_event_id}的参数(无缓存)...")
        start_time = time.time()
        params1 = self.param_service.get_parameters_by_event(test_event_id, use_cache=True)
        time1 = time.time() - start_time
        print(f"耗时: {time1:.4f}秒")
        print(f"参数数量: {len(params1)}")
        
        # 第二次查询(有缓存)
        print(f"\n第二次查询事件{test_event_id}的参数(有缓存)...")
        start_time = time.time()
        params2 = self.param_service.get_parameters_by_event(test_event_id, use_cache=True)
        time2 = time.time() - start_time
        print(f"耗时: {time2:.4f}秒")
        print(f"参数数量: {len(params2)}")
        
        # 计算性能提升
        improvement = ((time1 - time2) / time1) * 100 if time1 > 0 else 0
        print(f"\n性能提升: {improvement:.2f}%")
        print(f"速度提升: {time1/time2:.2f}x" if time2 > 0 else "速度提升: ∞")
        
        return {
            'test': '参数查询缓存',
            'time_without_cache': time1,
            'time_with_cache': time2,
            'improvement': improvement
        }
    
    def test_cache_stats(self):
        """测试缓存统计"""
        print("\n" + "=" * 60)
        print("测试4: 缓存统计信息")
        print("=" * 60)
        
        stats = self.cache.get_stats()
        
        print(f"\nL1缓存大小: {stats.get('l1_size', 0)}")
        print(f"L2连接状态: {'已连接' if stats.get('l2_connected', False) else '未连接'}")
        print(f"总命中率: {stats.get('hit_rate', 0):.2f}%")
        print(f"总请求数: {stats.get('total_requests', 0)}")
        print(f"命中次数: {stats.get('hits', 0)}")
        print(f"未命中次数: {stats.get('misses', 0)}")
        
        return stats
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("缓存性能测试开始")
        print("=" * 80)
        
        # 初始化数据库
        try:
            init_db()
            print("✅ 数据库初始化成功")
        except Exception as e:
            print(f"⚠️ 数据库初始化失败: {e}")
            print("将继续运行测试,但部分测试可能失败")
        
        results = []
        
        # 运行测试
        try:
            results.append(self.test_hql_generation_cache())
        except Exception as e:
            print(f"❌ HQL生成缓存测试失败: {e}")
        
        try:
            results.append(self.test_hql_validation_cache())
        except Exception as e:
            print(f"❌ HQL验证缓存测试失败: {e}")
        
        try:
            results.append(self.test_parameter_query_cache())
        except Exception as e:
            print(f"❌ 参数查询缓存测试失败: {e}")
        
        try:
            stats = self.test_cache_stats()
        except Exception as e:
            print(f"❌ 缓存统计测试失败: {e}")
        
        # 打印总结
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        
        for result in results:
            print(f"\n{result['test']}:")
            print(f"  无缓存耗时: {result['time_without_cache']:.4f}秒")
            print(f"  有缓存耗时: {result['time_with_cache']:.4f}秒")
            print(f"  性能提升: {result['improvement']:.2f}%")
        
        # 计算平均性能提升
        if results:
            avg_improvement = sum(r['improvement'] for r in results) / len(results)
            print(f"\n平均性能提升: {avg_improvement:.2f}%")
        
        print("\n" + "=" * 80)
        print("缓存性能测试完成")
        print("=" * 80)


if __name__ == '__main__':
    tester = CachePerformanceTest()
    tester.run_all_tests()

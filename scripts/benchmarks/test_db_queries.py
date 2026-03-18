#!/usr/bin/env python3
"""
Database Query Performance Benchmark Script
测试典型数据库查询的性能，建立性能基线
"""

import time
import sqlite3
import statistics
from typing import List, Dict, Any
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from backend.core.config import get_db_path

# 典型的数据库查询
TYPICAL_QUERIES = [
    {
        "name": "Get All Games",
        "sql": "SELECT * FROM games",
        "description": "获取所有游戏列表"
    },
    {
        "name": "Get Game by GID",
        "sql": "SELECT * FROM games WHERE gid = ?",
        "params": (10000147,),
        "description": "根据GID获取单个游戏"
    },
    {
        "name": "Get All Events",
        "sql": "SELECT * FROM log_events",
        "description": "获取所有事件"
    },
    {
        "name": "Get Events by Game GID",
        "sql": "SELECT * FROM log_events WHERE game_gid = ?",
        "params": (10000147,),
        "description": "根据游戏GID获取事件"
    },
    {
        "name": "Get Events with Game Join",
        "sql": """
            SELECT le.*, g.name as game_name
            FROM log_events le
            INNER JOIN games g ON le.game_gid = g.gid
            LIMIT 100
        """,
        "description": "JOIN查询：事件和游戏"
    },
    {
        "name": "Count Events by Game",
        "sql": """
            SELECT
                g.gid,
                g.name,
                COUNT(le.id) as event_count
            FROM games g
            LEFT JOIN log_events le ON g.gid = le.game_gid
            GROUP BY g.gid, g.name
        """,
        "description": "聚合查询：统计每个游戏的事件数"
    },
    {
        "name": "Get All Parameters",
        "sql": "SELECT * FROM event_params",
        "description": "获取所有参数"
    },
    {
        "name": "Get Parameters by Event",
        "sql": """
            SELECT ep.*
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            WHERE le.event_type = ?
            LIMIT 50
        """,
        "params": ("login",),
        "description": "根据事件类型获取参数"
    },
    {
        "name": "Complex Join Query",
        "sql": """
            SELECT
                g.gid,
                g.name,
                COUNT(DISTINCT le.id) as event_count,
                COUNT(DISTINCT ep.id) as param_count
            FROM games g
            LEFT JOIN log_events le ON g.gid = le.game_gid
            LEFT JOIN event_params ep ON le.id = ep.event_id
            GROUP BY g.gid, g.name
            ORDER BY event_count DESC
        """,
        "description": "复杂JOIN：游戏、事件、参数"
    },
]


class DatabasePerformanceTester:
    """数据库性能测试器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = get_db_path()

        self.db_path = db_path
        self.results: List[Dict[str, Any]] = []

        # 验证数据库文件存在
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found: {db_path}")

        print(f"Database: {db_path}")
        print(f"Size: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")

    def test_query(self, query: Dict[str, Any], iterations: int = 10) -> Dict[str, Any]:
        """
        测试单个查询性能

        Args:
            query: 查询配置
            iterations: 测试迭代次数

        Returns:
            查询性能结果
        """
        durations = []
        row_counts = []
        errors = []

        print(f"\nTesting: {query['name']}")
        print(f"Description: {query['description']}")
        print(f"SQL: {query['sql'][:100]}...")

        for i in range(iterations):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                start_time = time.perf_counter()
                cursor.execute(query['sql'], query.get('params', ()))
                rows = cursor.fetchall()
                end_time = time.perf_counter()

                duration_ms = (end_time - start_time) * 1000
                durations.append(duration_ms)
                row_counts.append(len(rows))

                conn.close()

                print(f"  Iteration {i+1}/{iterations}: {duration_ms:.2f}ms ({len(rows)} rows)")

            except Exception as e:
                errors.append(str(e))
                print(f"  Iteration {i+1}/{iterations}: ERROR - {e}")

        # 计算统计数据
        result = {
            "name": query['name'],
            "description": query['description'],
            "sql": query['sql'],
            "iterations": iterations,
            "successful": len(durations),
            "failed": len(errors),
            "row_counts": {
                "min": min(row_counts) if row_counts else 0,
                "max": max(row_counts) if row_counts else 0,
                "mean": round(statistics.mean(row_counts), 2) if row_counts else 0,
            },
            "durations": {
                "min": round(min(durations), 2) if durations else 0,
                "max": round(max(durations), 2) if durations else 0,
                "mean": round(statistics.mean(durations), 2) if durations else 0,
                "median": round(statistics.median(durations), 2) if durations else 0,
                "stdev": round(statistics.stdev(durations), 2) if len(durations) > 1 else 0,
            },
            "percentiles": {
                "p50": round(statistics.quantiles(durations, n=2)[0], 2) if len(durations) > 1 else 0,
                "p95": round(statistics.quantiles(durations, n=20)[18], 2) if len(durations) > 1 else 0,
                "p99": round(statistics.quantiles(durations, n=100)[98], 2) if len(durations) > 1 else 0,
            } if len(durations) > 1 else {},
            "errors": errors
        }

        self.results.append(result)
        return result

    def test_all_queries(self, iterations: int = 10) -> List[Dict[str, Any]]:
        """
        测试所有查询

        Args:
            iterations: 每个查询的测试迭代次数

        Returns:
            所有查询的测试结果
        """
        print(f"\n{'='*60}")
        print(f"Database Query Performance Benchmark")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        for query in TYPICAL_QUERIES:
            self.test_query(query, iterations)

        return self.results

    def generate_summary(self) -> Dict[str, Any]:
        """
        生成性能测试摘要

        Returns:
            性能测试摘要
        """
        total_queries = sum(r['successful'] + r['failed'] for r in self.results)
        total_successful = sum(r['successful'] for r in self.results)
        total_failed = sum(r['failed'] for r in self.results)

        # 找出最慢的查询
        slowest_queries = sorted(
            [r for r in self.results if r['successful'] > 0],
            key=lambda x: x['durations']['mean'],
            reverse=True
        )[:3]

        # 找出返回最多行数的查询
        largest_results = sorted(
            [r for r in self.results if r['successful'] > 0],
            key=lambda x: x['row_counts']['mean'],
            reverse=True
        )[:3]

        summary = {
            "timestamp": datetime.now().isoformat(),
            "database_path": self.db_path,
            "database_size_mb": round(os.path.getsize(self.db_path) / 1024 / 1024, 2),
            "total_queries": total_queries,
            "successful_queries": total_successful,
            "failed_queries": total_failed,
            "success_rate": round(total_successful / total_queries * 100, 2) if total_queries > 0 else 0,
            "total_query_types": len(self.results),
            "slowest_queries": [
                {
                    "name": q['name'],
                    "mean_duration_ms": q['durations']['mean']
                }
                for q in slowest_queries
            ],
            "largest_results": [
                {
                    "name": q['name'],
                    "mean_row_count": q['row_counts']['mean']
                }
                for q in largest_results
            ]
        }

        return summary

    def print_summary(self):
        """打印性能测试摘要"""
        summary = self.generate_summary()

        print(f"\n{'='*60}")
        print("Performance Summary")
        print(f"{'='*60}")
        print(f"Database: {summary['database_path']}")
        print(f"Size: {summary['database_size_mb']} MB")
        print(f"Total Queries: {summary['total_queries']}")
        print(f"Successful: {summary['successful_queries']}")
        print(f"Failed: {summary['failed_queries']}")
        print(f"Success Rate: {summary['success_rate']}%")

        print(f"\nSlowest Queries:")
        for q in summary['slowest_queries']:
            print(f"  - {q['name']}: {q['mean_duration_ms']}ms")

        print(f"\nLargest Result Sets:")
        for q in summary['largest_results']:
            print(f"  - {q['name']}: {q['mean_row_count']:.0f} rows")

    def export_results(self, output_file: str = None):
        """
        导出测试结果到JSON文件

        Args:
            output_file: 输出文件路径
        """
        import json

        if output_file is None:
            output_file = f"output/db-baseline-{datetime.now().strftime('%Y-%m-%d')}.json"

        report = {
            "summary": self.generate_summary(),
            "detailed_results": self.results
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nResults exported to: {output_file}")


def main():
    """主函数"""
    try:
        tester = DatabasePerformanceTester()

        # 测试所有查询
        tester.test_all_queries(iterations=10)

        # 打印摘要
        tester.print_summary()

        # 导出结果
        tester.export_results()

        print(f"\n{'='*60}")
        print("Benchmark completed!")
        print(f"{'='*60}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nPlease ensure the database exists and the path is correct.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

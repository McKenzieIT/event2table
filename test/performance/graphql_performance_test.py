"""
GraphQL vs REST API 性能对比测试

测试GraphQL和REST API的性能差异
"""

import requests
import time
import json
import statistics
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import pandas as pd


class PerformanceTest:
    """性能测试类"""

    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.rest_url = f"{base_url}/api"
        self.graphql_url = f"{base_url}/api/graphql"
        self.results = []

    def measure_time(self, func, *args, **kwargs) -> Dict[str, Any]:
        """测量函数执行时间"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            return {
                'success': True,
                'duration': duration,
                'result': result,
                'error': None
            }
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            return {
                'success': False,
                'duration': duration,
                'result': None,
                'error': str(e)
            }

    def test_rest_games_list(self) -> Dict[str, Any]:
        """测试REST API获取游戏列表"""
        response = requests.get(f"{self.rest_url}/games")
        response.raise_for_status()
        return response.json()

    def test_graphql_games_list(self) -> Dict[str, Any]:
        """测试GraphQL获取游戏列表"""
        query = """
        query GetGames {
            games(limit: 100, offset: 0) {
                gid
                name
                odsDb
                eventCount
                parameterCount
            }
        }
        """
        response = requests.post(
            self.graphql_url,
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()

    def test_rest_events_list(self, game_gid: int = 1) -> Dict[str, Any]:
        """测试REST API获取事件列表"""
        response = requests.get(
            f"{self.rest_url}/events",
            params={'game_gid': game_gid, 'page': 1, 'per_page': 50}
        )
        response.raise_for_status()
        return response.json()

    def test_graphql_events_list(self, game_gid: int = 1) -> Dict[str, Any]:
        """测试GraphQL获取事件列表"""
        query = """
        query GetEvents($gameGid: Int!) {
            events(gameGid: $gameGid, limit: 50, offset: 0) {
                id
                eventName
                eventNameCn
                categoryName
                paramCount
            }
        }
        """
        response = requests.post(
            self.graphql_url,
            json={'query': query, 'variables': {'gameGid': game_gid}},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()

    def test_rest_parameters_list(self, game_gid: int = 1) -> Dict[str, Any]:
        """测试REST API获取参数列表"""
        response = requests.get(
            f"{self.rest_url}/parameters/all",
            params={'game_gid': game_gid}
        )
        response.raise_for_status()
        return response.json()

    def test_graphql_parameters_list(self, game_gid: int = 1) -> Dict[str, Any]:
        """测试GraphQL获取参数列表"""
        query = """
        query GetParametersManagement($gameGid: Int!) {
            parametersManagement(gameGid: $gameGid, mode: "all") {
                id
                paramName
                paramNameCn
                paramType
                isActive
                isCommon
                eventName
            }
        }
        """
        response = requests.post(
            self.graphql_url,
            json={'query': query, 'variables': {'gameGid': game_gid}},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()

    def test_rest_dashboard_stats(self) -> Dict[str, Any]:
        """测试REST API获取Dashboard统计"""
        # REST API需要多次请求
        games_response = requests.get(f"{self.rest_url}/games")
        games_response.raise_for_status()
        games_data = games_response.json()

        # 计算统计数据
        games = games_data.get('data', [])
        total_events = sum(g.get('event_count', 0) for g in games)
        total_params = sum(g.get('param_count', 0) for g in games)

        return {
            'totalGames': len(games),
            'totalEvents': total_events,
            'totalParameters': total_params
        }

    def test_graphql_dashboard_stats(self) -> Dict[str, Any]:
        """测试GraphQL获取Dashboard统计"""
        query = """
        query GetDashboardStats {
            dashboardStats {
                totalGames
                totalEvents
                totalParameters
                totalCategories
            }
        }
        """
        response = requests.post(
            self.graphql_url,
            json={'query': query},
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()

    def run_comparison_test(
        self,
        test_name: str,
        rest_func,
        graphql_func,
        iterations: int = 10
    ) -> Dict[str, Any]:
        """运行对比测试"""
        rest_times = []
        graphql_times = []

        print(f"\n运行测试: {test_name}")
        print(f"迭代次数: {iterations}")

        # 测试REST API
        print("测试REST API...")
        for i in range(iterations):
            result = self.measure_time(rest_func)
            if result['success']:
                rest_times.append(result['duration'])
            else:
                print(f"  REST API 第{i+1}次失败: {result['error']}")

        # 测试GraphQL API
        print("测试GraphQL API...")
        for i in range(iterations):
            result = self.measure_time(graphql_func)
            if result['success']:
                graphql_times.append(result['duration'])
            else:
                print(f"  GraphQL API 第{i+1}次失败: {result['error']}")

        # 计算统计数据
        rest_stats = {
            'mean': statistics.mean(rest_times) if rest_times else 0,
            'median': statistics.median(rest_times) if rest_times else 0,
            'min': min(rest_times) if rest_times else 0,
            'max': max(rest_times) if rest_times else 0,
            'stdev': statistics.stdev(rest_times) if len(rest_times) > 1 else 0
        }

        graphql_stats = {
            'mean': statistics.mean(graphql_times) if graphql_times else 0,
            'median': statistics.median(graphql_times) if graphql_times else 0,
            'min': min(graphql_times) if graphql_times else 0,
            'max': max(graphql_times) if graphql_times else 0,
            'stdev': statistics.stdev(graphql_times) if len(graphql_times) > 1 else 0
        }

        # 计算改进百分比
        if rest_stats['mean'] > 0:
            improvement = ((rest_stats['mean'] - graphql_stats['mean']) / rest_stats['mean']) * 100
        else:
            improvement = 0

        result = {
            'test_name': test_name,
            'iterations': iterations,
            'rest_api': rest_stats,
            'graphql': graphql_stats,
            'improvement_percent': improvement,
            'rest_times': rest_times,
            'graphql_times': graphql_times
        }

        self.results.append(result)
        return result

    def run_all_tests(self, iterations: int = 10):
        """运行所有性能测试"""
        print("=" * 80)
        print("GraphQL vs REST API 性能对比测试")
        print("=" * 80)

        # 测试1: 游戏列表
        self.run_comparison_test(
            "游戏列表查询",
            self.test_rest_games_list,
            self.test_graphql_games_list,
            iterations
        )

        # 测试2: 事件列表
        self.run_comparison_test(
            "事件列表查询",
            self.test_rest_events_list,
            self.test_graphql_events_list,
            iterations
        )

        # 测试3: 参数列表
        self.run_comparison_test(
            "参数列表查询",
            self.test_rest_parameters_list,
            self.test_graphql_parameters_list,
            iterations
        )

        # 测试4: Dashboard统计
        self.run_comparison_test(
            "Dashboard统计查询",
            self.test_rest_dashboard_stats,
            self.test_graphql_dashboard_stats,
            iterations
        )

        # 生成报告
        self.generate_report()

    def generate_report(self):
        """生成性能测试报告"""
        print("\n" + "=" * 80)
        print("性能测试报告")
        print("=" * 80)

        for result in self.results:
            print(f"\n测试: {result['test_name']}")
            print(f"  REST API 平均时间: {result['rest_api']['mean']*1000:.2f}ms")
            print(f"  GraphQL 平均时间: {result['graphql']['mean']*1000:.2f}ms")
            print(f"  性能提升: {result['improvement_percent']:.1f}%")

            if result['improvement_percent'] > 0:
                print(f"  ✅ GraphQL更快")
            elif result['improvement_percent'] < 0:
                print(f"  ⚠️  REST API更快")
            else:
                print(f"  ➖ 性能相当")

        # 生成图表
        self.generate_charts()

        # 保存结果到JSON
        self.save_results()

    def generate_charts(self):
        """生成性能对比图表"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('GraphQL vs REST API 性能对比', fontsize=16)

        for idx, result in enumerate(self.results):
            ax = axes[idx // 2, idx % 2]

            # 准备数据
            categories = ['REST API', 'GraphQL']
            times = [
                result['rest_api']['mean'] * 1000,
                result['graphql']['mean'] * 1000
            ]

            # 绘制柱状图
            bars = ax.bar(categories, times, color=['#FF6B6B', '#4ECDC4'])
            ax.set_title(result['test_name'])
            ax.set_ylabel('响应时间 (ms)')
            ax.set_ylim(0, max(times) * 1.2)

            # 添加数值标签
            for bar, time in zip(bars, times):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.,
                    height,
                    f'{time:.2f}ms',
                    ha='center',
                    va='bottom'
                )

            # 添加改进百分比
            improvement = result['improvement_percent']
            color = 'green' if improvement > 0 else 'red'
            ax.text(
                0.5, 0.95,
                f'性能提升: {improvement:.1f}%',
                transform=ax.transAxes,
                ha='center',
                va='top',
                fontsize=10,
                color=color,
                weight='bold'
            )

        plt.tight_layout()
        plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
        print("\n图表已保存到: performance_comparison.png")

    def save_results(self):
        """保存测试结果到JSON文件"""
        output = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'results': []
        }

        for result in self.results:
            output['results'].append({
                'test_name': result['test_name'],
                'iterations': result['iterations'],
                'rest_api': result['rest_api'],
                'graphql': result['graphql'],
                'improvement_percent': result['improvement_percent']
            })

        with open('performance_results.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print("结果已保存到: performance_results.json")


def main():
    """主函数"""
    tester = PerformanceTest()

    try:
        tester.run_all_tests(iterations=10)
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保后端服务正在运行")
        print("启动后端服务: python backend/app.py")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

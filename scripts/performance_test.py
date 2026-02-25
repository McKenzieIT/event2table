#!/usr/bin/env python3
"""
Performance Testing Script

Comprehensive performance testing for GraphQL API.
Compares GraphQL vs REST API performance and generates detailed reports.
"""

import time
import json
import statistics
import requests
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    operation: str
    api_type: str  # 'graphql' or 'rest'
    duration: float  # milliseconds
    status_code: int
    response_size: int
    success: bool
    error: str = None


class PerformanceTester:
    """
    Performance Tester
    
    Tests GraphQL and REST API performance with various metrics.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.metrics: List[PerformanceMetric] = []
        
        # Test scenarios
        self.test_scenarios = [
            {
                'name': 'Get Games List',
                'rest': {
                    'method': 'GET',
                    'url': f'{base_url}/api/games',
                },
                'graphql': {
                    'query': '''
                        query {
                            games(limit: 50, offset: 0) {
                                id
                                gid
                                name
                                nameCn
                                isActive
                            }
                        }
                    ''',
                }
            },
            {
                'name': 'Get Events List',
                'rest': {
                    'method': 'GET',
                    'url': f'{base_url}/api/events',
                    'params': {'game_gid': 1}
                },
                'graphql': {
                    'query': '''
                        query {
                            events(gameGid: 1, limit: 50, offset: 0) {
                                id
                                eventName
                                eventNameCn
                                description
                                isActive
                            }
                        }
                    ''',
                }
            },
            {
                'name': 'Get Categories',
                'rest': {
                    'method': 'GET',
                    'url': f'{base_url}/api/categories',
                },
                'graphql': {
                    'query': '''
                        query {
                            categories(limit: 50, offset: 0) {
                                id
                                name
                                nameCn
                                description
                            }
                        }
                    ''',
                }
            },
        ]
    
    def run_test(self, scenario: Dict, iterations: int = 10) -> List[PerformanceMetric]:
        """
        Run performance test for a scenario.
        
        Args:
            scenario: Test scenario configuration
            iterations: Number of iterations to run
            
        Returns:
            List of performance metrics
        """
        metrics = []
        
        # Test REST API
        logger.info(f"Testing REST API: {scenario['name']}")
        for i in range(iterations):
            metric = self._test_rest_api(scenario)
            metrics.append(metric)
            time.sleep(0.1)  # Small delay between requests
        
        # Test GraphQL API
        logger.info(f"Testing GraphQL API: {scenario['name']}")
        for i in range(iterations):
            metric = self._test_graphql_api(scenario)
            metrics.append(metric)
            time.sleep(0.1)  # Small delay between requests
        
        return metrics
    
    def _test_rest_api(self, scenario: Dict) -> PerformanceMetric:
        """Test REST API endpoint"""
        rest_config = scenario['rest']
        
        start_time = time.time()
        try:
            if rest_config['method'] == 'GET':
                response = requests.get(
                    rest_config['url'],
                    params=rest_config.get('params', {}),
                    timeout=10
                )
            else:
                response = requests.post(
                    rest_config['url'],
                    json=rest_config.get('data', {}),
                    timeout=10
                )
            
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            return PerformanceMetric(
                operation=scenario['name'],
                api_type='rest',
                duration=duration,
                status_code=response.status_code,
                response_size=len(response.content),
                success=response.status_code == 200
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return PerformanceMetric(
                operation=scenario['name'],
                api_type='rest',
                duration=duration,
                status_code=0,
                response_size=0,
                success=False,
                error=str(e)
            )
    
    def _test_graphql_api(self, scenario: Dict) -> PerformanceMetric:
        """Test GraphQL API endpoint"""
        graphql_config = scenario['graphql']
        
        start_time = time.time()
        try:
            response = requests.post(
                f'{self.base_url}/graphql',
                json={'query': graphql_config['query']},
                timeout=10
            )
            
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            return PerformanceMetric(
                operation=scenario['name'],
                api_type='graphql',
                duration=duration,
                status_code=response.status_code,
                response_size=len(response.content),
                success=response.status_code == 200
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return PerformanceMetric(
                operation=scenario['name'],
                api_type='graphql',
                duration=duration,
                status_code=0,
                response_size=0,
                success=False,
                error=str(e)
            )
    
    def run_all_tests(self, iterations: int = 10) -> List[PerformanceMetric]:
        """Run all test scenarios"""
        all_metrics = []
        
        for scenario in self.test_scenarios:
            metrics = self.run_test(scenario, iterations)
            all_metrics.extend(metrics)
        
        self.metrics = all_metrics
        return all_metrics
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        if not self.metrics:
            return {'error': 'No metrics collected'}
        
        report = {
            'summary': {},
            'by_operation': {},
            'comparison': {},
        }
        
        # Overall summary
        rest_metrics = [m for m in self.metrics if m.api_type == 'rest']
        graphql_metrics = [m for m in self.metrics if m.api_type == 'graphql']
        
        report['summary'] = {
            'total_tests': len(self.metrics),
            'rest_tests': len(rest_metrics),
            'graphql_tests': len(graphql_metrics),
            'rest_success_rate': sum(1 for m in rest_metrics if m.success) / len(rest_metrics) * 100,
            'graphql_success_rate': sum(1 for m in graphql_metrics if m.success) / len(graphql_metrics) * 100,
        }
        
        # By operation
        operations = set(m.operation for m in self.metrics)
        for operation in operations:
            op_rest = [m for m in rest_metrics if m.operation == operation]
            op_graphql = [m for m in graphql_metrics if m.operation == operation]
            
            report['by_operation'][operation] = {
                'rest': {
                    'avg_duration': statistics.mean([m.duration for m in op_rest]),
                    'min_duration': min([m.duration for m in op_rest]),
                    'max_duration': max([m.duration for m in op_rest]),
                    'median_duration': statistics.median([m.duration for m in op_rest]),
                    'avg_response_size': statistics.mean([m.response_size for m in op_rest]),
                },
                'graphql': {
                    'avg_duration': statistics.mean([m.duration for m in op_graphql]),
                    'min_duration': min([m.duration for m in op_graphql]),
                    'max_duration': max([m.duration for m in op_graphql]),
                    'median_duration': statistics.median([m.duration for m in op_graphql]),
                    'avg_response_size': statistics.mean([m.response_size for m in op_graphql]),
                }
            }
        
        # Comparison
        for operation in operations:
            op_report = report['by_operation'][operation]
            rest_avg = op_report['rest']['avg_duration']
            graphql_avg = op_report['graphql']['avg_duration']
            
            improvement = ((rest_avg - graphql_avg) / rest_avg * 100) if rest_avg > 0 else 0
            
            report['comparison'][operation] = {
                'faster_api': 'graphql' if graphql_avg < rest_avg else 'rest',
                'improvement_percent': improvement,
                'duration_difference': rest_avg - graphql_avg,
            }
        
        return report
    
    def save_report(self, filepath: str):
        """Save report to file"""
        report = self.generate_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {filepath}")


def main():
    """Main function"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"🚀 Starting performance tests...")
    print(f"Base URL: {base_url}")
    print(f"Iterations per test: {iterations}")
    print()
    
    tester = PerformanceTester(base_url)
    metrics = tester.run_all_tests(iterations)
    
    print(f"\n✅ Completed {len(metrics)} tests")
    
    # Generate and display report
    report = tester.generate_report()
    
    print("\n" + "="*60)
    print("PERFORMANCE TEST REPORT")
    print("="*60)
    
    print(f"\n📊 Summary:")
    print(f"  Total tests: {report['summary']['total_tests']}")
    print(f"  REST success rate: {report['summary']['rest_success_rate']:.1f}%")
    print(f"  GraphQL success rate: {report['summary']['graphql_success_rate']:.1f}%")
    
    print(f"\n📈 Performance Comparison:")
    for operation, comparison in report['comparison'].items():
        print(f"\n  {operation}:")
        print(f"    Faster API: {comparison['faster_api'].upper()}")
        print(f"    Improvement: {comparison['improvement_percent']:.1f}%")
        print(f"    Time saved: {comparison['duration_difference']:.2f}ms")
    
    # Save report
    tester.save_report('performance_test_report.json')
    print(f"\n✅ Detailed report saved to: performance_test_report.json")


if __name__ == '__main__':
    main()

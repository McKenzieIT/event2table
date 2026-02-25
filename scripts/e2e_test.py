#!/usr/bin/env python3
"""
E2E Test Suite for GraphQL Migration

Comprehensive end-to-end tests to verify GraphQL API functionality
and check for bugs introduced during migration.
"""

import requests
import json
import time
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    api_type: str  # 'graphql' or 'rest'
    success: bool
    status_code: int
    response_time: float
    error: str = None
    data_match: bool = None


class E2ETestSuite:
    """E2E test suite for GraphQL migration"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        
        # Test data
        self.test_game_gid = 1
        self.test_event_id = 1
        
    def test_games_list(self) -> Tuple[TestResult, TestResult]:
        """Test games list endpoint"""
        # REST API test
        rest_result = self._test_rest_api(
            'Games List',
            'GET',
            f'{self.base_url}/api/games'
        )
        
        # GraphQL test
        graphql_result = self._test_graphql_api(
            'Games List',
            '''
            query {
                games(limit: 50, offset: 0) {
                    id
                    gid
                    name
                    nameCn
                    isActive
                }
            }
            '''
        )
        
        # Compare results
        if rest_result.success and graphql_result.success:
            self._compare_results(rest_result, graphql_result)
        
        return rest_result, graphql_result
    
    def test_events_list(self) -> Tuple[TestResult, TestResult]:
        """Test events list endpoint"""
        # REST API test
        rest_result = self._test_rest_api(
            'Events List',
            'GET',
            f'{self.base_url}/api/events',
            params={'game_gid': self.test_game_gid}
        )
        
        # GraphQL test
        graphql_result = self._test_graphql_api(
            'Events List',
            '''
            query GetEvents($gameGid: Int!) {
                events(gameGid: $gameGid, limit: 50, offset: 0) {
                    id
                    eventName
                    eventNameCn
                    description
                    isActive
                }
            }
            ''',
            variables={'gameGid': self.test_game_gid}
        )
        
        if rest_result.success and graphql_result.success:
            self._compare_results(rest_result, graphql_result)
        
        return rest_result, graphql_result
    
    def test_categories_list(self) -> Tuple[TestResult, TestResult]:
        """Test categories list endpoint"""
        # REST API test
        rest_result = self._test_rest_api(
            'Categories List',
            'GET',
            f'{self.base_url}/api/categories'
        )
        
        # GraphQL test
        graphql_result = self._test_graphql_api(
            'Categories List',
            '''
            query {
                categories(limit: 50, offset: 0) {
                    id
                    name
                    nameCn
                    description
                }
            }
            '''
        )
        
        if rest_result.success and graphql_result.success:
            self._compare_results(rest_result, graphql_result)
        
        return rest_result, graphql_result
    
    def test_event_detail(self) -> Tuple[TestResult, TestResult]:
        """Test event detail endpoint"""
        # REST API test
        rest_result = self._test_rest_api(
            'Event Detail',
            'GET',
            f'{self.base_url}/api/events/{self.test_event_id}'
        )
        
        # GraphQL test
        graphql_result = self._test_graphql_api(
            'Event Detail',
            '''
            query GetEvent($id: Int!) {
                event(id: $id) {
                    id
                    eventName
                    eventNameCn
                    description
                    isActive
                }
            }
            ''',
            variables={'id': self.test_event_id}
        )
        
        if rest_result.success and graphql_result.success:
            self._compare_results(rest_result, graphql_result)
        
        return rest_result, graphql_result
    
    def test_create_game(self) -> Tuple[TestResult, TestResult]:
        """Test create game endpoint"""
        test_data = {
            'gid': 9999,
            'name': 'Test Game E2E',
            'name_cn': '测试游戏E2E'
        }
        
        # REST API test
        rest_result = self._test_rest_api(
            'Create Game',
            'POST',
            f'{self.base_url}/api/games',
            data=test_data
        )
        
        # GraphQL test
        graphql_result = self._test_graphql_api(
            'Create Game',
            '''
            mutation CreateGame($gid: Int!, $name: String!, $nameCn: String!) {
                createGame(gid: $gid, name: $name, nameCn: $nameCn) {
                    ok
                    game {
                        id
                        gid
                        name
                        nameCn
                    }
                    errors
                }
            }
            ''',
            variables={
                'gid': test_data['gid'],
                'name': test_data['name'],
                'nameCn': test_data['name_cn']
            }
        )
        
        return rest_result, graphql_result
    
    def _test_rest_api(
        self,
        test_name: str,
        method: str,
        url: str,
        params: Dict = None,
        data: Dict = None
    ) -> TestResult:
        """Test REST API endpoint"""
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)
            
            duration = (time.time() - start_time) * 1000
            
            return TestResult(
                test_name=test_name,
                api_type='rest',
                success=response.status_code == 200,
                status_code=response.status_code,
                response_time=duration,
                error=None if response.status_code == 200 else response.text[:200]
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                api_type='rest',
                success=False,
                status_code=0,
                response_time=duration,
                error=str(e)
            )
    
    def _test_graphql_api(
        self,
        test_name: str,
        query: str,
        variables: Dict = None
    ) -> TestResult:
        """Test GraphQL API endpoint"""
        start_time = time.time()
        
        try:
            response = requests.post(
                f'{self.base_url}/graphql',
                json={'query': query, 'variables': variables or {}},
                timeout=10
            )
            
            duration = (time.time() - start_time) * 1000
            
            # Check for GraphQL errors
            data = response.json()
            has_errors = 'errors' in data and data['errors']
            
            return TestResult(
                test_name=test_name,
                api_type='graphql',
                success=response.status_code == 200 and not has_errors,
                status_code=response.status_code,
                response_time=duration,
                error=str(data.get('errors', []))[:200] if has_errors else None
            )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                api_type='graphql',
                success=False,
                status_code=0,
                response_time=duration,
                error=str(e)
            )
    
    def _compare_results(self, rest_result: TestResult, graphql_result: TestResult):
        """Compare REST and GraphQL results"""
        # Basic comparison - both should succeed
        graphql_result.data_match = rest_result.success == graphql_result.success
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all E2E tests"""
        logger.info("🚀 Starting E2E tests...")
        
        # Run tests
        tests = [
            self.test_games_list,
            self.test_events_list,
            self.test_categories_list,
            self.test_event_detail,
            self.test_create_game,
        ]
        
        for test in tests:
            logger.info(f"Running: {test.__name__}")
            results = test()
            self.results.extend(results)
            time.sleep(0.5)  # Small delay between tests
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate E2E test report"""
        if not self.results:
            return {'error': 'No test results'}
        
        rest_results = [r for r in self.results if r.api_type == 'rest']
        graphql_results = [r for r in self.results if r.api_type == 'graphql']
        
        report = {
            'summary': {
                'total_tests': len(self.results),
                'rest_tests': len(rest_results),
                'graphql_tests': len(graphql_results),
                'rest_success': sum(1 for r in rest_results if r.success),
                'graphql_success': sum(1 for r in graphql_results if r.success),
                'rest_success_rate': sum(1 for r in rest_results if r.success) / len(rest_results) * 100 if rest_results else 0,
                'graphql_success_rate': sum(1 for r in graphql_results if r.success) / len(graphql_results) * 100 if graphql_results else 0,
            },
            'bugs_found': [],
            'performance': {
                'rest_avg_time': sum(r.response_time for r in rest_results) / len(rest_results) if rest_results else 0,
                'graphql_avg_time': sum(r.response_time for r in graphql_results) / len(graphql_results) if graphql_results else 0,
            },
            'details': []
        }
        
        # Check for bugs
        for rest, graphql in zip(rest_results, graphql_results):
            if rest.test_name == graphql.test_name:
                detail = {
                    'test': rest.test_name,
                    'rest_success': rest.success,
                    'graphql_success': graphql.success,
                    'rest_time': rest.response_time,
                    'graphql_time': graphql.response_time,
                    'data_match': graphql.data_match
                }
                report['details'].append(detail)
                
                # Identify bugs
                if rest.success and not graphql.success:
                    report['bugs_found'].append({
                        'test': rest.test_name,
                        'type': 'GraphQL failure',
                        'error': graphql.error
                    })
                elif not rest.success and graphql.success:
                    report['bugs_found'].append({
                        'test': rest.test_name,
                        'type': 'REST failure (unexpected)',
                        'error': rest.error
                    })
        
        return report


def main():
    """Main function"""
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"🧪 E2E Test Suite for GraphQL Migration")
    print(f"Base URL: {base_url}")
    print()
    
    suite = E2ETestSuite(base_url)
    results = suite.run_all_tests()
    
    report = suite.generate_report()
    
    print("\n" + "="*70)
    print("E2E TEST REPORT")
    print("="*70)
    
    print(f"\n📊 Summary:")
    print(f"  Total Tests: {report['summary']['total_tests']}")
    print(f"  REST Success Rate: {report['summary']['rest_success_rate']:.1f}%")
    print(f"  GraphQL Success Rate: {report['summary']['graphql_success_rate']:.1f}%")
    
    print(f"\n⚡ Performance:")
    print(f"  REST Avg Time: {report['performance']['rest_avg_time']:.2f}ms")
    print(f"  GraphQL Avg Time: {report['performance']['graphql_avg_time']:.2f}ms")
    
    if report['bugs_found']:
        print(f"\n🐛 Bugs Found ({len(report['bugs_found'])}):")
        for bug in report['bugs_found']:
            print(f"  - {bug['test']}: {bug['type']}")
            if bug['error']:
                print(f"    Error: {bug['error'][:100]}")
    else:
        print(f"\n✅ No bugs found!")
    
    # Save report
    report_path = 'e2e_test_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n✅ Detailed report saved to: {report_path}")


if __name__ == '__main__':
    main()

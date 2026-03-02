#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REST API 到 GraphQL 迁移工具

自动将REST API调用转换为GraphQL查询

使用方法:
    python scripts/rest_to_graphql_converter.py --api "/api/games" --method "GET"
    python scripts/rest_to_graphql_converter.py --api "/api/games/10000147" --method "GET"
    python scripts/rest_to_graphql_converter.py --api "/api/games" --method "POST" --data '{"gid":10000147,"name":"新游戏"}'
"""

import argparse
import json
import re
from typing import Dict, Any, Optional, Tuple


class RESTToGraphQLConverter:
    """REST API到GraphQL转换器"""
    
    # REST API到GraphQL映射规则
    MAPPING_RULES = {
        # Games API
        r'GET /api/games$': {
            'query': 'query GetGames($limit: Int, $offset: Int) {\n  games(limit: $limit, offset: $offset) {\n    id\n    gid\n    name\n    ods_db\n    eventCount\n    parameterCount\n  }\n}',
            'variables': {'limit': 10, 'offset': 0}
        },
        r'GET /api/games/(\d+)$': {
            'query': 'query GetGame($gid: Int!) {\n  game(gid: $gid) {\n    id\n    gid\n    name\n    ods_db\n    createdAt\n    updatedAt\n  }\n}',
            'variables': {'gid': '{path_param_1}'}
        },
        r'POST /api/games$': {
            'query': 'mutation CreateGame($gid: Int!, $name: String!, $ods_db: String!) {\n  createGame(gid: $gid, name: $name, ods_db: $ods_db) {\n    ok\n    game {\n      id\n      gid\n      name\n    }\n    errors\n  }\n}',
            'variables': ['gid', 'name', 'ods_db']
        },
        r'PUT /api/games/(\d+)$': {
            'query': 'mutation UpdateGame($gid: Int!, $name: String, $ods_db: String) {\n  updateGame(gid: $gid, name: $name, ods_db: $ods_db) {\n    ok\n    game {\n      id\n      gid\n      name\n    }\n    errors\n  }\n}',
            'variables': {'gid': '{path_param_1}'}
        },
        r'DELETE /api/games/(\d+)$': {
            'query': 'mutation DeleteGame($gid: Int!, $confirm: Boolean) {\n  deleteGame(gid: $gid, confirm: $confirm) {\n    ok\n    message\n    errors\n  }\n}',
            'variables': {'gid': '{path_param_1}', 'confirm': True}
        },
        
        # Events API
        r'GET /api/events\?game_gid=(\d+)': {
            'query': 'query GetEvents($game_gid: Int!, $limit: Int, $offset: Int) {\n  events(game_gid: $game_gid, limit: $limit, offset: $offset) {\n    id\n    eventName\n    eventNameCn\n    gameGid\n    categoryName\n    paramCount\n  }\n}',
            'variables': {'game_gid': '{query_param_game_gid}', 'limit': 50, 'offset': 0}
        },
        r'GET /api/events/(\d+)$': {
            'query': 'query GetEvent($id: Int!) {\n  event(id: $id) {\n    id\n    eventName\n    eventNameCn\n    gameGid\n    categoryId\n    paramCount\n  }\n}',
            'variables': {'id': '{path_param_1}'}
        },
        
        # Parameters API
        r'GET /api/parameters\?event_id=(\d+)': {
            'query': 'query GetParameters($event_id: Int!, $activeOnly: Boolean) {\n  parameters(event_id: $event_id, activeOnly: $activeOnly) {\n    id\n    paramName\n    paramType\n    jsonPath\n    isActive\n  }\n}',
            'variables': {'event_id': '{query_param_event_id}', 'activeOnly': True}
        },
        
        # Categories API
        r'GET /api/categories$': {
            'query': 'query GetCategories($limit: Int, $offset: Int) {\n  categories(limit: $limit, offset: $offset) {\n    id\n    name\n    description\n  }\n}',
            'variables': {'limit': 50, 'offset': 0}
        },
    }
    
    def convert(self, method: str, api_path: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        转换REST API调用为GraphQL查询
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE)
            api_path: API路径
            data: POST/PUT请求体数据
            
        Returns:
            GraphQL查询和变量
        """
        # 构建匹配模式
        pattern = f"{method} {api_path}"
        
        # 查找匹配规则
        for regex, graphql_config in self.MAPPING_RULES.items():
            match = re.match(regex, pattern)
            if match:
                return self._build_graphql_query(graphql_config, match, data)
        
        # 未找到匹配规则
        return {
            'error': f'No GraphQL mapping found for: {pattern}',
            'suggestion': 'Please manually create GraphQL query or add mapping rule'
        }
    
    def _build_graphql_query(self, config: Dict, match, data: Optional[Dict]) -> Dict[str, Any]:
        """构建GraphQL查询"""
        query = config['query']
        variables = config['variables'].copy()
        
        # 替换路径参数
        if isinstance(variables, dict):
            for key, value in variables.items():
                if isinstance(value, str) and value.startswith('{path_param_'):
                    param_index = int(value.split('_')[2].rstrip('}')) - 1
                    variables[key] = int(match.group(param_index + 1))
                elif isinstance(value, str) and value.startswith('{query_param_'):
                    param_name = value.split('_')[2].rstrip('}')
                    # 从查询字符串提取参数(简化处理)
                    variables[key] = f'<extract_{param_name}_from_query_string>'
        
        # 合并POST/PUT数据
        if data and isinstance(variables, dict):
            for key in variables.keys():
                if key in data:
                    variables[key] = data[key]
        
        return {
            'query': query,
            'variables': variables,
            'endpoint': '/api/graphql',
            'method': 'POST'
        }
    
    def generate_migration_code(self, rest_code: str) -> str:
        """
        生成迁移代码
        
        Args:
            rest_code: REST API调用代码
            
        Returns:
            GraphQL迁移代码
        """
        # 示例: 将fetch('/api/games')转换为Apollo Client查询
        template = '''// REST API (旧代码)
{rest_code}

// GraphQL API (新代码)
import {{ useQuery }} from '@apollo/client';
import {{ GET_GAMES }} from './queries';

const {{ loading, error, data }} = useQuery(GET_GAMES);
'''
        return template.format(rest_code=rest_code)


def main():
    parser = argparse.ArgumentParser(description='REST API to GraphQL Converter')
    parser.add_argument('--api', required=True, help='REST API path (e.g., /api/games)')
    parser.add_argument('--method', required=True, help='HTTP method (GET, POST, PUT, DELETE)')
    parser.add_argument('--data', help='Request body data (JSON string)')
    
    args = parser.parse_args()
    
    # 解析数据
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON data: {args.data}")
            return
    
    # 转换
    converter = RESTToGraphQLConverter()
    result = converter.convert(args.method, args.api, data)
    
    # 输出结果
    print("\n" + "="*60)
    print("REST API to GraphQL Conversion Result")
    print("="*60)
    print(f"\nREST API: {args.method} {args.api}")
    if data:
        print(f"Request Body: {json.dumps(data, indent=2)}")
    
    print("\n" + "-"*60)
    print("GraphQL Query:")
    print("-"*60)
    if 'error' in result:
        print(f"❌ {result['error']}")
        print(f"💡 {result['suggestion']}")
    else:
        print(f"Endpoint: {result['endpoint']}")
        print(f"Method: {result['method']}")
        print(f"\nQuery:\n{result['query']}")
        print(f"\nVariables:\n{json.dumps(result['variables'], indent=2)}")
        
        # 生成curl命令示例
        print("\n" + "-"*60)
        print("Example curl command:")
        print("-"*60)
        curl_data = {
            'query': result['query'],
            'variables': result['variables']
        }
        print(f"curl -X POST http://localhost:5001/api/graphql \\")
        print(f"  -H 'Content-Type: application/json' \\")
        print(f"  -d '{json.dumps(curl_data)}'")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    main()

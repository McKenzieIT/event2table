#!/usr/bin/env python3
"""
REST API迁移状态检查脚本
检查哪些REST API端点还未迁移到GraphQL
"""

import os
import re
from pathlib import Path

def extract_routes(file_path):
    """从文件中提取路由定义"""
    routes = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 匹配Flask路由装饰器
        patterns = [
            r'@(\w+)\.route\([\'"]([^\'"]+)[\'"]',
            r'@app\.route\([\'"]([^\'"]+)[\'"]',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    routes.append({
                        'method': match[0] if len(match) > 1 else 'GET',
                        'path': match[1] if len(match) > 1 else match[0]
                    })
                else:
                    routes.append({
                        'method': 'GET',
                        'path': match
                    })
    return routes

def check_graphql_coverage(route_path):
    """检查GraphQL是否覆盖该路由"""
    # GraphQL覆盖的关键词
    graphql_keywords = [
        'games', 'events', 'categories', 'parameters',
        'dashboard', 'flows', 'templates', 'nodes',
        'hql', 'join_configs'
    ]
    
    # 检查路径是否被GraphQL覆盖
    for keyword in graphql_keywords:
        if keyword in route_path.lower():
            return True
    return False

def main():
    """主函数"""
    backend_path = Path('/Users/mckenzie/Documents/event2table/backend/api/routes')
    
    print("🔍 检查REST API迁移状态...\n")
    
    # 排除的文件
    exclude_files = ['graphql.py', '__init__.py', '_param_helpers.py', '_hql_helpers.py']
    
    # 统计数据
    total_routes = 0
    graphql_covered = 0
    not_covered = 0
    route_details = []
    
    # 遍历所有路由文件
    for file_path in backend_path.glob('*.py'):
        if file_path.name in exclude_files or file_path.name.startswith('__pycache__'):
            continue
        
        routes = extract_routes(file_path)
        for route in routes:
            total_routes += 1
            is_covered = check_graphql_coverage(route['path'])
            
            if is_covered:
                graphql_covered += 1
            else:
                not_covered += 1
                route_details.append({
                    'file': file_path.name,
                    'method': route['method'],
                    'path': route['path']
                })
    
    # 输出结果
    print(f"📊 REST API端点统计:")
    print(f"  总计: {total_routes} 个端点")
    print(f"  GraphQL已覆盖: {graphql_covered} 个 ({graphql_covered/total_routes*100:.1f}%)")
    print(f"  未覆盖: {not_covered} 个 ({not_covered/total_routes*100:.1f}%)")
    
    if route_details:
        print(f"\n⚠️  未被GraphQL覆盖的端点:")
        for detail in route_details[:20]:  # 只显示前20个
            print(f"  - {detail['file']}: {detail['method']} {detail['path']}")
        
        if len(route_details) > 20:
            print(f"  ... 还有 {len(route_details) - 20} 个端点未显示")
    
    return {
        'total': total_routes,
        'covered': graphql_covered,
        'not_covered': not_covered,
        'details': route_details
    }

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
GraphQL优化需求检查脚本
识别需要优化的GraphQL内容
"""

import os
import re
from pathlib import Path

def check_query_complexity(file_path):
    """检查查询复杂度"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查查询深度
    max_depth = 0
    current_depth = 0
    
    for line in content.split('\n'):
        if '{' in line:
            current_depth += line.count('{')
            max_depth = max(max_depth, current_depth)
        if '}' in line:
            current_depth -= line.count('}')
    
    return max_depth

def check_missing_dataloader(file_path):
    """检查是否缺少DataLoader"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否使用了DataLoader
    has_dataloader = 'DataLoader' in content or 'dataloader' in content
    
    # 检查是否有批量查询需求
    has_batch_patterns = bool(re.search(r'for.*in.*:', content))
    
    return has_batch_patterns and not has_dataloader

def main():
    """主函数"""
    print("🔍 检查GraphQL优化需求...\n")
    
    # 检查GraphQL schema和resolvers
    gql_path = Path('/Users/mckenzie/Documents/event2table/backend/gql_api')
    
    print("📊 GraphQL查询复杂度检查:")
    complex_queries = []
    
    for file_path in gql_path.rglob('*.py'):
        if file_path.name.startswith('__'):
            continue
        
        depth = check_query_complexity(file_path)
        if depth > 5:
            complex_queries.append({
                'file': str(file_path.relative_to(gql_path)),
                'depth': depth
            })
    
    if complex_queries:
        print(f"  找到 {len(complex_queries)} 个复杂查询:")
        for item in complex_queries[:10]:
            print(f"  - {item['file']}: 深度 {item['depth']}")
    else:
        print("  ✅ 所有查询复杂度正常")
    
    # 检查DataLoader使用
    print(f"\n🔄 DataLoader使用检查:")
    missing_dataloader = []
    
    for file_path in gql_path.rglob('*.py'):
        if file_path.name.startswith('__'):
            continue
        
        if check_missing_dataloader(file_path):
            missing_dataloader.append(str(file_path.relative_to(gql_path)))
    
    if missing_dataloader:
        print(f"  找到 {len(missing_dataloader)} 个可能需要DataLoader的文件:")
        for file in missing_dataloader[:10]:
            print(f"  - {file}")
    else:
        print("  ✅ DataLoader使用正常")
    
    # 检查缓存优化
    print(f"\n💾 缓存优化检查:")
    cache_path = Path('/Users/mckenzie/Documents/event2table/backend/gql_api/middleware/cache_middleware.py')
    
    if cache_path.exists():
        with open(cache_path, 'r') as f:
            cache_content = f.read()
        
        cache_patterns = [
            ('缓存键生成', 'cache_key' in cache_content),
            ('缓存失效', 'invalidate' in cache_content),
            ('缓存统计', 'stats' in cache_content),
        ]
        
        for name, has_pattern in cache_patterns:
            status = "✅" if has_pattern else "❌"
            print(f"  {status} {name}")
    
    # 检查订阅优化
    print(f"\n📡 订阅功能检查:")
    subscription_path = Path('/Users/mckenzie/Documents/event2table/backend/gql_api/subscriptions.py')
    
    if subscription_path.exists():
        print("  ✅ 订阅文件存在")
        with open(subscription_path, 'r') as f:
            sub_content = f.read()
        
        sub_features = [
            ('WebSocket连接', 'websocket' in sub_content.lower()),
            ('实时更新', 'subscribe' in sub_content.lower()),
            ('错误处理', 'error' in sub_content.lower()),
        ]
        
        for name, has_feature in sub_features:
            status = "✅" if has_feature else "⚠️"
            print(f"  {status} {name}")
    else:
        print("  ❌ 订阅文件不存在")
    
    return {
        'complex_queries': complex_queries,
        'missing_dataloader': missing_dataloader
    }

if __name__ == '__main__':
    main()

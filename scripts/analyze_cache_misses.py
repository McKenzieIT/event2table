#!/usr/bin/env python3
"""
Cache Miss Analysis Script
分析Redis缓存未命中模式
"""

import json
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def analyze_cache():
    """分析Redis缓存"""
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)

        # 获取所有缓存键
        cache_keys = r.keys('dwd_gen:v3:*')

        # 分析键模式
        key_patterns = defaultdict(int)
        ttl_distribution = defaultdict(int)
        key_details = []

        for key in cache_keys:
            # 统计键模式（提取模块和实体部分）
            parts = key.split(':')
            if len(parts) >= 4:
                # 格式: dwd_gen:v3:module:entity:params
                # 提取 module:entity
                pattern = ':'.join(parts[2:4])
                key_patterns[pattern] += 1
            elif len(parts) >= 2:
                pattern = ':'.join(parts[:2])
                key_patterns[pattern] += 1

            # 获取TTL
            try:
                ttl = r.ttl(key)
                if ttl == -1:  # 永不过期
                    ttl_distribution['no_expiry'] += 1
                elif ttl == -2:  # 不存在
                    ttl_distribution['not_found'] += 1
                elif ttl < 60:
                    ttl_distribution['<1min'] += 1
                elif ttl < 300:
                    ttl_distribution['1-5min'] += 1
                elif ttl < 1800:
                    ttl_distribution['5-30min'] += 1
                elif ttl < 3600:
                    ttl_distribution['30min-1hour'] += 1
                else:
                    ttl_distribution['>1hour'] += 1

                # 获取值大小
                try:
                    value_size = r.memory_usage(key)
                except:
                    value_size = 0

                # 记录键详情（仅前20个）
                if len(key_details) < 20:
                    key_details.append({
                        'key': key,
                        'ttl': ttl,
                        'type': r.type(key),
                        'size_bytes': value_size
                    })
            except Exception as e:
                ttl_distribution['error'] += 1

        # 获取缓存统计
        info = r.info('stats')
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        hit_rate = (hits / total * 100) if total > 0 else 0

        # 获取内存使用
        memory_info = r.info('memory')
        used_memory = memory_info.get('used_memory', 0)
        used_memory_human = memory_info.get('used_memory_human', '0B')

        # 生成报告
        report = {
            'cache_stats': {
                'hits': hits,
                'misses': misses,
                'total': total,
                'hit_rate_percent': round(hit_rate, 2)
            },
            'memory_stats': {
                'used_memory_bytes': used_memory,
                'used_memory_human': used_memory_human
            },
            'total_keys': len(cache_keys),
            'key_patterns': dict(sorted(key_patterns.items(), key=lambda x: x[1], reverse=True)),
            'ttl_distribution': dict(ttl_distribution),
            'sample_keys': key_details,
            'optimization_suggestions': []
        }

        # 生成优化建议
        if hit_rate < 85:
            report['optimization_suggestions'].append({
                'priority': 'HIGH',
                'issue': f'Cache hit rate ({hit_rate:.2f}%) below 85% (current target)',
                'suggestion': 'Implement cache warming strategy: pre-load frequently accessed data on startup',
                'action': 'Add @app.before_first_request cache warming for games.list, events.list, parameters.list'
            })

        if len(cache_keys) < 10:
            report['optimization_suggestions'].append({
                'priority': 'HIGH',
                'issue': f'Only {len(cache_keys)} cached keys (low cache utilization)',
                'suggestion': 'Cache is not being utilized effectively. Check if @cached decorators are applied to query functions.',
                'action': 'Review Service layer methods to ensure @cached decorators are used'
            })

        if ttl_distribution.get('<1min', 0) > len(cache_keys) * 0.3:
            report['optimization_suggestions'].append({
                'priority': 'MEDIUM',
                'issue': f'{ttl_distribution.get("<1min", 0)} keys ({ttl_distribution.get("<1min", 0)/len(cache_keys)*100:.1f}%) have TTL < 1 minute',
                'suggestion': 'Increase TTL for keys that change infrequently to reduce cache churn',
                'action': 'Adjust TTL values: static data (3600s), semi-static (1800s), dynamic (300s)'
            })

        if ttl_distribution.get('no_expiry', 0) > len(cache_keys) * 0.5:
            report['optimization_suggestions'].append({
                'priority': 'LOW',
                'issue': f'{ttl_distribution.get("no_expiry", 0)} keys ({ttl_distribution.get("no_expiry", 0)/len(cache_keys)*100:.1f}%) never expire',
                'suggestion': 'Review keys with no expiry to ensure they are not stale data',
                'action': 'Set reasonable TTL even for static data (e.g., 7200s for config)'
            })

        if misses > 0:
            miss_rate = (misses / total * 100) if total > 0 else 0
            report['optimization_suggestions'].append({
                'priority': 'MEDIUM',
                'issue': f'{misses} cache misses ({miss_rate:.2f}% miss rate)',
                'suggestion': 'Analyze which queries are missing cache and add @cached decorators',
                'action': 'Check logs for cache.miss patterns or add X-Cache-Status header monitoring'
            })

        if len(key_patterns) > 0:
            top_pattern = list(key_patterns.keys())[0]
            top_count = key_patterns[top_pattern]
            report['optimization_suggestions'].append({
                'priority': 'INFO',
                'issue': f'Most common pattern: {top_pattern} ({top_count} keys)',
                'suggestion': 'Consider pre-warming this pattern to improve hit rate',
                'action': f'Add cache warming for {top_pattern} in startup sequence'
            })

        # 保存报告
        os.makedirs('output', exist_ok=True)
        with open('output/cache_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        # 打印摘要
        print("="*60)
        print("Cache Analysis Report")
        print("="*60)
        print(f"Hit Rate: {hit_rate:.2f}% ({hits} hits, {misses} misses)")
        print(f"Total Keys: {len(cache_keys)}")
        print(f"Memory Used: {used_memory_human}")
        print(f"\nTop Key Patterns:")
        for pattern, count in sorted(key_patterns.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {pattern}: {count}")
        print(f"\nTTL Distribution:")
        for ttl_range, count in sorted(ttl_distribution.items()):
            print(f"  {ttl_range}: {count}")
        print(f"\nOptimization Suggestions: {len(report['optimization_suggestions'])}")
        for suggestion in report['optimization_suggestions']:
            print(f"  - [{suggestion['priority']}] {suggestion['issue']}")
        print(f"\nReport saved to: output/cache_analysis_report.json")

        return report

    except Exception as e:
        print(f"Error analyzing cache: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e)}

if __name__ == '__main__':
    analyze_cache()

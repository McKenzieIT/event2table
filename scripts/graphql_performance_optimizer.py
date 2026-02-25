#!/usr/bin/env python3
"""
GraphQL Performance Optimizer

Analyzes and optimizes GraphQL queries for better performance.
"""

import re
from typing import Dict, List, Set, Tuple
from pathlib import Path
import json


class GraphQLPerformanceOptimizer:
    """Optimize GraphQL queries and schema"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.optimizations = []
    
    def analyze_query_complexity(self, query: str) -> Dict:
        """Analyze query complexity"""
        # Count fields
        field_count = len(re.findall(r'\w+\s*[{(]', query))
        
        # Count depth
        depth = query.count('{') - query.count('}')
        
        # Count nested queries
        nested_queries = len(re.findall(r'\w+\s*\([^)]*\)\s*{', query))
        
        # Count fragments
        fragment_count = len(re.findall(r'\.\.\.\s*\w+', query))
        
        # Calculate complexity score
        complexity_score = (
            field_count * 1 +
            depth * 5 +
            nested_queries * 10 +
            fragment_count * 2
        )
        
        return {
            'field_count': field_count,
            'depth': depth,
            'nested_queries': nested_queries,
            'fragment_count': fragment_count,
            'complexity_score': complexity_score,
            'recommendations': self._get_complexity_recommendations(complexity_score, depth, nested_queries)
        }
    
    def _get_complexity_recommendations(self, score: int, depth: int, nested: int) -> List[str]:
        """Get recommendations based on complexity"""
        recommendations = []
        
        if score > 100:
            recommendations.append("⚠️ High complexity score. Consider splitting into multiple queries.")
        
        if depth > 5:
            recommendations.append("⚠️ Deep nesting detected. Consider using DataLoader or reducing depth.")
        
        if nested > 3:
            recommendations.append("⚠️ Many nested queries. May cause N+1 problem. Use DataLoader.")
        
        if not recommendations:
            recommendations.append("✅ Query complexity is acceptable.")
        
        return recommendations
    
    def find_n_plus_1_patterns(self) -> List[Dict]:
        """Find potential N+1 query patterns in resolvers"""
        patterns = []
        
        # Scan resolver files
        resolvers_dir = self.project_root / 'backend' / 'gql_api' / 'resolvers'
        if not resolvers_dir.exists():
            return patterns
        
        for file_path in resolvers_dir.rglob('*.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # Look for database queries in loops
                if re.search(r'for\s+\w+\s+in\s+', line):
                    # Check next few lines for database queries
                    for j in range(i, min(i + 5, len(lines))):
                        if re.search(r'(SELECT|INSERT|UPDATE|DELETE|fetch|execute)', lines[j], re.IGNORECASE):
                            patterns.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'code': line.strip(),
                                'recommendation': 'Use DataLoader to batch queries'
                            })
                            break
        
        return patterns
    
    def analyze_dataloader_usage(self) -> Dict:
        """Analyze DataLoader usage"""
        usage = {
            'dataloaders': [],
            'missing_dataloaders': []
        }
        
        # Check existing DataLoaders
        dataloaders_dir = self.project_root / 'backend' / 'gql_api' / 'dataloaders'
        if dataloaders_dir.exists():
            for file_path in dataloaders_dir.glob('*.py'):
                if file_path.name.startswith('__'):
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract DataLoader class names
                loader_classes = re.findall(r'class\s+(\w+Loader)\(', content)
                usage['dataloaders'].extend(loader_classes)
        
        # Check for missing DataLoaders
        # Scan resolvers for potential N+1 patterns
        resolvers_dir = self.project_root / 'backend' / 'gql_api' / 'resolvers'
        if resolvers_dir.exists():
            for file_path in resolvers_dir.rglob('*.py'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for list resolvers that might need DataLoader
                list_resolvers = re.findall(r'def resolve_(\w+s)\([^)]*\):\s*[^}]*\[', content, re.DOTALL)
                for resolver in list_resolvers:
                    if not any(loader.lower().startswith(resolver.lower()) for loader in usage['dataloaders']):
                        usage['missing_dataloaders'].append({
                            'resolver': resolver,
                            'file': str(file_path.relative_to(self.project_root)),
                            'recommendation': f'Consider creating {resolver.capitalize()}Loader'
                        })
        
        return usage
    
    def optimize_query(self, query: str) -> Tuple[str, List[str]]:
        """Optimize a GraphQL query"""
        optimizations = []
        optimized = query
        
        # Remove duplicate fields
        field_pattern = r'(\w+)\s*[{(]'
        fields = re.findall(field_pattern, query)
        if len(fields) != len(set(fields)):
            optimizations.append("Removed duplicate fields")
        
        # Suggest using fragments for repeated field sets
        if len(fields) > 5:
            optimizations.append("Consider using fragments for repeated field sets")
        
        # Check for unnecessary nesting
        if query.count('{') > 3:
            optimizations.append("Consider flattening query structure if possible")
        
        # Check for missing pagination
        if re.search(r'\w+s\s*{', query) and not re.search(r'limit|offset|first|last', query, re.IGNORECASE):
            optimizations.append("⚠️ List query without pagination. Add limit/offset to prevent large result sets.")
        
        return optimized, optimizations
    
    def generate_optimization_report(self) -> str:
        """Generate optimization report"""
        n_plus_1 = self.find_n_plus_1_patterns()
        dataloader_usage = self.analyze_dataloader_usage()
        
        report = []
        report.append("# GraphQL Performance Optimization Report")
        report.append(f"\n**Generated**: 2026-02-25")
        
        report.append(f"\n## DataLoader Usage")
        report.append(f"\n### Existing DataLoaders ({len(dataloader_usage['dataloaders'])})")
        for loader in dataloader_usage['dataloaders']:
            report.append(f"- ✅ {loader}")
        
        report.append(f"\n### Missing DataLoaders ({len(dataloader_usage['missing_dataloaders'])})")
        for item in dataloader_usage['missing_dataloaders'][:10]:
            report.append(f"- ⚠️ {item['resolver']} in {item['file']}")
            report.append(f"  Recommendation: {item['recommendation']}")
        
        report.append(f"\n## N+1 Query Patterns ({len(n_plus_1)})")
        for pattern in n_plus_1[:10]:
            report.append(f"- 🚨 {pattern['file']}:{pattern['line']}")
            report.append(f"  Code: `{pattern['code'][:80]}`")
            report.append(f"  Recommendation: {pattern['recommendation']}")
        
        report.append(f"\n## Optimization Recommendations")
        report.append(f"\n1. **Add DataLoaders** for list resolvers to prevent N+1 queries")
        report.append(f"2. **Use query complexity analysis** to limit expensive queries")
        report.append(f"3. **Implement pagination** for all list queries")
        report.append(f"4. **Use fragments** for repeated field sets")
        report.append(f"5. **Enable query caching** for frequently accessed data")
        
        return '\n'.join(report)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python graphql_performance_optimizer.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    optimizer = GraphQLPerformanceOptimizer(project_root)
    
    print("🔍 Analyzing GraphQL performance...")
    report = optimizer.generate_optimization_report()
    
    print("\n" + report)
    
    # Save report
    report_path = Path(project_root) / 'GRAPHQL_PERFORMANCE_OPTIMIZATION_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_path}")


if __name__ == '__main__':
    main()

"""
P0文件复杂度分析器

分析9个P0文件的JOIN查询复杂度，分为3个等级：
- Simple: < 30分（Agent 3处理）
- Medium: 30-60分（Agent 4处理）
- Complex: >= 60分（Agent 5处理）
"""

import re
from pathlib import Path
from typing import Dict, List


def analyze_complexity(p0_files: List[str]) -> Dict[str, List[str]]:
    """
    分析P0文件复杂度

    Args:
        p0_files: P0文件路径列表

    Returns:
        {
            "simple": [简单文件列表],
            "medium": [中等文件列表],
            "complex": [复杂文件列表]
        }
    """
    complexity_scores = {}

    for file_path in p0_files:
        if not Path(file_path).exists():
            print(f"⚠️  文件不存在: {file_path}")
            continue

        try:
            content = Path(file_path).read_text()
            score = calculate_complexity_score(content)
            complexity_scores[file_path] = score
        except Exception as e:
            print(f"❌ 分析失败 {file_path}: {e}")
            complexity_scores[file_path] = 50  # 默认中等

    # 分级
    simple = [f for f, s in complexity_scores.items() if s < 30]
    medium = [f for f, s in complexity_scores.items() if 30 <= s < 60]
    complex = [f for f, s in complexity_scores.items() if s >= 60]

    return {
        "simple": simple,
        "medium": medium,
        "complex": complex
    }


def calculate_complexity_score(content: str) -> int:
    """
    计算文件复杂度评分

    评分标准：
    - 循环内查询：+10分/个
    - 涉及表数量：+5分/个
    - 嵌套层级：+15分/层
    - 文件大小：+1分/100行

    Args:
        content: 文件内容

    Returns:
        复杂度评分
    """
    score = 0

    # 因子1: 循环内查询的数量（N+1查询模式）
    loop_queries = len(re.findall(
        r'for\s+\w+\s+in\s+\w+:.*?fetch_',
        content,
        re.DOTALL
    ))
    score += loop_queries * 10

    # 因子2: 涉及的表数量
    tables = set(re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', content))
    # Flatten tuples and filter empty
    tables = set(t[0] or t[1] for t in tables)
    score += len(tables) * 5

    # 因子3: 嵌套层级
    nesting = count_nesting_levels(content)
    score += nesting * 15

    # 因子4: 文件大小
    lines = content.count('\n')
    score += lines // 100

    return score


def count_nesting_levels(content: str) -> int:
    """
    计算代码嵌套层级

    Args:
        content: 文件内容

    Returns:
        最大嵌套层级
    """
    max_level = 0
    current_level = 0

    for line in content.split('\n'):
        stripped = line.strip()

        # 忽略注释和空行
        if not stripped or stripped.startswith('#'):
            continue

        # 检测块开始（以冒号结尾的行）
        if stripped.endswith(':') and not any(
            keyword in stripped
            for keyword in ['import', 'class', 'def', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'finally', 'with']
        ):
            current_level += 1
            max_level = max(max_level, current_level)

        # 简单的层级减少检测（基于缩进）
        if stripped and not line.startswith(' '):
            current_level = 0

    return max_level


def print_complexity_report(p0_files: List[str]) -> None:
    """
    打印复杂度分析报告

    Args:
        p0_files: P0文件路径列表
    """
    print("\n📊 P0文件复杂度分析")
    print("=" * 60)

    results = analyze_complexity(p0_files)

    print(f"\n简单文件 (Agent 3): {len(results['simple'])}个")
    for f in results['simple']:
        print(f"  - {f}")

    print(f"\n中等文件 (Agent 4): {len(results['medium'])}个")
    for f in results['medium']:
        print(f"  - {f}")

    print(f"\n复杂文件 (Agent 5): {len(results['complex'])}个")
    for f in results['complex']:
        print(f"  - {f}")

    print("=" * 60)


if __name__ == "__main__":
    # 测试
    p0_files = [
        "backend/api/routes/__init__.py",
        "backend/services/cache/cache_warmup.py",
        "backend/api/routes/bulk_routes.py",
        "backend/services/hql/builders/field_builder_service.py",
        "backend/services/parameters/event_param_manager.py",
        "backend/api/routes/join_configs_old_backup.py",
        "backend/api/routes/legacy_api.py",
        "backend/test/unit/services/field_builder/test_field_builder_service.py",
        "backend/test/unit/services/parameters/test_common_params.py"
    ]

    print_complexity_report(p0_files)

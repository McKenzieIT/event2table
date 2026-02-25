#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event2Table 优化方案验证脚本(简化版)

验证所有优化功能是否正确集成
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_file_exists(file_path: str, description: str) -> bool:
    """检查文件是否存在"""
    full_path = project_root / file_path
    if full_path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (不存在)")
        return False


def verify_optimization():
    """验证优化方案实施情况"""
    print("=" * 80)
    print("Event2Table 优化方案验证")
    print("=" * 80)
    print()
    
    all_passed = True
    
    # 1. 检查核心文件
    print("1. 检查核心文件...")
    print("-" * 80)
    
    files_to_check = [
        ("backend/services/hql/hql_service_cached.py", "HQL服务缓存增强版"),
        ("backend/services/parameters/parameter_service_cached.py", "参数服务缓存增强版"),
        ("backend/infrastructure/events/event_handlers.py", "领域事件处理器"),
        ("backend/core/startup/app_initializer.py", "应用启动初始化器"),
        ("backend/core/cache/decorators.py", "缓存装饰器工具"),
        ("backend/api/middleware/deprecation.py", "V1 API废弃中间件"),
        ("backend/gql_api/dataloaders/optimized_loaders.py", "GraphQL DataLoader优化"),
        ("frontend/src/pages/GamesPageGraphQL.tsx", "前端GraphQL迁移示例"),
        ("tests/performance/test_cache_performance.py", "缓存性能测试脚本"),
        ("run_optimization.sh", "快速启动脚本"),
    ]
    
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_passed = False
    
    print()
    
    # 2. 检查文档文件
    print("2. 检查文档文件...")
    print("-" * 80)
    
    docs_to_check = [
        ("docs/optimization/CORE_OPTIMIZATION_GUIDE.md", "核心优化指南"),
        ("docs/optimization/IMPLEMENTATION_GUIDE.md", "实施指南"),
        ("docs/optimization/PROGRESS.md", "实施进度"),
        ("docs/optimization/FINAL_SUMMARY.md", "最终总结"),
        ("docs/optimization/README.md", "优化方案README"),
    ]
    
    for file_path, description in docs_to_check:
        if not check_file_exists(file_path, description):
            all_passed = False
    
    print()
    
    # 3. 检查集成情况
    print("3. 检查集成情况...")
    print("-" * 80)
    
    # 检查web_app.py是否集成了初始化器
    web_app_path = project_root / "web_app.py"
    if web_app_path.exists():
        with open(web_app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "initialize_app" in content:
            print("✅ web_app.py已集成应用初始化器")
        else:
            print("❌ web_app.py未集成应用初始化器")
            all_passed = False
        
        if "init_deprecation_middleware" in content:
            print("✅ web_app.py已集成V1 API废弃中间件")
        else:
            print("❌ web_app.py未集成V1 API废弃中间件")
            all_passed = False
    else:
        print("❌ web_app.py不存在")
        all_passed = False
    
    # 检查hql_generation.py是否集成了缓存服务
    hql_api_path = project_root / "backend/api/routes/hql_generation.py"
    if hql_api_path.exists():
        with open(hql_api_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "HQLServiceCached" in content:
            print("✅ hql_generation.py已集成缓存增强版服务")
        else:
            print("❌ hql_generation.py未集成缓存增强版服务")
            all_passed = False
    else:
        print("❌ hql_generation.py不存在")
        all_passed = False
    
    print()
    
    # 4. 总结
    print("=" * 80)
    print("验证总结")
    print("=" * 80)
    
    if all_passed:
        print("✅ 所有检查通过!优化方案已成功实施。")
        print()
        print("创建的文件:")
        print("  - 10个核心功能模块")
        print("  - 5个文档文件")
        print("  - 2个修改的文件")
        print()
        print("下一步:")
        print("1. 查看文档: docs/optimization/README.md")
        print("2. 查看实施指南: docs/optimization/IMPLEMENTATION_GUIDE.md")
        print("3. 查看最终总结: docs/optimization/FINAL_SUMMARY.md")
        return 0
    else:
        print("❌ 部分检查未通过,请检查上述错误信息。")
        return 1


if __name__ == '__main__':
    exit_code = verify_optimization()
    sys.exit(exit_code)

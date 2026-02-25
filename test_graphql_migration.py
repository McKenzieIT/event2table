#!/usr/bin/env python3
"""
GraphQL迁移测试脚本
验证迁移后的GraphQL功能是否正常工作
"""

import sys
import os
import subprocess

def run_command(cmd, description):
    """运行命令并输出结果"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - 成功")
            if result.stdout:
                print(result.stdout[:500])  # 只显示前500字符
            return True
        else:
            print(f"❌ {description} - 失败")
            print(f"错误: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} - 超时")
        return False
    except Exception as e:
        print(f"❌ {description} - 异常: {e}")
        return False

def main():
    """主测试流程"""
    print("🚀 开始GraphQL迁移测试")
    
    tests = [
        # 后端GraphQL测试
        ("cd /Users/mckenzie/Documents/event2table && python3 -m pytest backend/tests/test_graphql_schema.py -v", 
         "GraphQL Schema测试"),
        
        ("cd /Users/mckenzie/Documents/event2table && python3 -m pytest backend/tests/test_games_graphql.py -v", 
         "Games GraphQL测试"),
        
        ("cd /Users/mckenzie/Documents/event2table && python3 -m pytest backend/tests/test_events_graphql.py -v", 
         "Events GraphQL测试"),
        
        # 前端GraphQL测试
        ("cd /Users/mckenzie/Documents/event2table/frontend && npm test -- graphql/hooks.test.ts --passWithNoTests",
         "前端GraphQL Hooks测试"),
        
        ("cd /Users/mckenzie/Documents/event2table/frontend && npm test -- graphql/integration.test.ts --passWithNoTests",
         "前端GraphQL集成测试"),
    ]
    
    results = []
    for cmd, desc in tests:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    # 输出测试总结
    print(f"\n{'='*60}")
    print("📊 测试总结")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for desc, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} - {desc}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())

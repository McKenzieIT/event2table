#!/bin/bash
# 快速验证测试覆盖率

echo "================================"
echo "后端测试覆盖率验证脚本"
echo "================================"
echo ""

# 激活虚拟环境
source backend/venv/bin/activate

echo "1. 运行安全测试..."
echo "--------------------------------"
python3 -m pytest backend/test/integration/security/test_sql_injection_prevention.py -v --tb=short

echo ""
echo "2. 统计测试文件..."
echo "--------------------------------"
echo "安全测试文件:"
find backend/test/integration/security -name "test_*.py" | wc -l
echo "HQL测试文件:"
find backend/test/unit/services/hql -name "test_*.py" | wc -l

echo ""
echo "3. 测试用例统计..."
echo "--------------------------------"
echo "总测试数:"
python3 -m pytest backend/test/ --collect-only -q | grep "test session starts" -A 2

echo ""
echo "4. 生成覆盖率报告..."
echo "--------------------------------"
python3 -m pytest backend/test/integration/security/ --cov=backend/core/security --cov=backend/models --cov-report=term-missing --tb=no

echo ""
echo "================================"
echo "验证完成！"
echo "================================"

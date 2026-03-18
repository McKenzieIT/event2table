#!/bin/bash
#
# Checkpoint 1 Verification Script
# 验证性能监控基线设置是否完成
#

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Checkpoint 1: Monitoring Baseline Setup"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
PASSED=0
FAILED=0
WARNINGS=0

# 检查函数
check_file() {
    local file=$1
    local description=$2

    echo -n "Checking $description... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  File not found: $file"
        ((FAILED++))
        return 1
    fi
}

check_directory() {
    local dir=$1
    local description=$2

    echo -n "Checking $description... "
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Directory not found: $dir"
        ((FAILED++))
        return 1
    fi
}

check_command() {
    local cmd=$1
    local description=$2

    echo -n "Checking $description... "
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠ WARN${NC}"
        echo "  Command not found: $cmd"
        ((WARNINGS++))
        return 1
    fi
}

check_package() {
    local package=$1
    local description=$2

    echo -n "Checking $description... "
    if grep -q "\"$package\"" frontend/package.json 2>/dev/null; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  Package not installed: $package"
        ((FAILED++))
        return 1
    fi
}

# 切换到项目根目录
cd "$(dirname "$0")/../.." || exit 1

echo "1. Lighthouse CI Setup"
echo "----------------------"
check_file ".github/workflows/lighthouse-ci.yml" "GitHub Actions workflow"
check_file "lighthouserc.json" "Lighthouse configuration"
check_file "lighthouse-budget.json" "Performance budget"
check_package "@lhci/cli" "Lighthouse CI package"
echo ""

echo "2. Performance Monitor Implementation"
echo "--------------------------------------"
check_file "frontend/src/monitoring/PerformanceMonitor.ts" "PerformanceMonitor class"
check_file "frontend/src/monitoring/__tests__/PerformanceMonitor.test.ts" "PerformanceMonitor tests"
check_directory "frontend/src/monitoring" "Monitoring module directory"
echo ""

echo "3. Coordination Dashboard"
echo "--------------------------"
check_file "frontend/src/monitoring/CoordinationDashboard.tsx" "CoordinationDashboard component"
check_file "frontend/src/monitoring/__tests__/CoordinationDashboard.test.tsx" "CoordinationDashboard tests"
echo ""

echo "4. Benchmark Scripts"
echo "--------------------"
check_file "scripts/benchmarks/test_api_performance.py" "API performance benchmark"
check_file "scripts/benchmarks/test_db_queries.py" "Database query benchmark"
check_file "scripts/benchmarks/generate_baseline_report.py" "Baseline report generator"
echo ""

echo "5. TypeScript Compilation"
echo "-------------------------"
echo -n "Checking TypeScript compilation... "
if cd frontend && npm run type-check 2>&1 | grep -q "No semantic errors"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC}"
    echo "  TypeScript compilation has errors or warnings"
    ((WARNINGS++))
fi
cd ..
echo ""

echo "6. Unit Tests"
echo "--------------"
echo -n "Running PerformanceMonitor tests... "
if cd frontend && npm test -- PerformanceMonitor.test.ts --run 2>&1 | grep -q "passed"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  PerformanceMonitor tests failed"
    ((FAILED++))
fi
cd ..

echo -n "Running CoordinationDashboard tests... "
if cd frontend && npm test -- CoordinationDashboard.test.tsx --run 2>&1 | grep -q "passed"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    echo "  CoordinationDashboard tests failed"
    ((FAILED++))
fi
cd ..
echo ""

echo "7. Output Directory"
echo "-------------------"
check_directory "output" "Output directory for reports"
echo ""

# 生成总结报告
echo "=========================================="
echo "CHECKPOINT SUMMARY"
echo "=========================================="
echo -e "Passed:   ${GREEN}$PASSED${NC}"
echo -e "Failed:   ${RED}$FAILED${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Checkpoint 1 PASSED${NC}"
    echo ""
    echo "All critical checks passed successfully!"
    echo "Monitoring baseline setup is complete."
    echo ""
    echo "Next Steps:"
    echo "1. Run baseline tests: python scripts/benchmarks/generate_baseline_report.py"
    echo "2. Review baseline report in output/baseline-*.json"
    echo "3. Proceed to Checkpoint 2"
    exit 0
else
    echo -e "${RED}✗ Checkpoint 1 FAILED${NC}"
    echo ""
    echo "Some critical checks failed. Please fix the issues above."
    exit 1
fi

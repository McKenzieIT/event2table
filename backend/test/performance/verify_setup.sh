#!/bin/bash

###############################################################################
# Performance Test Setup Verification Script
#
# This script verifies that all dependencies and requirements are met
# for running the cache performance tests.
#
# Usage:
#   bash verify_setup.sh
#
# Author: Event2Table Development Team
# Date: 2026-02-24
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS_COUNT=0
FAIL_COUNT=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS_COUNT++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL_COUNT++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "=========================================="
echo "Performance Test Setup Verification"
echo "=========================================="
echo ""

# Check Python
echo "Checking Python..."
if python3 --version &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "Python installed: $PYTHON_VERSION"
else
    check_fail "Python not found"
fi
echo ""

# Check Virtual Environment
echo "Checking Virtual Environment..."
if [ -f "backend/venv/bin/activate" ]; then
    check_pass "Virtual environment exists"
    source backend/venv/bin/activate
else
    check_fail "Virtual environment not found"
fi
echo ""

# Check Locust
echo "Checking Locust..."
if pip show locust &>/dev/null; then
    LOCUST_VERSION=$(pip show locust | grep "Version:" | cut -d' ' -f2)
    check_pass "Locust installed: $LOCUST_VERSION"
else
    check_fail "Locust not installed"
    echo "  Install with: pip install locust"
fi
echo ""

# Check psutil
echo "Checking psutil..."
if pip show psutil &>/dev/null; then
    PSUTIL_VERSION=$(pip show psutil | grep "Version:" | cut -d' ' -f2)
    check_pass "psutil installed: $PSUTIL_VERSION"
else
    check_fail "psutil not installed"
    echo "  Install with: pip install psutil"
fi
echo ""

# Check Backend Files
echo "Checking Backend Files..."
FILES=(
    "backend/test/performance/test_cache_performance.py"
    "backend/test/performance/run_performance_test.sh"
    "backend/test/performance/quick_test.sh"
    "backend/test/performance/README.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "File exists: $file"
    else
        check_fail "File missing: $file"
    fi
done
echo ""

# Check Script Permissions
echo "Checking Script Permissions..."
if [ -x "backend/test/performance/run_performance_test.sh" ]; then
    check_pass "run_performance_test.sh is executable"
else
    check_warn "run_performance_test.sh not executable (run: chmod +x backend/test/performance/run_performance_test.sh)"
fi

if [ -x "backend/test/performance/quick_test.sh" ]; then
    check_pass "quick_test.sh is executable"
else
    check_warn "quick_test.sh not executable (run: chmod +x backend/test/performance/quick_test.sh)"
fi
echo ""

# Check Backend Server
echo "Checking Backend Server..."
if curl -s http://127.0.0.1:5001/api/cache/stats &>/dev/null; then
    check_pass "Backend server is running on http://127.0.0.1:5001"
else
    check_warn "Backend server not running (start with: python3 web_app.py)"
fi
echo ""

# Check Database
echo "Checking Database..."
if [ -f "data/dwd_generator.db" ]; then
    DB_SIZE=$(du -h data/dwd_generator.db | cut -f1)
    check_pass "Database exists: data/dwd_generator.db ($DB_SIZE)"
else
    check_fail "Database not found: data/dwd_generator.db"
fi
echo ""

# Check Test Data
echo "Checking Test Data..."
source backend/venv/bin/activate 2>/dev/null || true
GAME_COUNT=$(sqlite3 data/dwd_generator.db "SELECT COUNT(*) FROM games;" 2>/dev/null || echo "0")
if [ "$GAME_COUNT" -gt 0 ]; then
    check_pass "Test games found: $GAME_COUNT games"
else
    check_warn "No games found in database (add test data first)"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo -e "${GREEN}Passed:${NC} $PASS_COUNT"
echo -e "${RED}Failed:${NC} $FAIL_COUNT"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to run performance tests.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Start backend (if not running): python3 web_app.py"
    echo "  2. Run tests: bash backend/test/performance/run_performance_test.sh"
    echo "  3. Or quick test: bash backend/test/performance/quick_test.sh normal"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix the issues above.${NC}"
    exit 1
fi

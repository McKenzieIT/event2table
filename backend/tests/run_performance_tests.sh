#!/bin/bash
# Performance Test Runner for Event2Table
#
# Runs comprehensive performance tests for:
# - REST API endpoints
# - Database queries
# - Cache operations
# - Frontend rendering

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/Users/mckenzie/Documents/event2table"
cd "$PROJECT_ROOT"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🚀 Event2Table Performance Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if backend is running
echo -e "${YELLOW}📋 Checking backend server...${NC}"
if ! curl -s http://127.0.0.1:5001/api/games > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend server not running!${NC}"
    echo -e "${YELLOW}Start with: python web_app.py${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Backend server is running${NC}"
echo ""

# Create output directory
OUTPUT_DIR="$PROJECT_ROOT/output/performance-tests"
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$OUTPUT_DIR/performance_report_$TIMESTAMP.txt"

# Function to run test suite
run_test_suite() {
    local suite_name=$1
    local test_command=$2

    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo -e "${BLUE}🧪 Running: $suite_name${NC}"
    echo -e "${BLUE}───────────────────────────────────────────────────────────────${NC}"
    echo ""

    if eval "$test_command 2>&1 | tee -a $REPORT_FILE"; then
        echo -e "${GREEN}✅ $suite_name PASSED${NC}"
    else
        echo -e "${RED}❌ $suite_name FAILED${NC}"
        return 1
    fi
    echo ""
}

# Initialize report
cat > "$REPORT_FILE" << EOF
═══════════════════════════════════════════════════════════════
Event2Table Performance Test Report
═══════════════════════════════════════════════════════════════
Date: $(date)
Environment: Development
Python: $(python --version)
Node: $(node --version 2>/dev/null || echo "N/A")

EOF

# Test 1: API Performance
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 Backend Performance Tests${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

run_test_suite "REST API Performance" \
    "python3 -m pytest backend/tests/performance/test_api_performance.py -v --tb=short"

run_test_suite "Database Query Performance" \
    "python3 -m pytest backend/tests/performance/test_database_performance.py -v --tb=short"

run_test_suite "Cache Performance" \
    "python3 -m pytest backend/tests/performance/test_cache_performance.py -v --tb=short"

# Test 2: Frontend Performance (if frontend is running)
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📊 Frontend Performance Tests${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📋 Checking frontend server...${NC}"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend server is running${NC}"

    cd "$PROJECT_ROOT/frontend"

    run_test_suite "Frontend Rendering Performance" \
        "npx playwright test test/e2e/performance/frontend-performance.spec.js --reporter=line"

    cd "$PROJECT_ROOT"
else
    echo -e "${YELLOW}⚠️  Frontend server not running, skipping frontend tests${NC}"
    echo -e "${YELLOW}   Start with: cd frontend && npm run dev${NC}"
fi

# Generate summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📋 Performance Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Count passed/failed tests from report
if [ -f "$REPORT_FILE" ]; then
    PASSED=$(grep -c "PASSED" "$REPORT_FILE" || echo "0")
    FAILED=$(grep -c "FAILED" "$REPORT_FILE" || echo "0")
    TOTAL=$((PASSED + FAILED))

    echo "Total Tests: $TOTAL"
    echo -e "Passed: ${GREEN}$PASSED${NC}"
    echo -e "Failed: ${RED}$FAILED${NC}"

    if [ $FAILED -eq 0 ]; then
        echo -e "\n${GREEN}✅ All performance tests PASSED!${NC}"
    else
        echo -e "\n${RED}❌ Some performance tests FAILED${NC}"
        echo -e "${YELLOW}See report: $REPORT_FILE${NC}"
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📄 Full report saved to:${NC}"
echo -e "$REPORT_FILE"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Exit with appropriate code
if [ "$FAILED" -gt 0 ]; then
    exit 1
fi

exit 0

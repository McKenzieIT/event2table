#!/bin/bash

# Event Node Builder Config Management E2E Test Verification Script
# 快速验证测试环境和依赖

set -e

echo "========================================="
echo "Event Node Builder Config Management"
echo "E2E Test Verification Script"
echo "========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_service() {
    local name=$1
    local url=$2

    echo -n "Checking $name... "
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not available${NC}"
        return 1
    fi
}

check_file() {
    local file=$1
    local description=$2

    echo -n "Checking $description... "
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ Found${NC}"
        return 0
    else
        echo -e "${RED}✗ Not found${NC}"
        return 1
    fi
}

# 1. Check if backend is running
echo "1. Backend Service"
check_service "Backend API" "http://127.0.0.1:5001/api/health" || \
check_service "Backend API" "http://127.0.0.1:5001/api/games"
echo ""

# 2. Check if frontend is running
echo "2. Frontend Service"
check_service "Frontend Dev Server" "http://localhost:5173"
echo ""

# 3. Check test files
echo "3. Test Files"
check_file \
    "/Users/mckenzie/Documents/event2table/frontend/test/e2e/critical/config-management.spec.ts" \
    "Config Management Test File"
check_file \
    "/Users/mckenzie/Documents/event2table/frontend/test/e2e/critical/README-CONFIG-MANAGEMENT.md" \
    "Test README"
check_file \
    "/Users/mckenzie/Documents/event2table/CONFIG-MANAGEMENT-E2E-TEST-SUMMARY.md" \
    "Test Summary"
echo ""

# 4. Check Playwright installation
echo "4. Playwright Installation"
echo -n "Checking Playwright... "
if command -v npx &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
fi
echo ""

# 5. Check test data (Game GID: 10000147)
echo "5. Test Data"
echo -n "Checking Game Data (GID: 10000147)... "
if curl -s "http://127.0.0.1:5001/api/games?game_gid=10000147" | grep -q "STAR001\|10000147"; then
    echo -e "${GREEN}✓ Available${NC}"
else
    echo -e "${YELLOW}⚠ Not verified${NC}"
fi
echo ""

# 6. Summary
echo "========================================="
echo "Verification Summary"
echo "========================================="

BACKEND_RUNNING=false
FRONTEND_RUNNING=false
TEST_FILES_OK=false

if curl -s -f "http://127.0.0.1:5001/api/games" > /dev/null 2>&1; then
    BACKEND_RUNNING=true
fi

if curl -s -f "http://localhost:5173" > /dev/null 2>&1; then
    FRONTEND_RUNNING=true
fi

if [ -f "/Users/mckenzie/Documents/event2table/frontend/test/e2e/critical/config-management.spec.ts" ]; then
    TEST_FILES_OK=true
fi

if [ "$BACKEND_RUNNING" = true ] && [ "$FRONTEND_RUNNING" = true ] && [ "$TEST_FILES_OK" = true ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to run tests.${NC}"
    echo ""
    echo "Run tests with:"
    echo "  cd /Users/mckenzie/Documents/event2table/frontend"
    echo "  npm run test:e2e -- config-management.spec.ts"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please fix the issues above.${NC}"
    echo ""
    if [ "$BACKEND_RUNNING" = false ]; then
        echo -e "${YELLOW}→ Start backend: ${NC}cd backend && source venv/bin/activate && python web_app.py"
    fi
    if [ "$FRONTEND_RUNNING" = false ]; then
        echo -e "${YELLOW}→ Start frontend: ${NC}cd frontend && npm run dev"
    fi
    if [ "$TEST_FILES_OK" = false ]; then
        echo -e "${YELLOW}→ Test files missing${NC}"
    fi
    echo ""
    exit 1
fi

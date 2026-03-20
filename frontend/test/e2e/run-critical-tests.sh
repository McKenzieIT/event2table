#!/bin/bash

###############################################################################
# E2E Test Runner - Critical Pages
#
# This script runs all critical E2E tests and generates coverage reports.
#
# Usage:
#   ./run-critical-tests.sh              # Run all tests
#   ./run-critical-tests.sh --ui         # Run with UI
#   ./run-critical-tests.sh --debug      # Run with debug mode
#   ./run-critical-tests.sh --update     # Update snapshots
#
# Requirements:
#   - Backend server running on http://127.0.0.1:5001
#   - Frontend dev server running on http://localhost:5173
#   - Playwright installed (npm install -D @playwright/test)
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Event2Table E2E Test Runner${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if backend is running
echo -e "${YELLOW}Checking backend server...${NC}"
if curl -s http://127.0.0.1:5001/api/games > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend server is running${NC}"
else
    echo -e "${RED}✗ Backend server is not running!${NC}"
    echo -e "${YELLOW}Please start backend with: cd backend && python web_app.py${NC}"
    exit 1
fi

# Check if frontend is running
echo -e "${YELLOW}Checking frontend dev server...${NC}"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Frontend dev server is running${NC}"
else
    echo -e "${RED}✗ Frontend dev server is not running!${NC}"
    echo -e "${YELLOW}Please start frontend with: cd frontend && npm run dev${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Running E2E Tests${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Change to frontend directory
cd "$FRONTEND_DIR"

# Parse command line arguments
PLAYWRIGHT_ARGS=""
if [[ "$1" == "--ui" ]]; then
    PLAYWRIGHT_ARGS="--ui"
elif [[ "$1" == "--debug" ]]; then
    PLAYWRIGHT_ARGS="--debug"
elif [[ "$1" == "--update" ]]; then
    PLAYWRIGHT_ARGS="--update-snapshots"
fi

# Run tests
echo -e "${YELLOW}Running critical page tests...${NC}"
npx playwright test critical/ $PLAYWRIGHT_ARGS

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Test Results${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Test report: file://$FRONTEND_DIR/test/e2e/playwright-report/index.html"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Test report: file://$FRONTEND_DIR/test/e2e/playwright-report/index.html"
    echo ""
    echo "To debug failing tests:"
    echo "  npx playwright test critical/ --debug"
fi

exit $TEST_EXIT_CODE

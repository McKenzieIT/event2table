#!/bin/bash

# Performance Test Runner for @shared/ui Component Library

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

FRONTEND_DIR="/Users/mckenzie/Documents/event2table/frontend"

echo -e "${BOLD}${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     @shared/ui Performance Test Suite                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$FRONTEND_DIR"

# Step 1: Build the application
echo -e "\n${BOLD}${BLUE}Step 1: Building application...${NC}"
npm run build

# Step 2: Run re-render tests
echo -e "\n${BOLD}${BLUE}Step 2: Running Re-render Tests...${NC}"
npm test -- src/shared/ui/__tests__/performance/RerenderTest.tsx --run 2>&1 || true

# Step 3: Run rendering performance tests
echo -e "\n${BOLD}${BLUE}Step 3: Running Rendering Performance Tests...${NC}"
npm test -- src/shared/ui/__tests__/performance/RenderingPerformanceTest.tsx --run 2>&1 || true

# Step 4: Run memory leak tests
echo -e "\n${BOLD}${BLUE}Step 4: Running Memory Leak Tests...${NC}"
npm test -- src/shared/ui/__tests__/performance/MemoryLeakTest.tsx --run 2>&1 || true

# Step 5: Generate bundle size report
echo -e "\n${BOLD}${BLUE}Step 5: Analyzing Bundle Size...${NC}"
npx tsx src/shared/ui/__tests__/performance/BundleSizeTest.ts 2>&1 || true

# Step 6: Generate final report
echo -e "\n${BOLD}${BLUE}Step 6: Generating Final Report...${NC}"
npx tsx src/shared/ui/__tests__/performance/GenerateReport.ts 2>&1 || true

echo -e "\n${BOLD}${GREEN}✅ Performance testing complete!${NC}\n"
echo -e "Reports saved to:"
echo -e "  - ${FRONTEND_DIR}/PERFORMANCE_TEST_REPORT.json"
echo -e "  - ${FRONTEND_DIR}/bundle-size-report.json"
echo -e ""

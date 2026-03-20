#!/bin/bash
# E2E Test Runner Script for Event2Table
#
# This script runs the complete E2E test suite for parameter management
# and event builder functionality.
#
# Usage:
#   ./frontend/test/e2e/run-e2e-tests.sh [options]
#
# Options:
#   --quick          Run only smoke tests
#   --full           Run all E2E tests (default)
#   --parameter      Run only parameter management tests
#   --builder        Run only event builder tests
#   --headed         Run tests in headed mode (show browser)
#   --debug          Run tests in debug mode
#   --report         Generate HTML report
#   --help           Show this help message

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="/Users/mckenzie/Documents/event2table"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
cd "$FRONTEND_DIR"

# Default options
RUN_MODE="full"
HEADED=""
DEBUG=""
REPORT=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --quick)
      RUN_MODE="quick"
      shift
      ;;
    --full)
      RUN_MODE="full"
      shift
      ;;
    --parameter)
      RUN_MODE="parameter"
      shift
      ;;
    --builder)
      RUN_MODE="builder"
      shift
      ;;
    --headed)
      HEADED="--headed"
      shift
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    --report)
      REPORT="--report"
      shift
      ;;
    --help)
      echo "Event2Table E2E Test Runner"
      echo ""
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  --quick          Run only smoke tests"
      echo "  --full           Run all E2E tests (default)"
      echo "  --parameter      Run only parameter management tests"
      echo "  --builder        Run only event builder tests"
      echo "  --headed         Run tests in headed mode (show browser)"
      echo "  --debug          Run tests in debug mode"
      echo "  --report         Generate HTML report"
      echo "  --help           Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0 --quick                     # Run smoke tests only"
      echo "  $0 --parameter --headed        # Run parameter tests with visible browser"
      echo "  $0 --builder --debug           # Debug event builder tests"
      echo "  $0 --full --report             # Run all tests and generate report"
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      echo "Use --help to see available options"
      exit 1
      ;;
  esac
done

# Function to print colored messages
print_info() {
  echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
  echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
  echo -e "${RED}✗ ${1}${NC}"
}

print_section() {
  echo ""
  echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  ${1}${NC}"
  echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
  echo ""
}

# Check if Node.js is installed
print_section "Checking Environment"

if ! command -v node &> /dev/null; then
  print_error "Node.js is not installed"
  exit 1
fi

print_success "Node.js $(node --version) found"

if ! command -v npm &> /dev/null; then
  print_error "npm is not installed"
  exit 1
fi

print_success "npm $(npm --version) found"

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
  print_warning "Dependencies not installed. Installing..."
  npm install
  print_success "Dependencies installed"
else
  print_success "Dependencies already installed"
fi

# Check if Playwright is installed
if ! npx playwright --version &> /dev/null; then
  print_warning "Playwright not found. Installing..."
  npx playwright install
  print_success "Playwright installed"
else
  print_success "Playwright $(npx playwright --version) found"
fi

# Check server status
print_section "Checking Server Status"

BACKEND_URL="http://127.0.0.1:5001"
FRONTEND_URL="http://localhost:5173"

if curl -s "$BACKEND_URL/api/health" > /dev/null 2>&1; then
  print_success "Backend server is running ($BACKEND_URL)"
else
  print_error "Backend server is not running!"
  echo ""
  echo "Start backend with:"
  echo "  cd $PROJECT_ROOT"
  echo "  python web_app.py"
  echo ""
  exit 1
fi

if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
  print_success "Frontend server is running ($FRONTEND_URL)"
else
  print_error "Frontend server is not running!"
  echo ""
  echo "Start frontend with:"
  echo "  cd $FRONTEND_DIR"
  echo "  npm run dev"
  echo ""
  exit 1
fi

# Run tests based on mode
print_section "Running E2E Tests"

TEST_COMMAND="npx playwright test"

case $RUN_MODE in
  quick)
    print_info "Running smoke tests only..."
    TEST_COMMAND="$TEST_COMMAND test/e2e/smoke/"
    ;;
  parameter)
    print_info "Running parameter management tests..."
    TEST_COMMAND="$TEST_COMMAND test/e2e/critical/test-parameter-management.spec.js"
    ;;
  builder)
    print_info "Running event builder tests..."
    TEST_COMMAND="$TEST_COMMAND test/e2e/critical/test-event-builder-fields.spec.js"
    ;;
  full)
    print_info "Running full E2E test suite..."
    TEST_COMMAND="$TEST_COMMAND test/e2e/critical/"
    ;;
esac

# Add options
if [ -n "$HEADED" ]; then
  TEST_COMMAND="$TEST_COMMAND $HEADED"
fi

if [ -n "$DEBUG" ]; then
  TEST_COMMAND="$TEST_COMMAND $DEBUG"
fi

if [ -n "$REPORT" ]; then
  TEST_COMMAND="$TEST_COMMAND $REPORT"
fi

print_info "Test command: $TEST_COMMAND"
echo ""

# Run tests
START_TIME=$(date +%s)

eval $TEST_COMMAND

TEST_EXIT_CODE=$?

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Display results
echo ""
print_section "Test Results"

if [ $TEST_EXIT_CODE -eq 0 ]; then
  print_success "All tests passed! (Duration: ${DURATION}s)"
else
  print_error "Some tests failed! (Duration: ${DURATION}s)"
  echo ""
  echo "View detailed report:"
  echo "  open test/e2e/playwright-report/index.html"
fi

# Show report location
if [ -f "test/e2e/results.json" ]; then
  print_info "Test results: test/e2e/results.json"
fi

if [ -d "test/e2e/playwright-report" ]; then
  print_info "HTML report: test/e2e/playwright-report/index.html"

  if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    read -p "Open HTML report? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      open test/e2e/playwright-report/index.html
    fi
  fi
fi

# Show screenshots if tests failed
if [ $TEST_EXIT_CODE -ne 0 ] && [ -d "test/e2e/output/screenshots" ]; then
  SCREENSHOT_COUNT=$(ls -1 test/e2e/output/screenshots/*.png 2>/dev/null | wc -l)
  if [ $SCREENSHOT_COUNT -gt 0 ]; then
    print_warning "Screenshots saved: test/e2e/output/screenshots/ ($SCREENSHOT_COUNT files)"
  fi
fi

exit $TEST_EXIT_CODE

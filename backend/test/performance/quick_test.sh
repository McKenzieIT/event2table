#!/bin/bash

###############################################################################
# Quick Performance Test - Single Scenario
#
# This script runs a single performance test scenario.
# Useful for quick validation during development.
#
# Usage:
#   bash quick_test.sh [normal|high|extreme]
#
# Default: normal
#
# Author: Event2Table Development Team
# Date: 2026-02-24
###############################################################################

set -e

# Configuration
SCENARIO=${1:-normal}
PROJECT_ROOT="/Users/mckenzie/Documents/event2table"
TEST_DIR="$PROJECT_ROOT/backend/test/performance"
HOST="http://127.0.0.1:5001"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[INFO]${NC} Quick Performance Test - Scenario: $SCENARIO"
echo ""

# Check backend
if ! curl -s "$HOST/api/cache/stats" > /dev/null 2>&1; then
    echo -e "${BLUE}[INFO]${NC} Backend not running. Starting..."
    cd "$PROJECT_ROOT"
    source backend/venv/bin/activate
    python3 web_app.py > /tmp/backend_quick_test.log 2>&1 &
    BACKEND_PID=$!
    echo -e "${GREEN}[SUCCESS]${NC} Backend started (PID: $BACKEND_PID)"
    sleep 5
fi

# Run test based on scenario
cd "$TEST_DIR"

case $SCENARIO in
    normal)
        echo "Running NORMAL load test (100 users)..."
        locust -f test_cache_performance.py \
            --headless \
            --host "$HOST" \
            --users 100 \
            --spawn-rate 10 \
            --run-time 30s \
            --csv quick_normal
        ;;
    high)
        echo "Running HIGH load test (500 users)..."
        locust -f test_cache_performance.py \
            --headless \
            --host "$HOST" \
            --users 500 \
            --spawn-rate 50 \
            --run-time 30s \
            --csv quick_high
        ;;
    extreme)
        echo "Running EXTREME load test (1000 users)..."
        locust -f test_cache_performance.py \
            --headless \
            --host "$HOST" \
            --users 1000 \
            --spawn-rate 100 \
            --run-time 30s \
            --csv quick_extreme
        ;;
    *)
        echo "Unknown scenario: $SCENARIO"
        echo "Usage: bash quick_test.sh [normal|high|extreme]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}[SUCCESS]${NC} Test completed!"
echo "Results: quick_${SCENARIO}_stats.csv"

# Cleanup (optional - comment out if you want to keep backend running)
# if [ -n "$BACKEND_PID" ]; then
#     kill $BACKEND_PID
# fi

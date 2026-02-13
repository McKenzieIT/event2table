#!/bin/bash

# Frontend Performance Test Script
# DWD Generator - event2table
#
# This script runs automated performance tests on the frontend
# and generates a comprehensive report.

set -e  # Exit on error

echo "========================================"
echo "Frontend Performance Testing"
echo "DWD Generator - event2table"
echo "========================================"
echo "Date: $(date)"
echo "Environment: $(uname -a)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results array
declare -a RESULTS
declare -a METRICS

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for server to be ready
wait_for_server() {
    local port=$1
    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$port > /dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    return 1
}

# Change to frontend directory
cd "$(dirname "$0")/../..""
FRONTEND_DIR=$(pwd)
print_info "Frontend directory: $FRONTEND_DIR"

# Check dependencies
echo ""
echo "========================================"
echo "Checking Dependencies"
echo "========================================"

if ! command_exists npm; then
    print_error "npm not found. Please install Node.js first."
    echo "Download from: https://nodejs.org/"
    exit 1
fi
print_success "npm found"

if ! command_exists node; then
    print_error "node not found. Please install Node.js first."
    exit 1
fi
print_success "node found"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_warning "node_modules not found. Installing dependencies..."
    npm install
fi
print_success "Dependencies installed"

# Create results directory
RESULTS_DIR="$FRONTEND_DIR/tests/performance/results"
mkdir -p "$RESULTS_DIR"
print_info "Results directory: $RESULTS_DIR"

# ========================================
# Test 1: Development Server Start Time
# ========================================
echo ""
echo "========================================"
echo "Test 1: Development Server Start Time"
echo "========================================"
echo "Target: < 5s"

if port_in_use 5173; then
    print_warning "Port 5173 already in use. Using port 5174."
    VITE_PORT=5174
else
    VITE_PORT=5173
fi

START=$(date +%s%N)  # Nanoseconds
npm run dev -- --port=$VITE_PORT > /dev/null 2>&1 &
DEV_PID=$!

if wait_for_server $VITE_PORT; then
    END=$(date +%s%N)
    ELAPSED=$(( (END - START) / 1000000 ))  # Convert to milliseconds
    ELAPSED_SEC=$(echo "scale=2; $ELAPSED / 1000" | bc)
    echo "Dev server started in ${ELAPSED_SEC}s"

    if [ $ELAPSED -lt 5000 ]; then
        print_success "PASS (${ELAPSED_SEC}s)"
        RESULTS+=("Dev Start: PASS (${ELAPSED_SEC}s)")
        METRICS+=("dev_start_ms:$ELAPSED")
    else
        print_warning "WARNING - Target: < 5s, Actual: ${ELAPSED_SEC}s"
        RESULTS+=("Dev Start: WARNING (${ELAPSED_SEC}s)")
        METRICS+=("dev_start_ms:$ELAPSED")
    fi
else
    print_error "FAIL - Server did not start in time"
    RESULTS+=("Dev Start: FAIL (timeout)")
    METRICS+=("dev_start_ms:timeout")
fi

# ========================================
# Test 2: Production Build Time
# ========================================
echo ""
echo "========================================"
echo "Test 2: Production Build Time"
echo "========================================"
echo "Target: < 60s"

START=$(date +%s%N)

if npm run build > /tmp/build.log 2>&1; then
    END=$(date +%s%N)
    ELAPSED=$(( (END - START) / 1000000 ))
    ELAPSED_SEC=$(echo "scale=2; $ELAPSED / 1000" | bc)
    echo "Build completed in ${ELAPSED_SEC}s"

    if [ $ELAPSED -lt 60000 ]; then
        print_success "PASS (${ELAPSED_SEC}s)"
        RESULTS+=("Build Time: PASS (${ELAPSED_SEC}s)")
        METRICS+=("build_time_ms:$ELAPSED")
    else
        print_error "FAIL - Target: < 60s, Actual: ${ELAPSED_SEC}s"
        RESULTS+=("Build Time: FAIL (${ELAPSED_SEC}s)")
        METRICS+=("build_time_ms:$ELAPSED")
    fi
else
    print_error "Build failed. Check /tmp/build.log for details."
    RESULTS+=("Build Time: FAIL (build error)")
    METRICS+=("build_time_ms:error")
fi

# ========================================
# Test 3: Bundle Size Analysis
# ========================================
echo ""
echo "========================================"
echo "Test 3: Bundle Size Analysis"
echo "========================================"
echo "Target: Main bundle < 500 KB"

if [ -d "dist/assets" ]; then
    # Find largest JavaScript file
    LARGEST_BUNDLE=$(find dist/assets -name "*.js" -type f -exec du -h {} \; | sort -rh | head -1)
    BUNDLE_SIZE=$(echo "$LARGEST_BUNDLE" | cut -f1)
    BUNDLE_FILE=$(echo "$LARGEST_BUNDLE" | cut -f2)

    echo "Largest bundle: $BUNDLE_FILE ($BUNDLE_SIZE)"

    # Convert to MB for comparison
    BUNDLE_MB=$(echo $BUNDLE_SIZE | sed 's/M//')
    BUNDLE_KB=$(echo $BUNDLE_SIZE | sed 's/K//' | awk '{print $1}')

    if [[ $BUNDLE_SIZE == *"M"* ]]; then
        # Size is in MB
        if (( $(echo "$BUNDLE_MB < 1.0" | bc -l) )); then
            print_success "PASS ($BUNDLE_SIZE)"
            RESULTS+=("Bundle Size: PASS ($BUNDLE_SIZE)")
            METRICS+=("bundle_size_kb:$(( ${BUNDLE_MB%.*} * 1024 ))")
        else
            print_warning "WARNING - Target: < 1 MB, Actual: $BUNDLE_SIZE"
            RESULTS+=("Bundle Size: WARNING ($BUNDLE_SIZE)")
            METRICS+=("bundle_size_kb:$(( ${BUNDLE_MB%.*} * 1024 ))")
        fi
    else
        # Size is in KB
        if [ $BUNDLE_KB -lt 500 ]; then
            print_success "PASS ($BUNDLE_SIZE)"
            RESULTS+=("Bundle Size: PASS ($BUNDLE_SIZE)")
            METRICS+=("bundle_size_kb:$BUNDLE_KB")
        else
            print_warning "WARNING - Target: < 500 KB, Actual: $BUNDLE_SIZE"
            RESULTS+=("Bundle Size: WARNING ($BUNDLE_SIZE)")
            METRICS+=("bundle_size_kb:$BUNDLE_KB")
        fi
    fi

    # Total bundle size
    TOTAL_SIZE=$(du -sh dist | cut -f1)
    echo "Total bundle size: $TOTAL_SIZE"
else
    print_error "dist directory not found"
    RESULTS+=("Bundle Size: FAIL (no build)")
    METRICS+=("bundle_size_kb:error")
fi

# ========================================
# Test 4: Lighthouse Performance Score
# ========================================
echo ""
echo "========================================"
echo "Test 4: Lighthouse Performance Test"
echo "========================================"
echo "Target: Performance score > 90"

if command_exists lighthouse; then
    print_info "Running Lighthouse..."

    # Ensure dev server is running
    if ! port_in_use $VITE_PORT; then
        npm run dev -- --port=$VITE_PORT > /dev/null 2>&1 &
        DEV_PID=$!
        sleep 5
    fi

    # Run Lighthouse
    LIGHTHOUSE_REPORT="$RESULTS_DIR/lighthouse-report-$(date +%Y%m%d-%H%M%S).json"

    if lighthouse http://localhost:$VITE_PORT \
        --output=json \
        --output=html \
        --chrome-flags="--headless" \
        --only-categories=performance \
        --output-path="$LIGHTHOUSE_REPORT" \
        --quiet; then

        # Extract performance score
        if [ -f "$LIGHTHOUSE_REPORT" ]; then
            PERFORMANCE_SCORE=$(node -e "const fs = require('fs'); const report = JSON.parse(fs.readFileSync('$LIGHTHOUSE_REPORT', 'utf8')); console.log(Math.round(report.categories.performance.score * 100));")
            echo "Performance Score: $PERFORMANCE_SCORE"

            if [ $PERFORMANCE_SCORE -gt 90 ]; then
                print_success "PASS ($PERFORMANCE_SCORE)"
                RESULTS+=("Lighthouse: PASS ($PERFORMANCE_SCORE)")
                METRICS+=("lighthouse_score:$PERFORMANCE_SCORE")
            elif [ $PERFORMANCE_SCORE -gt 70 ]; then
                print_warning "WARNING - Target: > 90, Actual: $PERFORMANCE_SCORE"
                RESULTS+=("Lighthouse: WARNING ($PERFORMANCE_SCORE)")
                METRICS+=("lighthouse_score:$PERFORMANCE_SCORE")
            else
                print_error "FAIL - Target: > 90, Actual: $PERFORMANCE_SCORE"
                RESULTS+=("Lighthouse: FAIL ($PERFORMANCE_SCORE)")
                METRICS+=("lighthouse_score:$PERFORMANCE_SCORE")
            fi

            # Extract detailed metrics
            FCP=$(node -e "const fs = require('fs'); const report = JSON.parse(fs.readFileSync('$LIGHTHOUSE_REPORT', 'utf8')); console.log(Math.round(report.audits['first-contentful-paint'].numericValue));")
            LCP=$(node -e "const fs = require('fs'); const report = JSON.parse(fs.readFileSync('$LIGHTHOUSE_REPORT', 'utf8')); console.log(Math.round(report.audits['largest-contentful-paint'].numericValue));")
            TTI=$(node -e "const fs = require('fs'); const report = JSON.parse(fs.readFileSync('$LIGHTHOUSE_REPORT', 'utf8')); console.log(Math.round(report.audits['interactive'].numericValue));")
            TBT=$(node -e "const fs = require('fs'); const report = JSON.parse(fs.readFileSync('$LIGHTHOUSE_REPORT', 'utf8')); console.log(Math.round(report.audits['total-blocking-time'].numericValue));")

            echo "FCP: ${FCP}ms"
            echo "LCP: ${LCP}ms"
            echo "TTI: ${TTI}ms"
            echo "TBT: ${TBT}ms"

            METRICS+=("fcp_ms:$FCP")
            METRICS+=("lcp_ms:$LCP")
            METRICS+=("tti_ms:$TTI")
            METRICS+=("tbt_ms:$TBT")
        fi
    else
        print_error "Lighthouse run failed"
        RESULTS+=("Lighthouse: FAIL (run error)")
        METRICS+=("lighthouse_score:error")
    fi
else
    print_warning "Lighthouse not found. Install with: npm install -g lighthouse"
    RESULTS+=("Lighthouse: SKIPPED (not installed)")
    METRICS+=("lighthouse_score:skipped")
fi

# ========================================
# Test 5: Dependency Analysis
# ========================================
echo ""
echo "========================================"
echo "Test 5: Dependency Analysis"
echo "========================================"

if [ -f "package.json" ]; then
    TOTAL_DEPS=$(cat package.json | jq '.dependencies | length')
    TOTAL_DEV_DEPS=$(cat package.json | jq '.devDependencies | length')
    TOTAL_DEPS_ALL=$((TOTAL_DEPS + TOTAL_DEV_DEPS))

    echo "Total dependencies: $TOTAL_DEPS_ALL"
    echo "  - Production: $TOTAL_DEPS"
    echo "  - Development: $TOTAL_DEV_DEPS"

    if [ $TOTAL_DEPS_ALL -lt 50 ]; then
        print_success "PASS ($TOTAL_DEPS_ALL dependencies)"
        RESULTS+=("Dependencies: PASS ($TOTAL_DEPS_ALL)")
        METRICS+=("total_deps:$TOTAL_DEPS_ALL")
    else
        print_warning "WARNING - Consider reducing dependencies"
        RESULTS+=("Dependencies: WARNING ($TOTAL_DEPS_ALL)")
        METRICS+=("total_deps:$TOTAL_DEPS_ALL")
    fi
else
    print_error "package.json not found"
    METRICS+=("total_deps:error")
fi

# ========================================
# Cleanup
# ========================================
echo ""
echo "========================================"
echo "Cleanup"
echo "========================================"

# Kill dev server
if [ -n "$DEV_PID" ]; then
    print_info "Stopping dev server (PID: $DEV_PID)..."
    kill $DEV_PID 2>/dev/null || true
fi

# ========================================
# Summary
# ========================================
echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"

for result in "${RESULTS[@]}"; do
    echo "$result"
done

# ========================================
# Save Results
# ========================================
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULTS_FILE="$RESULTS_DIR/performance-results-$TIMESTAMP.txt"

echo "" > "$RESULTS_FILE"
echo "Frontend Performance Test Results" >> "$RESULTS_FILE"
echo "========================================" >> "$RESULTS_FILE"
echo "Date: $(date)" >> "$RESULTS_FILE"
echo "Environment: $(uname -a)" >> "$RESULTS_FILE"
echo "" >> "$RESULTS_FILE"
echo "Test Results:" >> "$RESULTS_FILE"
for result in "${RESULTS[@]}"; do
    echo "$result" >> "$RESULTS_FILE"
done

echo "" >> "$RESULTS_FILE"
echo "Detailed Metrics:" >> "$RESULTS_FILE"
for metric in "${METRICS[@]}"; do
    echo "$metric" >> "$RESULTS_FILE"
done

print_info "Results saved to: $RESULTS_FILE"

# ========================================
# Generate JSON Report
# ========================================
JSON_REPORT="$RESULTS_DIR/performance-results-$TIMESTAMP.json"

cat > "$JSON_REPORT" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": {
    "os": "$(uname -s)",
    "arch": "$(uname -m)",
    "node_version": "$(node --version)",
    "npm_version": "$(npm --version)"
  },
  "results": [
$(IFS=,; printf '%s\n' "${RESULTS[@]}" | sed 's/"//g' | awk -F: '{print "{\"test\": \""$1"\", \"status\": \""$2"\", \"value\": \""$3"\"}"}' | paste -sd ',' -)
  ],
  "metrics": {
$(IFS=,; printf '%s\n' "${METRICS[@]}" | awk -F: '{print "\""$1"\": "$2""}' | paste -sd ',' -)
  }
}
EOF

print_info "JSON report saved to: $JSON_REPORT"

echo ""
echo "========================================"
echo "Performance Testing Complete!"
echo "========================================"

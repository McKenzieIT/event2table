#!/bin/bash

# Event2Table - Chrome DevTools Protocol Performance Test Runner
#
# This script uses chrome-devtools-mcp to run comprehensive performance tests
# on all key pages of the Event2Table application.
#
# Usage:
#   ./run-cdp-performance-test.sh
#
# Requirements:
#   - Frontend server running on http://localhost:5173
#   - Backend server running on http://127.0.0.1:5001
#   - chrome-devtools-mcp installed and configured
#
# @version 1.0.0
# @date 2026-02-13

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL="http://localhost:5173"
BACKEND_URL="http://127.0.0.1:5001"
OUTPUT_DIR="$(dirname "$0")/results"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Event2Table - CDP Performance Testing${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if servers are running
echo -e "${BLUE}🔍 Checking servers...${NC}"

if ! curl -s -o /dev/null "$FRONTEND_URL" 2>&1; then
    echo -e "${RED}❌ Frontend server is not running${NC}"
    echo -e "${YELLOW}Please start it with: cd frontend && npm run dev${NC}"
    exit 1
fi

if ! curl -s -o /dev/null "$BACKEND_URL" 2>&1; then
    echo -e "${RED}❌ Backend server is not running${NC}"
    echo -e "${YELLOW}Please start it with: python web_app.py${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Both servers are running${NC}"
echo -e "   Frontend: $FRONTEND_URL"
echo -e "   Backend: $BACKEND_URL"
echo ""

# Function to test a single page using CDP
test_page() {
    local page_name="$1"
    local page_path="$2"
    local full_url="${FRONTEND_URL}/#${page_path}"

    echo -e "${BLUE}🧪 Testing: ${page_name}${NC}"
    echo -e "   URL: $full_url"

    # Create a temporary CDP script for this page
    local temp_script="/tmp/cdp-test-${page_name}-${TIMESTAMP}.js"

    cat > "$temp_script" <<'EOF'
const { ChromeLauncher } = require('chrome-launcher');
const CDP = require('chrome-remote-interface');

async function testPage(url) {
  let chrome;
  let client;

  try {
    // Launch Chrome
    chrome = await ChromeLauncher.launch({
      chromeFlags: [
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
      ]
    });

    // Connect to Chrome DevTools Protocol
    client = await CDP({ port: chrome.port });

    const { Page, Performance, Network, Runtime } = client;

    // Enable domains
    await Page.enable();
    await Performance.enable();
    await Network.enable();
    await Runtime.enable();

    // Navigate to page
    await Page.navigate({ url });

    // Wait for page load
    await Page.loadEventFired();

    // Get performance metrics
    const metrics = await Performance.getMetrics();

    // Calculate key metrics
    const navigationStart = metrics.metrics.find(m => m.name === 'NavigationStart');
    const domContentLoaded = metrics.metrics.find(m => m.name === 'DomContentLoadedEventEnd');
    const loadEventEnd = metrics.metrics.find(m => m.name === 'LoadEventEnd');
    const firstPaint = metrics.metrics.find(m => m.name === 'FirstPaint');
    const firstContentfulPaint = metrics.metrics.find(m => m.name === 'FirstContentfulPaint');

    const loadTime = loadEventEnd ? loadEventEnd.value - navigationStart.value : 0;
    const domContentLoadedTime = domContentLoaded ? domContentLoaded.value - navigationStart.value : 0;
    const fcp = firstContentfulPaint ? firstContentfulPaint.value - navigationStart.value : 0;
    const fp = firstPaint ? firstPaint.value - navigationStart.value : 0;

    // Get resource timing
    const resourceTree = await Page.getResourceTree();

    return {
      loadTime,
      domContentLoadedTime,
      fcp,
      fp,
      timestamp: new Date().toISOString(),
    };
  } finally {
    if (client) {
      await client.close();
    }
    if (chrome) {
      await chrome.kill();
    }
  }
}

// Get URL from command line argument
const url = process.argv[2];
if (!url) {
  console.error('Usage: node script.js <url>');
  process.exit(1);
}

testPage(url)
  .then(metrics => {
    console.log(JSON.stringify(metrics, null, 2));
  })
  .catch(error => {
    console.error('Error:', error);
    process.exit(1);
  });
EOF

    # Run the CDP test
    if node "$temp_script" "$full_url" > "${OUTPUT_DIR}/${page_name}-${TIMESTAMP}.json" 2>&1; then
        echo -e "${GREEN}✅ ${page_name}: Test completed${NC}"
    else
        echo -e "${RED}❌ ${page_name}: Test failed${NC}"
    fi

    # Clean up
    rm -f "$temp_script"

    echo ""
}

# Test all key pages
echo -e "${BLUE}📊 Testing all pages...${NC}"
echo ""

test_page "Dashboard" "/"
test_page "Games" "/games"
test_page "Events" "/events"
test_page "Parameters" "/parameters"
test_page "Canvas" "/canvas"
test_page "EventNodeBuilder" "/event-node-builder"
test_page "FieldBuilder" "/field-builder"
test_page "Categories" "/categories"
test_page "Flows" "/flows"
test_page "HqlManage" "/hql-manage"
test_page "Generate" "/generate"
test_page "ParameterAnalysis" "/parameter-analysis"
test_page "ParameterNetwork" "/parameter-network"

echo -e "${GREEN}✨ Testing complete!${NC}"
echo -e "Results saved to: $OUTPUT_DIR"
echo ""
echo -e "${BLUE}📝 Next steps:${NC}"
echo -e "1. Review individual JSON files in $OUTPUT_DIR"
echo -e "2. Run the Node.js script to generate HTML report:"
echo -e "   node comprehensive-page-test.mcp.js"
echo ""

# Exit successfully
exit 0

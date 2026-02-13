#!/bin/bash
# Apache Bench Performance Testing Script
# Tests API endpoints with concurrent load

echo "=========================================="
echo "Apache Bench Performance Testing"
echo "=========================================="
echo ""

# Check if Apache Bench is installed
if ! command -v ab &> /dev/null; then
    echo "❌ Apache Bench (ab) is not installed"
    echo "Install with: brew install httping"
    exit 1
fi

# Configuration
HOST="http://127.0.0.1:5001"
REQUESTS=1000
CONCURRENCY=10

echo "Test Configuration:"
echo "  Host: $HOST"
echo "  Requests: $REQUESTS"
echo "  Concurrency: $CONCURRENCY"
echo ""

# Check if server is running
echo "Checking if server is running..."
if ! curl -s "$HOST/test" > /dev/null 2>&1; then
    echo "❌ Server is not running at $HOST"
    echo "Start the server first: python web_app.py"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Test 1: GET /api/games (list all games)
echo "=========================================="
echo "Test 1: GET /api/games"
echo "=========================================="
ab -n $REQUESTS -c $CONCURRENCY -g api_games.tsv "$HOST/api/games"
echo ""

# Test 2: GET /api/games/10000147 (get single game)
echo "=========================================="
echo "Test 2: GET /api/games/<gid>"
echo "=========================================="
ab -n $REQUESTS -c $CONCURRENCY -g api_single_game.tsv "$HOST/api/games/10000147"
echo ""

# Test 3: GET /api/events (paginated events)
echo "=========================================="
echo "Test 3: GET /api/events (paginated)"
echo "=========================================="
ab -n $REQUESTS -c $CONCURRENCY -g api_events.tsv "$HOST/api/events?game_gid=10000147&page=1&per_page=10"
echo ""

# Generate summary
echo "=========================================="
echo "Test Results Summary"
echo "=========================================="
echo ""
echo "TSV files generated:"
echo "  - api_games.tsv"
echo "  - api_single_game.tsv"
echo "  - api_events.tsv"
echo ""
echo "You can visualize these files using gnuplot or other tools"
echo ""

# Extract key metrics from ab output
echo "Key Metrics:"
echo "------------"

# This is a placeholder - in real usage, you'd parse the ab output
echo "Check the ab output above for:"
echo "  - Requests per second"
echo "  - Time per request (mean)"
echo "  - Time per request (mean, across all concurrent requests)"
echo "  - Percentage of requests served within a certain time"
echo ""

echo "=========================================="
echo "Testing Complete"
echo "=========================================="

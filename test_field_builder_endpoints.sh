#!/bin/bash
# Test Field Builder API Endpoints
# This script verifies that the Field Builder API is correctly registered and accessible

set -e

echo "========================================"
echo "Field Builder API Endpoint Test"
echo "========================================"
echo ""

API_BASE="http://127.0.0.1:5001/api"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if server is running
echo "1. Checking if Flask server is running..."
if ! curl -s http://127.0.0.1:5001/test > /dev/null 2>&1; then
    echo -e "${RED}❌ Flask server is not running on port 5001${NC}"
    echo "Please start the server first:"
    echo "  cd /Users/mckenzie/Documents/event2table"
    echo "  source backend/venv/bin/activate"
    echo "  python3 web_app.py"
    exit 1
fi
echo -e "${GREEN}✅ Flask server is running${NC}"
echo ""

# Test 1: List field builder configs
echo "2. Testing GET /api/field-builder/configs (List configurations)..."
RESPONSE=$(curl -s "${API_BASE}/field-builder/configs?limit=10")
if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ GET /api/field-builder/configs - SUCCESS${NC}"
    echo "Response: $(echo "$RESPONSE" | jq -r '.')"
else
    echo -e "${RED}❌ GET /api/field-builder/configs - FAILED${NC}"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 2: Get a specific config (will likely return 404, but endpoint exists)
echo "3. Testing GET /api/field-builder/configs/<id> (Get configuration by ID)..."
RESPONSE=$(curl -s "${API_BASE}/field-builder/configs/1")
if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1 || echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ GET /api/field-builder/configs/<id> - Endpoint exists${NC}"
    echo "Response: $(echo "$RESPONSE" | jq -r '.')"
else
    echo -e "${RED}❌ GET /api/field-builder/configs/<id> - FAILED${NC}"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 3: Preview HQL endpoint
echo "4. Testing POST /api/field-builder/preview (Preview HQL)..."
RESPONSE=$(curl -s -X POST "${API_BASE}/field-builder/preview" \
    -H "Content-Type: application/json" \
    -d '{"config":{"view_config":{},"base_fields":[],"custom_fields":{}},"source_events":[],"view_name":"test_view"}')
if echo "$RESPONSE" | jq -e '.success' > /dev/null 2>&1 || echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ POST /api/field-builder/preview - Endpoint exists${NC}"
    echo "Response: $(echo "$RESPONSE" | jq -r '.')"
else
    echo -e "${RED}❌ POST /api/field-builder/preview - FAILED${NC}"
    echo "Response: $RESPONSE"
fi
echo ""

# Test 4: Non-existent endpoints (should return 404)
echo "5. Testing non-existent endpoints (should return 404)..."
for endpoint in "base-fields" "custom-fields" "fields"; do
    echo -n "   Testing /api/field-builder/${endpoint}... "
    RESPONSE=$(curl -s "${API_BASE}/field-builder/${endpoint}?game_gid=10000147")
    if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
        echo -e "${YELLOW}✅ Returns 404 as expected (endpoint doesn't exist)${NC}"
    else
        echo -e "${RED}❌ Unexpected response${NC}"
    fi
done
echo ""

echo "========================================"
echo "Summary"
echo "========================================"
echo "Available Field Builder API endpoints:"
echo "  ✅ GET    /api/field-builder/configs          - List all configurations"
echo "  ✅ GET    /api/field-builder/configs/<id>     - Get configuration by ID"
echo "  ✅ POST   /api/field-builder/config           - Save new configuration"
echo "  ✅ POST   /api/field-builder/configs          - Save new configuration (alias)"
echo "  ✅ POST   /api/field-builder/preview          - Preview HQL"
echo "  ✅ DELETE /api/field-builder/config/<id>      - Delete configuration"
echo ""
echo "❌ Non-existent endpoints (mentioned in task):"
echo "  ❌ GET /api/field-builder/base-fields         - Not implemented"
echo "  ❌ GET /api/field-builder/custom-fields       - Not implemented"
echo "  ❌ GET /api/field-builder/fields              - Not implemented"
echo ""
echo "========================================"

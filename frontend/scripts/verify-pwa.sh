#!/bin/bash
# Quick PWA Verification Script
# Run this after production build to verify PWA setup

echo "🔍 PWA Verification Script"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if dist folder exists
if [ ! -d "dist" ]; then
  echo -e "${RED}❌ dist/ folder not found. Run 'npm run build' first.${NC}"
  exit 1
fi

echo -e "${GREEN}✅ dist/ folder found${NC}"
echo ""

# Check Service Worker
if [ -f "dist/sw.js" ]; then
  SIZE=$(wc -c < dist/sw.js)
  echo -e "${GREEN}✅ Service Worker found: dist/sw.js (${SIZE} bytes)${NC}"
else
  echo -e "${RED}❌ Service Worker not found: dist/sw.js${NC}"
fi

# Check Manifest
if [ -f "dist/manifest.webmanifest" ]; then
  SIZE=$(wc -c < dist/manifest.webmanifest)
  echo -e "${GREEN}✅ Manifest found: dist/manifest.webmanifest (${SIZE} bytes)${NC}"

  # Validate manifest JSON
  if command -v jq &> /dev/null; then
    echo ""
    echo "📋 Manifest Content:"
    cat dist/manifest.webmanifest | jq '.'
  else
    echo ""
    echo "📋 Manifest Content:"
    cat dist/manifest.webmanifest
  fi
else
  echo -e "${RED}❌ Manifest not found: dist/manifest.webmanifest${NC}"
fi

# Check Workbox
WORKBOX_FILE=$(ls dist/workbox-*.js 2>/dev/null | head -1)
if [ -n "$WORKBOX_FILE" ]; then
  SIZE=$(wc -c < "$WORKBOX_FILE")
  echo -e "${GREEN}✅ Workbox found: $WORKBOX_FILE (${SIZE} bytes)${NC}"
else
  echo -e "${RED}❌ Workbox not found${NC}"
fi

# Check icons
echo ""
echo "🎨 Icons:"
if [ -f "dist/icons/icon-192x192.svg" ]; then
  echo -e "${GREEN}  ✅ 192x192 icon found${NC}"
else
  echo -e "${RED}  ❌ 192x192 icon missing${NC}"
fi

if [ -f "dist/icons/icon-512x512.svg" ]; then
  echo -e "${GREEN}  ✅ 512x512 icon found${NC}"
else
  echo -e "${RED}  ❌ 512x512 icon missing${NC}"
fi

# Count pre-cached assets
echo ""
echo "📦 Pre-cached Assets:"
ASSET_COUNT=$(find dist/assets -type f 2>/dev/null | wc -l | tr -d ' ')
echo "  Total assets: $ASSET_COUNT"

JS_COUNT=$(find dist/assets -name "*.js" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "  JavaScript files: $JS_COUNT"

CSS_COUNT=$(find dist/assets -name "*.css" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "  CSS files: $CSS_COUNT"

# Summary
echo ""
echo "=========================="
echo -e "${GREEN}✅ PWA Verification Complete${NC}"
echo ""
echo "📝 Next Steps:"
echo "  1. Deploy 'dist/' folder to production server"
echo "  2. Configure HTTPS (required for Service Workers)"
echo "  3. Test on mobile devices"
echo "  4. Run Lighthouse audit for PWA score"
echo ""

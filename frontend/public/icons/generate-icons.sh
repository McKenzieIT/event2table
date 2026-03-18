#!/bin/bash
# PWA Icon Generation Script
#
# This script generates PWA icons from a source image.
#
# Prerequisites:
# - ImageMagick: brew install imagemagick
# - OR use online tool: https://realfavicongenerator.net/
#
# Usage:
#   ./generate-icons.sh source-image.png
#
# Output:
#   - public/icon-192x192.png
#   - public/icon-512x512.png

SOURCE_IMAGE=$1

if [ -z "$SOURCE_IMAGE" ]; then
  echo "Usage: $0 <source-image.png>"
  echo "Example: $0 logo.png"
  exit 1
fi

if [ ! -f "$SOURCE_IMAGE" ]; then
  echo "Error: Source image '$SOURCE_IMAGE' not found"
  exit 1
fi

echo "Generating PWA icons from $SOURCE_IMAGE..."

# Generate 192x192 icon
convert "$SOURCE_IMAGE" -resize 192x192! public/icon-192x192.png
echo "✓ Generated public/icon-192x192.png"

# Generate 512x512 icon
convert "$SOURCE_IMAGE" -resize 512x512! public/icon-512x512.png
echo "✓ Generated public/icon-512x512.png"

# Generate favicon
convert "$SOURCE_IMAGE" -resize 48x48! public/favicon.ico
echo "✓ Generated public/favicon.ico"

echo ""
echo "PWA icons generated successfully!"
echo "Add these to your git repository:"
echo "  git add public/icon-192x192.png public/icon-512x512.png public/favicon.ico"

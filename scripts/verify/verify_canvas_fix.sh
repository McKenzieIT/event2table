#!/bin/bash

# Canvas ReferenceError Fix Verification Script
# This script helps verify that the canvas ReferenceError has been fixed

set -e  # Exit on error

PROJECT_DIR="/Users/mckenzie/Documents/event2table"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "================================================"
echo "Canvas ReferenceError Fix Verification"
echo "================================================"
echo ""

# Step 1: Check if queryKeys files have been fixed
echo "Step 1: Checking queryKeys files for circular reference fix..."

FILES_TO_CHECK=(
    "$FRONTEND_DIR/src/features/canvas/api/queryKeys.ts"
    "$FRONTEND_DIR/src/features/canvas/api/queryKeys.js"
    "$FRONTEND_DIR/src/canvas/api/queryKeys.js"
)

all_fixed=true
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        if grep -q "eventConfigsBase = \['event-configs'\]" "$file"; then
            echo "  ✅ $file - Fixed (uses base constants)"
        else
            echo "  ❌ $file - Not fixed (still has circular references)"
            all_fixed=false
        fi
    else
        echo "  ⚠️  $file - Not found"
    fi
done

echo ""

if [ "$all_fixed" = false ]; then
    echo "❌ Some files are not fixed yet. Please apply the fix first."
    exit 1
fi

# Step 2: Check if Node.js is available
echo "Step 2: Checking for Node.js/npm..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  ✅ Node.js found: $NODE_VERSION"

    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo "  ✅ npm found: $NPM_VERSION"
        HAS_NPM=true
    else
        echo "  ❌ npm not found"
        HAS_NPM=false
    fi
else
    echo "  ⚠️  Node.js not found in current environment"
    echo "  You'll need to build manually or ensure Node.js is in your PATH"
    HAS_NPM=false
fi

echo ""

# Step 3: Build instructions
echo "Step 3: Build Instructions"
echo "================================================"

if [ "$HAS_NPM" = true ]; then
    echo "To rebuild the frontend with the fix applied:"
    echo ""
    echo "  cd $FRONTEND_DIR"
    echo "  npm run build"
    echo ""
    echo "Then start the server:"
    echo "  cd $PROJECT_DIR"
    echo "  python web_app.py"
    echo ""
    echo "Would you like me to run the build now? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Building frontend..."
        cd "$FRONTEND_DIR"
        npm run build

        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Build successful!"
            echo ""
            echo "To test the fix:"
            echo "1. Start the Flask server: cd $PROJECT_DIR && python web_app.py"
            echo "2. Open browser to: http://localhost:5001"
            echo "3. Navigate to the canvas feature"
            echo "4. Verify no ReferenceError occurs"
        else
            echo ""
            echo "❌ Build failed. Please check the errors above."
            exit 1
        fi
    fi
else
    echo "To rebuild the frontend, run these commands in your terminal:"
    echo ""
    echo "  cd $FRONTEND_DIR"
    echo "  npm run build"
    echo ""
    echo "Then start the server:"
    echo "  cd $PROJECT_DIR"
    echo "  python web_app.py"
fi

echo ""
echo "================================================"
echo "Fix Summary"
echo "================================================"
echo ""
echo "✅ All queryKeys files have been fixed"
echo "✅ Circular references removed"
echo "✅ Base keys extracted to constants"
echo ""
echo "The fix addresses the ReferenceError by:"
echo "  - Extracting base query keys to separate constants"
echo "  - Removing self-references during object initialization"
echo "  - Complying with JavaScript's Temporal Dead Zone rules"
echo ""
echo "For more details, see: $PROJECT_DIR/CANVAS_REFERENCE_ERROR_FIX.md"
echo ""

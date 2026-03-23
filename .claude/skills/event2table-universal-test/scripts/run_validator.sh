#!/bin/bash
###############################################################################
# Selector Validation Runner
#
# This script provides a convenient wrapper for running the selector validation
# tool with common configurations.
#
# Usage:
#   ./run_validator.sh [options]
#
# Options:
#   --production    Test against production URL
#   --staging       Test against staging URL
#   --local         Test against local development (default)
#   --url URL       Test against custom URL
#   --output FILE   Save report to specific file
#   --verbose       Enable verbose output
#   --help          Show this help message
#
# Author: Event2Table Test System
# Version: 1.0.0
###############################################################################

set -e  # Exit on error

# Default configuration
DEFAULT_URL="http://localhost:5173"
URL="$DEFAULT_URL"
OUTPUT=""
VERBOSE=""

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATOR_SCRIPT="$SCRIPT_DIR/validate_selectors.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

# Print help
print_help() {
    grep '^#' "$BASH_SOURCE" | grep -v '#!/bin/bash' | grep -v 'Author:' | grep -v 'Version:' | sed 's/^# //' | sed 's/^#//'
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            URL="https://event2table.com"
            shift
            ;;
        --staging)
            URL="https://staging.event2table.com"
            shift
            ;;
        --local)
            URL="$DEFAULT_URL"
            shift
            ;;
        --url)
            URL="$2"
            shift 2
            ;;
        --output)
            OUTPUT="--output $2"
            shift 2
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --help)
            print_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            print_help
            exit 1
            ;;
    esac
done

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    print_msg "$RED" "❌ Python 3 not found"
    print_msg "$YELLOW" "   Please install Python 3.7 or higher"
    exit 1
fi

# Check if validator script exists
if [[ ! -f "$VALIDATOR_SCRIPT" ]]; then
    print_msg "$RED" "❌ Validator script not found: $VALIDATOR_SCRIPT"
    exit 1
fi

# Print configuration
print_msg "$BLUE" "🚀 Selector Validation Runner"
echo ""
print_msg "$BLUE" "Configuration:"
echo "  URL:      $URL"
echo "  Script:   $VALIDATOR_SCRIPT"
echo "  Verbose:  ${VERBOSE:-No}"
echo ""

# Check if agent-browser is available
print_msg "$BLUE" "🔍 Checking agent-browser..."
if ! command -v agent-browser &> /dev/null; then
    print_msg "$RED" "❌ agent-browser not found"
    print_msg "$YELLOW" "   Installing agent-browser..."
    npm install -g @agent-browser/cli
fi

# Check if application is running
print_msg "$BLUE" "🔍 Checking application at $URL..."
if ! curl -s -o /dev/null -w "%{http_code}" "$URL" | grep -q "200\|302\|304"; then
    print_msg "$YELLOW" "⚠️  Application may not be running at $URL"
    print_msg "$YELLOW" "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_msg "$RED" "❌ Aborted by user"
        exit 1
    fi
fi

# Run validator
print_msg "$BLUE" "🔍 Running selector validation..."
echo ""

# Run the Python script
if python3 "$VALIDATOR_SCRIPT" --url "$URL" $OUTPUT $VERBOSE; then
    exit_code=0
else
    exit_code=$?
fi

# Print result
echo ""
if [[ $exit_code -eq 0 ]]; then
    print_msg "$GREEN" "✅ Validation completed successfully"
else
    print_msg "$RED" "❌ Validation failed with exit code $exit_code"
fi

exit $exit_code

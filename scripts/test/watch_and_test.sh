#!/bin/bash
###############################################################################
# Watch and Test Script
# 
# Description: Run tests in watch mode for backend or frontend
# Usage: ./watch_and_test.sh [backend|frontend]
#
# Author: Event2Table Development Team
# Version: 1.0.0
# Last Updated: 2026-02-11
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="/Users/mckenzie/Documents/event2table"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show usage
usage() {
    cat << USAGE
Usage: $0 [backend|frontend]

Arguments:
  backend    Run backend tests in watch mode (pytest)
  frontend   Run frontend tests in watch mode (Vitest)

Examples:
  $0 backend
  $0 frontend

USAGE
    exit 1
}

# Function to run backend tests in watch mode
watch_backend() {
    print_info "Starting backend test watch mode..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment if it exists
    if [ -f "venv/bin/activate" ]; then
        print_info "Activating virtual environment..."
        source venv/bin/activate
    else
        print_warning "Virtual environment not found. Using system Python."
    fi
    
    # Check if pytest-watch is installed
    if command -v pytest-watch &> /dev/null || pip show pytest-watch &> /dev/null; then
        print_info "Using pytest-watch for automatic test rerun..."
        print_warning "Press Ctrl+C to stop watching"
        pytest-watch backend/tests/ \
            --ext=.py \
            -v \
            --tb=short \
            --color=yes
    else
        print_warning "pytest-watch not installed. Falling back to manual polling..."
        print_info "Install pytest-watch for better experience: pip install pytest-watch"
        
        # Manual polling fallback
        while true; do
            print_info "Running backend tests..."
            pytest backend/tests/ -v --tb=short --color=yes
            
            print_info "Waiting for changes... (check every 5 seconds)"
            sleep 5
        done
    fi
}

# Function to run frontend tests in watch mode
watch_frontend() {
    print_info "Starting frontend test watch mode..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_error "node_modules not found. Running npm install..."
        npm install
    fi
    
    # Check if Vitest is available
    if npm list vitest &> /dev/null || grep -q '"vitest"' package.json; then
        print_info "Using Vitest watch mode..."
        print_warning "Press Ctrl+C to stop watching"
        npm run test -- --watch --reporter=verbose 2>/dev/null || \
        npx vitest watch --reporter=verbose
    else
        print_error "Vitest not found. Please install it first."
        print_info "Run: cd frontend && npm install -D vitest"
        exit 1
    fi
}

# Main script logic
main() {
    local component="${1:-}"
    
    # Validate argument
    if [ -z "$component" ]; then
        print_error "No component specified"
        usage
    fi
    
    # Show banner
    echo ""
    echo "=================================="
    echo "  Watch and Test - Event2Table"
    echo "=================================="
    echo ""
    
    # Route to appropriate function
    case "$component" in
        backend)
            watch_backend
            ;;
        frontend)
            watch_frontend
            ;;
        *)
            print_error "Invalid component: $component"
            echo ""
            usage
            ;;
    esac
}

# Trap Ctrl+C and exit gracefully
trap 'print_info "Stopping watch mode..."; exit 0' INT

# Run main function
main "$@"

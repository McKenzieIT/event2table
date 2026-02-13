#!/bin/bash
###############################################################################
# Dev Server with Tests Script
# 
# Description: Start dev servers and run smoke tests against them
# Usage: ./dev_with_tests.sh [--no-cleanup]
#
# Options:
#   --no-cleanup    Keep servers running after tests (don't auto-kill)
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
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="/Users/mckenzie/Documents/event2table"
BACKEND_PORT=5001
FRONTEND_PORT=5173

# Process IDs for cleanup
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup flag
NO_CLEANUP=false

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

print_step() {
    echo -e "${MAGENTA}[STEP]${NC} $1"
}

# Function to show usage
usage() {
    cat << USAGE
Usage: $0 [OPTIONS]

Options:
  --no-cleanup    Keep servers running after tests (don't auto-kill)

Examples:
  $0                # Start servers, run tests, then cleanup
  $0 --no-cleanup   # Start servers, run tests, keep servers running

USAGE
    exit 1
}

# Function to cleanup processes
cleanup() {
    print_info "Cleaning up..."
    
    # Kill backend server
    if [ -n "$BACKEND_PID" ]; then
        print_info "Stopping backend server (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        wait $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill frontend server
    if [ -n "$FRONTEND_PID" ]; then
        print_info "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        wait $FRONTEND_PID 2>/dev/null || true
    fi
    
    # Kill any process using the ports
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Trap Ctrl+C and cleanup
trap 'print_info "Interrupted by user"; cleanup; exit 1' INT

# Function to wait for server to be ready
wait_for_server() {
    local url="$1"
    local name="$2"
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for $name to be ready at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_success "$name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    echo ""
    print_error "$name failed to start within $max_attempts seconds"
    return 1
}

# Function to start backend server
start_backend() {
    print_step "Starting Flask backend server..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # Check if port is already in use
    if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
        print_warning "Port $BACKEND_PORT is already in use. Killing existing process..."
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start Flask server in background
    python web_app.py > logs/backend_dev.log 2>&1 &
    BACKEND_PID=$!
    
    print_info "Backend server started with PID: $BACKEND_PID"
    print_info "Backend log: logs/backend_dev.log"
    
    # Wait for backend to be ready
    if wait_for_server "http://127.0.0.1:$BACKEND_PORT/api/health" "Backend server"; then
        return 0
    else
        print_error "Backend server failed to start. Check logs/backend_dev.log"
        return 1
    fi
}

# Function to start frontend server
start_frontend() {
    print_step "Starting Vite frontend server..."
    
    cd "$PROJECT_ROOT/frontend"
    
    # Check if port is already in use
    if lsof -ti:$FRONTEND_PORT > /dev/null 2>&1; then
        print_warning "Port $FRONTEND_PORT is already in use. Killing existing process..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "node_modules not found. Running npm install..."
        npm install
    fi
    
    # Start Vite dev server in background
    npm run dev > ../logs/frontend_dev.log 2>&1 &
    FRONTEND_PID=$!
    
    print_info "Frontend server started with PID: $FRONTEND_PID"
    print_info "Frontend log: logs/frontend_dev.log"
    
    # Wait for frontend to be ready (Vite usually takes a few seconds)
    sleep 3
    
    if wait_for_server "http://localhost:$FRONTEND_PORT" "Frontend server"; then
        return 0
    else
        print_error "Frontend server failed to start. Check logs/frontend_dev.log"
        return 1
    fi
}

# Function to run smoke tests
run_smoke_tests() {
    print_step "Running smoke tests against running servers..."
    
    local test_results=()
    
    # Backend smoke tests
    print_info "Testing backend endpoints..."
    
    # Test health endpoint
    if curl -s -f "http://127.0.0.1:$BACKEND_PORT/api/health" > /dev/null; then
        test_results+=("Backend Health Check: PASSED")
        print_success "✓ Backend health check"
    else
        test_results+=("Backend Health Check: FAILED")
        print_error "✗ Backend health check"
    fi
    
    # Test games list endpoint
    if curl -s -f "http://127.0.0.1:$BACKEND_PORT/api/games" > /dev/null; then
        test_results+=("Backend Games API: PASSED")
        print_success "✓ Backend games API"
    else
        test_results+=("Backend Games API: FAILED")
        print_error "✗ Backend games API"
    fi
    
    # Frontend smoke tests
    print_info "Testing frontend accessibility..."
    
    # Test frontend is accessible
    if curl -s -f "http://localhost:$FRONTEND_PORT" > /dev/null; then
        test_results+=("Frontend Accessibility: PASSED")
        print_success "✓ Frontend is accessible"
    else
        test_results+=("Frontend Accessibility: FAILED")
        print_error "✗ Frontend is not accessible"
    fi
    
    # Print test results summary
    echo ""
    echo "=================================="
    echo "  Smoke Test Results"
    echo "=================================="
    
    local passed=0
    local failed=0
    
    for result in "${test_results[@]}"; do
        if [[ "$result" == *"PASSED"* ]]; then
            echo -e "${GREEN}✓${NC} $result"
            passed=$((passed + 1))
        else
            echo -e "${RED}✗${NC} $result"
            failed=$((failed + 1))
        fi
    done
    
    echo ""
    echo "Total: $passed passed, $failed failed"
    
    if [ $failed -gt 0 ]; then
        print_error "Some smoke tests failed!"
        return 1
    else
        print_success "All smoke tests passed!"
        return 0
    fi
}

# Function to run automated tests
run_automated_tests() {
    print_step "Running automated tests..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    fi
    
    # Run backend unit tests
    print_info "Running backend unit tests..."
    if pytest backend/tests/ -v --tb=short; then
        print_success "Backend tests passed"
    else
        print_error "Backend tests failed"
        return 1
    fi
    
    # Run frontend tests (if available)
    print_info "Running frontend tests..."
    cd "$PROJECT_ROOT/frontend"
    if npm run test 2>/dev/null || npx vitest run 2>/dev/null; then
        print_success "Frontend tests passed"
    else
        print_warning "Frontend tests not available or failed"
    fi
    
    return 0
}

# Main script logic
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-cleanup)
                NO_CLEANUP=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                print_error "Unknown option: $1"
                usage
                ;;
        esac
    done
    
    # Show banner
    echo ""
    echo "=================================="
    echo "  Dev Server with Tests"
    echo "  Event2Table"
    echo "=================================="
    echo ""
    
    # Create logs directory if it doesn't exist
    mkdir -p "$PROJECT_ROOT/logs"
    
    # Start servers
    if ! start_backend; then
        cleanup
        exit 1
    fi
    
    if ! start_frontend; then
        cleanup
        exit 1
    fi
    
    echo ""
    print_success "Both servers are running!"
    echo "  Backend:  http://127.0.0.1:$BACKEND_PORT"
    echo "  Frontend: http://localhost:$FRONTEND_PORT"
    echo ""
    
    # Run smoke tests
    if ! run_smoke_tests; then
        print_error "Smoke tests failed. Check logs for details."
        if [ "$NO_CLEANUP" = false ]; then
            cleanup
            exit 1
        fi
    fi
    
    echo ""
    
    # Run automated tests
    if ! run_automated_tests; then
        print_warning "Automated tests failed."
    fi
    
    echo ""
    print_step "Server startup and testing completed!"
    
    if [ "$NO_CLEANUP" = true ]; then
        print_info "Servers are kept running as requested"
        print_info "Press Ctrl+C to stop servers"
        print_info "Backend PID: $BACKEND_PID"
        print_info "Frontend PID: $FRONTEND_PID"
        
        # Wait for user to stop
        wait
    else
        print_info "Servers will be stopped in 5 seconds..."
        print_info "Press Ctrl+C to stop immediately"
        sleep 5
        
        cleanup
        print_success "All done!"
    fi
}

# Run main function
main "$@"

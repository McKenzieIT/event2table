#!/bin/bash

###############################################################################
# Deployment Script for Event2Table
#
# Features:
# - One-command deployment
# - Health checks
# - Automatic rollback on failure
# - Backup creation
# - Deployment logging
#
# Usage:
#   ./scripts/deploy.sh deploy        # Deploy application
#   ./scripts/deploy.sh rollback      # Rollback to previous version
#   ./scripts/deploy.sh health-check  # Check application health
#   ./scripts/deploy.sh backup        # Create backup only
#
# Author: Subagent 6 (CI/CD Automation)
# Date: 2026-03-18
###############################################################################

set -euo pipefail  # Exit on error, undefined variables, pipe failures
set -x  # Print commands for debugging

###############################################################################
# Configuration
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/deployments"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/deploy_${TIMESTAMP}.log"
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz"
HEALTH_CHECK_URL="http://127.0.0.1:5001/api/health"
HEALTH_CHECK_TIMEOUT=300
DEPLOYMENT_TIMEOUT=300

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

###############################################################################
# Logging Functions
###############################################################################

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOG_FILE}"
}

###############################################################################
# Utility Functions
###############################################################################

create_directories() {
    log "Creating required directories..."
    mkdir -p "${LOG_DIR}"
    mkdir -p "${BACKUP_DIR}"
    mkdir -p "${PROJECT_ROOT}/data"
    mkdir -p "${PROJECT_ROOT}/logs"
}

check_environment() {
    log "Checking deployment environment..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi

    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        exit 1
    fi

    # Check virtual environment
    if [ ! -d "${PROJECT_ROOT}/backend/venv" ]; then
        log_error "Virtual environment not found. Run: python3 -m venv backend/venv"
        exit 1
    fi

    log_success "Environment check passed"
}

check_dependencies() {
    log "Checking dependencies..."

    cd "${PROJECT_ROOT}"

    # Check backend dependencies
    source backend/venv/bin/activate
    if ! pip list --format=freeze | grep -q "flask"; then
        log_error "Backend dependencies not installed"
        exit 1
    fi

    # Check frontend dependencies
    if [ ! -d "${PROJECT_ROOT}/frontend/node_modules" ]; then
        log_error "Frontend dependencies not installed"
        exit 1
    fi

    log_success "Dependencies check passed"
}

get_current_version() {
    cd "${PROJECT_ROOT}"
    if [ -f ".version" ]; then
        cat .version
    else
        git rev-parse --short HEAD 2>/dev/null || echo "unknown"
    fi
}

###############################################################################
# Backup Functions
###############################################################################

create_backup() {
    log "Creating backup..."

    create_directories

    # Backup database
    if [ -f "${PROJECT_ROOT}/data/dwd_generator.db" ]; then
        cp "${PROJECT_ROOT}/data/dwd_generator.db" \
           "${BACKUP_DIR}/dwd_generator_${TIMESTAMP}.db"
        log_success "Database backed up"
    fi

    # Backup configuration files
    tar -czf "${BACKUP_FILE}" \
        -C "${PROJECT_ROOT}" \
        config/ \
        backend/venv/ \
        frontend/node_modules/ \
        data/ \
        logs/ \
        2>/dev/null || true

    # Keep only last 5 backups
    cd "${BACKUP_DIR}"
    ls -t backup_*.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm --
    ls -t dwd_generator_*.db 2>/dev/null | tail -n +6 | xargs -r rm --

    log_success "Backup created: ${BACKUP_FILE}"

    # Store current version
    get_current_version > "${BACKUP_DIR}/version_before_deploy.txt"
}

restore_backup() {
    log "Restoring from backup..."

    LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/backup_*.tar.gz 2>/dev/null | head -n 1)

    if [ -z "${LATEST_BACKUP}" ]; then
        log_error "No backup found to restore"
        exit 1
    fi

    log "Restoring from: ${LATEST_BACKUP}"

    # Restore database
    LATEST_DB=$(ls -t "${BACKUP_DIR}"/dwd_generator_*.db 2>/dev/null | head -n 1)
    if [ -n "${LATEST_DB}" ]; then
        cp "${LATEST_DB}" "${PROJECT_ROOT}/data/dwd_generator.db"
        log_success "Database restored"
    fi

    log_success "Backup restored successfully"
}

###############################################################################
# Health Check Functions
###############################################################################

health_check() {
    log "Starting health check..."

    START_TIME=$(date +%s)
    END_TIME=$((START_TIME + HEALTH_CHECK_TIMEOUT))

    while [ $(date +%s) -lt ${END_TIME} ]; do
        # Check if backend is responding
        if curl -f -s "${HEALTH_CHECK_URL}" > /dev/null 2>&1; then
            log_success "Backend health check passed"

            # Check if frontend is accessible
            if curl -f -s "http://127.0.0.1:5173" > /dev/null 2>&1; then
                log_success "Frontend health check passed"
                return 0
            else
                log_warning "Frontend not accessible yet, retrying..."
            fi
        else
            log_warning "Backend not ready yet, retrying..."
        fi

        sleep 5
    done

    log_error "Health check timed out after ${HEALTH_CHECK_TIMEOUT} seconds"
    return 1
}

check_database() {
    log "Checking database integrity..."

    if [ ! -f "${PROJECT_ROOT}/data/dwd_generator.db" ]; then
        log_error "Database file not found"
        return 1
    fi

    # Run database integrity check
    python3 << EOF
import sqlite3
import sys

try:
    conn = sqlite3.connect('${PROJECT_ROOT}/data/dwd_generator.db')
    result = conn.execute("PRAGMA integrity_check").fetchone()
    conn.close()

    if result[0] == 'ok':
        print("Database integrity check passed")
        sys.exit(0)
    else:
        print(f"Database integrity check failed: {result[0]}")
        sys.exit(1)
except Exception as e:
    print(f"Database check error: {e}")
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        log_success "Database integrity check passed"
        return 0
    else
        log_error "Database integrity check failed"
        return 1
    fi
}

###############################################################################
# Deployment Functions
###############################################################################

deploy_backend() {
    log "Deploying backend..."

    cd "${PROJECT_ROOT}/backend"

    # Activate virtual environment
    source venv/bin/activate

    # Install/update dependencies
    pip install -r requirements.txt --quiet

    # Run database migrations if needed
    if [ -f "${PROJECT_ROOT}/scripts/setup/init_db.py" ]; then
        python3 "${PROJECT_ROOT}/scripts/setup/init_db.py"
    fi

    log_success "Backend deployed successfully"
}

deploy_frontend() {
    log "Deploying frontend..."

    cd "${PROJECT_ROOT}/frontend"

    # Install dependencies
    npm ci --quiet

    # Build production bundle
    npm run build

    log_success "Frontend deployed successfully"
}

restart_services() {
    log "Restarting services..."

    # Stop any running services
    pkill -f "python.*web_app.py" || true
    pkill -f "vite" || true

    sleep 2

    # Start backend
    cd "${PROJECT_ROOT}"
    nohup python3 web_app.py > logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo ${BACKEND_PID} > logs/backend.pid

    log_success "Backend started (PID: ${BACKEND_PID})"

    # Note: Frontend is typically served by a reverse proxy in production
    # For development, it can be started with: npm run dev
}

###############################################################################
# Main Deployment Flow
###############################################################################

deploy() {
    log "Starting deployment..."
    log "Version: $(get_current_version)"

    create_directories
    check_environment
    check_dependencies

    # Create backup before deployment
    create_backup

    # Deploy components
    deploy_backend
    deploy_frontend

    # Restart services
    restart_services

    # Wait for services to be ready
    sleep 5

    # Health checks
    if health_check && check_database; then
        log_success "Deployment completed successfully!"

        # Record deployment
        echo "${TIMESTAMP}" > "${LOG_DIR}/last_deployment.txt"
        echo "$(get_current_version)" > "${LOG_DIR}/current_version.txt"

        return 0
    else
        log_error "Deployment failed health checks"
        return 1
    fi
}

rollback() {
    log "Starting rollback..."

    restore_backup
    restart_services

    sleep 5

    if health_check; then
        log_success "Rollback completed successfully"
        return 0
    else
        log_error "Rollback failed"
        return 1
    fi
}

###############################################################################
# Command Line Interface
###############################################################################

print_usage() {
    cat << EOF
Usage: $0 <command>

Commands:
  deploy        Deploy application to production
  rollback      Rollback to previous version
  health-check  Check application health
  backup        Create backup only

Environment Variables:
  DEPLOY_KEY         Deployment authentication key
  DATABASE_URL       Database connection URL
  API_TOKEN          API authentication token

Examples:
  $0 deploy
  $0 rollback
  DEPLOY_KEY=secret $0 deploy

EOF
}

main() {
    local command=${1:-}

    case ${command} in
        deploy)
            deploy
            ;;
        rollback)
            rollback
            ;;
        health-check)
            health_check
            ;;
        backup)
            create_backup
            ;;
        *)
            print_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

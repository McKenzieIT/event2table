#!/bin/bash
# ========================================
# Component Migration Batch Script
# ========================================
# 
# This script performs batch component migration with safety checks and rollback support.
# It uses the AST-based migration tool to transform components safely.
#
# @usage
#   ./scripts/batch-replace.sh --dry-run
#   ./scripts/batch-replace.sh --directory frontend/src/features
#   ./scripts/batch-replace.sh --components Modal,Form --execute
#
# @features
# - Dry-run mode for preview
# - Selective component migration
# - Automatic backup creation
# - Rollback support
# - Detailed logging
# - Safety checks

set -euo pipefail

# ========================================
# Configuration
# ========================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_DIR="${PROJECT_ROOT}/logs/migration"
BACKUP_DIR="${PROJECT_ROOT}/backups/migration"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ========================================
# Utility Functions
# ========================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ========================================
# Safety Checks
# ========================================

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    # Check if tsx is installed
    if ! command -v npx &> /dev/null; then
        log_error "npx is not installed"
        exit 1
    fi
    
    # Check if project root exists
    if [[ ! -d "${PROJECT_ROOT}" ]]; then
        log_error "Project root not found: ${PROJECT_ROOT}"
        exit 1
    fi
    
    # Check if migration tool exists
    if [[ ! -f "${SCRIPT_DIR}/migrate-components.ts" ]]; then
        log_error "Migration tool not found: ${SCRIPT_DIR}/migrate-components.ts"
        exit 1
    fi
    
    log_success "All prerequisites checked"
}

# ========================================
# Backup Functions
# ========================================

create_backup() {
    local file_path="$1"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local relative_path=${file_path#"${PROJECT_ROOT}/"}
    local backup_file="${BACKUP_DIR}/${timestamp}/${relative_path}"
    
    # Create backup directory
    mkdir -p "$(dirname "${backup_file}")"
    
    # Copy file to backup
    cp "${file_path}" "${backup_file}"
    
    echo "${backup_file}"
}

create_full_backup() {
    log_info "Creating full backup..."
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="${BACKUP_DIR}/${timestamp}"
    
    # Create backup directory
    mkdir -p "${backup_path}"
    
    # Backup frontend source
    if [[ -d "${PROJECT_ROOT}/frontend/src" ]]; then
        cp -r "${PROJECT_ROOT}/frontend/src" "${backup_path}/"
        log_success "Frontend source backed up to: ${backup_path}"
    fi
    
    # Backup package.json
    if [[ -f "${PROJECT_ROOT}/frontend/package.json" ]]; then
        cp "${PROJECT_ROOT}/frontend/package.json" "${backup_path}/"
    fi
    
    echo "${backup_path}"
}

# ========================================
# Migration Functions
# ========================================

run_migration() {
    local dry_run="$1"
    local directory="$2"
    local components="$3"
    
    log_info "Running migration..."
    log_info "Dry run: ${dry_run}"
    log_info "Directory: ${directory}"
    log_info "Components: ${components}"
    
    # Build command
    local cmd="npx tsx ${SCRIPT_DIR}/migrate-components.ts"
    
    if [[ "${dry_run}" == "true" ]]; then
        cmd="${cmd} --dry-run"
    fi
    
    if [[ -n "${directory}" ]]; then
        cmd="${cmd} --directory ${directory}"
    fi
    
    if [[ -n "${components}" ]]; then
        cmd="${cmd} --components ${components}"
    fi
    
    # Run migration
    if eval "${cmd}"; then
        log_success "Migration completed successfully"
        return 0
    else
        log_error "Migration failed"
        return 1
    fi
}

# ========================================
# Validation Functions
# ========================================

validate_migration() {
    log_info "Validating migration..."
    
    # Run validation tool
    if npx tsx "${SCRIPT_DIR}/validate-migration.ts"; then
        log_success "Migration validation passed"
        return 0
    else
        log_error "Migration validation failed"
        return 1
    fi
}

# ========================================
# Rollback Functions
# ========================================

rollback_migration() {
    local backup_path="$1"
    
    log_warning "Rolling back migration..."
    log_info "Backup location: ${backup_path}"
    
    if [[ ! -d "${backup_path}" ]]; then
        log_error "Backup directory not found: ${backup_path}"
        return 1
    fi
    
    # Restore frontend source
    if [[ -d "${backup_path}/src" ]]; then
        rm -rf "${PROJECT_ROOT}/frontend/src"
        cp -r "${backup_path}/src" "${PROJECT_ROOT}/frontend/"
        log_success "Frontend source restored"
    fi
    
    # Restore package.json
    if [[ -f "${backup_path}/package.json" ]]; then
        cp "${backup_path}/package.json" "${PROJECT_ROOT}/frontend/"
        log_success "package.json restored"
    fi
    
    log_success "Rollback completed"
}

# ========================================
# Logging Functions
# ========================================

setup_logging() {
    mkdir -p "${LOG_DIR}"
    
    local log_file="${LOG_DIR}/migration_$(date +%Y%m%d_%H%M%S).log"
    
    # Redirect stdout and stderr to log file
    exec > >(tee -a "${log_file}")
    exec 2>&1
    
    log_info "Logging to: ${log_file}"
}

# ========================================
# Help Function
# ========================================

show_help() {
    cat << EOF
Component Migration Batch Script

USAGE:
    ./scripts/batch-replace.sh [OPTIONS]

OPTIONS:
    -d, --directory <path>     Target directory for migration
    -c, --components <list>    Comma-separated list of components (Modal,Form,Table)
    -n, --dry-run              Preview changes without applying
    -e, --execute              Execute migration (requires confirmation)
    -b, --backup               Create backup before migration
    -r, --rollback <path>      Rollback from backup path
    -v, --verbose              Enable verbose output
    -h, --help                 Show this help message

EXAMPLES:
    # Dry run on features directory
    ./scripts/batch-replace.sh --dry-run --directory frontend/src/features

    # Execute migration with backup
    ./scripts/batch-replace.sh --execute --backup --directory frontend/src/features

    # Migrate specific components
    ./scripts/batch-replace.sh --execute --components Modal,Form

    # Rollback migration
    ./scripts/batch-replace.sh --rollback backups/migration/20240320_120000

SAFETY:
    - Always run --dry-run first to preview changes
    - Use --backup to create automatic backups
    - Review logs in logs/migration/ directory
    - Rollback is available if needed

EOF
}

# ========================================
# Main Function
# ========================================

main() {
    local dry_run=false
    local execute=false
    local backup=false
    local rollback=""
    local directory=""
    local components=""
    local verbose=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -d|--directory)
                directory="$2"
                shift 2
                ;;
            -c|--components)
                components="$2"
                shift 2
                ;;
            -n|--dry-run)
                dry_run=true
                shift
                ;;
            -e|--execute)
                execute=true
                shift
                ;;
            -b|--backup)
                backup=true
                shift
                ;;
            -r|--rollback)
                rollback="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Handle rollback
    if [[ -n "${rollback}" ]]; then
        rollback_migration "${rollback}"
        exit $?
    fi
    
    # Setup logging
    setup_logging
    
    # Check prerequisites
    check_prerequisites
    
    # Create backup if requested
    local backup_path=""
    if [[ "${backup}" == "true" ]]; then
        backup_path=$(create_full_backup)
        log_info "Backup created: ${backup_path}"
    fi
    
    # Set default directory if not specified
    if [[ -z "${directory}" ]]; then
        directory="${PROJECT_ROOT}/frontend/src"
    fi
    
    # Confirm execution
    if [[ "${execute}" == "true" ]]; then
        echo ""
        log_warning "You are about to execute component migration!"
        log_warning "This will modify files in: ${directory}"
        echo ""
        read -p "Are you sure you want to continue? (yes/no): " confirm
        
        if [[ "${confirm}" != "yes" ]]; then
            log_info "Migration cancelled by user"
            exit 0
        fi
    else
        dry_run=true
        log_info "Running in dry-run mode (use --execute to apply changes)"
    fi
    
    # Run migration
    if run_migration "${dry_run}" "${directory}" "${components}"; then
        # Validate if not dry run
        if [[ "${execute}" == "true" ]]; then
            if validate_migration; then
                log_success "Migration and validation completed successfully"
                
                if [[ -n "${backup_path}" ]]; then
                    echo ""
                    log_info "Backup location: ${backup_path}"
                    log_info "To rollback: ./scripts/batch-replace.sh --rollback ${backup_path}"
                fi
            else
                log_error "Validation failed, rolling back..."
                if [[ -n "${backup_path}" ]]; then
                    rollback_migration "${backup_path}"
                fi
                exit 1
            fi
        fi
    else
        log_error "Migration failed"
        if [[ -n "${backup_path}" ]]; then
            log_info "Backup available at: ${backup_path}"
        fi
        exit 1
    fi
}

# Run main function
main "$@"

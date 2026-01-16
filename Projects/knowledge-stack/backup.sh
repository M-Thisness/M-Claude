#!/bin/bash
# Knowledge Stack Backup Script
# This script creates a complete backup of Silverbullet and Paperless-ngx

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_ROOT="${SCRIPT_DIR}/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_docker_compose() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available"
        exit 1
    fi
}

# Main backup process
main() {
    log_info "Starting backup process..."
    log_info "Backup directory: ${BACKUP_DIR}"

    # Check prerequisites
    check_docker_compose

    # Create backup directory
    mkdir -p "${BACKUP_DIR}"

    # Change to script directory
    cd "${SCRIPT_DIR}"

    # Stop containers to ensure consistent backup
    log_info "Stopping Silverbullet and Paperless containers..."
    docker compose stop silverbullet paperless-ngx || log_warn "Failed to stop containers"

    # Backup Silverbullet
    log_info "Backing up Silverbullet space..."
    if [ -d "data/silverbullet/space" ]; then
        tar -czf "${BACKUP_DIR}/silverbullet-space.tar.gz" \
            -C data/silverbullet space/ \
            && log_info "Silverbullet backup complete" \
            || log_error "Silverbullet backup failed"
    else
        log_warn "Silverbullet data directory not found"
    fi

    # Backup Paperless media
    log_info "Backing up Paperless media files..."
    if [ -d "data/paperless/media" ]; then
        tar -czf "${BACKUP_DIR}/paperless-media.tar.gz" \
            -C data/paperless media/ \
            && log_info "Paperless media backup complete" \
            || log_error "Paperless media backup failed"
    else
        log_warn "Paperless media directory not found"
    fi

    # Backup Paperless data
    log_info "Backing up Paperless data files..."
    if [ -d "data/paperless/data" ]; then
        tar -czf "${BACKUP_DIR}/paperless-data.tar.gz" \
            -C data/paperless data/ \
            && log_info "Paperless data backup complete" \
            || log_error "Paperless data backup failed"
    else
        log_warn "Paperless data directory not found"
    fi

    # Start database for backup
    log_info "Starting database for backup..."
    docker compose start paperless-db
    sleep 5

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    for i in {1..30}; do
        if docker compose exec -T paperless-db pg_isready -U paperless &> /dev/null; then
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            log_error "Database did not become ready in time"
            docker compose start silverbullet paperless-ngx
            exit 1
        fi
    done

    # Backup database
    log_info "Backing up Paperless database..."
    docker compose exec -T paperless-db pg_dump -U paperless paperless \
        > "${BACKUP_DIR}/paperless-db.sql" \
        && log_info "Database backup complete" \
        || log_error "Database backup failed"

    # Compress database backup
    log_info "Compressing database backup..."
    gzip "${BACKUP_DIR}/paperless-db.sql"

    # Backup configuration files
    log_info "Backing up configuration files..."
    tar -czf "${BACKUP_DIR}/config.tar.gz" \
        docker-compose.yml \
        .env \
        2>/dev/null || log_warn "Some config files missing"

    # Restart all services
    log_info "Restarting all services..."
    docker compose start silverbullet paperless-ngx

    # Calculate backup size
    BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
    log_info "Backup size: ${BACKUP_SIZE}"

    # Create backup manifest
    cat > "${BACKUP_DIR}/MANIFEST.txt" << EOF
Knowledge Stack Backup
=====================

Backup Date: $(date)
Backup Directory: ${BACKUP_DIR}
Backup Size: ${BACKUP_SIZE}

Contents:
- silverbullet-space.tar.gz    Silverbullet notes and pages
- paperless-media.tar.gz       Paperless document files
- paperless-data.tar.gz        Paperless application data
- paperless-db.sql.gz          PostgreSQL database dump
- config.tar.gz                Configuration files

To restore:
1. Stop containers: docker compose down
2. Extract archives to data/ directory
3. Restore database: zcat paperless-db.sql.gz | docker compose exec -T paperless-db psql -U paperless paperless
4. Start containers: docker compose up -d
EOF

    log_info "Backup complete!"
    log_info "Location: ${BACKUP_DIR}"

    # Optional: Clean up old backups (keep last 30 days)
    if [ "${CLEANUP_OLD_BACKUPS}" = "true" ]; then
        log_info "Cleaning up backups older than 30 days..."
        find "${BACKUP_ROOT}" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
    fi

    # Optional: Sync to remote
    if [ -n "${RCLONE_REMOTE}" ]; then
        log_info "Syncing to remote: ${RCLONE_REMOTE}"
        rclone sync "${BACKUP_ROOT}" "${RCLONE_REMOTE}" --verbose || log_warn "Remote sync failed"
    fi

    log_info "All done!"
}

# Run main function
main "$@"

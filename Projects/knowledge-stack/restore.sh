#!/bin/bash
# Knowledge Stack Restore Script
# This script restores a backup created by backup.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
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

list_backups() {
    echo -e "\n${BLUE}Available backups:${NC}"
    local backups_dir="./backups"

    if [ ! -d "$backups_dir" ]; then
        log_error "No backups directory found"
        exit 1
    fi

    local count=0
    for backup in "$backups_dir"/*; do
        if [ -d "$backup" ]; then
            count=$((count + 1))
            local backup_name=$(basename "$backup")
            local backup_size=$(du -sh "$backup" 2>/dev/null | cut -f1)
            echo "  $count. $backup_name ($backup_size)"
        fi
    done

    if [ $count -eq 0 ]; then
        log_error "No backups found in $backups_dir"
        exit 1
    fi
}

# Main restore process
main() {
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    log_info "Knowledge Stack Restore Utility"
    echo ""

    # Check prerequisites
    check_docker_compose

    # List available backups
    list_backups

    # Prompt for backup to restore
    echo ""
    if [ -z "$1" ]; then
        echo -ne "${YELLOW}Enter backup directory name (e.g., 20260116-020000):${NC} "
        read backup_name
    else
        backup_name="$1"
    fi

    BACKUP_DIR="./backups/${backup_name}"

    # Validate backup directory
    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "Backup directory not found: $BACKUP_DIR"
        exit 1
    fi

    # Show backup manifest if available
    if [ -f "$BACKUP_DIR/MANIFEST.txt" ]; then
        echo ""
        log_info "Backup manifest:"
        cat "$BACKUP_DIR/MANIFEST.txt"
        echo ""
    fi

    # Confirmation
    echo -ne "${RED}This will OVERWRITE current data. Continue? (yes/no):${NC} "
    read confirmation

    if [ "$confirmation" != "yes" ]; then
        log_info "Restore cancelled"
        exit 0
    fi

    log_step "Starting restore from: $BACKUP_DIR"

    # Stop all containers
    log_step "Stopping all containers..."
    docker compose down

    # Backup current data (just in case)
    log_step "Creating safety backup of current data..."
    SAFETY_BACKUP="./backups/pre-restore-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$SAFETY_BACKUP"
    [ -d "data" ] && cp -r data "$SAFETY_BACKUP/" || log_warn "No current data to backup"
    log_info "Safety backup created at: $SAFETY_BACKUP"

    # Restore Silverbullet
    log_step "Restoring Silverbullet space..."
    if [ -f "$BACKUP_DIR/silverbullet-space.tar.gz" ]; then
        rm -rf data/silverbullet/space
        mkdir -p data/silverbullet
        tar -xzf "$BACKUP_DIR/silverbullet-space.tar.gz" -C data/silverbullet
        log_info "Silverbullet restored"
    else
        log_warn "Silverbullet backup not found, skipping"
    fi

    # Restore Paperless media
    log_step "Restoring Paperless media..."
    if [ -f "$BACKUP_DIR/paperless-media.tar.gz" ]; then
        rm -rf data/paperless/media
        mkdir -p data/paperless
        tar -xzf "$BACKUP_DIR/paperless-media.tar.gz" -C data/paperless
        log_info "Paperless media restored"
    else
        log_warn "Paperless media backup not found, skipping"
    fi

    # Restore Paperless data
    log_step "Restoring Paperless data..."
    if [ -f "$BACKUP_DIR/paperless-data.tar.gz" ]; then
        rm -rf data/paperless/data
        mkdir -p data/paperless
        tar -xzf "$BACKUP_DIR/paperless-data.tar.gz" -C data/paperless
        log_info "Paperless data restored"
    else
        log_warn "Paperless data backup not found, skipping"
    fi

    # Start database for restore
    log_step "Starting database..."
    docker compose up -d paperless-db
    sleep 10

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    for i in {1..60}; do
        if docker compose exec -T paperless-db pg_isready -U paperless &> /dev/null; then
            break
        fi
        sleep 1
        if [ $i -eq 60 ]; then
            log_error "Database did not become ready in time"
            exit 1
        fi
    done

    # Restore database
    log_step "Restoring database..."
    if [ -f "$BACKUP_DIR/paperless-db.sql.gz" ]; then
        # Drop and recreate database
        docker compose exec -T paperless-db psql -U paperless -c "DROP DATABASE IF EXISTS paperless;" postgres || true
        docker compose exec -T paperless-db psql -U paperless -c "CREATE DATABASE paperless;" postgres

        # Restore from backup
        zcat "$BACKUP_DIR/paperless-db.sql.gz" | docker compose exec -T paperless-db psql -U paperless paperless
        log_info "Database restored"
    elif [ -f "$BACKUP_DIR/paperless-db.sql" ]; then
        # Uncompressed backup
        docker compose exec -T paperless-db psql -U paperless -c "DROP DATABASE IF EXISTS paperless;" postgres || true
        docker compose exec -T paperless-db psql -U paperless -c "CREATE DATABASE paperless;" postgres
        cat "$BACKUP_DIR/paperless-db.sql" | docker compose exec -T paperless-db psql -U paperless paperless
        log_info "Database restored"
    else
        log_warn "Database backup not found, skipping"
    fi

    # Restore configuration (optional)
    if [ -f "$BACKUP_DIR/config.tar.gz" ]; then
        echo -ne "${YELLOW}Restore configuration files? (yes/no):${NC} "
        read restore_config
        if [ "$restore_config" = "yes" ]; then
            log_step "Restoring configuration..."
            tar -xzf "$BACKUP_DIR/config.tar.gz"
            log_info "Configuration restored"
            log_warn "Please review .env file for any needed changes"
        fi
    fi

    # Fix permissions
    log_step "Fixing permissions..."
    sudo chown -R 1000:1000 data/silverbullet/ 2>/dev/null || true
    sudo chown -R 1000:1000 data/paperless/ 2>/dev/null || true

    # Start all services
    log_step "Starting all services..."
    docker compose up -d

    # Wait for services to be healthy
    log_info "Waiting for services to start..."
    sleep 15

    # Check health
    log_step "Checking service health..."
    docker compose ps

    echo ""
    log_info "Restore complete!"
    log_info ""
    log_info "Services should be available at:"
    log_info "  - Silverbullet: http://localhost:3000"
    log_info "  - Paperless-ngx: http://localhost:8000"
    log_info ""
    log_info "Monitor logs with: docker compose logs -f"
    log_info "Safety backup location: $SAFETY_BACKUP"
}

# Run main function
main "$@"

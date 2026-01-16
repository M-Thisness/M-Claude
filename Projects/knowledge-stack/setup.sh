#!/bin/bash
# Knowledge Stack Setup Script
# Automates initial setup of the knowledge management stack

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

check_dependencies() {
    log_step "Checking dependencies..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first:"
        echo "  https://docs.docker.com/get-docker/"
        exit 1
    fi
    log_info "Docker: $(docker --version)"

    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose v2:"
        echo "  https://docs.docker.com/compose/install/"
        exit 1
    fi
    log_info "Docker Compose: $(docker compose version)"

    # Check openssl for secret generation
    if ! command -v openssl &> /dev/null; then
        log_warn "openssl not found. You'll need to set PAPERLESS_SECRET_KEY manually."
    fi
}

generate_secret() {
    if command -v openssl &> /dev/null; then
        openssl rand -base64 32
    else
        # Fallback to urandom
        cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
    fi
}

create_env_file() {
    log_step "Creating environment file..."

    if [ -f ".env" ]; then
        log_warn ".env file already exists. Creating .env.new instead."
        ENV_FILE=".env.new"
    else
        ENV_FILE=".env"
    fi

    # Generate secure random values
    local SECRET_KEY=$(generate_secret)
    local DB_PASSWORD=$(generate_secret | cut -c1-16)

    # Prompt for configuration
    echo ""
    echo -e "${BLUE}Configuration Setup${NC}"
    echo "Press Enter to use default values shown in [brackets]"
    echo ""

    read -p "Paperless admin username [admin]: " ADMIN_USER
    ADMIN_USER=${ADMIN_USER:-admin}

    read -sp "Paperless admin password [auto-generated]: " ADMIN_PASSWORD
    echo ""
    ADMIN_PASSWORD=${ADMIN_PASSWORD:-$(generate_secret | cut -c1-16)}

    read -p "Paperless admin email [admin@localhost]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@localhost}

    read -p "Timezone [America/New_York]: " TIMEZONE
    TIMEZONE=${TIMEZONE:-America/New_York}

    read -p "OCR Language [eng]: " OCR_LANG
    OCR_LANG=${OCR_LANG:-eng}

    # Create .env file
    cat > "$ENV_FILE" << EOF
# Knowledge Management Stack Environment Variables
# Generated: $(date)

# =============================================================================
# Silverbullet Configuration
# =============================================================================
SB_USER=${ADMIN_USER}
# SB_PASSWORD=  # Optional: Set a password for Silverbullet

# =============================================================================
# Paperless-ngx Configuration
# =============================================================================

# Database Configuration
PAPERLESS_DBNAME=paperless
PAPERLESS_DBUSER=paperless
PAPERLESS_DBPASS=${DB_PASSWORD}

# Security
PAPERLESS_SECRET_KEY=${SECRET_KEY}
PAPERLESS_ADMIN_USER=${ADMIN_USER}
PAPERLESS_ADMIN_PASSWORD=${ADMIN_PASSWORD}
PAPERLESS_ADMIN_MAIL=${ADMIN_EMAIL}

# OCR Settings
PAPERLESS_OCR_LANGUAGE=${OCR_LANG}
PAPERLESS_OCR_MODE=skip
PAPERLESS_OCR_CLEAN=clean
PAPERLESS_OCR_DESKEW=true
PAPERLESS_OCR_ROTATE_PAGES=true
PAPERLESS_OCR_ROTATE_PAGES_THRESHOLD=12.0

# Performance Settings
PAPERLESS_WEBSERVER_WORKERS=2
PAPERLESS_TASK_WORKERS=2
PAPERLESS_THREADS_PER_WORKER=2

# URL Configuration
PAPERLESS_URL=http://localhost:8000

# Consumer Settings
PAPERLESS_CONSUMER_POLLING=60
PAPERLESS_CONSUMER_RECURSIVE=true
PAPERLESS_CONSUMER_SUBDIRS_AS_TAGS=true

# =============================================================================
# General Settings
# =============================================================================
TZ=${TIMEZONE}
EOF

    log_info "Environment file created: $ENV_FILE"

    if [ "$ENV_FILE" = ".env.new" ]; then
        log_warn "Please review .env.new and merge with your existing .env file"
    fi

    # Show credentials
    echo ""
    echo -e "${GREEN}=== Important Credentials ===${NC}"
    echo "Paperless Admin Username: ${ADMIN_USER}"
    echo "Paperless Admin Password: ${ADMIN_PASSWORD}"
    echo "Database Password: ${DB_PASSWORD}"
    echo ""
    log_warn "Save these credentials securely!"
    echo ""
}

create_directories() {
    log_step "Creating data directories..."

    mkdir -p data/silverbullet/space
    mkdir -p data/paperless/{data,media,export,consume,pgdata,redis}
    mkdir -p backups

    log_info "Directories created"
}

set_permissions() {
    log_step "Setting permissions..."

    # Set ownership to user 1000:1000 (typical Docker user)
    if [ -d "data" ]; then
        sudo chown -R 1000:1000 data/ 2>/dev/null || {
            log_warn "Could not set ownership (need sudo). You may need to fix this manually."
        }
    fi

    # Make scripts executable
    chmod +x backup.sh restore.sh setup.sh 2>/dev/null || true

    log_info "Permissions set"
}

pull_images() {
    log_step "Pulling Docker images (this may take a while)..."

    docker compose pull

    log_info "Images pulled"
}

start_stack() {
    log_step "Starting the knowledge stack..."

    docker compose up -d

    log_info "Containers starting..."
}

wait_for_services() {
    log_step "Waiting for services to be ready..."

    echo -n "  Waiting for database"
    for i in {1..60}; do
        if docker compose exec -T paperless-db pg_isready -U paperless &> /dev/null; then
            echo " ✓"
            break
        fi
        echo -n "."
        sleep 1
        if [ $i -eq 60 ]; then
            echo " ✗"
            log_error "Database did not become ready in time"
            return 1
        fi
    done

    echo -n "  Waiting for Paperless"
    for i in {1..90}; do
        if curl -s http://localhost:8000 &> /dev/null; then
            echo " ✓"
            break
        fi
        echo -n "."
        sleep 2
        if [ $i -eq 90 ]; then
            echo " ✗"
            log_warn "Paperless may not be fully ready yet"
            break
        fi
    done

    echo -n "  Waiting for Silverbullet"
    for i in {1..30}; do
        if curl -s http://localhost:3000 &> /dev/null; then
            echo " ✓"
            break
        fi
        echo -n "."
        sleep 1
        if [ $i -eq 30 ]; then
            echo " ✗"
            log_warn "Silverbullet may not be fully ready yet"
            break
        fi
    done

    log_info "Services are ready!"
}

show_summary() {
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Knowledge Stack Setup Complete!                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Services:${NC}"
    echo "  🗒️  Silverbullet:  http://localhost:3000"
    echo "  📄 Paperless-ngx: http://localhost:8000"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Open Silverbullet and start taking notes"
    echo "  2. Log into Paperless with your admin credentials"
    echo "  3. Upload documents to data/paperless/consume/ or via web UI"
    echo "  4. Set up automated backups (see README.md)"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs:       docker compose logs -f"
    echo "  Stop stack:      docker compose stop"
    echo "  Start stack:     docker compose start"
    echo "  Restart stack:   docker compose restart"
    echo "  Update images:   docker compose pull && docker compose up -d"
    echo "  Backup:          ./backup.sh"
    echo ""
    echo -e "${BLUE}Documentation:${NC}"
    echo "  Local:  ./README.md"
    echo "  Research: ../Docs/KNOWLEDGE-MANAGEMENT-STACK-RESEARCH.md"
    echo ""
}

check_system_resources() {
    log_step "Checking system resources..."

    # Check available memory
    if command -v free &> /dev/null; then
        local available_mem=$(free -g | awk '/^Mem:/{print $7}')
        if [ "$available_mem" -lt 6 ]; then
            log_warn "Less than 6GB RAM available. Consider reducing worker counts in .env"
            log_warn "See README.md 'Optimize for Limited Resources' section"
        else
            log_info "Memory: ${available_mem}GB available"
        fi
    fi

    # Check available disk space
    if command -v df &> /dev/null; then
        local available_disk=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
        if [ "$available_disk" -lt 100 ]; then
            log_warn "Less than 100GB disk space available"
        else
            log_info "Disk: ${available_disk}GB available"
        fi
    fi
}

# Main setup process
main() {
    local SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Knowledge Management Stack - Setup Wizard                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Check if already set up
    if [ -f ".env" ] && [ -d "data" ]; then
        log_warn "Stack appears to be already set up"
        echo -n "Continue anyway? (yes/no): "
        read continue_setup
        if [ "$continue_setup" != "yes" ]; then
            log_info "Setup cancelled"
            exit 0
        fi
    fi

    # Run setup steps
    check_dependencies
    check_system_resources
    create_env_file
    create_directories
    set_permissions
    pull_images
    start_stack
    wait_for_services
    show_summary

    log_info "Setup complete! Enjoy your knowledge management stack!"
}

# Run main function
main "$@"

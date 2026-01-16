#!/bin/bash
# Home Assistant Docker Setup Script for Proxmox LXC
# This script automates the initial setup of Home Assistant with Docker Compose

set -e  # Exit on error

echo "================================================"
echo "Home Assistant Docker Setup Script"
echo "================================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)"
    exit 1
fi

# Configuration
INSTALL_DIR="/opt/homeassistant"
COMPOSE_VERSION="2.24.0"

echo "Configuration:"
echo "  Install directory: $INSTALL_DIR"
echo "  Docker Compose version: $COMPOSE_VERSION"
echo ""

read -p "Continue with installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# Update system
echo ""
echo "[1/8] Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo ""
echo "[2/8] Installing dependencies..."
apt install -y \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    software-properties-common \
    usbutils

# Install Docker
echo ""
echo "[3/8] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installed successfully."
else
    echo "Docker already installed, skipping."
fi

# Install Docker Compose plugin
echo ""
echo "[4/8] Installing Docker Compose plugin..."
if ! docker compose version &> /dev/null; then
    apt install -y docker-compose-plugin
    echo "Docker Compose plugin installed successfully."
else
    echo "Docker Compose already installed, skipping."
fi

# Disable ModemManager (interferes with USB dongles)
echo ""
echo "[5/8] Disabling ModemManager (prevents USB dongle issues)..."
if systemctl is-active --quiet ModemManager; then
    systemctl stop ModemManager
    systemctl disable ModemManager
    echo "ModemManager disabled."
else
    echo "ModemManager not active, skipping."
fi

# Create directory structure
echo ""
echo "[6/8] Creating directory structure..."
mkdir -p $INSTALL_DIR/{homeassistant/config,mariadb/data,mosquitto/{config,data,log}}

# Create .env file
echo ""
echo "[7/8] Creating .env file..."
cat > $INSTALL_DIR/.env << 'EOF'
# Home Assistant Environment Variables
# IMPORTANT: Change these passwords before deploying!

# MariaDB Configuration
MYSQL_ROOT_PASSWORD=change_this_root_password_NOW
MYSQL_PASSWORD=change_this_ha_password_NOW

# Timezone (change to your timezone)
TZ=America/New_York
EOF

echo "Created .env file at $INSTALL_DIR/.env"
echo "IMPORTANT: Edit this file and change the default passwords!"

# Create mosquitto configuration
echo ""
echo "Creating Mosquitto configuration..."
cat > $INSTALL_DIR/mosquitto/config/mosquitto.conf << 'EOF'
# Mosquitto MQTT Broker Configuration
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout

# Default Listener
listener 1883
protocol mqtt

# WebSocket Listener
listener 9001
protocol websockets

# Authentication - Initially allow anonymous
# After setup, create password file and disable anonymous access
allow_anonymous true

# To enable authentication:
# 1. docker exec -it homeassistant_mosquitto mosquitto_passwd -c /mosquitto/config/passwd <username>
# 2. Uncomment these lines and restart mosquitto:
# allow_anonymous false
# password_file /mosquitto/config/passwd
EOF

# Detect USB devices
echo ""
echo "[8/8] Detecting USB devices..."
echo "Available USB devices:"
echo "====================="
lsusb
echo ""
echo "Serial devices:"
echo "==============="
ls -l /dev/serial/by-id/ 2>/dev/null || echo "No serial devices found"
echo ""

# Create docker-compose.yml (note: user should copy the provided file)
echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Copy home-assistant-docker-compose.yml to $INSTALL_DIR/docker-compose.yml"
echo "2. Edit $INSTALL_DIR/.env and change the default passwords"
echo "3. Edit docker-compose.yml and update USB device paths if needed"
echo "4. Start the stack: cd $INSTALL_DIR && docker compose up -d"
echo "5. Access Home Assistant at: http://$(hostname -I | awk '{print $1}'):8123"
echo ""
echo "USB Device Configuration:"
echo "  - Check 'Available USB devices' output above"
echo "  - Update device paths in docker-compose.yml"
echo "  - Use /dev/serial/by-id/ paths for stability"
echo ""
echo "Useful commands:"
echo "  Start:   docker compose -f $INSTALL_DIR/docker-compose.yml up -d"
echo "  Stop:    docker compose -f $INSTALL_DIR/docker-compose.yml down"
echo "  Logs:    docker compose -f $INSTALL_DIR/docker-compose.yml logs -f"
echo "  Restart: docker compose -f $INSTALL_DIR/docker-compose.yml restart"
echo ""
echo "Configuration files:"
echo "  Environment:  $INSTALL_DIR/.env"
echo "  HA Config:    $INSTALL_DIR/homeassistant/config/"
echo "  Mosquitto:    $INSTALL_DIR/mosquitto/config/mosquitto.conf"
echo ""

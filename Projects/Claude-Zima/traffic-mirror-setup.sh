#!/bin/bash
# Traffic Mirroring Setup for Proxmox
# Mirrors traffic from client networks to monitoring bridge for IDS/analysis
#
# This script sets up port mirroring using tc (traffic control) to copy
# packets from vmbr2 (Legion), vmbr3 (Book), and vmbr4 (IoT) to vmbr_monitor

set -e

echo "========================================"
echo "Traffic Mirroring Configuration"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (sudo)"
    exit 1
fi

# Install required packages
echo "[1/4] Installing required packages..."
apt-get update -qq
apt-get install -y iproute2 tcpdump

# ============================================================================
# FUNCTION: Setup mirroring for a bridge
# ============================================================================

setup_mirror() {
    local SOURCE_BRIDGE=$1
    local DEST_BRIDGE=$2
    local DESCRIPTION=$3

    echo "[INFO] Setting up mirroring: $SOURCE_BRIDGE -> $DEST_BRIDGE ($DESCRIPTION)"

    # Remove existing qdisc if present
    tc qdisc del dev "$SOURCE_BRIDGE" ingress 2>/dev/null || true
    tc qdisc del dev "$SOURCE_BRIDGE" root 2>/dev/null || true

    # Add ingress qdisc for incoming traffic
    tc qdisc add dev "$SOURCE_BRIDGE" handle ffff: ingress

    # Mirror all ingress traffic to monitoring bridge
    tc filter add dev "$SOURCE_BRIDGE" parent ffff: \
        protocol all \
        u32 match u8 0 0 \
        action mirred egress mirror dev "$DEST_BRIDGE"

    # Add egress qdisc for outgoing traffic
    tc qdisc add dev "$SOURCE_BRIDGE" root handle 1: prio

    # Mirror all egress traffic to monitoring bridge
    tc filter add dev "$SOURCE_BRIDGE" parent 1: \
        protocol all \
        u32 match u8 0 0 \
        action mirred egress mirror dev "$DEST_BRIDGE"

    echo "[OK] Mirroring configured for $SOURCE_BRIDGE"
}

# ============================================================================
# CONFIGURE MIRRORING
# ============================================================================

echo "[2/4] Configuring traffic mirroring..."

# Mirror Legion network (vmbr2)
setup_mirror "vmbr2" "vmbr_monitor" "Legion Network"

# Mirror Book network (vmbr3)
setup_mirror "vmbr3" "vmbr_monitor" "Book Network"

# Mirror IoT network (vmbr4)
setup_mirror "vmbr4" "vmbr_monitor" "IoT Network"

# ============================================================================
# VERIFY CONFIGURATION
# ============================================================================

echo "[3/4] Verifying configuration..."
echo ""

for BRIDGE in vmbr2 vmbr3 vmbr4; do
    echo "--- Traffic Control for $BRIDGE ---"
    tc -s qdisc show dev "$BRIDGE"
    tc -s filter show dev "$BRIDGE" ingress 2>/dev/null || echo "No ingress filters"
    tc -s filter show dev "$BRIDGE" parent 1: 2>/dev/null || echo "No egress filters"
    echo ""
done

# ============================================================================
# CREATE SYSTEMD SERVICE FOR PERSISTENCE
# ============================================================================

echo "[4/4] Creating systemd service for persistence..."

cat > /etc/systemd/system/traffic-mirror.service << 'EOF'
[Unit]
Description=Traffic Mirroring for Network Monitoring
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/local/bin/setup-traffic-mirror.sh
ExecStop=/usr/local/bin/teardown-traffic-mirror.sh

[Install]
WantedBy=multi-user.target
EOF

# Create the setup script
cp "$0" /usr/local/bin/setup-traffic-mirror.sh
chmod +x /usr/local/bin/setup-traffic-mirror.sh

# Create teardown script
cat > /usr/local/bin/teardown-traffic-mirror.sh << 'EOF'
#!/bin/bash
# Teardown traffic mirroring
tc qdisc del dev vmbr2 ingress 2>/dev/null || true
tc qdisc del dev vmbr2 root 2>/dev/null || true
tc qdisc del dev vmbr3 ingress 2>/dev/null || true
tc qdisc del dev vmbr3 root 2>/dev/null || true
tc qdisc del dev vmbr4 ingress 2>/dev/null || true
tc qdisc del dev vmbr4 root 2>/dev/null || true
echo "Traffic mirroring disabled"
EOF

chmod +x /usr/local/bin/teardown-traffic-mirror.sh

# Enable and start service
systemctl daemon-reload
systemctl enable traffic-mirror.service
systemctl start traffic-mirror.service

echo ""
echo "========================================"
echo "Traffic mirroring configured!"
echo "========================================"
echo ""
echo "Summary:"
echo "  ✓ vmbr2 (Legion) -> vmbr_monitor"
echo "  ✓ vmbr3 (Book) -> vmbr_monitor"
echo "  ✓ vmbr4 (IoT) -> vmbr_monitor"
echo "  ✓ Systemd service created for persistence"
echo ""
echo "All traffic from client networks is now mirrored to vmbr_monitor"
echo "for analysis by Suricata and ntopng."
echo ""
echo "Test mirroring with:"
echo "  tcpdump -i vmbr_monitor -c 10"
echo ""
echo "View mirroring stats:"
echo "  tc -s filter show dev vmbr2 ingress"
echo ""
echo "Disable mirroring:"
echo "  systemctl stop traffic-mirror.service"
echo ""
echo "Re-enable mirroring:"
echo "  systemctl start traffic-mirror.service"
echo ""

# ============================================================================
# OPTIONAL: Test the mirroring
# ============================================================================

read -p "Would you like to test the mirroring now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Testing traffic mirroring..."
    echo "Running tcpdump on vmbr_monitor for 10 seconds..."
    echo "(You should see traffic if Legion/Book/IoT devices are active)"
    echo ""
    timeout 10 tcpdump -i vmbr_monitor -n -c 50 || true
    echo ""
    echo "Test complete!"
fi

echo ""
echo "Setup complete!"

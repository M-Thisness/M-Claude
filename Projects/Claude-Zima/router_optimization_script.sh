#!/bin/bash
# GL-BE3600 Network Optimization Script
# Date: 2026-01-10
# WARNING: This script makes significant changes to router configuration
# Backup your config before running: sysupgrade -b /tmp/backup.tar.gz

set -e  # Exit on error

ROUTER_IP="192.168.8.1"

echo "========================================="
echo "GL-BE3600 Network Optimization Script"
echo "========================================="
echo ""
echo "This script will:"
echo "  1. Configure static IP reservations"
echo "  2. Optimize WiFi settings for performance"
echo "  3. Configure IoT network isolation"
echo "  4. Optimize DHCP and DNS settings"
echo ""
echo "BACKUP YOUR CONFIGURATION FIRST!"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Connecting to router at $ROUTER_IP..."
echo ""

# ============================================
# PHASE 1: DHCP Configuration & Static IPs
# ============================================

cat << 'EOF_DHCP' | ssh root@$ROUTER_IP "cat > /tmp/dhcp_config.sh && chmod +x /tmp/dhcp_config.sh && /tmp/dhcp_config.sh"
#!/bin/sh
echo "[Phase 1] Configuring DHCP and Static IPs..."

# Update DHCP pool to start at .201 instead of .100
uci set dhcp.lan.start='201'
uci set dhcp.lan.limit='50'

# Increase DNS cache for better performance
uci set dhcp.@dnsmasq[0].cachesize='5000'

# Update existing static reservations with clearer tags
# Legion Pro 7i (wired) - C8:53:09:F6:33:09 -> 192.168.8.23
uci set dhcp.@host[0].ip='192.168.8.23'
uci set dhcp.@host[0].name='legion-wired'
uci set dhcp.@host[0].dns='1'

# MacBook Pro M3 (WiFi) - 16:63:EA:84:8B:C6 -> 192.168.8.52
uci set dhcp.@host[1].ip='192.168.8.52'
uci set dhcp.@host[1].name='macbook-wifi'
uci set dhcp.@host[1].dns='1'

# Legion Pro 7i (WiFi) - 90:10:57:D2:AE:E2 -> 192.168.8.53
uci set dhcp.@host[2].ip='192.168.8.53'
uci set dhcp.@host[2].name='legion-wifi'
uci set dhcp.@host[2].dns='1'

# Add Pixel 10 Pro XL - 1A:91:39:0E:6F:09 -> 192.168.8.51
uci add dhcp host
uci set dhcp.@host[-1].mac='1A:91:39:0E:6F:09'
uci set dhcp.@host[-1].ip='192.168.8.51'
uci set dhcp.@host[-1].name='pixel'
uci set dhcp.@host[-1].dns='1'

# Note: Zimaboard and other device MACs need to be added manually
# Format: uci add dhcp host; uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'; uci set dhcp.@host[-1].ip='192.168.8.21'

uci commit dhcp

echo "[Phase 1] DHCP configuration updated"
EOF_DHCP

echo "[✓] Phase 1 complete: DHCP and static IPs configured"
echo ""

# ============================================
# PHASE 2: WiFi Optimization
# ============================================

cat << 'EOF_WIFI' | ssh root@$ROUTER_IP "cat > /tmp/wifi_config.sh && chmod +x /tmp/wifi_config.sh && /tmp/wifi_config.sh"
#!/bin/sh
echo "[Phase 2] Optimizing WiFi settings..."

# ============================================
# 5GHz Radio - Optimize for performance
# ============================================
# Set fixed channel instead of auto for better performance
uci set wireless.wifi1.channel='36'

# Increase TX power for better range (max 23 dBm for US)
uci set wireless.wifi1.txpower='23'

# Ensure HT160 for maximum throughput
uci set wireless.wifi1.htmode='HT160'

# Keep WPA3 for 5GHz main network (modern devices support it)
uci set wireless.wifi5g.encryption='sae-mixed'

# Disable SAE for compatibility if issues occur (can re-enable later)
# uci set wireless.wifi5g.sae='0'

# ============================================
# 2.4GHz Radio - Optimize for IoT compatibility
# ============================================
# Set fixed channel (1, 6, or 11 are non-overlapping)
uci set wireless.wifi0.channel='6'

# Set moderate TX power for 2.4GHz
uci set wireless.wifi0.txpower='20'

# Set HT20 for IoT compatibility (many devices don't support HT40)
uci set wireless.wifi0.htmode='HT20'

# ============================================
# Guest Network for IoT Devices
# ============================================
# Enable guest network
uci set wireless.guest2g.disabled='0'

# Make guest network visible (not hidden) so IoT devices can find it
uci set wireless.guest2g.hidden='0'

# Set simpler SSID for IoT
uci set wireless.guest2g.ssid='slate-iot'

# Use WPA2 for ESP32 compatibility (not WPA3)
uci set wireless.guest2g.encryption='psk2+ccmp'
uci set wireless.guest2g.sae='0'

# Set simple password for IoT network
uci set wireless.guest2g.key='iot-network-2026'

# Isolate guest network clients from each other
uci set wireless.guest2g.isolate='1'

# ============================================
# 5GHz Guest Network for IoT
# ============================================
# Some IoT devices support 5GHz, so enable it
uci set wireless.guest5g.disabled='0'
uci set wireless.guest5g.hidden='0'
uci set wireless.guest5g.ssid='slate-iot'
uci set wireless.guest5g.encryption='psk2+ccmp'
uci set wireless.guest5g.sae='0'
uci set wireless.guest5g.key='iot-network-2026'
uci set wireless.guest5g.isolate='1'

uci commit wireless

echo "[Phase 2] WiFi optimization complete"
EOF_WIFI

echo "[✓] Phase 2 complete: WiFi settings optimized"
echo ""

# ============================================
# PHASE 3: Network Segmentation & Firewall
# ============================================

cat << 'EOF_FW' | ssh root@$ROUTER_IP "cat > /tmp/firewall_config.sh && chmod +x /tmp/firewall_config.sh && /tmp/firewall_config.sh"
#!/bin/sh
echo "[Phase 3] Configuring network segmentation..."

# Create guest zone if it doesn't exist
if ! uci show firewall | grep -q "zone.*guest"; then
    uci add firewall zone
    uci set firewall.@zone[-1].name='guest'
    uci set firewall.@zone[-1].input='REJECT'
    uci set firewall.@zone[-1].output='ACCEPT'
    uci set firewall.@zone[-1].forward='REJECT'
    uci add_list firewall.@zone[-1].network='guest'
fi

# Allow guest to access WAN
if ! uci show firewall | grep -q "forwarding.*guest.*wan"; then
    uci add firewall forwarding
    uci set firewall.@forwarding[-1].src='guest'
    uci set firewall.@forwarding[-1].dest='wan'
fi

# Block guest -> LAN access (IoT isolation)
uci add firewall rule
uci set firewall.@rule[-1].name='Block-Guest-to-LAN'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].target='REJECT'
uci set firewall.@rule[-1].enabled='1'

# Allow LAN -> Guest for management
if ! uci show firewall | grep -q "forwarding.*lan.*guest"; then
    uci add firewall forwarding
    uci set firewall.@forwarding[-1].src='lan'
    uci set firewall.@forwarding[-1].dest='guest'
fi

# Allow DHCP and DNS from guest to router
uci add firewall rule
uci set firewall.@rule[-1].name='Allow-Guest-DHCP'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].proto='udp'
uci set firewall.@rule[-1].dest_port='67 68'
uci set firewall.@rule[-1].target='ACCEPT'

uci add firewall rule
uci set firewall.@rule[-1].name='Allow-Guest-DNS'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].proto='udp'
uci set firewall.@rule[-1].dest_port='53'
uci set firewall.@rule[-1].target='ACCEPT'

uci commit firewall

echo "[Phase 3] Firewall and segmentation configured"
EOF_FW

echo "[✓] Phase 3 complete: Network segmentation configured"
echo ""

# ============================================
# PHASE 4: System Optimization
# ============================================

cat << 'EOF_SYS' | ssh root@$ROUTER_IP "cat > /tmp/system_config.sh && chmod +x /tmp/system_config.sh && /tmp/system_config.sh"
#!/bin/sh
echo "[Phase 4] Applying system optimizations..."

# Disable IPv6 if not needed (reduces overhead)
uci set network.wan6.disabled='1'
uci set network.lan.ip6assign=''

# Optimize network settings
uci set network.globals.packet_steering='1'

# Commit all changes
uci commit network

echo "[Phase 4] System optimizations applied"
EOF_SYS

echo "[✓] Phase 4 complete: System optimized"
echo ""

# ============================================
# PHASE 5: Apply Configuration
# ============================================

echo "[Phase 5] Restarting services to apply changes..."

ssh root@$ROUTER_IP << 'EOF_RESTART'
# Restart network services
/etc/init.d/network reload
sleep 5

# Restart DHCP/DNS
/etc/init.d/dnsmasq restart
sleep 2

# Restart WiFi
wifi reload
sleep 5

# Restart firewall
/etc/init.d/firewall restart
sleep 2

echo ""
echo "Configuration applied successfully!"
echo ""
EOF_RESTART

echo ""
echo "========================================="
echo "✓ Optimization Complete!"
echo "========================================="
echo ""
echo "Summary of changes:"
echo "  ✓ Static IP reservations configured"
echo "  ✓ DHCP pool reduced to .201-.250"
echo "  ✓ DNS cache increased to 5000 entries"
echo "  ✓ WiFi 5GHz: Channel 36, 23 dBm, 160MHz"
echo "  ✓ WiFi 2.4GHz: Channel 6, 20 dBm, 20MHz"
echo "  ✓ IoT network: slate-iot (WPA2)"
echo "  ✓ Guest network isolated from LAN"
echo "  ✓ IPv6 disabled for performance"
echo ""
echo "Next steps:"
echo "  1. Connect IoT devices to 'slate-iot' network"
echo "  2. Test WiFi speeds on main devices"
echo "  3. Verify IoT isolation (IoT can't reach LAN)"
echo "  4. Monitor performance and adjust if needed"
echo ""
echo "IoT Network Credentials:"
echo "  SSID: slate-iot"
echo "  Password: iot-network-2026"
echo ""
echo "To add missing device static IPs:"
echo "  ssh root@192.168.8.1"
echo "  uci add dhcp host"
echo "  uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'"
echo "  uci set dhcp.@host[-1].ip='192.168.8.XX'"
echo "  uci set dhcp.@host[-1].name='device-name'"
echo "  uci commit dhcp && /etc/init.d/dnsmasq restart"
echo ""
echo "Configuration backup recommended:"
echo "  ssh root@192.168.8.1 'sysupgrade -b /tmp/backup-optimized.tar.gz'"
echo "  scp root@192.168.8.1:/tmp/backup-optimized.tar.gz ."
echo ""

#!/bin/bash
# Proxmox Firewall Configuration for Zimaboard HomeLab
# This script configures iptables rules for:
# - Inter-bridge routing
# - IoT network isolation
# - Port forwarding
# - Traffic prioritization

set -e

echo "========================================"
echo "Proxmox Firewall Configuration Script"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (sudo)"
    exit 1
fi

# Install iptables-persistent for rule persistence
echo "[1/6] Installing iptables-persistent..."
apt-get update -qq
apt-get install -y iptables-persistent netfilter-persistent

# Flush existing rules (be careful!)
echo "[2/6] Flushing existing iptables rules..."
iptables -F
iptables -t nat -F
iptables -t mangle -F
iptables -X

# Set default policies
echo "[3/6] Setting default policies..."
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

# ============================================================================
# BASIC SECURITY RULES
# ============================================================================

echo "[4/6] Configuring basic security rules..."

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Allow SSH from management network only
iptables -A INPUT -p tcp --dport 22 -s 192.168.8.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -j DROP

# Allow Proxmox web interface from management network
iptables -A INPUT -p tcp --dport 8006 -s 192.168.8.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8006 -j DROP

# Allow ping (ICMP)
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT
iptables -A FORWARD -p icmp -j ACCEPT

# ============================================================================
# INTER-BRIDGE ROUTING RULES
# ============================================================================

echo "[5/6] Configuring inter-bridge routing..."

# Allow traffic from Management network to all networks
iptables -A FORWARD -i vmbr0 -o vmbr2 -j ACCEPT
iptables -A FORWARD -i vmbr0 -o vmbr3 -j ACCEPT
iptables -A FORWARD -i vmbr0 -o vmbr4 -j ACCEPT

# Allow traffic from Legion (vmbr2) to:
# - Management network (vmbr0) - for accessing services
# - Book network (vmbr3) - for file sharing
# - Internet (vmbr1) - for downloads
iptables -A FORWARD -i vmbr2 -o vmbr0 -j ACCEPT
iptables -A FORWARD -i vmbr2 -o vmbr3 -j ACCEPT
iptables -A FORWARD -i vmbr2 -o vmbr1 -j ACCEPT

# Allow traffic from Book (vmbr3) to:
# - Management network (vmbr0) - for accessing services
# - Legion network (vmbr2) - for file sharing
# - Internet (vmbr1) - for downloads
iptables -A FORWARD -i vmbr3 -o vmbr0 -j ACCEPT
iptables -A FORWARD -i vmbr3 -o vmbr2 -j ACCEPT
iptables -A FORWARD -i vmbr3 -o vmbr1 -j ACCEPT

# ============================================================================
# IOT NETWORK ISOLATION
# ============================================================================

# IoT devices (vmbr4) can ONLY:
# 1. Access internet (for cloud services)
# 2. Receive connections from management network (for control)
# 3. CANNOT access other internal networks (security)

echo "   - Configuring IoT isolation rules..."

# Allow IoT to internet
iptables -A FORWARD -i vmbr4 -o vmbr1 -j ACCEPT

# Allow management to IoT (for Home Assistant control)
iptables -A FORWARD -i vmbr0 -o vmbr4 -m conntrack --ctstate NEW,ESTABLISHED,RELATED -j ACCEPT

# Allow specific services from IoT to management (e.g., Sonos discovery)
# Sonos uses SSDP (UDP 1900) and various ports
iptables -A FORWARD -i vmbr4 -o vmbr0 -p udp --dport 1900 -j ACCEPT # SSDP
iptables -A FORWARD -i vmbr4 -o vmbr0 -p tcp --dport 1400:1500 -j ACCEPT # Sonos control

# BLOCK everything else from IoT network
iptables -A FORWARD -i vmbr4 -o vmbr0 -m conntrack --ctstate NEW -j DROP
iptables -A FORWARD -i vmbr4 -o vmbr2 -j DROP
iptables -A FORWARD -i vmbr4 -o vmbr3 -j DROP

# Log dropped IoT traffic (for debugging)
iptables -A FORWARD -i vmbr4 -j LOG --log-prefix "IoT-BLOCKED: " --log-level 4
iptables -A FORWARD -i vmbr4 -j DROP

# ============================================================================
# NAT RULES FOR INTERNET ACCESS
# ============================================================================

echo "   - Configuring NAT rules..."

# Masquerade outbound traffic from all internal networks
iptables -t nat -A POSTROUTING -s 192.168.8.0/24 -o vmbr1 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 192.168.10.0/24 -o vmbr1 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 192.168.20.0/24 -o vmbr1 -j MASQUERADE
iptables -t nat -A POSTROUTING -s 192.168.30.0/24 -o vmbr1 -j MASQUERADE

# ============================================================================
# QoS / TRAFFIC PRIORITIZATION (MANGLE TABLE)
# ============================================================================

echo "   - Configuring QoS rules..."

# Mark packets for prioritization
# Priority 1: Real-time (Deskflow, PipeWire audio)
iptables -t mangle -A FORWARD -p tcp --dport 24800 -j DSCP --set-dscp-class EF
iptables -t mangle -A FORWARD -p tcp --dport 4656 -j DSCP --set-dscp-class EF

# Priority 2: Interactive (SSH, Home Assistant)
iptables -t mangle -A FORWARD -p tcp --dport 22 -j DSCP --set-dscp-class AF41
iptables -t mangle -A FORWARD -p tcp --dport 8123 -j DSCP --set-dscp-class AF41
iptables -t mangle -A FORWARD -p tcp --dport 1883 -j DSCP --set-dscp-class AF41 # MQTT

# Priority 3: Streaming (Jellyfin)
iptables -t mangle -A FORWARD -p tcp --dport 8096 -j DSCP --set-dscp-class AF21

# Priority 4: Bulk (Torrents)
iptables -t mangle -A FORWARD -p tcp --dport 6881:6889 -j DSCP --set-dscp-class CS1

# ============================================================================
# OPTIONAL PORT FORWARDING (if needed)
# ============================================================================

# Example: Forward external port 8096 to Jellyfin
# Uncomment and modify as needed:
# iptables -t nat -A PREROUTING -i vmbr1 -p tcp --dport 8096 -j DNAT --to-destination 192.168.8.40:8096
# iptables -A FORWARD -i vmbr1 -o vmbr0 -p tcp --dport 8096 -d 192.168.8.40 -j ACCEPT

# ============================================================================
# MONITORING BRIDGE (no filtering)
# ============================================================================

# vmbr_monitor should accept all traffic for passive monitoring
iptables -A FORWARD -i vmbr_monitor -j ACCEPT
iptables -A FORWARD -o vmbr_monitor -j ACCEPT

# ============================================================================
# SAVE RULES
# ============================================================================

echo "[6/6] Saving iptables rules..."
netfilter-persistent save

echo ""
echo "========================================"
echo "Firewall configuration complete!"
echo "========================================"
echo ""
echo "Summary:"
echo "  ✓ Basic security rules configured"
echo "  ✓ Inter-bridge routing enabled"
echo "  ✓ IoT network isolated"
echo "  ✓ NAT configured for internet access"
echo "  ✓ QoS/DSCP markings applied"
echo "  ✓ Rules saved and will persist across reboots"
echo ""
echo "To view current rules:"
echo "  iptables -L -v -n"
echo "  iptables -t nat -L -v -n"
echo "  iptables -t mangle -L -v -n"
echo ""
echo "To monitor dropped IoT traffic:"
echo "  tail -f /var/log/kern.log | grep IoT-BLOCKED"
echo ""

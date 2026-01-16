#!/bin/bash
# Device Information Collection Script
# Helps identify MAC addresses for static IP assignments

ROUTER_IP="192.168.8.1"

echo "========================================="
echo "Device Information Collection"
echo "========================================="
echo ""
echo "Collecting device information from router..."
echo ""

# Current DHCP leases
echo "═══════════════════════════════════════"
echo "Current DHCP Leases:"
echo "═══════════════════════════════════════"
ssh root@$ROUTER_IP "cat /tmp/dhcp.leases" | while read line; do
    timestamp=$(echo $line | awk '{print $1}')
    mac=$(echo $line | awk '{print $2}')
    ip=$(echo $line | awk '{print $3}')
    hostname=$(echo $line | awk '{print $4}')

    # Convert timestamp to readable date
    if command -v date &> /dev/null; then
        date_readable=$(date -d "@$timestamp" 2>/dev/null || date -r $timestamp 2>/dev/null)
    else
        date_readable="$timestamp"
    fi

    echo "  $hostname"
    echo "    MAC: $mac"
    echo "    IP:  $ip"
    echo "    Lease expires: $date_readable"
    echo ""
done

# ARP table
echo "═══════════════════════════════════════"
echo "ARP Table (All Connected Devices):"
echo "═══════════════════════════════════════"
ssh root@$ROUTER_IP "cat /proc/net/arp" | tail -n +2 | while read line; do
    ip=$(echo $line | awk '{print $1}')
    mac=$(echo $line | awk '{print $4}')
    dev=$(echo $line | awk '{print $6}')

    if [ "$mac" != "00:00:00:00:00:00" ]; then
        echo "  IP: $ip"
        echo "    MAC: $mac"
        echo "    Interface: $dev"
        echo ""
    fi
done

# WiFi 2.4GHz clients
echo "═══════════════════════════════════════"
echo "WiFi 2.4GHz Clients:"
echo "═══════════════════════════════════════"
ssh root@$ROUTER_IP "iw dev wlan0 station dump 2>/dev/null || echo '  No clients connected'" | grep -E "^Station|signal avg|rx bitrate|tx bitrate|connected time" | while read line; do
    echo "  $line"
done
echo ""

# WiFi 5GHz clients
echo "═══════════════════════════════════════"
echo "WiFi 5GHz Clients:"
echo "═══════════════════════════════════════"
ssh root@$ROUTER_IP "iw dev wlan1 station dump 2>/dev/null || echo '  No clients connected'" | grep -E "^Station|signal avg|rx bitrate|tx bitrate|connected time" | while read line; do
    echo "  $line"
done
echo ""

# Current static assignments
echo "═══════════════════════════════════════"
echo "Current Static IP Assignments:"
echo "═══════════════════════════════════════"
ssh root@$ROUTER_IP "uci show dhcp | grep '@host'" | while read line; do
    echo "  $line"
done
echo ""

echo "═══════════════════════════════════════"
echo "Device Mapping Checklist:"
echo "═══════════════════════════════════════"
echo ""
echo "Please identify these devices from above:"
echo ""
echo "  [ ] Zimaboard (wired) → 192.168.8.21"
echo "      MAC: _________________"
echo ""
echo "  [ ] MacBook Pro M3 (Trendnet 2.5GB wired adapter) → 192.168.8.22"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-01 → 192.168.8.151"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-02 → 192.168.8.152"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-03 → 192.168.8.153"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-04 → 192.168.8.154"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-05 → 192.168.8.155"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-06 → 192.168.8.156"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-07 → 192.168.8.157"
echo "      MAC: _________________"
echo ""
echo "  [ ] ESP32-08 → 192.168.8.158"
echo "      MAC: _________________"
echo ""
echo "  [ ] Renology → 192.168.8.160"
echo "      MAC: _________________"
echo ""
echo "═══════════════════════════════════════"
echo ""
echo "To add a device with static IP:"
echo ""
echo "  ssh root@192.168.8.1"
echo "  uci add dhcp host"
echo "  uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'"
echo "  uci set dhcp.@host[-1].ip='192.168.8.XX'"
echo "  uci set dhcp.@host[-1].name='device-name'"
echo "  uci commit dhcp"
echo "  /etc/init.d/dnsmasq restart"
echo ""
echo "Save this output for reference!"
echo "========================================="

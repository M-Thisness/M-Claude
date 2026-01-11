# GL-BE3600 Custom Display Information Guide

**Display Specs:** 284×76 pixels, 16-bit color, OLED-style touchscreen

---

## Understanding the Display System

### Architecture

```
┌─────────────────────────────────────┐
│  gl_screen (LVGL-based binary)      │
│  - Renders screens                  │
│  - Handles touch input              │
│  - Subscribes to ubus events        │
└─────────────────────────────────────┘
           ↕ (ubus)
┌─────────────────────────────────────┐
│  System Data Sources                │
│  - network.interface.*              │
│  - system (board, info, etc.)       │
│  - gl-clients (connected devices)   │
│  - Custom scripts                   │
└─────────────────────────────────────┘
```

### Current Display Modes

1. **"overview"** - Network overview (default)
2. **"network_status"** - Connection details
3. **"world_clock"** - Clock display
4. **"vpn_dashboard"** - VPN status

---

## Methods to Add Custom Information

### Method 1: Create Custom Text Overlay (Simplest)

Create a script that displays custom text on the framebuffer.

**Create overlay script:**

```bash
cat > /etc/gl_screen/custom_overlay.sh << 'EOF'
#!/bin/sh

# Get system information
UPTIME=$(uptime | awk '{print $3}' | sed 's/,//')
LOAD=$(uptime | awk '{print $(NF-2), $(NF-1), $NF}')
MEM_USED=$(free | awk '/Mem:/ {printf "%.1fMB", $3/1024}')
WAN_IP=$(ubus call network.interface.wan status | jsonfilter -e '@["ipv4-address"][0].address')
VPN_STATUS=$(wg show 2>/dev/null | grep -q "interface" && echo "ON" || echo "OFF")
CLIENTS=$(iw dev wlan1 station dump 2>/dev/null | grep "Station" | wc -l)
BLOCKY_STATUS=$(ps | grep -q '[b]locky' && echo "Active" || echo "Inactive")

# Output to file that can be displayed
cat > /tmp/custom_screen_data.txt << EOD
Uptime: $UPTIME
Load: $LOAD
Memory: $MEM_USED
WAN IP: $WAN_IP
VPN: $VPN_STATUS
WiFi Clients: $CLIENTS
Blocky: $BLOCKY_STATUS
EOD
EOF

chmod +x /etc/gl_screen/custom_overlay.sh
```

**Run periodically:**

```bash
# Add to crontab to update every minute
echo "* * * * * /etc/gl_screen/custom_overlay.sh" >> /etc/crontabs/root
/etc/init.d/cron restart
```

---

### Method 2: Custom Data via UBUS (Advanced)

Create a ubus service that provides custom data to the display.

**Create custom ubus service:**

```bash
cat > /usr/libexec/rpcd/custom-display << 'EOF'
#!/bin/sh

case "$1" in
    list)
        echo '{ "get_info": {} }'
        ;;
    call)
        case "$2" in
            get_info)
                # Gather custom information
                UPTIME=$(uptime | awk '{print $3}' | sed 's/,//')
                TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{print $1/1000"°C"}')
                WAN_IP=$(ubus call network.interface.wan status | jsonfilter -e '@["ipv4-address"][0].address')
                VPN=$(wg show 2>/dev/null | grep -q "interface" && echo "Connected" || echo "Disconnected")

                # Return JSON
                echo "{
                    \"uptime\": \"$UPTIME\",
                    \"temperature\": \"$TEMP\",
                    \"wan_ip\": \"$WAN_IP\",
                    \"vpn_status\": \"$VPN\"
                }"
                ;;
        esac
        ;;
esac
EOF

chmod +x /usr/libexec/rpcd/custom-display
/etc/init.d/rpcd restart
```

**Test it:**

```bash
ubus call custom-display get_info
```

---

### Method 3: Modify Event Handler (Custom Logic)

Add custom logic to the screen event handler.

**Edit event handler:**

```bash
# Backup original
cp /etc/gl_screen/scripts/gl_screen_event.lua /etc/gl_screen/scripts/gl_screen_event.lua.backup

# Add custom function to the event handler
cat >> /etc/gl_screen/scripts/gl_screen_event.lua << 'EOF'

-- Custom function to log custom data
function custom_display_update()
    local handle = io.popen("cat /tmp/custom_screen_data.txt")
    local data = handle:read("*a")
    handle:close()

    -- Log to syslog so you can see it
    os.execute("logger -t custom_screen 'Display updated: " .. data .. "'")
end

-- Call custom function
custom_display_update()
EOF
```

---

### Method 4: Direct Framebuffer Text (Most Control)

Write directly to the framebuffer for complete custom display.

**Install framebuffer tools:**

```bash
opkg update
opkg install fbset fbcat
```

**Create custom framebuffer display:**

```bash
cat > /usr/bin/custom_screen_display << 'EOF'
#!/bin/sh

# Simple text-based display to framebuffer
# This creates a status screen overlay

FB_DEVICE="/dev/fb0"

# Get data
HOSTNAME=$(uci get system.@system[0].hostname)
UPTIME=$(uptime | awk '{print $3}' | sed 's/,//')
WAN_IP=$(ubus call network.interface.wan status | jsonfilter -e '@["ipv4-address"][0].address')
CLIENTS=$(iw dev wlan1 station dump 2>/dev/null | grep "Station" | wc -l)
VPN=$(wg show 2>/dev/null | grep -q "interface" && echo "VPN: ON" || echo "VPN: OFF")
BLOCKY=$(ps | grep -q '[b]locky' && echo "Blocky: ✓" || echo "Blocky: ✗")

# Display using fbv or similar tool
# Note: This is a placeholder - actual implementation depends on available tools
echo "=== $HOSTNAME ==="
echo "Uptime: $UPTIME"
echo "WAN: $WAN_IP"
echo "Clients: $CLIENTS"
echo "$VPN | $BLOCKY"
EOF

chmod +x /usr/bin/custom_screen_display
```

---

## Practical Examples

### Example 1: Network Stats Display

**Show real-time network statistics:**

```bash
cat > /etc/gl_screen/scripts/network_stats.sh << 'EOF'
#!/bin/sh

# Get interface statistics
RX_BYTES=$(cat /sys/class/net/eth0/statistics/rx_bytes)
TX_BYTES=$(cat /sys/class/net/eth0/statistics/tx_bytes)

# Convert to MB
RX_MB=$(echo "$RX_BYTES / 1048576" | bc)
TX_MB=$(echo "$TX_BYTES / 1048576" | bc)

# Connected clients
WLAN_CLIENTS=$(iw dev wlan1 station dump 2>/dev/null | grep "Station" | wc -l)

# Output
cat > /tmp/network_stats.txt << EOD
Network Statistics
==================
WAN RX: ${RX_MB} MB
WAN TX: ${TX_MB} MB
WiFi Clients: ${WLAN_CLIENTS}
EOD

logger -t network_stats "RX: ${RX_MB}MB TX: ${TX_MB}MB Clients: ${WLAN_CLIENTS}"
EOF

chmod +x /etc/gl_screen/scripts/network_stats.sh
```

**Add to cron:**

```bash
echo "*/5 * * * * /etc/gl_screen/scripts/network_stats.sh" >> /etc/crontabs/root
/etc/init.d/cron restart
```

---

### Example 2: System Health Monitor

**Monitor CPU, memory, temperature:**

```bash
cat > /etc/gl_screen/scripts/system_health.sh << 'EOF'
#!/bin/sh

# CPU Load
LOAD_1MIN=$(uptime | awk '{print $(NF-2)}' | sed 's/,//')

# Memory
MEM_TOTAL=$(free | awk '/Mem:/ {print $2}')
MEM_USED=$(free | awk '/Mem:/ {print $3}')
MEM_PERCENT=$(echo "scale=1; $MEM_USED * 100 / $MEM_TOTAL" | bc)

# Temperature
TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{printf "%.1f", $1/1000}')

# Storage
STORAGE_USED=$(df / | awk 'NR==2 {print $5}')

# Output
cat > /tmp/system_health.txt << EOD
System Health
=============
Load: ${LOAD_1MIN}
Memory: ${MEM_PERCENT}%
Temp: ${TEMP}°C
Storage: ${STORAGE_USED}
EOD

logger -t system_health "Load: ${LOAD_1MIN} Mem: ${MEM_PERCENT}% Temp: ${TEMP}°C"
EOF

chmod +x /etc/gl_screen/scripts/system_health.sh
```

---

### Example 3: VPN & Security Status

**Show VPN, Firewall, DNS filtering status:**

```bash
cat > /etc/gl_screen/scripts/security_status.sh << 'EOF'
#!/bin/sh

# VPN Status (Mullvad WireGuard)
if wg show 2>/dev/null | grep -q "interface"; then
    VPN_STATUS="✓ Connected"
    VPN_IP=$(wg show wgclient1 2>/dev/null | grep endpoint | awk '{print $2}')
else
    VPN_STATUS="✗ Disconnected"
    VPN_IP="N/A"
fi

# Blocky DNS Status
if ps | grep -q '[b]locky'; then
    BLOCKY_STATUS="✓ Active"
else
    BLOCKY_STATUS="✗ Inactive"
fi

# Firewall Status
if nft list ruleset 2>/dev/null | grep -q "chain forward"; then
    FW_STATUS="✓ Active"
else
    FW_STATUS="✗ Inactive"
fi

# Output
cat > /tmp/security_status.txt << EOD
Security Status
===============
VPN: ${VPN_STATUS}
Blocky DNS: ${BLOCKY_STATUS}
Firewall: ${FW_STATUS}
EOD

logger -t security "VPN: ${VPN_STATUS} Blocky: ${BLOCKY_STATUS} FW: ${FW_STATUS}"
EOF

chmod +x /etc/gl_screen/scripts/security_status.sh
```

---

### Example 4: Connected Devices List

**Show currently connected devices:**

```bash
cat > /etc/gl_screen/scripts/device_list.sh << 'EOF'
#!/bin/sh

# Get connected devices
DEVICES=$(cat /tmp/dhcp.leases | awk '{print $4}' | sort | head -10)

# Count
TOTAL=$(cat /tmp/dhcp.leases | wc -l)

# Output
cat > /tmp/device_list.txt << EOD
Connected Devices (${TOTAL})
========================
${DEVICES}
EOD

logger -t devices "Total connected: ${TOTAL}"
EOF

chmod +x /etc/gl_screen/scripts/device_list.sh
```

---

## Custom Data Display Dashboard

**Combine all monitoring scripts:**

```bash
cat > /etc/gl_screen/scripts/custom_dashboard.sh << 'EOF'
#!/bin/sh

# Run all monitoring scripts
/etc/gl_screen/scripts/network_stats.sh
/etc/gl_screen/scripts/system_health.sh
/etc/gl_screen/scripts/security_status.sh
/etc/gl_screen/scripts/device_list.sh

# Combine into dashboard
cat > /tmp/custom_dashboard.txt << 'EOD'
╔════════════════════════════════╗
║    GL-BE3600 Dashboard         ║
╚════════════════════════════════╝
EOD

cat /tmp/network_stats.txt >> /tmp/custom_dashboard.txt
echo "" >> /tmp/custom_dashboard.txt
cat /tmp/system_health.txt >> /tmp/custom_dashboard.txt
echo "" >> /tmp/custom_dashboard.txt
cat /tmp/security_status.txt >> /tmp/custom_dashboard.txt

# Log summary
logger -t dashboard "Dashboard updated"
EOF

chmod +x /etc/gl_screen/scripts/custom_dashboard.sh
```

**Schedule dashboard update:**

```bash
# Every minute
echo "* * * * * /etc/gl_screen/scripts/custom_dashboard.sh" >> /etc/crontabs/root
/etc/init.d/cron restart
```

**View dashboard:**

```bash
cat /tmp/custom_dashboard.txt
```

---

## Viewing Custom Data

### Option 1: SSH and View

```bash
ssh root@192.168.8.1
cat /tmp/custom_dashboard.txt
```

### Option 2: Web Interface (Create Page)

```bash
# Create custom HTML page
cat > /www/custom_display.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Custom Display</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: monospace; background: #000; color: #0f0; padding: 20px; }
        pre { font-size: 14px; }
    </style>
</head>
<body>
    <h1>Router Status</h1>
    <pre id="status"></pre>
    <script>
        fetch('/cgi-bin/custom_status.sh')
            .then(r => r.text())
            .then(t => document.getElementById('status').textContent = t);
    </script>
</body>
</html>
EOF
```

**Create CGI script:**

```bash
cat > /www/cgi-bin/custom_status.sh << 'EOF'
#!/bin/sh
echo "Content-type: text/plain"
echo ""
cat /tmp/custom_dashboard.txt
EOF

chmod +x /www/cgi-bin/custom_status.sh
```

**Access:** http://192.168.8.1/custom_display.html

---

### Option 3: Mobile App / API

**Create JSON API endpoint:**

```bash
cat > /www/cgi-bin/status_api.sh << 'EOF'
#!/bin/sh
echo "Content-type: application/json"
echo ""

# Get all stats
UPTIME=$(uptime | awk '{print $3}' | sed 's/,//')
WAN_IP=$(ubus call network.interface.wan status | jsonfilter -e '@["ipv4-address"][0].address')
VPN=$(wg show 2>/dev/null | grep -q "interface" && echo "connected" || echo "disconnected")
CLIENTS=$(iw dev wlan1 station dump 2>/dev/null | grep "Station" | wc -l)

# Output JSON
cat << EOJ
{
  "uptime": "$UPTIME",
  "wan_ip": "$WAN_IP",
  "vpn_status": "$VPN",
  "wifi_clients": $CLIENTS,
  "timestamp": "$(date -Iseconds)"
}
EOJ
EOF

chmod +x /www/cgi-bin/status_api.sh
```

**Access:** http://192.168.8.1/cgi-bin/status_api.sh

---

## Information You Can Display

### Available Data Sources

1. **Network:**
   - WAN IP, subnet, gateway
   - WiFi clients (count, MACs, signal strength)
   - Traffic stats (RX/TX bytes)
   - Connected device list

2. **System:**
   - CPU load
   - Memory usage
   - Storage usage
   - Temperature
   - Uptime

3. **Security:**
   - VPN status (Mullvad)
   - Blocky DNS status
   - Firewall rules
   - Active connections

4. **Services:**
   - Blocky (running/stopped)
   - dnsmasq status
   - OpenVPN status
   - WireGuard peers

5. **Custom:**
   - Internet speed test results
   - External IP
   - ISP information
   - Custom alerts

---

## Automation & Alerts

### Example: Alert on VPN Disconnect

```bash
cat > /etc/gl_screen/scripts/vpn_monitor.sh << 'EOF'
#!/bin/sh

if ! wg show 2>/dev/null | grep -q "interface"; then
    # VPN is down - send alert
    logger -p user.alert -t vpn "VPN DISCONNECTED!"

    # Could also:
    # - Send email
    # - Trigger LED
    # - Block internet traffic
fi
EOF

chmod +x /etc/gl_screen/scripts/vpn_monitor.sh
echo "*/5 * * * * /etc/gl_screen/scripts/vpn_monitor.sh" >> /etc/crontabs/root
```

---

## Next Steps

1. **Choose which information to display:**
   - System stats?
   - Network info?
   - Security status?
   - Connected devices?

2. **Select display method:**
   - Text files (simplest)
   - UBUS service (integrated)
   - Web interface (accessible)
   - API endpoint (mobile app)

3. **Set up automation:**
   - Cron jobs for updates
   - Event-driven updates
   - Real-time monitoring

Would you like me to create a specific custom display script for your needs?

**What information would you like to show?**
- Blocky statistics (queries, blocks)?
- VPN connection details?
- Connected device names?
- Network speed?
- System temperature/load?
- Custom alerts?

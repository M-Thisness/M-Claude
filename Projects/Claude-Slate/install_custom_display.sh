#!/bin/bash
# Custom Display Information Installation Script
# Adds custom monitoring and information to GL-BE3600

ROUTER_IP="192.168.8.1"

echo "========================================="
echo "Custom Display Information Installer"
echo "========================================="
echo ""
echo "This will install custom monitoring scripts that show:"
echo "  • Network statistics"
echo "  • System health (CPU, memory, temp)"
echo "  • VPN & Blocky status"
echo "  • Connected devices"
echo "  • Custom dashboard"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Installing custom display scripts..."
echo ""

# =============================================
# Create monitoring scripts on router
# =============================================

ssh root@$ROUTER_IP << 'EOFSSH'

# Create scripts directory if it doesn't exist
mkdir -p /etc/gl_screen/scripts

echo "[1/6] Creating network stats script..."
cat > /etc/gl_screen/scripts/network_stats.sh << 'EOF'
#!/bin/sh
# Network Statistics Monitor

# Get interface statistics
RX_BYTES=$(cat /sys/class/net/eth0/statistics/rx_bytes 2>/dev/null || echo 0)
TX_BYTES=$(cat /sys/class/net/eth0/statistics/tx_bytes 2>/dev/null || echo 0)

# Convert to MB
RX_MB=$(awk "BEGIN {printf \"%.1f\", $RX_BYTES / 1048576}")
TX_MB=$(awk "BEGIN {printf \"%.1f\", $TX_BYTES / 1048576}")

# Connected clients
WLAN5_CLIENTS=$(iw dev wlan1 station dump 2>/dev/null | grep "Station" | wc -l)
WLAN2_CLIENTS=$(iw dev wlan0 station dump 2>/dev/null | grep "Station" | wc -l)
TOTAL_CLIENTS=$((WLAN5_CLIENTS + WLAN2_CLIENTS))

# WAN IP
WAN_IP=$(ubus call network.interface.wan status 2>/dev/null | jsonfilter -e '@["ipv4-address"][0].address' 2>/dev/null || echo "N/A")

# Output
cat > /tmp/network_stats.txt << EOD
Network Statistics
==================
WAN IP: ${WAN_IP}
Download: ${RX_MB} MB
Upload: ${TX_MB} MB
WiFi 5GHz: ${WLAN5_CLIENTS} clients
WiFi 2.4GHz: ${WLAN2_CLIENTS} clients
Total: ${TOTAL_CLIENTS} clients
EOD
EOF
chmod +x /etc/gl_screen/scripts/network_stats.sh

echo "[2/6] Creating system health script..."
cat > /etc/gl_screen/scripts/system_health.sh << 'EOF'
#!/bin/sh
# System Health Monitor

# CPU Load
LOAD=$(uptime | awk '{print $(NF-2)}' | sed 's/,//')

# Memory
MEM_TOTAL=$(free | awk '/Mem:/ {print $2}')
MEM_USED=$(free | awk '/Mem:/ {print $3}')
MEM_PERCENT=$(awk "BEGIN {printf \"%.0f\", $MEM_USED * 100 / $MEM_TOTAL}")

# Temperature (if available)
if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
    TEMP=$(awk '{printf "%.1f", $1/1000}' /sys/class/thermal/thermal_zone0/temp)
else
    TEMP="N/A"
fi

# Storage
STORAGE_PERCENT=$(df / | awk 'NR==2 {print $5}')

# Uptime
UPTIME=$(uptime | awk '{print $3}' | sed 's/,//')

# Output
cat > /tmp/system_health.txt << EOD
System Health
=============
Uptime: ${UPTIME}
Load: ${LOAD}
Memory: ${MEM_PERCENT}%
Temp: ${TEMP}°C
Storage: ${STORAGE_PERCENT}
EOD
EOF
chmod +x /etc/gl_screen/scripts/system_health.sh

echo "[3/6] Creating security status script..."
cat > /etc/gl_screen/scripts/security_status.sh << 'EOF'
#!/bin/sh
# Security & VPN Status Monitor

# VPN Status (Mullvad WireGuard)
if wg show 2>/dev/null | grep -q "interface"; then
    VPN_STATUS="✓ Connected"
    VPN_RX=$(wg show wgclient1 2>/dev/null | grep "transfer:" | awk '{print $2}')
    VPN_TX=$(wg show wgclient1 2>/dev/null | grep "transfer:" | awk '{print $3}')
else
    VPN_STATUS="✗ Disconnected"
    VPN_RX="0"
    VPN_TX="0"
fi

# Blocky DNS Status
if ps w | grep -q '[/]usr/bin/blocky'; then
    BLOCKY_STATUS="✓ Running"
else
    BLOCKY_STATUS="✗ Stopped"
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
Blocky: ${BLOCKY_STATUS}
Firewall: ${FW_STATUS}
EOD
EOF
chmod +x /etc/gl_screen/scripts/security_status.sh

echo "[4/6] Creating device list script..."
cat > /etc/gl_screen/scripts/device_list.sh << 'EOF'
#!/bin/sh
# Connected Devices List

# Get connected devices from DHCP leases
TOTAL=$(cat /tmp/dhcp.leases 2>/dev/null | wc -l)

# Get top 5 devices
DEVICES=$(cat /tmp/dhcp.leases 2>/dev/null | awk '{printf "  • %s (%s)\n", $4, $3}' | head -5)

# Output
cat > /tmp/device_list.txt << EOD
Connected Devices
=================
Total: ${TOTAL}

${DEVICES}
EOD
EOF
chmod +x /etc/gl_screen/scripts/device_list.sh

echo "[5/6] Creating custom dashboard script..."
cat > /etc/gl_screen/scripts/custom_dashboard.sh << 'EOF'
#!/bin/sh
# Custom Dashboard - Combines all monitoring

# Run all monitoring scripts
/etc/gl_screen/scripts/network_stats.sh
/etc/gl_screen/scripts/system_health.sh
/etc/gl_screen/scripts/security_status.sh
/etc/gl_screen/scripts/device_list.sh

# Combine into dashboard
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

cat > /tmp/custom_dashboard.txt << EOD
╔════════════════════════════════════════╗
║   GL-BE3600 Status Dashboard           ║
║   ${TIMESTAMP}     ║
╚════════════════════════════════════════╝

EOD

cat /tmp/network_stats.txt >> /tmp/custom_dashboard.txt
echo "" >> /tmp/custom_dashboard.txt
cat /tmp/system_health.txt >> /tmp/custom_dashboard.txt
echo "" >> /tmp/custom_dashboard.txt
cat /tmp/security_status.txt >> /tmp/custom_dashboard.txt
echo "" >> /tmp/custom_dashboard.txt
cat /tmp/device_list.txt >> /tmp/custom_dashboard.txt

# Log update
logger -t custom_dashboard "Dashboard updated at ${TIMESTAMP}"
EOF
chmod +x /etc/gl_screen/scripts/custom_dashboard.sh

echo "[6/6] Creating web interface..."
# Create custom HTML page for viewing dashboard
cat > /www/dashboard.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>GL-BE3600 Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #00ff00;
            text-align: center;
            border-bottom: 2px solid #00ff00;
            padding-bottom: 10px;
        }
        pre {
            background: #000;
            padding: 20px;
            border: 1px solid #00ff00;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
        }
        .refresh-btn {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .refresh-btn:hover {
            background: #00cc00;
        }
        .auto-refresh {
            text-align: center;
            margin: 10px 0;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ Router Status Dashboard</h1>
        <div class="auto-refresh">Auto-refreshes every 10 seconds</div>
        <button class="refresh-btn" onclick="loadDashboard()">🔄 Refresh Now</button>
        <pre id="dashboard">Loading...</pre>
    </div>
    <script>
        function loadDashboard() {
            fetch('/cgi-bin/dashboard_data')
                .then(r => r.text())
                .then(t => {
                    document.getElementById('dashboard').textContent = t;
                })
                .catch(e => {
                    document.getElementById('dashboard').textContent = 'Error loading dashboard: ' + e;
                });
        }

        // Load on page load
        loadDashboard();

        // Auto-refresh every 10 seconds
        setInterval(loadDashboard, 10000);
    </script>
</body>
</html>
EOF

# Create CGI script to serve dashboard data
cat > /www/cgi-bin/dashboard_data << 'EOF'
#!/bin/sh
echo "Content-type: text/plain"
echo "Cache-Control: no-cache"
echo ""

# Run dashboard update
/etc/gl_screen/scripts/custom_dashboard.sh

# Output dashboard
cat /tmp/custom_dashboard.txt
EOF
chmod +x /www/cgi-bin/dashboard_data

echo ""
echo "Setting up cron job for automatic updates..."
# Add cron job to update every minute
CRON_LINE="* * * * * /etc/gl_screen/scripts/custom_dashboard.sh"
if ! grep -q "custom_dashboard.sh" /etc/crontabs/root 2>/dev/null; then
    echo "$CRON_LINE" >> /etc/crontabs/root
    /etc/init.d/cron restart
    echo "✓ Cron job added"
else
    echo "✓ Cron job already exists"
fi

echo ""
echo "Running initial dashboard update..."
/etc/gl_screen/scripts/custom_dashboard.sh

echo ""
echo "========================================="
echo "✓ Installation Complete!"
echo "========================================="
echo ""
echo "Custom monitoring is now active."
echo ""
echo "View dashboard:"
echo "  • SSH: cat /tmp/custom_dashboard.txt"
echo "  • Web: http://192.168.8.1/dashboard.html"
echo "  • Mobile: http://192.168.8.1/dashboard.html"
echo ""
echo "Monitoring scripts installed:"
echo "  • Network statistics"
echo "  • System health monitor"
echo "  • Security status (VPN, Blocky, Firewall)"
echo "  • Connected devices list"
echo ""
echo "Updates every: 1 minute (automatic)"
echo ""
EOFSSH

echo ""
echo "Testing installation..."
echo ""

# Show the dashboard
echo "Current Dashboard:"
echo "=================="
ssh root@$ROUTER_IP "cat /tmp/custom_dashboard.txt"

echo ""
echo "========================================="
echo "Installation successful!"
echo "========================================="
echo ""
echo "Access your dashboard at:"
echo "  http://192.168.8.1/dashboard.html"
echo ""
echo "Or via SSH:"
echo "  ssh root@192.168.8.1 'cat /tmp/custom_dashboard.txt'"
echo ""

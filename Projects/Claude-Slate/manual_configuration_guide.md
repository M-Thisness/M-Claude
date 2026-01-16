# GL-BE3600 Manual Configuration Guide

This guide provides step-by-step instructions for manually configuring the router optimizations through the web interface or SSH.

---

## Pre-Configuration Checklist

### 1. Backup Current Configuration
```bash
ssh root@192.168.8.1 "sysupgrade -b /tmp/backup-before-optimization.tar.gz"
scp root@192.168.8.1:/tmp/backup-before-optimization.tar.gz ~/M-Claude/Claude-Slate/
```

### 2. Collect Missing MAC Addresses

You need MAC addresses for:
- **Zimaboard** (wired interface)
- **MacBook Pro M3** (wired - Trendnet 2.5GB adapter)
- **ESP32 devices** (8 devices)
- **Renology** device

**To find MAC addresses:**

```bash
# View current DHCP leases
ssh root@192.168.8.1 "cat /tmp/dhcp.leases"

# View ARP table
ssh root@192.168.8.1 "cat /proc/net/arp"

# View WiFi clients
ssh root@192.168.8.1 "iw dev wlan0 station dump && iw dev wlan1 station dump"
```

---

## Configuration Method 1: Automated Script

### Run the Optimization Script

```bash
cd ~/M-Claude/Claude-Slate/
./router_optimization_script.sh
```

The script will:
1. Configure static IP reservations
2. Optimize WiFi settings
3. Set up IoT network isolation
4. Apply performance optimizations

**Estimated time:** 2-3 minutes

---

## Configuration Method 2: Web Interface (Manual)

### Access Router Web Interface

1. Open browser: http://192.168.8.1
2. Login with admin credentials
3. Navigate to sections below

---

### A. Configure Static IP Reservations

**Path:** Network → DHCP Server → Static Leases

**Known Devices:**

| Hostname | MAC Address | IP Address |
|----------|-------------|------------|
| pixel | 1A:91:39:0E:6F:09 | 192.168.8.51 |
| macbook-wifi | 16:63:EA:84:8B:C6 | 192.168.8.52 |
| legion-wifi | 90:10:57:D2:AE:E2 | 192.168.8.53 |
| legion-wired | C8:53:09:F6:33:09 | 192.168.8.23 |

**To Add:**
1. Click "Add" button
2. Enter MAC address
3. Enter desired IP
4. Enter hostname
5. Click "Save & Apply"

**Unknown Devices (to be added later):**
- Zimaboard → 192.168.8.21
- MacBook M3 (wired) → 192.168.8.22
- ESP32-01 through ESP32-08 → 192.168.8.151-158
- Renology → 192.168.8.160

---

### B. Optimize WiFi Settings

#### 5GHz Radio (High Performance)

**Path:** Network → Wireless → wifi1 (5GHz) → Edit

Settings to change:
```
Channel: 36 (or 149 if DFS issues)
Channel Width: 160 MHz (HT160)
Transmit Power: 23 dBm
Operating Frequency: 5GHz
Country Code: US
```

**Main SSID Settings:**
```
SSID: slate
Mode: Access Point
Encryption: WPA3-SAE Mixed (or WPA2-PSK if compatibility issues)
Password: [keep current]
802.11k: Enabled
802.11v: Enabled
```

Click "Save & Apply"

---

#### 2.4GHz Radio (IoT Compatibility)

**Path:** Network → Wireless → wifi0 (2.4GHz) → Edit

Settings to change:
```
Channel: 6 (or 1 or 11 for less interference)
Channel Width: 20 MHz (HT20)
Transmit Power: 20 dBm
Operating Frequency: 2.4GHz
Country Code: US
```

Click "Save & Apply"

---

### C. Configure IoT Guest Network

**Path:** Network → Wireless → Guest Network

#### Enable Guest Network (2.4GHz)

1. Find "guest2g" interface
2. Click "Edit"

Settings:
```
Enabled: ✓ Yes
SSID: slate-iot
Network: guest
Mode: Access Point
Encryption: WPA2-PSK (NOT WPA3 - ESP32 compatibility)
Password: iot-network-2026
Hide SSID: ☐ No
Isolate Clients: ✓ Yes
```

Click "Save & Apply"

#### Enable Guest Network (5GHz) - Optional

1. Find "guest5g" interface (may need to add)
2. Click "Edit"

Settings:
```
Enabled: ✓ Yes
SSID: slate-iot
Network: guest
Mode: Access Point
Encryption: WPA2-PSK
Password: iot-network-2026
Hide SSID: ☐ No
Isolate Clients: ✓ Yes
```

Click "Save & Apply"

---

### D. Configure Guest Network Firewall (IoT Isolation)

**Path:** Network → Firewall → Zones

#### Create Guest Zone (if not exists)

1. Click "Add" to create new zone
2. Settings:
```
Name: guest
Input: REJECT
Output: ACCEPT
Forward: REJECT
Masquerading: ✓ Yes
MSS Clamping: ✓ Yes
Covered Networks: guest
```

3. Click "Save & Apply"

#### Create Forwarding Rules

**Path:** Network → Firewall → Forwarding Rules

1. **Allow Guest → WAN**
   - Click "Add"
   - Source: guest
   - Destination: wan
   - Click "Save & Apply"

2. **Allow LAN → Guest** (for management)
   - Click "Add"
   - Source: lan
   - Destination: guest
   - Click "Save & Apply"

#### Create Traffic Rules (Block Guest → LAN)

**Path:** Network → Firewall → Traffic Rules

1. Click "Add"
2. Settings:
```
Name: Block-Guest-to-LAN
Protocol: Any
Source zone: guest
Destination zone: lan
Action: REJECT
Enabled: ✓ Yes
```

3. Click "Save & Apply"

---

### E. DHCP Optimization

**Path:** Network → DHCP and DNS

#### General Settings

```
DNS Cache Size: 5000 (increase from 1000)
DNS Forwardings: 1.1.1.1, 1.0.0.1 (Cloudflare)
```

#### LAN DHCP Settings

```
Start Address: 201 (change from 100)
Address Limit: 50 (change from 150)
Lease Time: 12h
```

Click "Save & Apply"

---

### F. Network Performance Settings

**Path:** Network → Interfaces → LAN → Advanced Settings

```
IPv6 Assignment: None (disable if not using IPv6)
```

**Path:** System → Software

Install if not present:
```
sqm-scripts
luci-app-sqm
```

**Path:** Network → SQM QoS

If SQM installed:
```
Enable: ✓ Yes
Interface: eth0 (WAN)
Download Speed: 150000 kbps (adjust for your Starlink speed)
Upload Speed: 20000 kbps (adjust for your Starlink speed)
Queue Discipline: cake
Script: piece_of_cake.qos
```

---

## Configuration Method 3: SSH Commands

### Quick SSH Configuration

```bash
# Connect to router
ssh root@192.168.8.1

# === Static IPs ===
# Update DHCP pool
uci set dhcp.lan.start='201'
uci set dhcp.lan.limit='50'
uci set dhcp.@dnsmasq[0].cachesize='5000'

# Add Pixel static IP
uci add dhcp host
uci set dhcp.@host[-1].mac='1A:91:39:0E:6F:09'
uci set dhcp.@host[-1].ip='192.168.8.51'
uci set dhcp.@host[-1].name='pixel'

# === WiFi Optimization ===
# 5GHz settings
uci set wireless.wifi1.channel='36'
uci set wireless.wifi1.txpower='23'
uci set wireless.wifi1.htmode='HT160'

# 2.4GHz settings
uci set wireless.wifi0.channel='6'
uci set wireless.wifi0.txpower='20'
uci set wireless.wifi0.htmode='HT20'

# Enable and configure guest network for IoT
uci set wireless.guest2g.disabled='0'
uci set wireless.guest2g.hidden='0'
uci set wireless.guest2g.ssid='slate-iot'
uci set wireless.guest2g.encryption='psk2+ccmp'
uci set wireless.guest2g.key='iot-network-2026'
uci set wireless.guest2g.isolate='1'

# === Firewall ===
# Block guest -> LAN
uci add firewall rule
uci set firewall.@rule[-1].name='Block-Guest-to-LAN'
uci set firewall.@rule[-1].src='guest'
uci set firewall.@rule[-1].dest='lan'
uci set firewall.@rule[-1].target='REJECT'

# === Commit and Apply ===
uci commit
/etc/init.d/network reload
/etc/init.d/dnsmasq restart
wifi reload
/etc/init.d/firewall restart
```

---

## Post-Configuration Tasks

### 1. Reconnect Devices

**Main Network (slate):**
- Pixel 10 Pro XL (WiFi 5GHz)
- MacBook Pro M3 (WiFi 5GHz or wired)
- Legion Pro 7i (WiFi 5GHz or wired)
- Zimaboard (wired)

**IoT Network (slate-iot):**
- All ESP32 devices
- Renology device

**Credentials for IoT network:**
```
SSID: slate-iot
Password: iot-network-2026
```

### 2. Verify Static IPs

```bash
# Check DHCP leases
ssh root@192.168.8.1 "cat /tmp/dhcp.leases"

# Expected output should show devices with assigned static IPs
```

### 3. Test IoT Isolation

From an IoT device, try to ping a LAN device:
```bash
# This should FAIL (timeout/unreachable)
ping 192.168.8.51  # From ESP32 to Pixel
```

From a LAN device, try to ping an IoT device:
```bash
# This should SUCCEED
ping 192.168.8.151  # From Pixel to ESP32
```

### 4. WiFi Speed Test

On Pixel or MacBook:
- Run speed test (speedtest.net)
- Should see 1.5-2 Gbps on 5GHz (limited by Starlink WAN)

### 5. Monitor Performance

```bash
# View WiFi clients
ssh root@192.168.8.1 "iw dev wlan1 station dump"

# View network load
ssh root@192.168.8.1 "top"
```

---

## Adding Device MACs Later

### When Devices Connect, Add Them:

```bash
ssh root@192.168.8.1

# Check connected devices
cat /tmp/dhcp.leases
cat /proc/net/arp

# Add static IP
uci add dhcp host
uci set dhcp.@host[-1].mac='XX:XX:XX:XX:XX:XX'
uci set dhcp.@host[-1].ip='192.168.8.XX'
uci set dhcp.@host[-1].name='device-name'
uci commit dhcp
/etc/init.d/dnsmasq restart
```

### Priority-Based IP Assignments

**Critical (192.168.8.2-20):** Router, DNS
**Wired Devices (192.168.8.21-50):** Zimaboard, MacBook (wired), Legion (wired)
**WiFi High Priority (192.168.8.51-100):** Pixel, MacBook (WiFi), Legion (WiFi)
**IoT Devices (192.168.8.150-200):** ESP32s, Renology
**DHCP Pool (192.168.8.201-250):** Guests, temporary devices

---

## Troubleshooting

### WiFi Too Slow
```bash
# Check channel interference
ssh root@192.168.8.1 "iw dev wlan1 scan | grep -E 'freq|SSID|signal'"

# Try different channel if interference detected
uci set wireless.wifi1.channel='149'  # Non-DFS alternative
uci commit wireless
wifi reload
```

### IoT Devices Can't Connect
```bash
# Ensure WPA2 (not WPA3) on guest network
uci set wireless.guest2g.encryption='psk2+ccmp'
uci set wireless.guest2g.sae='0'
uci commit wireless
wifi reload
```

### Wired Devices Not Getting IP
```bash
# Check eth1 status
ssh root@192.168.8.1 "ip link show eth1"

# Should show UP, not DOWN
# If DOWN, check cable connection
```

### VPN Not Working
```bash
# Check Mullvad status
ssh root@192.168.8.1 "wg show"

# Should show active connection with handshake
```

---

## Rollback Instructions

If something goes wrong:

```bash
# Restore from backup
scp backup-before-optimization.tar.gz root@192.168.8.1:/tmp/
ssh root@192.168.8.1 "sysupgrade -r /tmp/backup-before-optimization.tar.gz"
```

Or via web interface:
1. Go to System → Backup / Flash Firmware
2. Click "Restore backup"
3. Upload backup file
4. Click "Upload Archive"

---

## Performance Expectations

### After Optimization:

**Wired (2.5GbE):**
- Throughput: Limited by Starlink WAN (typically 100-300 Mbps)
- Latency: <1ms to router, 20-40ms to internet

**WiFi 5GHz (Main):**
- Throughput: 1.5-2 Gbps to router (limited by WAN for internet)
- Range: Improved with 23 dBm TX power
- Latency: 2-5ms to router

**WiFi 2.4GHz (IoT):**
- Throughput: 50-100 Mbps (sufficient for ESP32)
- Range: Better than 5GHz
- Latency: 10-20ms (acceptable for sensors)

**Network Segmentation:**
- IoT devices isolated from main network
- Mullvad VPN with leak protection active
- Split tunneling configured (if enabled)

---

## Monitoring Commands

### Regular Checks

```bash
# View all connected devices
ssh root@192.168.8.1 "cat /tmp/dhcp.leases"

# Check WiFi clients and signal strength
ssh root@192.168.8.1 "iw dev wlan1 station dump | grep -E 'Station|signal|rx bitrate|tx bitrate'"

# Check VPN status
ssh root@192.168.8.1 "wg show wgclient1"

# Check WAN speed
ssh root@192.168.8.1 "ubus call network.interface.wan status"

# View firewall stats
ssh root@192.168.8.1 "nft list ruleset | grep counter"
```

---

## Next Steps After Configuration

1. **Test all functionality**
   - Verify internet access on all devices
   - Test VPN connection (check IP at https://mullvad.net/check)
   - Verify IoT isolation

2. **Document custom changes**
   - Note any device-specific configurations
   - Record MAC addresses as devices connect

3. **Schedule regular maintenance**
   - Weekly: Check VPN status
   - Monthly: Review firewall logs
   - Quarterly: Update firmware

4. **Create final backup**
   ```bash
   ssh root@192.168.8.1 "sysupgrade -b /tmp/backup-optimized-final.tar.gz"
   scp root@192.168.8.1:/tmp/backup-optimized-final.tar.gz ~/M-Claude/Claude-Slate/
   ```

---

**Questions or Issues?**
- Check router logs: System → System Log
- Review firewall logs: Status → Firewall
- Test DNS: `nslookup google.com`
- Test connectivity: `ping 8.8.8.8`

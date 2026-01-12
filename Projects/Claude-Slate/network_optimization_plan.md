# GL-BE3600 Network Optimization Plan

**Date:** 2026-01-10
**Network:** Starlink WAN → GL-BE3600 → Mixed wired/wireless clients

---

## Network Topology

```
[Starlink]
    ↓ WAN (eth0)
[GL-BE3600 Router]
    ├─ LAN (eth1 - 2.5GbE) → [Switch/Zimaboard]
    │   ├─ Zimaboard (Intel I225 4x2.5GB)
    │   ├─ MacBook Pro M3 Pro (Trendnet 2.5GB)
    │   └─ Lenovo Legion Pro 7i (Realtek)
    │
    ├─ WiFi 5GHz (MLO, 160MHz) - Private
    │   ├─ Pixel 10 Pro XL
    │   ├─ MacBook Pro M3
    │   └─ Legion Pro 7i
    │
    └─ WiFi 2.4GHz - IoT Network
        ├─ 8x ESP32 devices
        └─ Renology
```

---

## Static IP Assignment Plan

### Network Ranges
- **Router:** 192.168.8.1
- **Critical Infrastructure:** 192.168.8.2-20
- **Wired Devices:** 192.168.8.21-50
- **WiFi Devices (High Priority):** 192.168.8.51-100
- **IoT Devices:** 192.168.8.150-200
- **DHCP Pool:** 192.168.8.201-250

### Device Assignments

#### Critical Infrastructure
| Device | IP | MAC | Notes |
|--------|-----|-----|-------|
| Router (LAN) | 192.168.8.1 | 94:83:c4:c1:c0:af | Gateway |
| DNS (Router) | 192.168.8.1 | - | Primary DNS |

#### Wired Devices (High Priority)
| Device | IP | MAC | Interface | Notes |
|--------|-----|-----|-----------|-------|
| Zimaboard | 192.168.8.21 | *TBD* | eth1 | Local server - highest priority |
| MacBook Pro M3 (wired) | 192.168.8.22 | *TBD* | eth1 | Trendnet 2.5GB adapter |
| Legion Pro 7i (wired) | 192.168.8.23 | C8:53:09:F6:33:09 | eth1 | Gaming/workstation |

#### WiFi Devices (High Priority)
| Device | IP | MAC (WiFi) | Band | Notes |
|--------|-----|-----|------|-------|
| Pixel 10 Pro XL | 192.168.8.51 | 1a:91:39:0e:6f:09 | 5GHz MLO | Primary phone |
| MacBook Pro M3 (WiFi) | 192.168.8.52 | 16:63:ea:84:8b:c6 | 5GHz MLO | Dual: wired + WiFi |
| Legion Pro 7i (WiFi) | 192.168.8.53 | 90:10:57:d2:ae:e2 | 5GHz MLO | Dual: wired + WiFi |

#### IoT Devices (Lower Priority)
| Device | IP | MAC | Band | Notes |
|--------|-----|-----|------|-------|
| ESP32-01 | 192.168.8.151 | *TBD* | 2.4GHz | IoT device |
| ESP32-02 | 192.168.8.152 | *TBD* | 2.4GHz | IoT device |
| ESP32-03 | 192.168.8.153 | *TBD* | 2.4GHz | IoT device |
| ESP32-04 | 192.168.8.154 | *TBD* | 2.4GHz | IoT device |
| ESP32-05 | 192.168.8.155 | *TBD* | 2.4GHz | IoT device |
| ESP32-06 | 192.168.8.156 | *TBD* | 2.4GHz | IoT device |
| ESP32-07 | 192.168.8.157 | *TBD* | 2.4GHz | IoT device |
| ESP32-08 | 192.168.8.158 | *TBD* | 2.4GHz | IoT device |
| Renology | 192.168.8.160 | *TBD* | 2.4GHz | Solar monitoring |

---

## WiFi Optimization

### Current Configuration Issues
1. ✗ TX Power too low (9 dBm) - limits range
2. ✗ Channels set to "auto" - can cause interference
3. ✓ MLO enabled for main network
4. ✗ Guest network disabled but should be used for IoT isolation

### Optimized WiFi Settings

#### 5GHz Radio (wifi1) - Main Network
```
Channel: 36 (DFS channels 36-48 for 160MHz)
Channel Width: HT160 (160 MHz)
TX Power: 23 dBm (maximum for better range)
Band: 5GHz
Country: US
MLO: Enabled
Encryption: WPA3-SAE (for compatible devices)
802.11k/v: Enabled (roaming optimization)
```

**Rationale:**
- Channel 36 with 160MHz provides maximum throughput for WiFi 7
- Higher TX power improves coverage for devices like Pixel and MacBooks
- WPA3 for better security on modern devices

#### 2.4GHz Radio (wifi0) - IoT Network
```
Channel: 1 or 6 or 11 (non-overlapping)
Channel Width: HT20 (20 MHz for IoT compatibility)
TX Power: 20 dBm (moderate for IoT devices)
Band: 2.4GHz
Country: US
MLO: Disabled (IoT devices don't support it)
Encryption: WPA2-PSK (ESP32 compatibility)
Use Guest Network: Yes (isolation from main network)
```

**Rationale:**
- 20MHz channel width for maximum compatibility with ESP32
- Separate guest network isolates IoT from main network
- WPA2 for ESP32 compatibility (many don't support WPA3)

---

## QoS Configuration

### Priority Classes
1. **Highest Priority** - Real-time/Interactive
   - VoIP (SIP, RTP)
   - Gaming traffic (low latency required)
   - SSH, RDP

2. **High Priority** - Wired devices
   - Zimaboard traffic (192.168.8.21)
   - MacBook/Legion wired (192.168.8.22-23)
   - DNS queries

3. **Medium Priority** - WiFi devices
   - Pixel, MacBook, Legion WiFi (192.168.8.51-53)
   - Web browsing (HTTP/HTTPS)

4. **Low Priority** - IoT & Bulk
   - ESP32 devices (192.168.8.151-158)
   - Renology (192.168.8.160)
   - Bulk downloads, BitTorrent

### QoS Rules (SQM/Cake)
```bash
# Enable SQM on WAN interface
Download: 150 Mbps (adjust for Starlink speed)
Upload: 20 Mbps (adjust for Starlink speed)
Queue Discipline: cake
Script: piece_of_cake.qos
```

---

## Network Segmentation Strategy

### Option 1: Single Network with Firewall Rules (Recommended)
- Keep all devices on 192.168.8.0/24
- Use firewall rules to isolate IoT from main network
- Simpler management, better for small network

### Option 2: Separate VLANs
- VLAN 10: Main network (192.168.8.0/24)
- VLAN 20: IoT network (192.168.20.0/24)
- Requires VLAN-aware switch or configuration

**Recommendation:** Option 1 - Use guest network (192.168.9.0/24) for IoT isolation

---

## Firewall Rules

### IoT Isolation Rules
```
1. Block IoT → LAN devices
2. Allow IoT → Router (DNS, DHCP only)
3. Allow IoT → Internet
4. Allow LAN → IoT (for management)
```

### VPN Leak Protection
- Already configured with blackhole rules
- DNS leak protection active
- Kill switch for VPN failures

---

## Performance Optimizations

### 1. Wired Network
- Ensure eth1 (2.5GbE) is enabled and active
- Connect Zimaboard first (highest priority)
- Use quality Cat6/Cat6a cables for full 2.5GbE speed
- Disable flow control if experiencing issues

### 2. WiFi Performance
- Enable **airtime fairness** to prevent slow devices from degrading network
- Enable **WMM (WiFi Multimedia)** for QoS
- Disable **legacy rate limits** (already done)
- Enable **802.11ax/be features**: OFDMA, MU-MIMO, BSS coloring

### 3. DNS Optimization
- Increase DNS cache size: 1000 → 5000 entries
- Use Cloudflare DNS (1.1.1.1) or Quad9 (9.9.9.9) for upstream
- Enable DNSSEC if supported

### 4. System Performance
- Disable IPv6 if not needed (reduces overhead)
- Enable **hardware NAT** if available
- Disable unused services (UPnP if not gaming)

---

## Mullvad WireGuard Configuration

### Current Status
- VPN client configured: wgclient1 (disabled)
- Leak protection rules: ACTIVE
- Split tunneling support: CONFIGURED

### VPN Routing Tables
- Table 1001: VPN traffic
- Table main: Non-VPN traffic (mark 0x8000/0xf000)

### Failsafe Configuration
```
1. VPN leak protection: ENABLED
2. Blackhole rules for VPN failures
3. DNS leak protection: ENABLED
4. Kill switch: ACTIVE
```

---

## Implementation Steps

### Phase 1: Static IPs & DHCP
1. Backup current configuration
2. Add static IP reservations for all known devices
3. Reduce DHCP pool to 192.168.8.201-250
4. Update DNS cache size

### Phase 2: WiFi Optimization
1. Set fixed channels (not auto)
2. Increase TX power to maximum
3. Enable WPA3 on 5GHz
4. Configure guest network for IoT
5. Move ESP32/Renology to guest network

### Phase 3: QoS & Performance
1. Install and configure SQM/Cake
2. Set bandwidth limits based on Starlink speeds
3. Configure priority rules
4. Enable hardware offloading

### Phase 4: Network Segmentation
1. Configure guest network firewall rules
2. Block IoT → LAN communication
3. Test connectivity and access

### Phase 5: Testing & Validation
1. Test wired throughput (iperf3)
2. Test WiFi speeds on each device
3. Verify IoT isolation
4. Test VPN failsafe (disconnect Mullvad)
5. Monitor for DNS leaks

---

## Expected Performance

### Wired (2.5GbE)
- Zimaboard: 2.5 Gbps (limited by Starlink WAN)
- MacBook/Legion: 2.5 Gbps (limited by Starlink WAN)
- Latency: < 1ms to router

### WiFi 5GHz (160MHz, WiFi 7 MLO)
- Theoretical max: 2.8 Gbps
- Real-world (Pixel/MacBook): 1.5-2 Gbps (limited by Starlink)
- Latency: 2-5ms to router

### WiFi 2.4GHz (20MHz, IoT)
- ESP32 max: ~50-100 Mbps
- Real-world: 20-40 Mbps (sufficient for IoT)
- Latency: 10-20ms (acceptable for sensors)

---

## Monitoring & Maintenance

### Key Metrics to Monitor
1. **WAN Speed:** Starlink bandwidth (use speedtest)
2. **WiFi Interference:** Check 2.4GHz/5GHz channel utilization
3. **VPN Status:** Ensure Mullvad is connected
4. **DNS Leaks:** Regular leak tests
5. **Device Connectivity:** Monitor disconnections

### Tools
```bash
# WiFi status
iw dev wlan1 station dump

# Bandwidth test
iperf3 -c 192.168.8.21  # Test to Zimaboard

# VPN status
wg show

# Network stats
nload eth0  # WAN traffic
```

---

## Configuration Backup

**CRITICAL:** Backup configuration before making changes

```bash
# On router
sysupgrade -b /tmp/backup-$(date +%Y%m%d).tar.gz

# Copy to local machine
scp root@192.168.8.1:/tmp/backup-*.tar.gz ~/M-Claude/gemini-slate/
```

---

## Troubleshooting

### Common Issues

**Wired devices not getting 2.5Gbps:**
- Check cable quality (Cat6/6a required)
- Verify adapter negotiation: `ethtool eth1`
- Disable flow control if issues persist

**WiFi devices slow on 5GHz:**
- Check for DFS channel interference
- Move to non-DFS channels if needed (149-165)
- Reduce channel width to 80MHz if 160MHz unstable

**IoT devices can't connect:**
- Ensure WPA2-PSK (not WPA3)
- Check 2.4GHz channel (use 1, 6, or 11)
- Disable 802.11ax on 2.4GHz if compatibility issues

**VPN not working:**
- Check Mullvad subscription status
- Verify WireGuard configuration
- Check firewall rules blocking VPN

---

## Next Steps

1. ✅ Review this plan
2. ⏳ Collect MAC addresses for missing devices
3. ⏳ Backup current configuration
4. ⏳ Implement static IP reservations
5. ⏳ Optimize WiFi settings
6. ⏳ Configure QoS
7. ⏳ Test and validate
8. ⏳ Document final configuration

---

**Estimated Implementation Time:** 1-2 hours
**Recommended Maintenance Window:** Off-peak hours
**Rollback Plan:** Restore from backup if issues occur

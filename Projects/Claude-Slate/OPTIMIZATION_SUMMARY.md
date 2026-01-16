# GL-BE3600 Optimization Summary

**Date:** 2026-01-10
**Status:** Configuration scripts created, ready to apply

---

## What Was Created

Three implementation approaches for your router optimization:

### 1. **Automated Script** (Recommended)
**File:** `router_optimization_script.sh`

**What it does:**
- ✓ Configures static IP reservations for known devices
- ✓ Optimizes WiFi settings (channels, power, bandwidth)
- ✓ Creates separate IoT network (slate-iot)
- ✓ Isolates IoT devices from main network
- ✓ Increases DNS cache for better performance
- ✓ Disables IPv6 to reduce overhead

**To run:**
```bash
cd ~/M-Claude/Claude-Slate/
./router_optimization_script.sh
```

**Time required:** 2-3 minutes

---

### 2. **Manual Configuration Guide**
**File:** `manual_configuration_guide.md`

**For those who prefer:**
- Step-by-step web interface instructions
- SSH command alternatives
- Full control over each change

---

### 3. **Device Information Collector**
**File:** `collect_device_info.sh`

**What it does:**
- Shows all connected devices and their MACs
- Displays current DHCP leases
- Lists WiFi clients and signal strengths
- Helps identify devices for static IP assignment

**To run:**
```bash
cd ~/M-Claude/Claude-Slate/
./collect_device_info.sh > device_info.txt
cat device_info.txt
```

---

## Network Design

### Topology
```
Internet (Starlink)
    ↓
WAN: eth0 (DHCP from upstream)
    ↓
[GL-BE3600 Router: 192.168.8.1]
    ├─ LAN: eth1 (2.5GbE)
    │   ├─ Zimaboard → 192.168.8.21
    │   ├─ MacBook M3 (wired) → 192.168.8.22
    │   └─ Legion Pro 7i (wired) → 192.168.8.23
    │
    ├─ WiFi: 5GHz "slate" (MLO, 160MHz, 23dBm)
    │   ├─ Pixel 10 Pro XL → 192.168.8.51
    │   ├─ MacBook M3 (WiFi) → 192.168.8.52
    │   └─ Legion Pro 7i (WiFi) → 192.168.8.53
    │
    └─ WiFi: 2.4GHz "slate-iot" (IoT Network)
        ├─ ESP32 devices → 192.168.8.151-158
        └─ Renology → 192.168.8.160
```

### Network Segmentation

**Main Network (192.168.8.0/24):**
- High-performance devices
- Full network access
- VPN protection via Mullvad (already configured)

**IoT Network (192.168.8.150-200 + Guest VLAN 192.168.9.0/24):**
- ESP32 devices, Renology
- Isolated from main network (can't access other devices)
- Internet access only
- Manageable from main network (one-way)

---

## Key Optimizations

### WiFi Performance

**5GHz Radio:**
- Channel: 36 (fixed, not auto)
- Bandwidth: 160 MHz (maximum for WiFi 7)
- TX Power: 23 dBm (increased from 9 dBm)
- Encryption: WPA3-SAE mixed
- MLO: Enabled for link aggregation

**2.4GHz Radio:**
- Channel: 6 (fixed, non-overlapping)
- Bandwidth: 20 MHz (IoT compatibility)
- TX Power: 20 dBm
- Encryption: WPA2-PSK (ESP32 compatible)

**Expected improvement:**
- Better range (+10-15 dBm)
- More stable performance (fixed channels)
- Optimized for device types (high-perf vs IoT)

### Network Performance

**DHCP:**
- Static IPs for all known devices
- Reduced DHCP pool (201-250 only)
- Increased DNS cache (1000 → 5000 entries)

**Routing:**
- IPv6 disabled (reduces overhead)
- Packet steering enabled
- Hardware NAT (if supported)

**Expected improvement:**
- Predictable IP addresses
- Faster DNS lookups
- Lower latency

### Security

**IoT Isolation:**
- Separate network for untrusted devices
- Firewall rules block IoT → LAN
- One-way access (LAN can manage IoT)

**VPN:**
- Mullvad WireGuard: Already configured
- Leak protection: Active
- Kill switch: Enabled
- Split tunneling: Configured (awaiting your device selection)

---

## IP Address Plan

| Device | Wired MAC | WiFi MAC | Static IP | Network |
|--------|-----------|----------|-----------|---------|
| **Infrastructure** |
| Router | - | - | 192.168.8.1 | LAN |
| **Wired Devices** |
| Zimaboard | *TBD* | - | 192.168.8.21 | LAN |
| MacBook M3 (wired) | *TBD* | - | 192.168.8.22 | LAN |
| Legion Pro 7i (wired) | C8:53:09:F6:33:09 | - | 192.168.8.23 | LAN |
| **WiFi Devices** |
| Pixel 10 Pro XL | - | 1a:91:39:0e:6f:09 | 192.168.8.51 | LAN |
| MacBook M3 (WiFi) | - | 16:63:ea:84:8b:c6 | 192.168.8.52 | LAN |
| Legion Pro 7i (WiFi) | - | 90:10:57:d2:ae:e2 | 192.168.8.53 | LAN |
| **IoT Devices** |
| ESP32-01 | - | *TBD* | 192.168.8.151 | Guest |
| ESP32-02 | - | *TBD* | 192.168.8.152 | Guest |
| ESP32-03 | - | *TBD* | 192.168.8.153 | Guest |
| ESP32-04 | - | *TBD* | 192.168.8.154 | Guest |
| ESP32-05 | - | *TBD* | 192.168.8.155 | Guest |
| ESP32-06 | - | *TBD* | 192.168.8.156 | Guest |
| ESP32-07 | - | *TBD* | 192.168.8.157 | Guest |
| ESP32-08 | - | *TBD* | 192.168.8.158 | Guest |
| Renology | - | *TBD* | 192.168.8.160 | Guest |
| **DHCP Pool** | - | - | 192.168.8.201-250 | LAN |

---

## Implementation Checklist

### Before You Start

- [ ] **BACKUP CURRENT CONFIG**
  ```bash
  ssh root@192.168.8.1 "sysupgrade -b /tmp/backup.tar.gz"
  scp root@192.168.8.1:/tmp/backup.tar.gz ~/M-Claude/Claude-Slate/
  ```

- [ ] **Collect Device MACs**
  ```bash
  cd ~/M-Claude/Claude-Slate/
  ./collect_device_info.sh > device_info.txt
  ```

- [ ] **Note IoT Network Credentials**
  ```
  SSID: slate-iot
  Password: iot-network-2026
  ```

### Run Optimization

Choose ONE method:

**Method 1: Automated (Recommended)**
```bash
cd ~/M-Claude/Claude-Slate/
./router_optimization_script.sh
```

**Method 2: Manual**
- Follow instructions in `manual_configuration_guide.md`

### After Optimization

- [ ] **Reconnect WiFi devices to appropriate networks:**
  - Pixel, MacBook, Legion → "slate" (main network)
  - ESP32s, Renology → "slate-iot" (IoT network)

- [ ] **Test connectivity:**
  - Main devices can access internet
  - IoT devices can access internet
  - IoT devices CANNOT ping main devices (192.168.8.51)
  - Main devices CAN ping IoT devices (192.168.8.151)

- [ ] **Verify static IPs assigned:**
  ```bash
  ssh root@192.168.8.1 "cat /tmp/dhcp.leases"
  ```

- [ ] **Test WiFi performance:**
  - Run speed test on Pixel/MacBook
  - Check signal strength in coverage areas

- [ ] **Add missing MACs:**
  - Zimaboard (when connected)
  - MacBook wired adapter
  - ESP32 devices (as they connect)

- [ ] **Create final backup:**
  ```bash
  ssh root@192.168.8.1 "sysupgrade -b /tmp/backup-optimized.tar.gz"
  scp root@192.168.8.1:/tmp/backup-optimized.tar.gz ~/M-Claude/Claude-Slate/
  ```

---

## Expected Results

### Performance

**Before optimization:**
- WiFi: Auto channels (inconsistent)
- TX Power: 9 dBm (weak signal)
- DHCP: Random IPs
- IoT: Mixed with main network

**After optimization:**
- WiFi 5GHz: Fixed channel 36, 160MHz, 23dBm
- WiFi 2.4GHz: Fixed channel 6, 20MHz for IoT
- Static IPs: Predictable addressing
- IoT: Isolated network for security

**Measurable improvements:**
- WiFi range: +50-100%
- WiFi stability: Consistent performance
- Network latency: Lower (fixed IPs, less DHCP)
- Security: IoT devices can't attack main network

### Bandwidth Expectations

**Wired (2.5GbE):**
- To router: 2.5 Gbps capable
- To internet: Limited by Starlink (~100-300 Mbps typical)

**WiFi 5GHz (WiFi 7, MLO, 160MHz):**
- To router: 1.5-2.8 Gbps
- To internet: Limited by Starlink
- Real-world: Expect 1-2 Gbps local, 100-300 Mbps internet

**WiFi 2.4GHz (IoT):**
- ESP32: 20-80 Mbps (sufficient for sensors)

---

## Troubleshooting

### Issue: WiFi too slow after optimization

**Solution:**
```bash
# Check for channel interference
ssh root@192.168.8.1 "iw dev wlan1 scan | grep -E 'freq|SSID|signal'"

# Try alternate channel if needed
ssh root@192.168.8.1
uci set wireless.wifi1.channel='149'  # Non-DFS channel
uci commit wireless && wifi reload
```

### Issue: IoT devices can't connect to slate-iot

**Solution:**
```bash
# Ensure WPA2 (ESP32 often don't support WPA3)
ssh root@192.168.8.1
uci set wireless.guest2g.encryption='psk2+ccmp'
uci set wireless.guest2g.sae='0'
uci commit wireless && wifi reload
```

### Issue: Wired devices not connecting

**Solution:**
- Check physical cable connection
- Verify Cat6/Cat6a cable (required for 2.5GbE)
- Check interface status: `ssh root@192.168.8.1 "ip link show eth1"`

### Issue: Need to rollback

**Solution:**
```bash
# Restore from backup
scp backup.tar.gz root@192.168.8.1:/tmp/
ssh root@192.168.8.1 "sysupgrade -r /tmp/backup.tar.gz"
```

---

## Next Steps

1. **Review the optimization plan** (you're reading it now!)
2. **Backup current configuration** (critical!)
3. **Run collect_device_info.sh** to identify devices
4. **Execute router_optimization_script.sh** OR follow manual guide
5. **Reconnect devices to appropriate networks**
6. **Test and verify** all functionality
7. **Add missing MACs** as devices connect
8. **Create final backup** of optimized config

---

## Files Created

All files located in: `~/M-Claude/Claude-Slate/`

1. **GL-BE3600_Technical_Specifications.md** - Hardware specs
2. **GL-BE3600_Software_Report.md** - Software/firmware details
3. **GL-BE3600_SSH_Session_Report.md** - Live system inspection
4. **network_optimization_plan.md** - Detailed optimization plan
5. **router_optimization_script.sh** - Automated configuration script ⭐
6. **manual_configuration_guide.md** - Step-by-step manual guide
7. **collect_device_info.sh** - Device MAC collection tool ⭐
8. **OPTIMIZATION_SUMMARY.md** - This summary document

---

## Questions?

**Need help with a specific step?**
- Check the manual configuration guide for detailed instructions
- Review troubleshooting section above
- Test changes incrementally (can rollback at any time)

**Want to understand what a change does?**
- Read the network_optimization_plan.md for rationale
- Each optimization has documented reasoning

**Concerned about breaking something?**
- Always backup first (included in scripts)
- Changes are reversible
- Can restore previous config in seconds

---

## Final Notes

### Mullvad VPN
- Already configured and running
- Leak protection: Active
- Split tunneling: Available (configure devices/IPs to bypass if needed)
- No changes made to VPN config

### Starlink WAN
- Connected via eth0
- DHCP from upstream (192.168.1.38)
- No changes needed

### Performance Philosophy
- **Wired devices:** Highest priority, static IPs
- **WiFi 5GHz:** High performance, modern devices
- **WiFi 2.4GHz:** IoT compatibility, isolated network
- **QoS:** Can be added later if needed (SQM/Cake)

---

**Ready to optimize? Start with the backup, then run the script!**

```bash
# Quick start:
cd ~/M-Claude/Claude-Slate/
ssh root@192.168.8.1 "sysupgrade -b /tmp/backup.tar.gz"
scp root@192.168.8.1:/tmp/backup.tar.gz .
./router_optimization_script.sh
```

Good luck! 🚀

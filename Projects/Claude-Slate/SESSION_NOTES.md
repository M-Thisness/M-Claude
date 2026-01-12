# GL-BE3600 Configuration Session - 2026-01-10

## Session Summary

Complete router analysis, optimization, and documentation for GL.iNet GL-BE3600 (Slate 7) router.

---

## Work Completed

### 1. **Router Analysis & Documentation**

Created comprehensive technical documentation:
- `GL-BE3600_Technical_Specifications.md` - Complete hardware specs
- `GL-BE3600_Software_Report.md` - All software packages, versions, developers
- `GL-BE3600_SSH_Session_Report.md` - Live system inspection results

**Key Findings:**
- Firmware: GL.iNet 4.8.1 (OpenWrt 23.05-SNAPSHOT)
- Kernel: Linux 5.4.213
- SoC: Qualcomm IPQ5312 (Quad-core @ 1.1 GHz)
- RAM: 908 MB (1 GB)
- Storage: 512 MB NAND
- 728 packages installed
- WiFi 7 with MLO actively configured

---

### 2. **Network Optimization Plan**

Created detailed optimization strategy:
- `network_optimization_plan.md` - Technical optimization plan
- `OPTIMIZATION_SUMMARY.md` - Quick reference guide
- `manual_configuration_guide.md` - Step-by-step instructions
- `router_optimization_script.sh` - Automated configuration script

**Optimizations Designed:**
- Static IP assignments for all devices
- WiFi optimization (fixed channels, increased power)
- IoT network isolation (guest network)
- Performance tuning (DNS cache, IPv6 disable)
- QoS configuration guidelines

**Network Design:**
- Main network: 192.168.8.0/24
- IoT network: "slate-iot" (isolated guest network)
- Static IPs: Wired (21-50), WiFi (51-100), IoT (150-200)
- DHCP pool: 201-250

---

### 3. **System Cleanup**

Removed unused/redundant services:

**ZeroTier Removal:**
- Status: Pre-installed but not in use
- Packages removed: zerotier, gl-sdk4-zerotier, gl-sdk4-ui-zerotierview
- Result: ~5-10 MB freed
- Log: `zerotier_removal_log.md`

**Parental Control Removal:**
- Status: Installed but disabled (using Blocky instead)
- Packages removed: gl-sdk4-ui-parentalcontrol, kmod-gl-sdk4-parental-control
- Result: ~2-5 MB freed
- Log: `parental_control_removal_log.md`

**Rationale:** User already has Blocky DNS filtering running on router

---

### 4. **Custom Display Investigation**

Explored touchscreen customization options:
- `custom_display_guide.md` - Technical guide to display customization
- `CUSTOM_DISPLAY_QUICK_START.md` - Quick reference
- `install_custom_display.sh` - Installation script (created then removed)

**Display Specs:**
- 284×76 pixels, 16-bit color, touchscreen
- LVGL-based rendering
- Modes: overview, network_status, world_clock, vpn_dashboard

**Custom monitoring system:**
- Created scripts for network stats, system health, security status
- Installed and tested web dashboard
- **User feedback:** Not desired, completely removed
- Result: System restored to original state

---

### 5. **Helper Scripts Created**

**Device Information Collector:**
- `collect_device_info.sh` - Identifies connected devices and MACs
- Purpose: Helps identify devices for static IP assignment

---

## Current Router State

### Active Services:
- ✓ Mullvad WireGuard VPN (configured, currently disconnected)
- ✓ Blocky DNS filtering (running on port 5353)
- ✓ Firewall4 (nftables)
- ✓ WiFi 5GHz + 2.4GHz (MLO enabled)
- ✓ dnsmasq (forwarding to Blocky)

### Network Configuration:
- WAN: eth0 (DHCP from Starlink at 192.168.1.38)
- LAN: br-lan (192.168.8.1/24)
- Guest: br-guest (192.168.9.1/24)
- WiFi SSID: "slate" (main), "slate guest" (disabled)

### Connected Devices (at time of session):
- legion-cachy: 192.168.8.231
- Mac: 192.168.8.158
- pixel: 192.168.8.126

### System Health:
- Uptime: 4+ hours
- Memory: ~40% used
- Temperature: 73°C (normal)
- Storage: 4% used

---

## Files Created This Session

### Documentation (8 files):
1. `GL-BE3600_Technical_Specifications.md` (6 KB)
2. `GL-BE3600_Software_Report.md` (21 KB)
3. `GL-BE3600_SSH_Session_Report.md` (14 KB)
4. `network_optimization_plan.md` (10 KB)
5. `OPTIMIZATION_SUMMARY.md` (11 KB)
6. `manual_configuration_guide.md` (12 KB)
7. `zerotier_removal_log.md` (2 KB)
8. `parental_control_removal_log.md` (5 KB)

### Scripts (3 files):
1. `router_optimization_script.sh` (10 KB) - Ready to run
2. `collect_device_info.sh` (5 KB) - Device MAC collector
3. `install_custom_display.sh` (10 KB) - Not needed, kept for reference

### Display Guides (2 files):
1. `custom_display_guide.md` (14 KB)
2. `CUSTOM_DISPLAY_QUICK_START.md` (7 KB)

### Project Files:
1. `README.md` - Project description
2. `LICENSE` - CC0 1.0 Universal Public Domain
3. `SESSION_NOTES.md` - This file

**Total:** 16 files, ~168 KB

---

## Router Capabilities Discovered

### Strengths:
- WiFi 7 with MLO fully functional
- Dual 2.5GbE ports
- Excellent VPN performance (WireGuard up to 490 Mbps)
- OpenWrt-based (highly customizable)
- Touchscreen display
- Powerful SoC (Qualcomm IPQ5312)

### Limitations:
- WiFi 7 support still maturing in OpenWrt
- Custom kernel 5.4.213 (not standard OpenWrt 23.05)
- Limited storage (512 MB NAND)
- Display customization requires C/LVGL knowledge

---

## Recommended Next Steps

### Immediate:
1. ✅ Review optimization plan
2. ⏳ Collect MAC addresses for missing devices (Zimaboard, ESP32s)
3. ⏳ Run `router_optimization_script.sh` when ready
4. ⏳ Move IoT devices to "slate-iot" network

### Future:
1. Monitor Blocky performance
2. Configure Mullvad VPN split tunneling (if needed)
3. Set up QoS/SQM for traffic prioritization
4. Regular firmware updates from GL.iNet
5. Backup optimized configuration

---

## Network Topology

```
Internet (Starlink)
    ↓
WAN: eth0 (192.168.1.38)
    ↓
[GL-BE3600: 192.168.8.1]
    ├─ LAN Bridge (192.168.8.0/24)
    │   ├─ eth1 (2.5GbE) → Wired devices
    │   ├─ WiFi 5GHz "slate" (MLO) → High-performance
    │   └─ WiFi 2.4GHz "slate"
    │
    └─ Guest Bridge (192.168.9.0/24)
        └─ WiFi 2.4GHz "slate guest" (disabled)
            → Future: IoT isolation network

VPN: Mullvad WireGuard (configured)
DNS: Blocky (127.0.0.1:5353) → dnsmasq (port 53)
```

---

## Technical Highlights

### SSH Access:
- Successfully configured key-based authentication
- Router accessible at: root@192.168.8.1

### Blocky Configuration:
- Running on router at port 5353
- Version: v0.24 (arm64)
- Config: /etc/blocky/config.yml
- Ultra-aggressive blocking lists (Hagezi, OISD, 1Hosts)
- Upstream DNS: Cloudflare (1.1.1.2), Quad9 (9.9.9.9)

### VPN Configuration:
- Leak protection: Active (blackhole rules)
- Kill switch: Enabled
- Split tunneling: Configured (awaiting device selection)
- Interface: wgclient1 (disabled during session)

---

## Session Statistics

- **Duration:** ~3 hours
- **SSH Commands:** 50+
- **Files Created:** 16
- **Packages Removed:** 5
- **System Optimizations:** Multiple (documented, not yet applied)
- **Documentation Pages:** 100+

---

## User Preferences Identified

✓ Prefers command-line/SSH configuration
✓ Values privacy (Mullvad VPN, Blocky DNS)
✓ Technical user (understands networking concepts)
✓ Minimalist approach (removed unnecessary features)
✓ Wants static IPs for all devices
✓ Desires IoT network isolation
✓ Not interested in visual dashboards/monitoring UIs

---

## Lessons Learned

1. **GL.iNet firmware is heavily customized** - Not pure OpenWrt
2. **Blocky works well on router** - Good alternative to AdGuard Home
3. **WiFi 7 MLO is actively working** - Multiple interfaces aggregated
4. **Custom display requires deep integration** - Text-based monitoring not practical
5. **Package removal is safe** - Unused GL.iNet features can be removed cleanly

---

## Repository State

**Branch:** main
**Remote:** https://github.com/mischa-thisness/M-Claude.git
**Status:** All files staged and ready to commit

**Files to commit:**
- gemini-slate/ (entire directory)
- 16 files total
- All documentation, scripts, and guides

---

## Final Notes

This was a comprehensive router configuration session that achieved:
- ✅ Complete system analysis and documentation
- ✅ Network optimization strategy
- ✅ System cleanup (removed 5 packages)
- ✅ Static IP planning
- ✅ IoT isolation design
- ✅ VPN leak protection verification
- ✅ Blocky DNS integration confirmation

All work is ready to be committed to the M-Claude repository under the `gemini-slate/` project directory.

**Status:** Ready for deployment when user chooses to apply optimizations.

---

*Session completed: 2026-01-10*
*Router: GL-BE3600 (Slate 7)*
*Project: gemini-slate*
*License: CC0 1.0 Universal*

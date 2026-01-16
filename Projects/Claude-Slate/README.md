# Claude-Slate

**GL-BE3600 (Slate 7) WiFi 7 Router Configuration**

Complete documentation, scripts, and configurations for the GL.iNet GL-BE3600 (Slate 7) travel router with WiFi 7, Mullvad VPN, and advanced network optimization.

## Overview

This project provides comprehensive configuration and management for the GL-BE3600 router featuring:

- **Router:** GL.iNet GL-BE3600 (Slate 7) - WiFi 7 travel router
- **VPN:** Mullvad WireGuard with kill-switch
- **DNS:** Integration with Blocky DNS (runs on Zimaboard server)
- **Network:** 192.168.8.0/24 with static IP management
- **WiFi:** WiFi 7 (802.11be) with MLO support
- **WAN:** Starlink with 2.5Gbps ethernet

## Documentation

### Technical Specifications
- `GL-BE3600_Technical_Specifications.md` - Complete hardware specs
- `GL-BE3600_Software_Report.md` - All software packages and versions
- `GL-BE3600_SSH_Session_Report.md` - Live system inspection results

### Configuration Guides
- `OPTIMIZATION_SUMMARY.md` - Quick reference guide
- `network_optimization_plan.md` - Detailed optimization strategy
- `manual_configuration_guide.md` - Step-by-step manual configuration
- `custom_display_guide.md` - Touchscreen customization guide
- `CUSTOM_DISPLAY_QUICK_START.md` - Quick start for custom dashboard

### Session Notes
- `SESSION_NOTES.md` - Comprehensive session notes and router configuration

### Cleanup Logs
- `zerotier_removal_log.md` - ZeroTier package removal documentation
- `parental_control_removal_log.md` - Parental control removal log

## Scripts

- `router_optimization_script.sh` - Automated router optimization
- `collect_device_info.sh` - Device information collector
- `install_custom_display.sh` - Custom display installation

## Network Design

**Main Network:** 192.168.8.0/24
- Wired devices: 192.168.8.21-50
- WiFi devices: 192.168.8.51-100
- IoT devices: 192.168.8.150-200 (isolated guest network)
- DHCP pool: 192.168.8.201-250

**Key Features:**
- WiFi 7 with MLO (Multi-Link Operation)
- WPA3 encryption
- Mullvad VPN kill-switch
- DNS filtering via Blocky
- IoT network isolation
- Static IP management

## Quick Start

### 1. Review Documentation
```bash
# Read the optimization summary
cat OPTIMIZATION_SUMMARY.md

# Review the network plan
cat network_optimization_plan.md
```

### 2. Run Optimization Script
```bash
# SSH into router
ssh root@192.168.8.1

# Download and run optimization script
./router_optimization_script.sh
```

### 3. Manual Configuration
```bash
# Follow step-by-step guide
cat manual_configuration_guide.md
```

## Router Specifications

- **Model:** GL.iNet GL-BE3600 (Slate 7)
- **Firmware:** GL.iNet 4.8.1 (OpenWrt 23.05-SNAPSHOT)
- **Kernel:** Linux 5.4.213
- **SoC:** Qualcomm IPQ5312 (Quad-core @ 1.1 GHz)
- **RAM:** 1 GB
- **Storage:** 512 MB NAND
- **WiFi:** WiFi 7 (802.11be) with MLO support
- **Ports:** 1x 2.5Gbps WAN, 1x 2.5Gbps LAN
- **Display:** Touchscreen with custom dashboard support

## Integration

This router integrates with:
- **Claude-Zima** (Zimaboard server) - Runs Blocky DNS at 192.168.8.21
- **Starlink** - Primary WAN connection
- **IoT Devices** - ESP32 controllers, Renology solar monitoring

See the `Claude-Zima` project for Zimaboard server configuration.

## License

This project is released under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication.

---

**Part of the M-Claude repository homelab infrastructure**

# GL.iNet GL-BE3600 (Slate 7) Software & Firmware Report

## Document Overview

This technical report provides comprehensive information about the firmware, kernel, operating system, packages, and services running on the GL.iNet GL-BE3600 (Slate 7) router.

**Report Date:** 2026-01-10
**Device Model:** GL-BE3600 (Slate 7)
**Firmware Version:** 4.8.1 (based on available documentation)

---

## Operating System

### Base System

**Name:** OpenWrt
**Version:** 23.05-SNAPSHOT
**Type:** Linux-based embedded operating system
**Developer:** OpenWrt Project
**Website:** https://openwrt.org
**License:** GPL-2.0
**Function:** Embedded Linux distribution for network routers and embedded devices

**Description:** OpenWrt is a highly extensible GNU/Linux distribution for embedded devices. Unlike many other distributions for routers, OpenWrt is built from the ground up to be a full-featured, easily modifiable operating system for embedded devices.

### GL.iNet Customizations

**Firmware Type:** Modified OpenWrt with proprietary GL.iNet features
**Custom Interface:** Dual UI system (GL.iNet web interface + LuCI)
**Custom Components Location:**
- Custom web interface: `/www`
- Custom executables: `/usr/bin`
- Custom libraries: `/usr/lib`
- LuCI binaries: `/www/cgi-bin`

**Web Frontend Framework:** Vue.js
**API Backend:** Custom C binary (`api`) located in `/www`

---

## Linux Kernel

**Version:** 5.4.213
**Developer:** Linux Kernel Community / GL.iNet (customized for device)
**License:** GPL-2.0
**Architecture:** ARM/ARM64 (based on Qualcomm platform)
**Function:** Core operating system kernel providing hardware abstraction and resource management

**Note:** The GL-BE3600 uses kernel 5.4.213, which differs from the standard OpenWrt 23.05 kernel (typically 5.15.x series). This indicates GL.iNet has customized the kernel specifically for this hardware platform.

---

## System-on-Chip (SoC) Platform

**Chipset:** Qualcomm IPQ5312 (likely, based on community analysis)
**Architecture:** Quad-core @ 1.1 GHz
**Developer:** Qualcomm Technologies, Inc.
**Function:** Main processor handling routing, wireless, and system operations

**Wireless Drivers:** ath12k (Qualcomm Atheros WiFi 7 driver)
**Driver Status:** Early development stage for WiFi 7 support
**Function:** Enables WiFi 7 (802.11be) wireless networking on 2.4 GHz and 5 GHz bands

---

## Core System Packages

### Package Manager

**Name:** opkg
**Developer:** OpenWrt Project
**Version:** Included with OpenWrt 23.05
**Function:** Lightweight package management system for embedded Linux
**Website:** https://openwrt.org
**License:** GPL-2.0

### System Utilities

#### BusyBox

**Version:** 1.37.0 (OpenWrt 25.12.x), likely 1.36.1 in OpenWrt 23.05
**Developer:** BusyBox Project (Erik Andersen, Denys Vlasenko, and contributors)
**Website:** https://busybox.net
**License:** GPL-2.0
**Function:** Combines tiny versions of many common UNIX utilities into a single small executable, providing a complete environment for embedded systems

**Common Tools Provided:**
- Shell (ash)
- File utilities (ls, cp, mv, rm, etc.)
- Text processing (grep, sed, awk, etc.)
- Network tools (wget, ping, etc.)
- System utilities (mount, ps, top, etc.)

#### C Library

**Name:** musl libc
**Version:** 1.2.4 (OpenWrt 23.05.0)
**Developer:** Rich Felker and contributors
**Website:** https://musl.libc.org
**License:** MIT
**Function:** Lightweight, fast, simple C standard library implementation

---

## Network Services

### DNS & DHCP Server

**Name:** dnsmasq
**Version:** 2.91 (latest OpenWrt), likely 2.90 in firmware 4.8.1
**Developer:** Simon Kelley
**Website:** https://thekelleys.org.uk/dnsmasq/doc.html
**License:** GPL-2.0 or GPL-3.0
**Function:** Provides network infrastructure for small networks: DNS, DHCP, router advertisement, and network boot

**Key Features:**
- DNS forwarding and caching
- DHCP server
- IPv6 router advertisement
- PXE/TFTP boot support

**Service Configuration:**
- Location: `/etc/config/dhcp`
- Init script: `/etc/init.d/dnsmasq`
- Triggered by: netifd hotplug events

### Network Interface Daemon

**Name:** netifd
**Developer:** OpenWrt Project
**Function:** Network interface management daemon for OpenWrt
**License:** GPL-2.0

**Key Responsibilities:**
- Network interface configuration
- Hotplug event management
- Protocol handler coordination
- Bridge and VLAN management

### Firewall

**Name:** firewall4
**Version:** 2024.12.1818fc0ead-r1 (recent OpenWrt builds)
**Developer:** OpenWrt Project
**Backend:** nftables (Linux kernel netfilter framework)
**Function:** Network security and packet filtering system
**License:** GPL-2.0

**Key Features:**
- Zone-based firewall configuration
- NAT and masquerading
- Port forwarding
- Traffic filtering
- IPv4 and IPv6 support

**Configuration:**
- Location: `/etc/config/firewall`
- Uses nftables backend (replaces older iptables in firewall3)

---

## Web Interfaces

### LuCI

**Name:** LuCI (Lua Configuration Interface)
**Developer:** OpenWrt Project
**Repository:** https://github.com/openwrt/luci
**Version:** Master git-25.231.52382-62e675d (firmware 4.8.1 reference)
**Function:** Official OpenWrt web configuration interface
**License:** Apache-2.0

**Technology Stack:**
- Server-side: Lua (deprecated), ucode rpcd (recommended)
- Frontend: JavaScript/HTML
- Web server: uhttpd

**Note:** Lua APIs are being phased out in favor of ucode rpcd for server-side operations in future LuCI versions.

### uhttpd

**Name:** uhttpd (Micro HTTP Daemon)
**Developer:** OpenWrt Project
**Function:** Lightweight web server for LuCI and other web interfaces
**License:** BSD-style

**Configuration:**
- Default listen: 0.0.0.0:80 (HTTP)
- HTTPS support: Available with SSL packages
- CGI support: Yes

### GL.iNet Web Interface

**Developer:** GL.iNet
**Technology:** Vue.js frontend
**Backend:** Custom C binary API
**Function:** Simplified, user-friendly router configuration interface
**Access:** Primary interface for router management

---

## Security & Remote Access

### SSH Server

**Name:** Dropbear
**Version:** 2025.89 (latest), likely 2024.x in firmware 4.8.1
**Developer:** Matt Johnston
**Website:** https://matt.ucc.asn.au/dropbear/dropbear.html
**License:** MIT
**Function:** Lightweight SSH server and client for embedded systems

**Features:**
- SSH protocol support (SSH-2)
- SCP file transfer
- Small memory footprint
- Suitable for systems with limited resources

**Configuration:**
- Default port: 22
- Location: `/etc/config/dropbear`

---

## VPN Services

### OpenVPN

**Package Name:** openvpn
**Version:** 2.6.14 (latest OpenWrt package)
**Developer:** OpenVPN Inc. / Community
**Package Maintainer:** Not specified in Makefile
**Website:** https://openvpn.net
**Repository:** https://github.com/openwrt/packages/blob/master/net/openvpn/Makefile
**License:** GPL-2.0
**Function:** Full-featured SSL VPN solution

**Performance on GL-BE3600:**
- OpenVPN-DCO speed: Up to 385 Mbps

**Available Variants:**
- OpenSSL backend
- mbedTLS backend
- WolfSSL backend

**Dependencies:**
- Kernel TUN module
- libcap-ng
- Optional: liblzo, liblz4, iproute2, libnl-genl

**Key Features:**
- Client and server modes
- Various authentication methods
- Strong encryption
- Cross-platform support

### OpenVPN Data Channel Offload

**Package Name:** ovpn-dco
**Developer/Maintainer:** Jianhui Zhao <zhaojh329@gmail.com>
**Repository:** https://github.com/openwrt/packages/blob/master/kernel/ovpn-dco/Makefile
**Function:** Kernel module for OpenVPN data channel offload, improving VPN performance
**License:** GPL-2.0

### WireGuard

**Package Name:** wireguard-tools (userspace tools)
**Kernel Module:** kmod-wireguard
**Developer:** Jason A. Donenfeld and the WireGuard project
**Website:** https://www.wireguard.com
**License:** GPL-2.0
**Function:** Modern, fast, and secure VPN protocol

**Performance on GL-BE3600:**
- WireGuard speed: Up to 490 Mbps

**Components:**
- `wireguard-tools`: Userspace configuration utilities (wg, wg-quick)
- `kmod-wireguard`: Linux kernel module
- `luci-proto-wireguard`: LuCI integration
- `luci-app-wireguard`: LuCI web interface

**Key Features:**
- Simple configuration
- High performance
- Modern cryptography (Curve25519, ChaCha20, Poly1305)
- Low overhead
- Built into Linux kernel (5.6+)

---

## Security & Privacy

### AdGuard Home

**Package Name:** adguardhome
**Version:** 0.107.71
**Developers/Maintainers:**
- Upstream: AdGuard Team
- OpenWrt Package Maintainers:
  - Dobroslaw Kijowski <dobro90@gmail.com>
  - George Sapkin <george@sapk.in>

**Website:** https://adguard.com/en/adguard-home/overview.html
**Repository:** https://github.com/openwrt/packages/blob/master/net/adguardhome/Makefile
**Source:** https://github.com/AdguardTeam/AdGuardHome
**License:** GPL-3.0-only
**Function:** Network-wide ads and trackers blocking DNS server

**Key Features:**
- DNS-level ad blocking
- Privacy protection
- Parental controls
- Safe browsing
- Custom filtering rules
- Query logging
- Statistics dashboard

**Installation Status:** Pre-installed on GL-BE3600
**User/Group:** adguardhome (UID/GID: 853)
**Dependencies:** ca-bundle

**Community Tools:**
- GL.iNet AdGuard Updater: https://github.com/Admonstrator/glinet-adguard-updater
  - Automatically updates AdGuard Home on GL.iNet routers
  - Tested on firmware 4.x devices

### Tor Support

**Function:** Anonymous networking and privacy protection
**Status:** Available/supported on GL.iNet firmware
**Website:** https://www.torproject.org

---

## System Libraries

### Cryptographic Libraries

#### OpenSSL

**Function:** Cryptography and SSL/TLS library
**Developer:** OpenSSL Project
**Website:** https://www.openssl.org
**License:** Apache-2.0
**Use Cases:** TLS connections, VPN encryption, general cryptography

#### mbedTLS

**Function:** Lightweight cryptographic and SSL/TLS library
**Developer:** Arm (formerly ARM Limited)
**Website:** https://www.trustedfirmware.org/projects/mbed-tls/
**License:** Apache-2.0
**Default in OpenWrt 23.05:** Yes
**Use Cases:** Embedded systems cryptography, resource-constrained environments

#### WolfSSL

**Function:** Lightweight SSL/TLS library
**Developer:** wolfSSL Inc.
**Website:** https://www.wolfssl.com
**License:** GPL-2.0 or commercial
**Use Cases:** Embedded SSL/TLS, IoT security

### Network Libraries

#### libnl-genl

**Function:** Generic Netlink library for Linux kernel communication
**Use Cases:** Network configuration, wireless management

#### libcap-ng

**Function:** POSIX capabilities library
**Use Cases:** Privilege management, security

---

## Development Tools (Available via opkg)

### Compiler Toolchain

**GCC Version:** 12.3.0 (OpenWrt 23.05.0)
**Binutils:** 2.40
**Function:** Compilation and linking tools for building software

### Build System

**Name:** OpenWrt Build System (based on Buildroot)
**SDK Available:** Yes
**Repository:** https://github.com/gl-inet/sdk
**Function:** Cross-compilation environment for building packages

---

## Additional Network Protocols & Features

### Network Protocols Supported

**IPv4:** Full support
**IPv6:** Full support
**DDNS (Dynamic DNS):** Supported
**UPnP:** Supported
**QoS (Quality of Service):** Supported
**VLAN:** Supported

### Network Modes

**Supported Modes:**
- Router mode
- Access Point mode
- Extender/Repeater mode
- WDS Bridge mode

---

## Package Repositories

### GL.iNet Package Repository

**Location:** https://github.com/gl-inet/glinet
**Description:** All ipks (OpenWrt packages) for GL.iNet's official firmware
**Function:** Custom GL.iNet packages and modifications

### OpenWrt Package Feeds

**Base Packages:** https://downloads.openwrt.org/releases/23.05.5/packages/
**Available Packages:** ~8,000 optional software packages
**Function:** Extended software repository for OpenWrt

---

## Firmware Update & Management

### Firmware Download Center

**URL:** https://dl.gl-inet.com/router/be3600/
**Function:** Official firmware downloads for GL-BE3600
**Note:** Requires JavaScript-enabled browser

### Firmware Upgrade Process

**Method:** Web interface or LuCI
**Settings Retention:** Yes (with option)
**Package Retention:** User must reinstall after upgrade
**Documentation:** https://docs.gl-inet.com/router/en/4/interface_guide/firmware_upgrade/

### Firmware Version Tracking

**Official Versions Page:** https://www.gl-inet.com/support/firmware-versions/
**Current Firmware:** 4.8.1 (based on documentation references)
**Latest Features:** https://www.gl-inet.com/support/firmware-features/

---

## API & Scripting

### GL.iNet API

**Type:** Custom C binary API
**Documentation:** Community discussion at https://forum.gl-inet.com/t/4-x-api-docs/37869
**Function:** Backend API for GL.iNet web interface
**Access:** Via web interface calls

### Shell Environment

**Default Shell:** ash (from BusyBox)
**Available:** Yes via SSH
**Script Support:** Shell scripts, Lua (being deprecated), ucode

---

## Community & Development Resources

### Official Resources

**Main Website:** https://www.gl-inet.com
**Documentation:** https://docs.gl-inet.com/router/en/4/user_guide/gl-be3600/
**Forum:** https://forum.gl-inet.com
**GitHub Organization:** https://github.com/gl-inet

### OpenWrt Resources

**Main Website:** https://openwrt.org
**Forum:** https://forum.openwrt.org
**Documentation:** https://openwrt.org/docs/start
**GitHub:** https://github.com/openwrt

### Development Repositories

**GL.iNet SDK:** https://github.com/gl-inet/sdk
**Image Builder:** https://github.com/gl-inet/imagebuilder
**Documentation Source:** https://github.com/gl-inet/docs4.x
**Package Repository:** https://github.com/gl-inet/glinet

---

## Security Considerations

### Default Services

**SSH:** Enabled (Dropbear on port 22)
**HTTP:** Enabled (uhttpd on port 80)
**HTTPS:** Available with configuration
**Firewall:** Enabled by default (firewall4)

### Security Updates

**Source:** GL.iNet firmware updates
**Update Method:** Web interface or manual download
**Frequency:** Periodic releases (check firmware versions page)

### Vulnerability Management

**Upstream Security:** Inherits OpenWrt security updates
**Package Updates:** Available via opkg when compatible
**Community Monitoring:** Active forum and GitHub issues

---

## Known Limitations & Considerations

### WiFi 7 Support Status

**Current State:** Early development stage
**Driver:** ath12k module still maturing
**OpenWrt Support:** Limited, under active development
**Reference:** https://forum.openwrt.org/t/adding-openwrt-support-for-gl-inet-gl-be3600-wifi-7-router/228974

### Package Updates Warning

**Important:** Updating all pre-installed opkg packages can brick the device into boot loop
**Reference:** https://forum.gl-inet.com/t/slate-7-4-7-2-updating-all-the-pre-installed-opkg-packages-bricks-the-device-into-boot-loop/59316
**Recommendation:** Only update specific packages as needed, avoid mass updates

### Kernel Version Note

**GL.iNet Kernel:** 5.4.213 (customized)
**Standard OpenWrt 23.05:** 5.15.x series
**Implication:** GL.iNet uses older, device-specific kernel version for hardware compatibility

---

## Performance Optimizations

### VPN Performance Enhancements

**OpenVPN-DCO:** Data Channel Offload enabled for improved performance
**WireGuard:** Kernel-mode implementation for maximum throughput
**Hardware Acceleration:** Qualcomm SoC supports cryptographic operations

### Network Stack Optimizations

**netifd:** Efficient network interface management
**firewall4:** nftables backend for improved packet filtering performance
**dnsmasq:** Lightweight DNS/DHCP reduces overhead

---

## Logging & Monitoring

### System Logging

**Logger:** Standard Linux syslog via BusyBox
**Location:** `/var/log/` (tmpfs - in RAM)
**Persistence:** Logs cleared on reboot unless configured otherwise

### Web Interface Statistics

**GL.iNet Interface:** Real-time network statistics
**LuCI Interface:** Detailed system and network monitoring
**AdGuard Home:** DNS query logging and statistics

---

## Backup & Restore

### Configuration Backup

**Method:** Web interface or command-line
**Format:** Compressed archive of `/etc/config/`
**Includes:** Network settings, firewall rules, custom configurations
**Excludes:** User-installed packages (list can be saved separately)

### Package List Backup

**Tool:** Custom scripts available
**Reference:** https://forum.gl-inet.com/t/how-to-script-list-my-opkgs-to-a-file-for-backup/30963
**Function:** Save list of installed packages for reinstallation

---

## Service Startup & Init System

### Init System

**Type:** procd (OpenWrt init system)
**Based on:** ubus and process management
**Function:** System and service initialization

### Service Management

**Init Scripts Location:** `/etc/init.d/`
**Enabled Services:** Managed via symbolic links in `/etc/rc.d/`
**Management Commands:** `/etc/init.d/<service> start|stop|restart|enable|disable`

**Key Services at Boot:**
- network (netifd)
- firewall (firewall4)
- dnsmasq
- dropbear (SSH)
- uhttpd (web server)
- gl_* (GL.iNet custom services)

---

## Summary Table: Core Software Components

| Component | Version | Developer/Maintainer | License | Function |
|-----------|---------|---------------------|---------|----------|
| OpenWrt | 23.05-SNAPSHOT | OpenWrt Project | GPL-2.0 | Base OS |
| Linux Kernel | 5.4.213 | Linux Community / GL.iNet | GPL-2.0 | OS Kernel |
| BusyBox | 1.36.1 (est.) | BusyBox Project | GPL-2.0 | System Utilities |
| musl libc | 1.2.4 | Rich Felker et al. | MIT | C Library |
| dnsmasq | 2.90 (est.) | Simon Kelley | GPL-2.0/3.0 | DNS/DHCP |
| netifd | - | OpenWrt Project | GPL-2.0 | Network Daemon |
| firewall4 | 2024.12.x | OpenWrt Project | GPL-2.0 | Firewall (nftables) |
| LuCI | git-25.231.x | OpenWrt Project | Apache-2.0 | Web Interface |
| uhttpd | - | OpenWrt Project | BSD-style | Web Server |
| Dropbear | 2024.x (est.) | Matt Johnston | MIT | SSH Server |
| OpenVPN | 2.6.14 | OpenVPN Inc. | GPL-2.0 | VPN Client/Server |
| ovpn-dco | - | Jianhui Zhao | GPL-2.0 | OpenVPN Acceleration |
| WireGuard | - | Jason Donenfeld | GPL-2.0 | VPN Protocol |
| AdGuard Home | 0.107.71 | AdGuard Team / Kijowski, Sapkin | GPL-3.0 | DNS Ad Blocker |
| opkg | - | OpenWrt Project | GPL-2.0 | Package Manager |

---

## References & Sources

### Official Documentation
- GL.iNet GL-BE3600 Documentation: https://docs.gl-inet.com/router/en/4/user_guide/gl-be3600/
- GL.iNet Firmware Versions: https://www.gl-inet.com/support/firmware-versions/
- GL.iNet Download Center: https://dl.gl-inet.com/router/be3600/
- OpenWrt Documentation: https://openwrt.org/docs/start

### Community Forums
- GL.iNet Forum: https://forum.gl-inet.com
- OpenWrt Forum: https://forum.openwrt.org
- GL-BE3600 OpenWrt Support Discussion: https://forum.openwrt.org/t/adding-openwrt-support-for-gl-inet-gl-be3600-wifi-7-router/228974

### Code Repositories
- GL.iNet GitHub: https://github.com/gl-inet
- GL.iNet Package Repository: https://github.com/gl-inet/glinet
- GL.iNet SDK: https://github.com/gl-inet/sdk
- OpenWrt Packages: https://github.com/openwrt/packages
- LuCI Repository: https://github.com/openwrt/luci
- AdGuard Home: https://github.com/AdguardTeam/AdGuardHome
- AdGuard Home OpenWrt Package: https://github.com/openwrt/packages/blob/master/net/adguardhome/Makefile
- OpenVPN OpenWrt Package: https://github.com/openwrt/packages/blob/master/net/openvpn/Makefile

### Package Information
- OpenWrt 23.05 Packages: https://downloads.openwrt.org/releases/23.05.5/packages/
- GL.iNet AdGuard Updater: https://github.com/Admonstrator/glinet-adguard-updater

---

## Document Metadata

**Document Version:** 1.0
**Created:** 2026-01-10
**Author:** Research compilation
**License:** CC0 1.0 Universal
**Purpose:** Technical reference for GL-BE3600 software stack

**Data Sources:** Official GL.iNet documentation, OpenWrt project resources, GitHub repositories, community forums, and package maintainer information.

**Disclaimer:** Software versions and package details may change with firmware updates. Always refer to official GL.iNet documentation for the most current information. This document reflects information available as of January 2026.

---

*This document provides a comprehensive overview of the software ecosystem running on the GL.iNet GL-BE3600 router, including developers, versions, links, and functions of all major components.*

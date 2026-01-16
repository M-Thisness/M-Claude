# Claude-Zima

**Zimaboard Homelab Server Configuration**

Documentation and configuration for the Zimaboard x86 single-board server running homelab services including Blocky DNS filtering, Docker containers, and network services.

## Overview

Claude-Zima is the homelab server component that provides:

- **Hardware:** Zimaboard x86 single-board computer
- **IP Address:** 192.168.8.21 (static, wired connection)
- **Primary Service:** Blocky DNS filtering (port 5353)
- **Integration:** Works with Claude-Slate (GL-BE3600 router)

## Current Services

### Blocky DNS
- **Port:** 5353
- **Function:** DNS filtering and ad-blocking
- **Integration:** Router forwards DNS queries to Zimaboard
- **Configuration:** Custom blocklists and allowlists

## Planned Services

Future expansion may include:
- Docker containers for homelab applications
- Media server (Plex/Jellyfin)
- Home automation hub
- Network monitoring (Grafana/Prometheus)
- File server (SMB/NFS)
- Backup server

## Server Specifications

- **Model:** Zimaboard (x86 single-board computer)
- **CPU:** Intel Celeron (quad-core)
- **RAM:** 8GB
- **Storage:** 32GB eMMC + expandable via SATA
- **Network:** Gigabit Ethernet
- **OS:** TBD (Linux-based)

## Network Configuration

**Static IP:** 192.168.8.21
**Network:** 192.168.8.0/24
**Gateway:** 192.168.8.1 (Claude-Slate router)
**DNS:** Self (127.0.0.1) or upstream via router

## Integration with Claude-Slate

The Zimaboard server integrates with the GL-BE3600 router:

1. **DNS Filtering:** Router forwards DNS queries to Zimaboard:5353
2. **Wired Connection:** Static IP in wired device range (21-50)
3. **Network Services:** Server provides services to all network clients
4. **IoT Isolation:** Server accessible from main network, not IoT network

See the `Claude-Slate` project for router configuration details.

## Quick Start

```bash
# SSH into Zimaboard
ssh user@192.168.8.21

# Check Blocky DNS status
systemctl status blocky

# View Blocky logs
journalctl -u blocky -f

# Test DNS resolution
dig @192.168.8.21 -p 5353 example.com
```

## Documentation

Documentation will be added as services are configured:
- Blocky DNS configuration
- Docker compose files
- Service management scripts
- Backup procedures
- Monitoring setup

## Status

🚧 **Project Status:** Initial Setup

This project is in early stages. Documentation and configurations will be added as the server is set up and services are deployed.

## License

This project is released under the CC0 1.0 Universal (CC0 1.0) Public Domain Dedication.

---

**Part of the M-Claude repository homelab infrastructure**

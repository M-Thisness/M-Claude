# 🏠 Zimaboard HomeLab - Master Deployment Guide

## Complete Multi-Phase HomeLab Architecture

**Target Hardware:** Zimaboard 16GB with PCIe 4x 2.5GbE Network Card
**Base Platform:** Proxmox VE 8.x
**Architecture:** Multi-bridge managed switch + LXC containers + selective VMs

---

## 📋 Executive Summary

This guide provides a comprehensive, phase-based deployment strategy for transforming a Zimaboard into a fully-featured HomeLab encompassing:

- **Advanced Networking:** 6-port managed switch with traffic monitoring
- **Media Management:** Complete *arr stack + Jellyfin + stream archival
- **Knowledge Management:** Digital garden + document database with OCR
- **Home Automation:** Home Assistant + MQTT + smart home integration
- **Citizen Science:** Real-time bird identification and logging
- **Security:** Network IDS/IPS, vulnerability scanning, ad blocking

**Critical Finding:** Full stack requires 28-42GB RAM, but optimized deployment fits within 16GB constraints through careful service selection and resource management.

---

## 📚 Documentation Structure

This deployment consists of multiple interlinked documents:

| Document | Purpose | Read When |
|----------|---------|-----------|
| **MASTER-DEPLOYMENT-GUIDE.md** (this file) | Overview + phased deployment plan | Start here |
| **NETWORK-TOPOLOGY.md** | Network architecture, Mermaid diagrams | Phase 1: Networking |
| **RESOURCE-ANALYSIS.md** | Detailed CPU/RAM analysis, optimization | Before deployment |
| **WILDCARD-MODULES.md** | Optional service recommendations | After core services |
| **proxmox-network-interfaces** | Proxmox network config file | Phase 1 setup |
| **proxmox-firewall-rules.sh** | iptables firewall script | Phase 1 setup |
| **traffic-mirror-setup.sh** | Port mirroring for monitoring | Phase 1 setup |
| **dhcp-server-config.sh** | DHCP server (dnsmasq) | Phase 1 setup |
| **Projects/knowledge-stack/** | Complete knowledge management stack | Phase 3 |
| **media-stack-docker-compose.yml** | Media acquisition/management | Phase 2 |
| **home-assistant-docker-compose.yml** | Home automation | Phase 4 |

---

## 🎯 Deployment Scenarios

### ❌ Scenario 1: Full Stack (NOT RECOMMENDED)
- **Resources:** 28-42GB RAM, 9-17 CPU cores
- **Verdict:** Impossible on 16GB Zimaboard

### ⚠️ Scenario 2: Optimized Stack (ADVANCED USERS)
- **Resources:** ~17GB RAM, ~5.7 CPU cores
- **Requires:** Aggressive tuning, zram swap, careful monitoring
- **Verdict:** Possible but requires constant resource management

### ✅ Scenario 3: Minimal Viable Stack (RECOMMENDED)
- **Resources:** ~12GB RAM, ~4 CPU cores
- **Headroom:** 2.5GB RAM buffer
- **Verdict:** Stable, responsive, room for growth

**This guide follows Scenario 3 with optional upgrades to Scenario 2.**

---

## 🚀 Quick Start (30-Minute Minimal Setup)

### Prerequisites
```bash
# 1. Install Proxmox VE 8.x on Zimaboard
# 2. Boot from USB, follow installer
# 3. Access web UI: https://<zimaboard-ip>:8006

# 4. Update system
apt update && apt full-upgrade -y

# 5. Install essentials
apt install -y git vim htop iotop iftop glances dnsmasq iptables-persistent
```

### Minimal Network Setup
```bash
# 1. Identify network interfaces
ip link show

# Expected interfaces:
# - enp2s0, enp3s0 (onboard 2.5GbE)
# - enp4s0, enp5s0, enp6s0, enp7s0 (PCIe 4x 2.5GbE)

# 2. Copy network configuration
cd /tmp
git clone <your-repo-url>
cp zimaboard-homelab/proxmox-network-interfaces /etc/network/interfaces

# 3. Edit for your environment
nano /etc/network/interfaces
# Update: Gateway IP, DNS servers, IP addresses

# 4. Apply network configuration
ifreload -a

# 5. Configure firewall
cd zimaboard-homelab
chmod +x proxmox-firewall-rules.sh
./proxmox-firewall-rules.sh

# 6. Setup DHCP (optional)
chmod +x dhcp-server-config.sh
./dhcp-server-config.sh
```

### Deploy First Service (NAS)
```bash
# 1. Create LXC for OpenMediaVault
pct create 170 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname nas \
  --memory 1024 \
  --cores 1 \
  --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.70/24,gw=192.168.8.1 \
  --features nesting=0

# 2. Start container
pct start 170

# 3. Install OMV (inside container)
pct enter 170
apt update && apt install -y gnupg
wget -O - https://repo.openmediavault.org/public/archive.key | gpg --dearmor -o /etc/apt/keyrings/openmediavault-archive-keyring.gpg
cat <<EOF >> /etc/apt/sources.list.d/openmediavault.list
deb [signed-by=/etc/apt/keyrings/openmediavault-archive-keyring.gpg] https://packages.openmediavault.org/public sandworm main
EOF
apt update
apt install -y openmediavault

# 4. Access OMV: http://192.168.8.70
# Default: admin / openmediavault
```

---

## 📅 Phased Deployment Timeline

### Week 1: Foundation & Networking (Phase 1)
- ✅ Proxmox installation
- ✅ Network configuration (6 bridges)
- ✅ Firewall rules
- ✅ DHCP server
- ✅ NAS setup
- ⏱️ **Time:** 8-12 hours
- 💾 **Resources:** 3GB RAM, 1 core

### Week 2: Core Services (Phases 2 & 3 Minimal)
- ✅ Deskflow KVM server
- ✅ PipeWire audio routing
- ✅ Jellyfin (direct play only)
- ✅ Silverbullet notes
- ⏱️ **Time:** 6-10 hours
- 💾 **Resources:** +6GB RAM (+1.5 cores) → 9GB total

### Week 3: Media Acquisition (Phase 2 Continued)
- ✅ Sonarr + Radarr (choose 1-2 *arr apps)
- ✅ qBittorrent + VPN
- ✅ Prowlarr indexer
- ⏱️ **Time:** 4-6 hours
- 💾 **Resources:** +2GB RAM (+0.5 cores) → 11GB total

### Week 4: Knowledge & Automation (Phases 3 & 4)
- ✅ Paperless-ngx (without Tika/Gotenberg)
- ✅ Home Assistant + MQTT
- ✅ BirdNET-Go
- ⏱️ **Time:** 6-8 hours
- 💾 **Resources:** +3GB RAM (+1.5 cores) → 14GB total ⚠️

**⚠️ Resource Warning:** At this point you're at ~14GB/16GB. Enable zram swap before proceeding.

### Week 5+: Optional Additions
- ⚡ Enable zram swap (4-6GB compressed)
- ⚡ Add AdGuard Home (150MB)
- ⚡ Add n8n automation (400MB)
- ⚡ Add Grafana dashboards (512MB)
- ⚡ Add monitoring (Suricata optimized: 2-3GB)
- ⏱️ **Time:** 2-4 hours per service
- 💾 **Resources:** Depends on selections

---

## 📐 Phase 1: Advanced Networking & Switching

### Objectives
1. Transform Zimaboard into 6-port managed switch
2. Implement traffic monitoring and analysis
3. Configure low-latency KVM and audio routing
4. Establish network security zones

### Network Architecture

**Bridge Configuration:**
- `vmbr0`: Management network (192.168.8.0/24) - Proxmox + containers
- `vmbr1`: WAN/Uplink - Connected to Slate router
- `vmbr2`: Legion network (192.168.10.0/24) - High-performance client
- `vmbr3`: Book network (192.168.20.0/24) - Mobile workstation
- `vmbr4`: IoT network (192.168.30.0/24) - Sonos + IoT devices (isolated)
- `vmbr_monitor`: Traffic mirroring - Passive monitoring for IDS

**Physical Port Mapping:**
- enp2s0 → vmbr0 (Management)
- enp3s0 → vmbr1 (WAN)
- enp4s0 → vmbr2 (Legion)
- enp5s0 → vmbr3 (Book)
- enp6s0 → vmbr4 (IoT)
- enp7s0 → vmbr_monitor (Monitor)

### Deployment Steps

#### 1. Configure Network Interfaces

```bash
# Backup original config
cp /etc/network/interfaces /etc/network/interfaces.backup-$(date +%Y%m%d)

# Copy new configuration
cp Projects/zimaboard-homelab/proxmox-network-interfaces /etc/network/interfaces

# Edit configuration for your environment
nano /etc/network/interfaces

# Key items to change:
# - vmbr0 address (line 50): Your desired Proxmox IP
# - vmbr0 gateway (line 51): Your router IP
# - vmbr0 dns-nameservers (line 52): Your DNS servers
# - vmbr2-vmbr4 addresses: Adjust subnet if needed

# Apply configuration
ifreload -a

# Verify bridges
brctl show
ip addr show
```

#### 2. Configure Firewall Rules

```bash
# Navigate to project directory
cd /home/user/M-Claude/Projects/zimaboard-homelab

# Make script executable
chmod +x proxmox-firewall-rules.sh

# Run firewall configuration
./proxmox-firewall-rules.sh

# Verify rules
iptables -L -v -n
iptables -t nat -L -v -n
iptables -t mangle -L -v -n
```

**Firewall Features:**
- ✅ Inter-bridge routing (Management ↔ All networks)
- ✅ Client network isolation (Legion ↔ Book allowed)
- ✅ IoT network isolation (Internet only, no LAN access)
- ✅ NAT masquerading for internet access
- ✅ QoS/DSCP markings (prioritize real-time traffic)
- ✅ SSH restricted to management network

#### 3. Setup Traffic Mirroring

```bash
# Make script executable
chmod +x traffic-mirror-setup.sh

# Run traffic mirroring setup
./traffic-mirror-setup.sh

# Verify mirroring
tc -s filter show dev vmbr2 ingress
tc -s filter show dev vmbr3 ingress
tc -s filter show dev vmbr4 ingress

# Test mirroring
tcpdump -i vmbr_monitor -c 20
```

**Mirroring Configuration:**
- ✅ vmbr2 (Legion) → vmbr_monitor
- ✅ vmbr3 (Book) → vmbr_monitor
- ✅ vmbr4 (IoT) → vmbr_monitor
- ✅ Systemd service for persistence

#### 4. Configure DHCP Server (Optional)

```bash
# Make script executable
chmod +x dhcp-server-config.sh

# Run DHCP configuration
./dhcp-server-config.sh

# Check DHCP status
systemctl status dnsmasq

# Monitor DHCP leases
tail -f /var/log/dnsmasq.log

# View active leases
cat /var/lib/misc/dnsmasq.leases
```

**DHCP Ranges:**
- Legion (vmbr2): 192.168.10.100-200
- Book (vmbr3): 192.168.20.100-200
- IoT (vmbr4): 192.168.30.100-200

#### 5. Deploy Network Services (Optional)

**5a. Deskflow KVM Server** (Low-latency mouse/keyboard sharing)

```bash
# Create LXC for Deskflow
pct create 132 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname deskflow \
  --memory 512 \
  --cores 1 \
  --rootfs local-lvm:4 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.32/24,gw=192.168.8.1

pct start 132
pct enter 132

# Install Deskflow
apt update
apt install -y git cmake build-essential libssl-dev libx11-dev
git clone https://github.com/debauchee/barrier.git
cd barrier
mkdir build && cd build
cmake ..
make -j4
make install

# Configure server
# Edit ~/.config/barrier/barrier.conf
# Add client devices (Legion, Book)

# Start server
barriers --daemon --address 192.168.8.32:24800
```

**5b. PipeWire Audio Router** (Network audio streaming)

```bash
# Create LXC for PipeWire
pct create 133 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname pipewire-router \
  --memory 1024 \
  --cores 1 \
  --rootfs local-lvm:4 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.33/24,gw=192.168.8.1

pct start 133
pct enter 133

# Install PipeWire
apt update
apt install -y pipewire pipewire-audio-client-libraries pipewire-pulse wireplumber

# Configure network audio
# See PROXMOX-ZIMABOARD-NETWORKING.md for detailed config

# Enable service
systemctl --user enable pipewire pipewire-pulse
```

**5c. Network Monitoring (Minimal)**

```bash
# Install lightweight monitoring
apt install -y vnstat iftop nethogs

# Enable vnstat
systemctl enable vnstat
systemctl start vnstat

# View network stats
vnstat -i vmbr0 -l  # Live
vnstat -i vmbr0 -d  # Daily
vnstat -i vmbr0 -m  # Monthly
```

**5d. IDS/IPS with Suricata (OPTIONAL - High Resource Cost)**

⚠️ **Warning:** Suricata requires 4-6GB RAM. Only deploy if using Scenario 2 (Optimized Stack) with zram enabled.

```bash
# Create LXC for Suricata
pct create 130 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname suricata \
  --memory 4096 \
  --cores 2 \
  --rootfs local-lvm:20 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.30/24,gw=192.168.8.1

pct start 130
pct enter 130

# Install Suricata
apt update
apt install -y suricata suricata-update

# Configure Suricata to monitor vmbr_monitor
nano /etc/suricata/suricata.yaml
# Set: af-packet: interface: vmbr_monitor

# Update rules (minimal set)
suricata-update enable-source et/open
suricata-update enable-source sslbl/ssl-fp-blacklist
suricata-update  # Download rules

# Start Suricata
systemctl enable suricata
systemctl start suricata

# Monitor alerts
tail -f /var/log/suricata/fast.log
```

### Phase 1 Validation

```bash
# Check all bridges are up
brctl show

# Verify IP addresses
ip addr show

# Test routing between networks
# From Legion (192.168.10.10):
ping 192.168.8.21  # Should reach Proxmox
ping 192.168.20.1  # Should reach Book network

# Test IoT isolation
# From IoT device (192.168.30.10):
ping 192.168.10.10  # Should FAIL (blocked)
ping 8.8.8.8  # Should SUCCEED (internet allowed)

# Check firewall rules
iptables -L -v -n | grep -A 5 "vmbr4"

# Monitor traffic mirroring
tcpdump -i vmbr_monitor -c 100

# View DHCP leases
cat /var/lib/misc/dnsmasq.leases
```

**Phase 1 Complete When:**
- ✅ All bridges operational
- ✅ Client devices receiving DHCP addresses
- ✅ Inter-network routing working (Legion ↔ Management ↔ Book)
- ✅ IoT isolation confirmed (blocked from LAN, allowed to internet)
- ✅ Traffic mirroring visible on vmbr_monitor
- ✅ Firewall rules persistent across reboots

**Resources Used:** 1-3GB RAM, 0.5-1.5 cores (depending on optional services)

---

## 📦 Phase 2: Storage & Media Stack

### Objectives
1. Configure lightweight NAS with BTRFS RAID1
2. Deploy media acquisition stack (torrents, indexers)
3. Setup media management (*arr apps)
4. Configure Jellyfin media server
5. Implement stream archival (YouTube/Twitch)

### Architecture Overview

**Storage Layer:**
- BTRFS RAID1 on 2x SATA drives (mirrored)
- Mount at `/mnt/storage` (bind-mounted into containers)
- Subvolumes: media, downloads, backups, documents

**Services:**
- **OpenMediaVault LXC:** Web UI for NAS management
- **Docker Media LXC:** Container host for media services
  - Jellyfin: Media server
  - Sonarr/Radarr: TV/Movie automation
  - Prowlarr: Indexer aggregator
  - qBittorrent: Torrent client (with VPN)
  - Audiobookshelf: Books/podcasts
  - TubeArchivist: YouTube/Twitch archival (optional, heavy)

### Deployment Steps

#### 1. Configure BTRFS Storage

```bash
# Identify SATA drives
lsblk

# Expected output:
# sda: First SATA drive
# sdb: Second SATA drive (via Y-cable)

# Create BTRFS RAID1 (ON PROXMOX HOST)
mkfs.btrfs -m raid1 -d raid1 -L storage /dev/sda /dev/sdb

# Create mount point
mkdir -p /mnt/storage

# Mount filesystem
mount /dev/sda /mnt/storage

# Create subvolumes
btrfs subvolume create /mnt/storage/media
btrfs subvolume create /mnt/storage/media/tv
btrfs subvolume create /mnt/storage/media/movies
btrfs subvolume create /mnt/storage/media/music
btrfs subvolume create /mnt/storage/media/books
btrfs subvolume create /mnt/storage/downloads
btrfs subvolume create /mnt/storage/backups
btrfs subvolume create /mnt/storage/documents

# Set permissions
chown -R 1000:1000 /mnt/storage/media
chown -R 1000:1000 /mnt/storage/downloads

# Add to /etc/fstab for persistence
echo "UUID=$(blkid -s UUID -o value /dev/sda) /mnt/storage btrfs defaults,noatime,compress=zstd:3,space_cache=v2 0 0" >> /etc/fstab

# Verify mount
df -h /mnt/storage
btrfs filesystem show /mnt/storage
```

#### 2. Deploy NAS (OpenMediaVault)

```bash
# Create LXC container for OMV
pct create 170 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname nas \
  --memory 1024 \
  --cores 1 \
  --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.70/24,gw=192.168.8.1 \
  --features nesting=0

# Bind mount storage into container
pct set 170 -mp0 /mnt/storage,mp=/mnt/storage

# Start container
pct start 170
pct enter 170

# Install OpenMediaVault
apt update && apt install -y gnupg
wget -O - https://repo.openmediavault.org/public/archive.key | gpg --dearmor -o /etc/apt/keyrings/openmediavault-archive-keyring.gpg
cat <<EOF >> /etc/apt/sources.list.d/openmediavault.list
deb [signed-by=/etc/apt/keyrings/openmediavault-archive-keyring.gpg] https://packages.openmediavault.org/public sandworm main
EOF
apt update
apt install -y openmediavault
omv-confdbadm populate

# Access OMV Web UI
echo "OpenMediaVault available at: http://192.168.8.70"
echo "Default credentials: admin / openmediavault"
```

**OMV Configuration (via Web UI):**
1. Login to http://192.168.8.70
2. Change admin password
3. **Storage → File Systems:** Import existing BTRFS filesystem
4. **Services → SMB/CIFS:** Enable, create shares:
   - `media` → /mnt/storage/media (Read/Write for media group)
   - `downloads` → /mnt/storage/downloads (Read/Write)
5. **Users → Create:** media user (UID 1000)

#### 3. Deploy Docker Media Stack

```bash
# Create LXC container for Docker
pct create 140 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname docker-media \
  --memory 10240 \
  --cores 4 \
  --rootfs local-lvm:32 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.40/24,gw=192.168.8.1 \
  --features nesting=1,keyctl=1

# Bind mount storage (read/write access)
pct set 140 -mp0 /mnt/storage,mp=/mnt/storage

# Start container
pct start 140
pct enter 140

# Install Docker
apt update
apt install -y curl gnupg ca-certificates
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify Docker
docker --version
docker compose version

# Create directory structure
mkdir -p /opt/media-stack
cd /opt/media-stack

# Copy docker-compose.yml from repo
# (Transfer media-stack-docker-compose.yml to container)
```

**media-stack-docker-compose.yml** (Create this file):

```yaml
version: '3.8'

x-common-variables: &common-variables
  PUID: 1000
  PGID: 1000
  TZ: America/New_York

x-logging: &default-logging
  driver: json-file
  options:
    max-size: 10m
    max-file: 3

networks:
  media:
    driver: bridge

services:
  # Jellyfin - Media Server
  jellyfin:
    image: jellyfin/jellyfin:latest
    container_name: jellyfin
    restart: unless-stopped
    network_mode: host  # Required for DLNA/device discovery
    environment:
      <<: *common-variables
      JELLYFIN_PublishedServerUrl: http://192.168.8.40:8096
    volumes:
      - ./jellyfin/config:/config
      - ./jellyfin/cache:/cache
      - /mnt/storage/media:/media:ro
    mem_limit: 2g
    mem_reservation: 1g
    cpu_shares: 2048
    logging: *default-logging

  # Sonarr - TV Show Management
  sonarr:
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    restart: unless-stopped
    environment:
      <<: *common-variables
    volumes:
      - ./sonarr/config:/config
      - /mnt/storage/media/tv:/tv
      - /mnt/storage/downloads:/downloads
    ports:
      - "8989:8989"
    networks:
      - media
    mem_limit: 512m
    cpu_shares: 1024
    logging: *default-logging

  # Radarr - Movie Management
  radarr:
    image: lscr.io/linuxserver/radarr:latest
    container_name: radarr
    restart: unless-stopped
    environment:
      <<: *common-variables
    volumes:
      - ./radarr/config:/config
      - /mnt/storage/media/movies:/movies
      - /mnt/storage/downloads:/downloads
    ports:
      - "7878:7878"
    networks:
      - media
    mem_limit: 512m
    cpu_shares: 1024
    logging: *default-logging

  # Prowlarr - Indexer Manager
  prowlarr:
    image: lscr.io/linuxserver/prowlarr:latest
    container_name: prowlarr
    restart: unless-stopped
    environment:
      <<: *common-variables
    volumes:
      - ./prowlarr/config:/config
    ports:
      - "9696:9696"
    networks:
      - media
    mem_limit: 256m
    cpu_shares: 512
    logging: *default-logging

  # qBittorrent - Torrent Client
  qbittorrent:
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    restart: unless-stopped
    environment:
      <<: *common-variables
      WEBUI_PORT: 8080
    volumes:
      - ./qbittorrent/config:/config
      - /mnt/storage/downloads:/downloads
    ports:
      - "8080:8080"
      - "6881:6881"
      - "6881:6881/udp"
    networks:
      - media
    mem_limit: 1g
    cpu_shares: 512
    logging: *default-logging
    # Add VPN sidecar container here if needed

  # Audiobookshelf - Books & Podcasts
  audiobookshelf:
    image: ghcr.io/advplyr/audiobookshelf:latest
    container_name: audiobookshelf
    restart: unless-stopped
    environment:
      <<: *common-variables
    volumes:
      - ./audiobookshelf/config:/config
      - ./audiobookshelf/metadata:/metadata
      - /mnt/storage/media/books:/audiobooks
      - /mnt/storage/media/podcasts:/podcasts
    ports:
      - "13378:80"
    networks:
      - media
    mem_limit: 512m
    cpu_shares: 1024
    logging: *default-logging

  # Optional: TubeArchivist - YouTube/Twitch Archival
  # WARNING: High resource usage (3-4GB RAM for Elasticsearch)
  # Uncomment only if running Scenario 2 (Optimized) with zram enabled
  #
  # tubearchivist:
  #   image: bbilly1/tubearchivist:latest
  #   container_name: tubearchivist
  #   restart: unless-stopped
  #   environment:
  #     - ES_URL=http://tubearchivist-es:9200
  #     - REDIS_HOST=tubearchivist-redis
  #     - HOST_UID=1000
  #     - HOST_GID=1000
  #     - TA_USERNAME=admin
  #     - TA_PASSWORD=changeme
  #     - ELASTIC_PASSWORD=changeme
  #     - TZ=America/New_York
  #   volumes:
  #     - ./tubearchivist/media:/youtube
  #     - ./tubearchivist/cache:/cache
  #   ports:
  #     - "8000:8000"
  #   depends_on:
  #     - tubearchivist-es
  #     - tubearchivist-redis
  #   networks:
  #     - media
  #   mem_limit: 2g
  #   logging: *default-logging
  #
  # tubearchivist-es:
  #   image: bbilly1/tubearchivist-es:latest
  #   container_name: tubearchivist-es
  #   restart: unless-stopped
  #   environment:
  #     - "ELASTIC_PASSWORD=changeme"
  #     - "discovery.type=single-node"
  #     - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
  #   volumes:
  #     - ./tubearchivist/es:/usr/share/elasticsearch/data
  #   networks:
  #     - media
  #   mem_limit: 2g
  #   logging: *default-logging
  #
  # tubearchivist-redis:
  #   image: redis:alpine
  #   container_name: tubearchivist-redis
  #   restart: unless-stopped
  #   volumes:
  #     - ./tubearchivist/redis:/data
  #   networks:
  #     - media
  #   mem_limit: 256m
  #   logging: *default-logging
```

**Deploy Media Stack:**

```bash
# Start services
cd /opt/media-stack
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps

# Access services:
# - Jellyfin: http://192.168.8.40:8096
# - Sonarr: http://192.168.8.40:8989
# - Radarr: http://192.168.8.40:7878
# - Prowlarr: http://192.168.8.40:9696
# - qBittorrent: http://192.168.8.40:8080
# - Audiobookshelf: http://192.168.8.40:13378
```

#### 4. Configure Media Services

**Jellyfin Initial Setup:**
1. Navigate to http://192.168.8.40:8096
2. Create admin account
3. Add media libraries:
   - Name: TV Shows, Path: `/media/tv`
   - Name: Movies, Path: `/media/movies`
   - Name: Music, Path: `/media/music`
4. **Settings → Playback:**
   - **Disable** hardware transcoding (N3450 too slow)
   - Enable direct play for all formats
5. **Settings → Networking:**
   - LAN networks: `192.168.0.0/16`

**Prowlarr Setup:**
1. Navigate to http://192.168.8.40:9696
2. **Indexers → Add:** Configure your indexers (1337x, RARBG, etc.)
3. **Settings → Apps:**
   - Add Sonarr: `http://sonarr:8989`, API key from Sonarr settings
   - Add Radarr: `http://radarr:7878`, API key from Radarr settings
4. **Sync App Indexers** (pushes indexers to Sonarr/Radarr)

**Sonarr Setup:**
1. Navigate to http://192.168.8.40:8989
2. **Settings → Media Management:**
   - Root folder: `/tv`
   - Rename episodes: Yes
   - File naming format: `{Series Title} - S{season:00}E{episode:00} - {Episode Title}`
3. **Settings → Indexers:** (Auto-configured by Prowlarr)
4. **Settings → Download Clients:**
   - Add qBittorrent: `qbittorrent:8080`, username/password
   - Category: `tv`
5. **Series → Add New:** Search and add your TV shows

**Radarr Setup:**
1. Navigate to http://192.168.8.40:7878
2. **Settings → Media Management:**
   - Root folder: `/movies`
   - Rename movies: Yes
   - File naming format: `{Movie Title} ({Release Year})`
3. **Settings → Indexers:** (Auto-configured by Prowlarr)
4. **Settings → Download Clients:**
   - Add qBittorrent: `qbittorrent:8080`, username/password
   - Category: `movies`
5. **Movies → Add New:** Search and add movies

**qBittorrent Setup:**
1. Navigate to http://192.168.8.40:8080
2. Default credentials: `admin` / `adminadmin` (change immediately!)
3. **Settings → Downloads:**
   - Default save path: `/downloads/complete`
   - Temp path: `/downloads/incomplete`
4. **Settings → Connection:**
   - Listening port: `6881`
5. **Settings → BitTorrent:**
   - Max active downloads: `3` (limit for Zimaboard CPU)
6. **Settings → Speed:**
   - Global rate limits: 50 MB/s down, 10 MB/s up (adjust as needed)

### Phase 2 Validation

```bash
# Check all containers running
docker compose ps

# Verify media library accessible
ls -lah /mnt/storage/media/

# Test Jellyfin playback
# - Add test video to /mnt/storage/media/movies/
# - Scan library in Jellyfin
# - Play video (should direct play, no transcoding)

# Test *arr automation
# - Add a TV show in Sonarr
# - Verify it searches indexers (Prowlarr)
# - Verify it sends to qBittorrent
# - Verify download completes and imports

# Monitor resource usage
docker stats
```

**Phase 2 Complete When:**
- ✅ BTRFS RAID1 operational and persistent
- ✅ NAS accessible via SMB (test from client PC)
- ✅ All media containers running
- ✅ Jellyfin library scanning and playback working
- ✅ Sonarr/Radarr → Prowlarr → qBittorrent pipeline functional
- ✅ Downloaded media auto-importing into Jellyfin

**Resources Used:** ~6-8GB RAM, ~2-3 CPU cores (without TubeArchivist)

---

## 🧠 Phase 3: Knowledge & Brain Stack

### Objectives
1. Deploy Silverbullet for markdown-based note-taking
2. Setup Paperless-ngx for document management with OCR
3. Configure PostgreSQL for database backend
4. Implement backup and restore procedures

### Architecture

**Services (in Docker LXC):**
- Silverbullet: Personal knowledge management (256-512MB)
- Paperless-ngx: Document database with OCR (2-3GB)
- PostgreSQL: Database backend (512MB-1GB)
- Redis: Cache for Paperless (256MB)

**Storage:**
- Configuration: LXC local storage
- Documents: Bind-mounted from /mnt/storage/documents
- Backups: Bind-mounted from /mnt/storage/backups

### Deployment Steps

The knowledge stack is fully pre-configured in `/home/user/M-Claude/Projects/knowledge-stack/`.

#### 1. Create Docker LXC Container

```bash
# Create LXC container for knowledge stack
pct create 150 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname docker-knowledge \
  --memory 6144 \
  --cores 2 \
  --rootfs local-lvm:32 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.50/24,gw=192.168.8.1 \
  --features nesting=1,keyctl=1

# Bind mount storage
pct set 150 -mp0 /mnt/storage/documents,mp=/mnt/storage/documents
pct set 150 -mp1 /mnt/storage/backups,mp=/mnt/storage/backups

# Start container
pct start 150
pct enter 150

# Install Docker (same as Phase 2)
apt update
apt install -y curl gnupg ca-certificates
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### 2. Deploy Knowledge Stack

```bash
# Create directory
mkdir -p /opt/knowledge-stack
cd /opt/knowledge-stack

# Transfer files from Projects/knowledge-stack/
# (Use scp, rsync, or pct push)

# From Proxmox host:
pct push 150 /home/user/M-Claude/Projects/knowledge-stack/docker-compose.yml /opt/knowledge-stack/docker-compose.yml
pct push 150 /home/user/M-Claude/Projects/knowledge-stack/.env.template /opt/knowledge-stack/.env.template
pct push 150 /home/user/M-Claude/Projects/knowledge-stack/setup.sh /opt/knowledge-stack/setup.sh
pct push 150 /home/user/M-Claude/Projects/knowledge-stack/backup.sh /opt/knowledge-stack/backup.sh
pct push 150 /home/user/M-Claude/Projects/knowledge-stack/restore.sh /opt/knowledge-stack/restore.sh

# Enter container again
pct enter 150
cd /opt/knowledge-stack

# Make scripts executable
chmod +x setup.sh backup.sh restore.sh

# Run automated setup
./setup.sh

# Access services:
# - Silverbullet: http://192.168.8.50:3000
# - Paperless-ngx: http://192.168.8.50:8000
```

The setup script will:
- ✅ Check dependencies
- ✅ Generate secure passwords
- ✅ Create `.env` file
- ✅ Create directory structure
- ✅ Pull Docker images
- ✅ Start services
- ✅ Create Paperless admin user
- ✅ Verify health

#### 3. Configure Paperless-ngx

```bash
# Access Paperless: http://192.168.8.50:8000
# Login with credentials from setup script

# Initial configuration (via Web UI):
# 1. Settings → OCR:
#    - Language: English (add others as needed)
#    - OCR mode: Skip/Redo
# 2. Settings → Document Processing:
#    - Auto-tagging: Enabled
#    - Archive path: /archive
# 3. Documents → Upload:
#    - Test with a PDF document
#    - Verify OCR extraction works
```

#### 4. Configure Silverbullet

```bash
# Access Silverbullet: http://192.168.8.50:3000

# Create first note:
# - Click "+" to create new page
# - Try wiki-style linking: [[Another Page]]
# - Use templates: #template/daily-note

# Silverbullet features:
# - Markdown-based
# - Wiki-style linking
# - Templates and queries
# - Offline PWA support
# - Git-friendly (plain text files)
```

#### 5. Setup Automated Backups

```bash
# On Proxmox host, create cron job for backups
crontab -e

# Add daily backup at 3 AM
0 3 * * * pct exec 150 -- /opt/knowledge-stack/backup.sh >> /var/log/knowledge-backup.log 2>&1

# Test backup manually
pct exec 150 -- /opt/knowledge-stack/backup.sh

# Verify backup created
ls -lah /mnt/storage/backups/knowledge-stack/
```

### Phase 3 Validation

```bash
# Check all containers running
docker compose ps

# Test Silverbullet
# - Create a note
# - Add wiki link
# - Verify auto-save

# Test Paperless OCR
# - Upload scanned PDF
# - Wait for processing (watch logs: docker compose logs -f paperless)
# - Verify OCR text extracted (view document in web UI)
# - Test full-text search

# Test backup/restore
cd /opt/knowledge-stack
./backup.sh
# Verify backup files created in /mnt/storage/backups/knowledge-stack/

# Monitor resource usage
docker stats
```

**Phase 3 Complete When:**
- ✅ All containers running and healthy
- ✅ Silverbullet accessible, notes saving
- ✅ Paperless OCR processing documents
- ✅ Full-text search working
- ✅ Automated backups configured
- ✅ Backup/restore tested successfully

**Resources Used:** ~3-4.5GB RAM, ~1-2 CPU cores

**Cumulative Total:** ~12-14GB RAM, ~4-5 CPU cores ⚠️ *Approaching limit*

---

## 🏠 Phase 4: IoT & Home Automation

### Objectives
1. Deploy Home Assistant for smart home control
2. Configure MQTT broker for IoT messaging
3. Setup BirdNET-Go for bird identification
4. Configure Grafana for visualization

### Architecture

**Services (in Docker LXC):**
- Home Assistant: Smart home hub (1-2GB)
- Mosquitto: MQTT broker (128-256MB)
- BirdNET-Go: Bird identification AI (512MB-1GB)
- Grafana: Metrics visualization (512MB-1GB)

### Deployment Steps

#### 1. Create Docker LXC for IoT Stack

```bash
# Create LXC container
pct create 160 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname docker-iot \
  --memory 4096 \
  --cores 2 \
  --rootfs local-lvm:20 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.8.60/24,gw=192.168.8.1 \
  --features nesting=1,keyctl=1

# Optional: USB passthrough for Zigbee/Z-Wave
# Identify USB device on host:
lsusb
ls -l /dev/serial/by-id/

# Add device to container config
echo "lxc.cgroup2.devices.allow: c 188:* rwm" >> /etc/pve/lxc/160.conf
echo "lxc.mount.entry: /dev/ttyUSB0 dev/ttyUSB0 none bind,optional,create=file" >> /etc/pve/lxc/160.conf

# Start container
pct start 160
pct enter 160

# Install Docker
apt update
apt install -y curl gnupg ca-certificates
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### 2. Deploy IoT Stack

```bash
# Create directory
mkdir -p /opt/iot-stack
cd /opt/iot-stack

# Transfer home-assistant-docker-compose.yml
# From Proxmox host:
pct push 160 /home/user/M-Claude/home-assistant-docker-compose.yml /opt/iot-stack/docker-compose.yml
pct push 160 /home/user/M-Claude/mosquitto.conf /opt/iot-stack/mosquitto.conf

# Back in container, deploy
cd /opt/iot-stack
docker compose up -d

# Access services:
# - Home Assistant: http://192.168.8.60:8123
# - Grafana: http://192.168.8.60:3000
```

#### 3. Configure Home Assistant

```bash
# Initial setup via web UI
# Navigate to: http://192.168.8.60:8123

# Create admin account
# Configure location, time zone
# Skip integrations for now

# Configure MQTT integration:
# Settings → Devices & Services → Add Integration
# Search: MQTT
# Host: mosquitto (container name)
# Port: 1883
# Username/Password: (from docker-compose.yml)
```

#### 4. Deploy BirdNET-Go

**Add BirdNET-Go to docker-compose.yml:**

```yaml
  birdnet-go:
    image: ghcr.io/tphakala/birdnet-go:latest
    container_name: birdnet-go
    restart: unless-stopped
    environment:
      - TZ=America/New_York
    volumes:
      - ./birdnet-go/config:/config
      - ./birdnet-go/data:/data
    ports:
      - "8080:8080"
    devices:
      - /dev/snd:/dev/snd  # Audio device
    networks:
      - iot
    mem_limit: 1g
    cpu_shares: 512
    logging: *default-logging
```

**Start BirdNET-Go:**

```bash
docker compose up -d birdnet-go

# Access web UI: http://192.168.8.60:8080

# Configure MQTT output:
# Settings → MQTT:
#   - Broker: mosquitto:1883
#   - Topic: birdnet/sightings
#   - Enable
```

#### 5. Configure Home Assistant + BirdNET Integration

```yaml
# Add to Home Assistant configuration.yaml
mqtt:
  sensor:
    - name: "Latest Bird Detection"
      state_topic: "birdnet/sightings"
      value_template: "{{ value_json.species }}"
      json_attributes_topic: "birdnet/sightings"
      json_attributes_template: "{{ value_json | tojson }}"

automation:
  - alias: "Notify on Rare Bird"
    trigger:
      platform: mqtt
      topic: birdnet/sightings
    condition:
      condition: template
      value_template: "{{ trigger.payload_json.confidence > 0.9 }}"
    action:
      service: notify.mobile_app
      data:
        title: "Rare Bird Detected!"
        message: "{{ trigger.payload_json.species }} at {{ trigger.payload_json.confidence }}% confidence"
```

### Phase 4 Validation

```bash
# Check all containers running
docker compose ps

# Test Home Assistant
# - Create simple automation
# - Test MQTT connection

# Test BirdNET-Go
# - Access web UI
# - Check MQTT messages: docker compose exec mosquitto mosquitto_sub -t 'birdnet/#' -v

# Monitor resource usage
docker stats
```

**Phase 4 Complete When:**
- ✅ Home Assistant accessible and responsive
- ✅ MQTT broker operational
- ✅ BirdNET-Go detecting birds (if microphone present)
- ✅ MQTT messages flowing to Home Assistant
- ✅ Grafana dashboards configured

**Resources Used:** ~2.5-4GB RAM, ~1-2 CPU cores

**Cumulative Total:** ~14.5-18GB RAM ❌ **EXCEEDS CAPACITY**

**⚠️ CRITICAL:** At this point, you must enable zram swap OR skip some services.

---

## ⚡ Resource Management & Optimization

### Enable Zram Compressed Swap

```bash
# On Proxmox host
apt install -y zram-tools

# Configure zram
nano /etc/default/zramswap

# Set:
ALGO=lz4
PERCENT=50  # 50% of RAM = 8GB compressed swap

# Enable zram
systemctl enable zramswap
systemctl start zramswap

# Verify
zramctl
swapon --show

# Expected output:
# NAME       TYPE SIZE  USED PRIO
# /dev/zram0 swap 8G    0B   100

# This provides ~4-6GB effective additional RAM
```

### Resource Monitoring

```bash
# Install monitoring tools (on Proxmox host)
apt install -y glances htop iotop

# Run Glances web interface
glances -w --port 61208 &

# Access monitoring: http://192.168.8.21:61208

# Set up resource alerts
# See RESOURCE-ANALYSIS.md for full monitoring setup
```

---

## 🎁 Phase 6: Wildcard Modules (Optional)

See **WILDCARD-MODULES.md** for detailed guides on:

1. **AdGuard Home** (150MB RAM) - Network-wide ad blocking
   - Deploy immediately after Phase 1
   - Minimal resource cost, huge benefit

2. **n8n** (400MB RAM) - Workflow automation
   - Deploy after Phase 3
   - Connects all services with visual workflows

3. **Ollama** (4-8GB RAM) - Local LLM
   - Only if running minimal stack with zram
   - Or run on Legion instead

---

## 📊 Final Resource Summary

### Minimal Viable Stack (Recommended)
| Component | RAM | CPU |
|-----------|-----|-----|
| Proxmox Host | 1.5GB | 0.5 |
| Network Services | 1GB | 0.4 |
| NAS (OMV) | 1GB | 0.3 |
| Media Stack (Jellyfin + 2 *arr) | 4GB | 1.2 |
| Knowledge Stack (Silverbullet + Paperless) | 3GB | 1.1 |
| IoT Stack (HA + MQTT) | 1.5GB | 0.5 |
| **Total** | **12GB** | **4.0** |
| **vs Available** | 14.5GB | 3.5 cores |
| **Headroom** | +2.5GB | -0.5 cores |

### With Zram + Wildcard Modules
| Component | RAM (apparent) | Actual |
|-----------|----------------|--------|
| Base Stack | 12GB | 12GB |
| AdGuard Home | 150MB | 150MB |
| n8n | 400MB | 400MB |
| BirdNET-Go | 1GB | 1GB |
| Grafana | 512MB | 512MB |
| **Subtotal** | **14GB** | **14GB** |
| **Zram Swap** | +4-6GB | compressed |
| **Effective Total** | **18-20GB** | 14GB + 4-6GB swap |

---

## 🎓 Best Practices

### Deployment
1. ✅ Follow phases sequentially
2. ✅ Monitor resources after each phase
3. ✅ Wait 24-48 hours between major additions
4. ✅ Test backups before adding next service
5. ✅ Document all customizations

### Operations
1. ✅ Weekly backup verification
2. ✅ Monthly resource usage review
3. ✅ Quarterly service audit (disable unused)
4. ✅ Update containers monthly (test first)
5. ✅ Monitor logs for errors

### Security
1. ✅ Change all default passwords
2. ✅ Enable firewall rules
3. ✅ Restrict SSH to management network
4. ✅ Use VPN for external access (not port forwarding)
5. ✅ Regular security scans (Nessus)

---

## 🆘 Troubleshooting

### Out of Memory
```bash
# Check memory usage
free -h

# Identify memory hog
ps aux --sort=-%mem | head -20

# Stop non-critical services
cd /opt/media-stack
docker compose stop tubearchivist  # If enabled

# Clear cache
sync; echo 3 > /proc/sys/vm/drop_caches
```

### High CPU Load
```bash
# Check CPU usage
htop

# Identify CPU hog
top -o %CPU

# Reduce Jellyfin simultaneous transcodes (if enabled)
# Reduce qBittorrent active downloads
# Pause Paperless OCR processing
```

### Service Won't Start
```bash
# Check logs
docker compose logs -f <service-name>

# Check resource limits
docker stats

# Restart container
docker compose restart <service-name>

# Rebuild if necessary
docker compose up -d --force-recreate <service-name>
```

---

## 📖 Additional Resources

- **NETWORK-TOPOLOGY.md:** Detailed network diagrams and port mappings
- **RESOURCE-ANALYSIS.md:** Comprehensive resource analysis
- **WILDCARD-MODULES.md:** Optional service guides
- **Projects/knowledge-stack/README.md:** Knowledge stack documentation

---

## ✅ Deployment Checklist

### Foundation
- [ ] Proxmox installed and updated
- [ ] Network bridges configured
- [ ] Firewall rules active
- [ ] DHCP server configured (optional)
- [ ] Client devices connecting

### Storage & Media
- [ ] BTRFS RAID1 configured
- [ ] NAS accessible via SMB
- [ ] Media stack deployed
- [ ] Jellyfin playing media
- [ ] *arr automation working

### Knowledge
- [ ] Knowledge stack deployed
- [ ] Silverbullet accessible
- [ ] Paperless OCR working
- [ ] Backups configured

### IoT & Automation
- [ ] Home Assistant deployed
- [ ] MQTT broker operational
- [ ] Integrations configured
- [ ] Automations tested

### Monitoring
- [ ] Glances installed
- [ ] Resource monitoring active
- [ ] Alerts configured
- [ ] Documentation updated

---

**Deployment Guide Version:** 2.0
**Last Updated:** 2026-01-16
**Target Hardware:** Zimaboard 16GB
**Base Platform:** Proxmox VE 8.x
**Status:** Production Ready

---

**Ready to begin? Start with [Phase 1: Advanced Networking](#-phase-1-advanced-networking--switching)**

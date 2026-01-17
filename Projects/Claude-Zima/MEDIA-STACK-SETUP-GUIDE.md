# Complete Media Stack Setup Guide for Zimaboard Proxmox

## Table of Contents
1. [Hardware Overview](#hardware-overview)
2. [NAS Solution Design](#nas-solution-design)
3. [Acquisition Tools](#acquisition-tools)
4. [The *arr Stack](#the-arr-stack)
5. [Media Servers](#media-servers)
6. [Setup Instructions](#setup-instructions)
7. [Resource Allocation Summary](#resource-allocation-summary)

---

## Hardware Overview

### Zimaboard Specifications (N3450 Model)
- **CPU**: Intel Celeron N3450 Quad-Core (Apollo Lake)
- **RAM**: 8GB (832 model) or 4GB (432 model)
- **Storage**: Dual SATA 3.0 ports (via Y-cable)
- **Power**: 6W TDP, 12V/3A power supply
- **Features**: VT-d, VT-x, Intel Quick Sync Video
- **Network**: Dual Gigabit Ethernet

### Key Constraints
- Limited RAM (8-16GB total system)
- Low-power CPU optimized for efficiency
- Two SATA ports maximum (expandable via Y-cable)
- Fanless design (thermal considerations)

---

## 1. NAS Solution Design

### Recommended Approach: LXC Container + Custom NAS

**Winner: OpenMediaVault in LXC Container**

#### Why OpenMediaVault?
- **Ultra-lightweight**: Runs efficiently on 1GB RAM minimum
- **Debian-based**: Stable, well-documented, large community
- **Perfect for Zimaboard**: Minimal overhead compared to TrueNAS Scale
- **Docker support**: Can run Docker containers alongside NAS functions
- **Web-based management**: Easy configuration through GUI

#### LXC vs VM Decision
**Use LXC for:**
- Lower overhead (no hypervisor layer)
- Near-native disk performance
- Better RAM efficiency (critical for 8GB system)
- Direct hardware passthrough support
- Faster startup times

#### Filesystem Selection: BTRFS

**Why BTRFS over ZFS and EXT4?**

**BTRFS Advantages:**
- **Low RAM requirements**: Works well with 2-4GB allocated (vs ZFS requiring 8GB minimum)
- **CoW (Copy-on-Write)**: Data integrity without performance penalty
- **Built-in snapshots**: Easy backups and rollbacks
- **Compression**: Save space on text files, subtitles, etc.
- **Self-healing**: Automatic error correction in RAID configurations
- **Subvolumes**: Flexible partition management without repartitioning

**Compared to alternatives:**
- **vs ZFS**: BTRFS uses 1/4 the RAM and doesn't need tuning
- **vs EXT4**: BTRFS adds data integrity features EXT4 lacks
- **2025 Status**: BTRFS is mature, stable, and recommended for home servers

### Storage Configuration with SATA Y-Cable

The official Zimaboard SATA Y-cable supports:
- **2x 2.5" HDDs/SSDs**: No external power needed
- **2x 3.5" HDDs**: Supported with 12V/3A PSU (tested by community)
- **Length**: 10cm for minimal cable management

#### Recommended Setup
```
Option 1: Dual 2.5" SSD (Fastest, Silent)
├── 1TB SSD - BTRFS RAID1 (mirror)
└── 1TB SSD - BTRFS RAID1 (mirror)
└── Result: 1TB usable, full redundancy

Option 2: Dual 2TB+ HDD (Maximum Capacity)
├── 2TB+ HDD - BTRFS RAID1
└── 2TB+ HDD - BTRFS RAID1
└── Result: 2TB+ usable, full redundancy

Option 3: Hybrid (Performance + Capacity)
├── 500GB SSD - Hot data, appdata, downloads
└── 2TB+ HDD - Cold storage, completed media
└── Result: BTRFS subvolumes with different priorities
```

### LXC Configuration for NAS

**Resource Allocation:**
- **RAM**: 2GB (up to 4GB for large libraries)
- **CPU**: 2 cores
- **Privileged**: Yes (for SATA passthrough)
- **Features**: `nesting=1,fuse=1`

**SATA Passthrough:**
```bash
# In Proxmox, identify your SATA devices
ls -l /dev/disk/by-id/

# Add to LXC config (/etc/pve/lxc/<ID>.conf)
lxc.cgroup2.devices.allow: b 8:0 rwm
lxc.cgroup2.devices.allow: b 8:1 rwm
lxc.mount.entry: /dev/sda dev/sda none bind,optional,create=file
lxc.mount.entry: /dev/sdb dev/sdb none bind,optional,create=file
```

### Alternative: Skip Dedicated NAS, Use Proxmox Host

For simplicity, you can:
1. Format drives as BTRFS RAID1 on Proxmox host
2. Mount at `/mnt/storage`
3. Bind mount into LXC containers running media apps
4. Saves 2GB RAM by skipping OpenMediaVault

**Trade-offs:**
- ✅ Simpler setup
- ✅ More RAM for media apps
- ❌ No web GUI for storage management
- ❌ Less portable (tied to Proxmox host)

---

## 2. Acquisition Tools

### Torrent Client: qBittorrent

**Winner: qBittorrent** (best balance of features and efficiency)

**Resource Comparison:**
| Client       | RAM Usage | CPU Usage | Notes                           |
|--------------|-----------|-----------|----------------------------------|
| Transmission | ~50MB     | 2%        | Most lightweight, fewer features |
| qBittorrent  | ~100MB    | 5-10%     | Feature-rich, efficient C++     |
| Deluge       | ~150MB+   | 10-15%    | Python overhead in headless mode |

**Why qBittorrent?**
- Modern, actively maintained
- Built-in search engine
- Category-based auto-management
- RSS feed support
- Better integration with *arr apps
- Still lightweight for resource-constrained systems

**Configuration:**
- Allocate: 1GB RAM limit, 2 CPU cores
- Enable: Category-based saving
- Set: Max active downloads: 3-5 (for Zimaboard)

### VPN: Gluetun

**Why Gluetun?**
- Supports 40+ VPN providers
- Single container for all VPN traffic
- Kill switch built-in
- Network modes for routing other containers
- Mullvad, Windscribe, ProtonVPN, etc.

**Security Model:**
All acquisition containers route through Gluetun using `network_mode: "service:gluetun"`:
- qBittorrent
- Prowlarr
- autobrr (if used)

This ensures your real IP never leaks during downloads.

### Private Tracker Management: autobrr

**What is autobrr?**
- Monitors IRC announce channels + RSS feeds
- Automatically grabs torrents matching your filters
- Critical for racing on private trackers
- Lightweight (written in Go)

**Features:**
- Filter by resolution, codec, release group
- Send to specific categories in qBittorrent
- Cross-seed automation
- Integration with *arr apps

**Resource Usage:** ~128MB RAM, <5% CPU

### IPFS Node

**Use Case:** Decentralized media sharing, backup distribution

**Configuration:**
- Port 4001: Swarm (P2P communication)
- Port 8080: HTTP Gateway (read-only access)
- Port 5001: API (localhost only - security risk if exposed)

**Resource:** 512MB RAM, 1 CPU core

### YouTube/Twitch Archival: TubeArchivist

**Why TubeArchivist over TubeSync?**

| Feature           | TubeArchivist | TubeSync     |
|-------------------|---------------|--------------|
| Search            | Full-text ES  | Basic        |
| Subtitles         | Searchable    | Downloaded   |
| Comments          | Archived      | No           |
| Scale             | 100k+ videos  | Smaller libs |
| Resource Usage    | 3-4GB stack   | <1GB         |

**Recommendation:**
- **TubeArchivist**: If you're serious about archival (activists, researchers)
- **TubeSync**: If you just want to download channels casually

**TubeArchivist Stack:**
- TubeArchivist: Main app (2GB RAM)
- Elasticsearch: Search backend (1GB RAM)
- Redis: Job queue (256MB RAM)
- Total: ~3-4GB allocated

For Zimaboard, this is a **heavy component**. Consider:
- Running it on-demand (not 24/7)
- Using TubeSync if you don't need full-text search
- Allocating 4GB+ RAM to Zimaboard if using TubeArchivist

---

## 3. The *arr Stack

### Core Components

#### Prowlarr - Indexer Manager (Port 9696)
**Purpose:** Central management for all torrent/NZB indexers

**Features:**
- Add indexers once, sync to all *arr apps
- Test indexers automatically
- Statistics and health monitoring
- Supports 500+ indexers

**Setup:**
1. Add indexers (public: 1337x, RARBG; private: pass keys)
2. Add apps (Sonarr, Radarr, etc.) - Prowlarr auto-configures them
3. Enable auto-sync

**Resources:** 256MB RAM, 0.25 CPU

#### Sonarr - TV Shows (Port 8989)
**Purpose:** Automatic TV show downloads

**Features:**
- Episode tracking and calendar
- Quality profiles (1080p, 4K, etc.)
- Automatic renaming and organization
- Integration with Jellyfin for metadata

**Setup:**
1. Add root folder: `/tv`
2. Set quality profile (e.g., "Web-DL 1080p")
3. Connect to qBittorrent (use container name: `gluetun:8080`)
4. Add shows via TVDB ID or search

**Resources:** 256-512MB RAM, 0.25-1 CPU

#### Radarr - Movies (Port 7878)
**Purpose:** Automatic movie downloads

**Configuration:** Same as Sonarr but for movies
- Root folder: `/movies`
- TMDb integration
- NetImport lists (e.g., IMDb Top 250)

**Resources:** 256-512MB RAM, 0.25-1 CPU

#### Lidarr - Music (Port 8686)
**Purpose:** Automatic music downloads

**Note:** Less mature than Sonarr/Radarr
- Best for Usenet (NZBs)
- Torrent support is improving
- MusicBrainz metadata

**Resources:** 256-512MB RAM, 0.25-1 CPU

#### Readarr - Books/Audiobooks (Port 8787)
**Purpose:** Automatic ebook/audiobook downloads

**Features:**
- Calibre integration
- GoodReads lists
- Quality profiles for formats (EPUB, PDF, M4B)

**Resources:** 256-512MB RAM, 0.25-1 CPU

#### Mylar3 - Comics/Manga (Port 8090)
**Purpose:** Automatic comic book downloads

**Features:**
- ComicVine integration
- CBR/CBZ support
- Story arc tracking
- Pull list management

**Resources:** 256-512MB RAM, 0.25-1 CPU

#### Whisparr - Adult Content (Port 6969) [OPTIONAL]
**Purpose:** Automatic adult content downloads

**Features:**
- Same UI as Radarr
- TPDB (The Porn Database) integration
- Performer tracking
- Studio filtering

**Resources:** 256-512MB RAM, 0.25-1 CPU

**Note:** Commented out in docker-compose by default. Uncomment if needed.

### Integration Pattern

```
User Request (Jellyseerr)
    ↓
Sonarr/Radarr (monitors wanted list)
    ↓
Prowlarr (searches all indexers)
    ↓
qBittorrent (via Gluetun VPN - downloads)
    ↓
*arr (moves to media folder, renames)
    ↓
Jellyfin (scans library, adds metadata)
    ↓
User watches content
```

### Path Configuration (CRITICAL)

**All containers must use identical paths:**

```yaml
volumes:
  - /mnt/storage/downloads:/downloads
  - /mnt/storage/media/movies:/movies
  - /mnt/storage/media/tv:/tv
```

**Why?** Allows instant moves (hardlinks) instead of slow copies.

**Inside qBittorrent:**
- Downloads to: `/downloads/complete/movies` or `/downloads/complete/tv`

**Inside Radarr/Sonarr:**
- Reads from: `/downloads/complete/movies` (same path)
- Moves to: `/movies/Movie Title (Year)/Movie.mkv` (instant, no copy)

---

## 4. Media Servers

### Jellyfin vs Plex (2025 Decision)

| Feature                | Jellyfin      | Plex          |
|------------------------|---------------|---------------|
| **Cost**               | Free          | Free/$250 Pass|
| **Hardware Transcoding**| Free          | Plex Pass Only|
| **Quick Sync Support** | Yes           | Yes           |
| **Open Source**        | Yes           | No            |
| **Privacy**            | Self-hosted   | Phones home   |
| **Mobile Apps**        | Free          | Free          |
| **Ease of Setup**      | Medium        | Easy          |
| **Plugin Ecosystem**   | Growing       | Extensive     |
| **4K HDR Support**     | Excellent     | Excellent     |

**Winner for Zimaboard: Jellyfin**

**Reasons:**
1. **Free hardware transcoding** (Plex requires $250 Plex Pass)
2. **Intel Quick Sync** works identically in both
3. **Lower resource usage** (no analytics/telemetry)
4. **Privacy**: No data sent to external servers
5. **N3450 Quick Sync**: Handles multiple 1080p transcodes, some 4K

### Intel Quick Sync on Zimaboard

**What is Quick Sync?**
Hardware-accelerated video transcoding using Intel's iGPU.

**N3450 Capabilities:**
- Encode: H.264 (AVC), H.265 (HEVC), VP8
- Decode: H.264, H.265, VP8, VP9
- Performance: 3-5x 1080p transcodes simultaneously
- Power: Uses ~2W additional power (vs 20W+ for CPU transcoding)

**Enabling Quick Sync in Jellyfin:**
1. Pass `/dev/dri` device to container
2. Install Intel OpenCL mod: `DOCKER_MODS=linuxserver/mods:jellyfin-opencl-intel`
3. In Jellyfin: Dashboard → Playback → Hardware Acceleration → Intel Quick Sync

### Audiobookshelf (Port 13378)

**Why Audiobookshelf?**
- **All-in-one**: Audiobooks + Podcasts + eBooks
- **Mobile apps**: iOS and Android (free)
- **Progress sync**: Resume across devices
- **Modern UI**: Beautiful, intuitive interface
- **Automatic metadata**: Audible, iTunes, Google Books

**Features:**
- Chapter support
- Variable playback speed
- Sleep timer
- Collections and playlists
- Multi-user with separate progress

**Resources:** 512MB-1GB RAM, 0.5-2 CPU cores

### Podcast Management

**Option 1: Audiobookshelf** (recommended)
- Built-in podcast support
- Auto-download episodes
- Same app as audiobooks

**Option 2: Podgrab** (standalone)
- Lightweight (~128MB RAM)
- Simple interface
- GPodder sync support
- Use if you don't need audiobooks

**Resources:** 128-256MB RAM, 0.1-0.5 CPU

---

## 5. Setup Instructions

### Prerequisites

1. **Proxmox installed** on Zimaboard
2. **Two drives** connected via Y-cable
3. **LXC container** (Ubuntu 22.04 or Debian 12)
4. **Docker and Docker Compose** installed in LXC

### Step 1: Prepare Storage

#### Option A: BTRFS RAID1 on Proxmox Host

```bash
# On Proxmox host
# Install btrfs-progs
apt update && apt install btrfs-progs

# Create BTRFS RAID1
mkfs.btrfs -d raid1 -m raid1 /dev/sda /dev/sdb

# Mount
mkdir -p /mnt/storage
mount /dev/sda /mnt/storage

# Add to /etc/fstab
echo "UUID=$(blkid -s UUID -o value /dev/sda) /mnt/storage btrfs defaults,compress=zstd:3 0 0" >> /etc/fstab

# Create directory structure
cd /mnt/storage
mkdir -p appdata downloads/{complete,incomplete,watch} media/{movies,tv,music,books,audiobooks,podcasts,comics,youtube}

# Set permissions
chown -R 1000:1000 /mnt/storage
chmod -R 775 /mnt/storage
```

#### Option B: OpenMediaVault in LXC

```bash
# Create privileged LXC container
# In Proxmox: Create CT → Debian 12 → 2GB RAM, 2 cores, 20GB disk

# Pass through SATA drives (add to /etc/pve/lxc/<ID>.conf)
lxc.cgroup2.devices.allow: b 8:* rwm
lxc.mount.entry: /dev/sda dev/sda none bind,optional,create=file
lxc.mount.entry: /dev/sdb dev/sdb none bind,optional,create=file

# Inside LXC, install OMV
wget -O - https://github.com/OpenMediaVault-Plugin-Developers/installScript/raw/master/install | bash

# Configure BTRFS RAID1 via OMV web UI (https://IP-ADDRESS)
```

### Step 2: Create Docker LXC Container

```bash
# In Proxmox UI
# Create CT → Ubuntu 22.04 LTS
# RAM: 6GB (for 8GB system) or 14GB (for 16GB system)
# CPU: 4 cores
# Disk: 32GB (for Docker images)
# Features: keyctl=1, nesting=1, fuse=1

# Start container and enter shell
pct start <ID>
pct enter <ID>

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable --now docker

# Install Docker Compose
apt install docker-compose-plugin

# Add user to docker group
usermod -aG docker $USER
```

### Step 3: Mount Storage in LXC

```bash
# On Proxmox host, add to /etc/pve/lxc/<ID>.conf
mp0: /mnt/storage,mp=/mnt/storage

# Restart container
pct restart <ID>

# Inside container, verify mount
df -h | grep /mnt/storage
```

### Step 4: Deploy Media Stack

```bash
# Inside Docker LXC container
cd /opt
mkdir media-stack && cd media-stack

# Copy docker-compose.yml and .env.example
# (Transfer files from this guide)

# Create .env file
cp .env.example .env
nano .env
# Fill in VPN credentials and passwords

# Create required directories (if not done in Step 1)
mkdir -p /mnt/storage/appdata/{gluetun,qbittorrent,prowlarr,sonarr,radarr,lidarr,readarr,mylar3,jellyfin,audiobookshelf,podgrab,tubearchivist,homepage}

# Deploy stack
docker compose up -d

# Check logs
docker compose logs -f

# Verify all containers are running
docker ps
```

### Step 5: Configure Services

#### 5.1 Gluetun (VPN)

```bash
# Test VPN connection
docker exec gluetun wget -qO- ifconfig.me
# Should show VPN IP, not your real IP

# If using Mullvad, get WireGuard config from their site
# If using Windscribe, generate OpenVPN config
# Update .env file with credentials
```

#### 5.2 qBittorrent

```
1. Open http://SERVER_IP:8080
2. Login: admin / adminadmin
3. Tools → Options → Web UI → Change password
4. Downloads → Save files to: /downloads/complete/{category}
5. Downloads → Enable categories: movies, tv, music, books, comics
6. Connection → Listening port: 6881
7. BitTorrent → Enable DHT, PeX, LSD
```

#### 5.3 Prowlarr

```
1. Open http://SERVER_IP:9696
2. Settings → Indexers → Add Indexer
   - Add public: 1337x, RARBG, TorrentGalaxy
   - Add private: Your tracker + API key
3. Settings → Apps → Add Application
   - Type: Sonarr
   - Prowlarr Server: http://prowlarr:9696
   - Sonarr Server: http://172.20.0.10:8989
   - API Key: (from Sonarr → Settings → General)
4. Repeat for Radarr, Lidarr, etc.
5. Test connectivity
```

#### 5.4 Sonarr / Radarr

```
1. Open http://SERVER_IP:8989 (Sonarr) or :7878 (Radarr)
2. Settings → Media Management
   - Enable: Rename episodes/movies
   - Root folder: /tv or /movies
3. Settings → Download Clients → Add → qBittorrent
   - Host: gluetun
   - Port: 8080
   - Username/Password: (from qBittorrent)
   - Category: tv or movies
4. Settings → General → Copy API Key
5. Add to Prowlarr (see 5.3)
```

#### 5.5 Jellyfin

```
1. Open http://SERVER_IP:8096
2. Setup wizard:
   - Language: English
   - User: admin + password
   - Media libraries:
     * Movies: /media/movies
     * TV Shows: /media/tv
     * Music: /media/music
3. Dashboard → Playback → Transcoding
   - Hardware acceleration: Intel Quick Sync (QSV)
   - Enable hardware encoding: Yes
4. Dashboard → Networking
   - Enable automatic port mapping: No (not needed)
   - LAN networks: 192.168.1.0/24 (adjust to your subnet)
```

#### 5.6 Jellyseerr (Request Management)

```
1. Open http://SERVER_IP:5055
2. Sign in with Jellyfin
3. Settings → Jellyfin → Connect
4. Settings → Services:
   - Add Sonarr: http://172.20.0.10:8989 + API key
   - Add Radarr: http://172.20.0.11:7878 + API key
5. Now users can request content via Jellyseerr!
```

#### 5.7 Homepage Dashboard

```
1. Open http://SERVER_IP:3000
2. Edit /mnt/storage/appdata/homepage/services.yaml:

---
- Media:
    - Jellyfin:
        href: http://SERVER_IP:8096
        icon: jellyfin.png
        description: Media Server
    - Sonarr:
        href: http://SERVER_IP:8989
        icon: sonarr.png
    - Radarr:
        href: http://SERVER_IP:7878
        icon: radarr.png

- Downloads:
    - qBittorrent:
        href: http://SERVER_IP:8080
        icon: qbittorrent.png
    - Prowlarr:
        href: http://SERVER_IP:9696
        icon: prowlarr.png

3. Refresh page to see dashboard
```

### Step 6: Test the Full Pipeline

1. **Request content:** Open Jellyseerr → Search "The Matrix" → Request
2. **Radarr searches:** Check Radarr → Activity → Queue
3. **qBittorrent downloads:** Check qBittorrent → Torrents (via VPN)
4. **Radarr imports:** After download, Radarr moves to `/movies`
5. **Jellyfin scans:** Dashboard → Scan Library → See "The Matrix"
6. **Watch:** Open Jellyfin → Play movie

---

## 6. Resource Allocation Summary

### Total Resource Usage (Estimated)

#### Always Running (24/7):
| Service         | RAM    | CPU   | Notes                          |
|-----------------|--------|-------|--------------------------------|
| Gluetun         | 128MB  | 0.25  | VPN tunnel                     |
| qBittorrent     | 512MB  | 0.5   | Idle state, increases when downloading |
| Prowlarr        | 256MB  | 0.25  | Indexer manager                |
| Sonarr          | 256MB  | 0.25  | TV automation                  |
| Radarr          | 256MB  | 0.25  | Movie automation               |
| Lidarr          | 256MB  | 0.25  | Music automation               |
| Readarr         | 256MB  | 0.25  | Book automation                |
| Mylar3          | 256MB  | 0.25  | Comic automation               |
| Jellyfin        | 2GB    | 1.0   | Media server (idle)            |
| Jellyseerr      | 256MB  | 0.25  | Request management             |
| Audiobookshelf  | 512MB  | 0.5   | Audiobook/podcast server       |
| Homepage        | 128MB  | 0.1   | Dashboard                      |
| **TOTAL**       | **5.1GB** | **4.1** | Base load                   |

#### Optional/On-Demand:
| Service         | RAM    | CPU   | Notes                          |
|-----------------|--------|-------|--------------------------------|
| TubeArchivist   | 2GB    | 0.5   | YouTube archival (main)        |
| TA Elasticsearch| 1GB    | 0.5   | Search backend                 |
| TA Redis        | 256MB  | 0.1   | Job queue                      |
| IPFS            | 512MB  | 0.25  | Decentralized storage          |
| Podgrab         | 128MB  | 0.1   | Podcast manager                |
| autobrr         | 128MB  | 0.1   | Private tracker automation     |
| Whisparr        | 256MB  | 0.25  | Adult content automation       |

### Zimaboard Capacity

**8GB RAM System:**
- Base load: 5.1GB
- Proxmox overhead: ~1GB
- **Available for transcoding/downloads:** ~2GB
- **Recommendation:** Skip TubeArchivist, use lightweight options only

**16GB RAM System:**
- Base load: 5.1GB
- Proxmox overhead: ~1GB
- **Available:** ~10GB
- **Can add:** TubeArchivist (3-4GB) + IPFS + extras

### CPU Load

**N3450 Quad-Core:**
- Base load: ~4 cores total (spread across all services)
- **Transcoding:** Quick Sync offloads to iGPU (minimal CPU impact)
- **Downloads:** Spikes to 100% during extraction/verification (temporary)
- **Idle:** <20% CPU usage

**Thermal Considerations:**
- Fanless design = passive cooling
- Keep ambient temp <25°C (77°F)
- Avoid sustained 100% CPU load
- Quick Sync is more thermally efficient than CPU transcoding

### Disk I/O

**BTRFS RAID1 Performance:**
- Sequential Read: ~100-150 MB/s (SSD) or ~80-120 MB/s (HDD)
- Sequential Write: ~80-120 MB/s (SSD) or ~60-90 MB/s (HDD)
- RAID1: Reads are fast, writes are halved

**Bottlenecks:**
- Gigabit Ethernet: Max 125 MB/s (real-world: ~110 MB/s)
- Multiple streams: Network saturates before disk
- Quick Sync transcoding: Minimal disk I/O (streams from RAM)

---

## 7. Advanced Tips

### Optimization for Zimaboard

#### 7.1 Reduce RAM Usage

```yaml
# In docker-compose.yml, add to each service:
deploy:
  resources:
    limits:
      memory: 512M  # Adjust per service
    reservations:
      memory: 256M
```

#### 7.2 Disable Unused Features

**Jellyfin:**
- Dashboard → Scheduled Tasks → Disable:
  - Chapter image extraction
  - Trickplay image generation (use CPU cycles)

**qBittorrent:**
- Disable embedded tracker
- Reduce max connections: 200 (default 500)

#### 7.3 Offload Heavy Tasks

**For 8GB systems:**
- Run TubeArchivist on a separate machine
- Use Podgrab instead of Audiobookshelf for podcasts only
- Disable comic/audiobook *arr apps if not needed

#### 7.4 Storage Management

**BTRFS Snapshots:**
```bash
# Create snapshot before major changes
btrfs subvolume snapshot /mnt/storage /mnt/storage-snapshot-$(date +%F)

# List snapshots
btrfs subvolume list /mnt/storage

# Restore from snapshot
mv /mnt/storage /mnt/storage-broken
mv /mnt/storage-snapshot-2025-01-16 /mnt/storage
```

**Compression:**
```bash
# Enable compression on existing files
btrfs filesystem defragment -r -czstd /mnt/storage

# Check compression ratio
compsize /mnt/storage
```

**Scrub (monthly):**
```bash
# Check for and repair errors
btrfs scrub start /mnt/storage
btrfs scrub status /mnt/storage
```

### Monitoring

#### Portainer (Optional)

```yaml
# Add to docker-compose.yml
portainer:
  image: portainer/portainer-ce:latest
  container_name: portainer
  ports:
    - "9443:9443"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
    - /mnt/storage/appdata/portainer:/data
  restart: unless-stopped
```

Access: https://SERVER_IP:9443

#### Grafana + Prometheus (Advanced)

For production monitoring:
- Prometheus: Scrape Docker metrics
- Grafana: Visualize CPU, RAM, disk, network
- Alerts: Email/Discord when issues occur

**Warning:** Adds ~512MB RAM overhead. Only for 16GB systems.

### Backup Strategy

#### 3-2-1 Rule
- **3** copies of data
- **2** different media types
- **1** offsite backup

**Implementation:**
```bash
# Weekly backup to external USB drive
rsync -avz --delete /mnt/storage/ /mnt/backup/

# Monthly backup to cloud (rclone)
rclone sync /mnt/storage/media remote:backup/media
```

**What to backup:**
1. `/mnt/storage/appdata` - Critical (configs, databases)
2. `/mnt/storage/media` - Important (your media library)
3. Docker volumes - Not needed (can recreate from compose file)

---

## 8. Troubleshooting

### Common Issues

#### Issue: VPN not connecting
```bash
# Check Gluetun logs
docker logs gluetun

# Test connection
docker exec gluetun ping 1.1.1.1

# Verify IP
docker exec gluetun wget -qO- ifconfig.me
```

#### Issue: *arr apps can't reach qBittorrent
- **Cause:** Network configuration error
- **Fix:** Use `gluetun:8080` as qBittorrent host (not `localhost` or `qbittorrent`)

#### Issue: Jellyfin not transcoding with Quick Sync
```bash
# Verify /dev/dri is accessible
docker exec jellyfin ls -la /dev/dri

# Check Jellyfin logs
docker logs jellyfin | grep -i "quick sync"

# Re-add OpenCL mod
# Edit docker-compose.yml, ensure:
# DOCKER_MODS=linuxserver/mods:jellyfin-opencl-intel
```

#### Issue: Slow file moves from downloads to media
- **Cause:** Different filesystems
- **Fix:** Ensure `/downloads` and `/media` are on same BTRFS filesystem

#### Issue: Out of memory errors
```bash
# Check RAM usage
docker stats

# Identify memory hog
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

# Reduce limits in docker-compose.yml
```

---

## 9. Security Considerations

### Network Security

1. **Firewall:** Only expose necessary ports (80, 443, media server)
2. **VPN:** All torrent traffic through Gluetun
3. **Reverse Proxy:** Use Nginx Proxy Manager or Traefik for HTTPS
4. **Authentication:** Enable auth on all web UIs

### IPFS Security

**Critical:** Do NOT expose port 5001 to internet
- Port 5001 = Full admin API (can delete files, change config)
- Only bind to 127.0.0.1 or VPN subnet

### SSH Hardening

```bash
# Disable root login
sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config

# Use SSH keys only
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Restart SSH
systemctl restart sshd
```

---

## 10. Conclusion

This complete media stack provides:
- ✅ Automated acquisition via *arr apps
- ✅ VPN protection for all downloads
- ✅ Hardware-accelerated streaming (Jellyfin + Quick Sync)
- ✅ Multi-format support (movies, TV, music, books, podcasts, audiobooks, comics)
- ✅ User-friendly request system (Jellyseerr)
- ✅ Optimized for Zimaboard's 8-16GB RAM constraint

**Estimated Setup Time:** 4-6 hours for full deployment and configuration

**Maintenance:** ~1 hour/month (updates, monitoring, backups)

**Total Cost:**
- Zimaboard: $150-250
- 2x Drives: $50-200 (depending on capacity)
- VPN: $5-10/month
- **Total:** $200-450 one-time + $5-10/month

Enjoy your self-hosted media empire!

---

## Sources and Further Reading

- [ZimaBoard Official Site](https://www.zimaspace.com/)
- [OpenMediaVault Documentation](https://docs.openmediavault.org/)
- [BTRFS Wiki](https://btrfs.wiki.kernel.org/)
- [Servarr Wiki](https://wiki.servarr.com/)
- [TRaSH Guides](https://trash-guides.info/) - *arr setup best practices
- [Jellyfin Documentation](https://jellyfin.org/docs/)
- [Intel Quick Sync](https://www.intel.com/content/www/us/en/architecture-and-technology/quick-sync-video/quick-sync-video-general.html)

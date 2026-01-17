# Media Stack Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ZIMABOARD HARDWARE                                  │
│  CPU: Intel N3450 (4 cores) | RAM: 8-16GB | Power: 6W TDP                  │
│  Storage: 2x SATA (via Y-cable) | Network: 2x 1GbE | iGPU: Quick Sync      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PROXMOX VE (Hypervisor)                             │
│                         Resource Management Layer                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
    ┌───────────────────────────┐      ┌───────────────────────────────┐
    │  LXC: OpenMediaVault      │      │  LXC: Docker Host             │
    │  (OPTIONAL)               │      │  Main Application Container    │
    │                           │      │                               │
    │  - SATA Passthrough       │      │  RAM: 6-14GB                  │
    │  - BTRFS RAID1            │      │  CPU: 4 cores                 │
    │  - NAS Web UI             │      │  Nesting: Enabled             │
    │  - RAM: 2GB               │      │                               │
    └──────────┬────────────────┘      └───────────┬───────────────────┘
               │                                    │
               │  /mnt/storage (bind mount)         │
               └────────────────┬───────────────────┘
                                ▼
               ┌──────────────────────────────────────┐
               │     BTRFS RAID1 Storage Pool         │
               │  /dev/sda + /dev/sdb (mirrored)      │
               │  Features: CoW, Snapshots,           │
               │            Compression, Checksums    │
               └──────────────────────────────────────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
      [/appdata]          [/downloads]         [/media]
   Config & DBs        Temp Downloads      Final Library


                    DOCKER CONTAINER NETWORK
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Network: 172.20.0.0/16                                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────────────────┐
    │                    VPN TUNNEL (Gluetun)                   │
    │  All acquisition traffic routed through this container     │
    │  IP: 172.20.0.2 | Exposes ports for nested containers     │
    └───────────────────────────────────────────────────────────┘
                 │              │              │
        ┌────────┘              │              └────────┐
        ▼                       ▼                       ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ qBittorrent  │      │   Prowlarr   │      │   autobrr    │
│ Port: 8080   │      │ Port: 9696   │      │ Port: 7474   │
│ Download     │      │ Indexer      │      │ Private      │
│ Client       │      │ Manager      │      │ Tracker      │
└──────────────┘      └──────────────┘      └──────────────┘
        │
        │ Downloads complete
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      /downloads/complete/                    │
│  Temporary storage for finished downloads                    │
└─────────────────────────────────────────────────────────────┘
        │
        │ Hardlink/Move (instant on same filesystem)
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   AUTOMATION LAYER (*arr)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  Sonarr  │ │  Radarr  │ │  Lidarr  │ │ Readarr  │      │
│  │  :8989   │ │  :7878   │ │  :8686   │ │  :8787   │      │
│  │  TV      │ │  Movies  │ │  Music   │ │  Books   │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐                                 │
│  │  Mylar3  │ │ Whisparr │ (Optional)                      │
│  │  :8090   │ │  :6969   │                                 │
│  │  Comics  │ │  Adult   │                                 │
│  └──────────┘ └──────────┘                                 │
│                                                             │
│  Functions:                                                 │
│  - Monitor wanted lists                                     │
│  - Search via Prowlarr                                      │
│  - Send to qBittorrent                                      │
│  - Import and rename files                                  │
│  - Update metadata                                          │
└─────────────────────────────────────────────────────────────┘
        │
        │ Writes organized media
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    /media/ (Library)                         │
│  ├── /movies/                                               │
│  ├── /tv/                                                   │
│  ├── /music/                                                │
│  ├── /books/                                                │
│  ├── /audiobooks/                                           │
│  ├── /podcasts/                                             │
│  ├── /comics/                                               │
│  └── /youtube/                                              │
└─────────────────────────────────────────────────────────────┘
        │
        │ Scanned by media servers
        ▼
┌─────────────────────────────────────────────────────────────┐
│                   STREAMING LAYER                            │
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │           Jellyfin :8096                     │           │
│  │  - Movies, TV, Music                         │           │
│  │  - Hardware transcoding (Quick Sync)         │           │
│  │  - Multi-user, mobile apps                   │           │
│  │  - /dev/dri passthrough for iGPU             │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │         Audiobookshelf :13378                │           │
│  │  - Audiobooks, Podcasts, eBooks              │           │
│  │  - Progress sync across devices              │           │
│  │  - iOS/Android apps                          │           │
│  └─────────────────────────────────────────────┘           │
│                                                             │
│  ┌─────────────────────────────────────────────┐           │
│  │           Podgrab :8083 (Optional)           │           │
│  │  - Standalone podcast downloader             │           │
│  │  - GPodder sync                              │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
        │
        │ User requests content
        ▼
┌─────────────────────────────────────────────────────────────┐
│              REQUEST MANAGEMENT (Jellyseerr)                 │
│  Port: 5055                                                 │
│  - Users search and request movies/TV                        │
│  - Integrates with Sonarr/Radarr                            │
│  - Approval workflows                                        │
│  - Jellyfin SSO                                             │
└─────────────────────────────────────────────────────────────┘


    AUXILIARY SERVICES

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ TubeArchivist│  │     IPFS     │  │  Homepage    │  │  Watchtower  │
│    :8082     │  │    :8081     │  │   :3000      │  │  (daemon)    │
│              │  │              │  │              │  │              │
│ YouTube      │  │ P2P File     │  │ Dashboard    │  │ Auto-update  │
│ Archival     │  │ Sharing      │  │ for all      │  │ containers   │
│              │  │              │  │ services     │  │              │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
       │
       └─ Requires: Elasticsearch + Redis (3-4GB RAM total)


    CLIENT DEVICES

┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Desktop    │  │   Laptop     │  │    Phone     │  │     TV       │
│   Browser    │  │   Browser    │  │  Jellyfin    │  │   Jellyfin   │
│              │  │              │  │    App       │  │     App      │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
       │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┘
                              │
                              ▼
                     [Gigabit Network]
                              │
                              ▼
                       [Zimaboard]
```

---

## Data Flow: Request to Watch

```
┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: USER REQUEST                                                  │
└────────────────────────────────────────────────────────────────────────┘

User opens Jellyseerr → Search "Breaking Bad" → Click "Request"
                                │
                                ▼
Jellyseerr → API call → Sonarr (172.20.0.10:8989)
                                │
                                ▼
Sonarr adds to wanted list, monitors for new episodes

┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: SEARCH & ACQUISITION                                          │
└────────────────────────────────────────────────────────────────────────┘

Sonarr → "Need Breaking Bad S01E01"
    │
    ▼
Sonarr → API call → Prowlarr (via Gluetun network) → "Search all indexers"
    │
    ▼
Prowlarr searches:
    - 1337x
    - RARBG
    - Private tracker #1
    - Private tracker #2
    │
    ▼
Returns results to Sonarr with:
    - Quality (1080p, 720p, etc.)
    - Size (2.5GB)
    - Seeders (143)
    - Indexer name
    │
    ▼
Sonarr picks best match based on quality profile
    │
    ▼
Sonarr → API call → qBittorrent (via Gluetun) → "Download this torrent"
    │           Category: "tv"
    │           Save path: "/downloads/complete/tv"
    │
    ▼
qBittorrent → [VPN Tunnel - Gluetun] → Torrent Swarm
    │
    │ [Downloading... 2.5GB]
    │ [Real IP hidden by VPN]
    │
    ▼
Download complete: /downloads/complete/tv/Breaking.Bad.S01E01.1080p.mkv

┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: IMPORT & ORGANIZE                                             │
└────────────────────────────────────────────────────────────────────────┘

qBittorrent → Webhook/Poll → Sonarr → "Download complete!"
    │
    ▼
Sonarr checks file:
    ✓ Correct episode (S01E01)
    ✓ Meets quality profile (1080p)
    ✓ Valid video file
    │
    ▼
Sonarr → Hardlink/Move file (instant, same filesystem)
    FROM: /downloads/complete/tv/Breaking.Bad.S01E01.1080p.mkv
    TO:   /tv/Breaking Bad (2008)/Season 01/Breaking Bad - S01E01 - Pilot.mkv
    │
    ▼
Sonarr → Renames file using naming template
Sonarr → Updates metadata (episode title, air date, etc.)
Sonarr → Marks episode as "Downloaded" ✓

┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: LIBRARY SCAN & METADATA                                       │
└────────────────────────────────────────────────────────────────────────┘

Jellyfin → Periodic scan of /tv folder (every 10 minutes or real-time)
    │
    ▼
Jellyfin detects new file: "Breaking Bad - S01E01 - Pilot.mkv"
    │
    ▼
Jellyfin → API call → TheTVDB → "Get metadata for Breaking Bad S01E01"
    │
    ▼
TheTVDB returns:
    - Episode title: "Pilot"
    - Description: "Walter White, a struggling..."
    - Air date: January 20, 2008
    - Runtime: 58 minutes
    - Thumbnail image
    │
    ▼
Jellyfin stores metadata in database
Jellyfin generates thumbnails, chapter images (optional)
Jellyfin indexes for search

┌────────────────────────────────────────────────────────────────────────┐
│ PHASE 5: USER WATCHES                                                  │
└────────────────────────────────────────────────────────────────────────┘

User opens Jellyfin app → "Recently Added" → Breaking Bad S01E01 → Play
    │
    ▼
Jellyfin checks:
    - Client device: iPhone
    - Video codec: H.264 (native support ✓)
    - Audio codec: AAC (native support ✓)
    - Resolution: 1080p → Client on WiFi → No transcode needed
    │
    ▼
Jellyfin → Direct stream → iPhone (no transcoding, minimal CPU)

--- OR (if transcoding needed) ---

User opens Jellyfin on old tablet → Play
    │
    ▼
Jellyfin checks:
    - Client device: Old Android tablet
    - Video codec: H.264 (OK)
    - Resolution: 1080p → Client on 3G → Too high bitrate
    │
    ▼
Jellyfin → Hardware transcode via Intel Quick Sync
    │       Original: 1080p @ 8 Mbps
    │       Target: 480p @ 2 Mbps
    │
    ▼
Intel iGPU (/dev/dri) → Encodes H.264 480p in real-time
    │       CPU usage: <10% (vs 80%+ software encoding)
    │       Power: +2W (vs +10W software encoding)
    │
    ▼
Jellyfin → Streams transcoded video → Tablet

User watches episode, progress is saved to Jellyfin database
Resume point syncs across all devices

┌────────────────────────────────────────────────────────────────────────┐
│ TOTAL TIME: Request to Watch                                           │
└────────────────────────────────────────────────────────────────────────┘

Request: 30 seconds
Search: 5 seconds
Download: 5-30 minutes (depending on speed/seeders)
Import: 10 seconds (hardlink)
Scan: 10 seconds
Watch: Immediate

TOTAL: ~5-30 minutes (mostly download time)
```

---

## Component Interaction Matrix

```
                 ┌──────┬────────┬────────┬────────┬─────────┬──────────┬──────────┐
                 │Gluetun│qBT     │Prowlarr│Sonarr  │Radarr   │Jellyfin  │Jellyseerr│
┌────────────────┼──────┼────────┼────────┼────────┼─────────┼──────────┼──────────┤
│Gluetun (VPN)   │  -   │ Routes │ Routes │   -    │    -    │    -     │    -     │
├────────────────┼──────┼────────┼────────┼────────┼─────────┼──────────┼──────────┤
│qBittorrent     │  ✓   │   -    │   -    │  ✓     │   ✓     │    -     │    -     │
├────────────────┼──────┼────────┼────────┼────────┼─────────┼──────────┼──────────┤
│Prowlarr        │  ✓   │   -    │   -    │  ✓     │   ✓     │    -     │    -     │
├────────────────┼──────┼────────┼────────┼────────┼─────────┼──────────┼──────────┤
│Sonarr          │  -   │   ✓    │   ✓    │   -    │    -    │    -     │    ✓     │
├────────────────┼──────┼────────┼────────┼────────┼─────────┼──────────┼──────────┤
│Radarr          │  -   │   ✓    │   ✓    │   -    │    -    │    -     │    ✓     │
├────────────────┼──────┼────────┼────────┼────────┼─────────┼──────────┼──────────┤
│Jellyfin        │  -   │   -    │   -    │   -    │    -    │    -     │    ✓     │
├────────────────┼──────┼────────┼────────┼────────┼─────────┼──────────┼──────────┤
│Jellyseerr      │  -   │   -    │   -    │  ✓     │   ✓     │    ✓     │    -     │
└────────────────┴──────┴────────┴────────┴────────┴─────────┴──────────┴──────────┘

Legend:
  -      : No interaction
  ✓      : Direct API communication
  Routes : Network traffic routed through this service
```

---

## Resource Allocation by Function

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      16GB SYSTEM (Recommended)                          │
└─────────────────────────────────────────────────────────────────────────┘

        [0GB]                                                     [16GB]
         │                                                          │
         ├─[Proxmox: 1GB]─────────────────────────────────────────┤
         ├─[VPN: 256MB]──┤                                         │
         ├─[qBittorrent: 1GB]────────────────┤                    │
         ├─[*arr Stack: 2GB]─────────────────────────────┤        │
         ├─[Jellyfin: 4GB]──────────────────────────────────────────┤
         ├─[Audiobookshelf: 1GB]────────────────┤                 │
         ├─[TubeArchivist: 4GB]──────────────────────────────────────┤
         ├─[Misc: 1GB]────────────────┤                            │
         └─[Free: 2GB]────────┘ (Buffer for transcoding spikes)   │

┌─────────────────────────────────────────────────────────────────────────┐
│                      8GB SYSTEM (Minimal)                               │
└─────────────────────────────────────────────────────────────────────────┘

        [0GB]                                                      [8GB]
         │                                                          │
         ├─[Proxmox: 1GB]─────────────────────────────────────────┤
         ├─[VPN: 128MB]─┤                                          │
         ├─[qBittorrent: 512MB]──────────┤                        │
         ├─[*arr Stack: 1.5GB]──────────────────────┤             │
         ├─[Jellyfin: 2GB]──────────────────────────────┤         │
         ├─[Audiobookshelf: 512MB]──────────┤                     │
         ├─[Misc: 512MB]──────────┤                               │
         └─[Free: 2GB]────────┘ (Buffer)                          │

         ⚠ Skip TubeArchivist on 8GB systems (requires 3-4GB)
```

---

## Technology Decision Matrix

### NAS Solution
| Option | RAM | Ease | Features | Verdict |
|--------|-----|------|----------|---------|
| **TrueNAS Scale** | 8GB+ | Medium | ZFS, VMs, Apps | Too heavy for Zimaboard |
| **OpenMediaVault** | 1GB+ | Easy | Web GUI, Plugins | ✓ Recommended for LXC |
| **Direct Proxmox** | 0GB | Hard | No GUI, Manual | ✓ Best for power users |

**Winner:** OpenMediaVault in LXC (beginners) or Direct Proxmox (advanced)

### Filesystem
| Option | RAM Req | Speed | Features | Zimaboard Fit |
|--------|---------|-------|----------|---------------|
| **ZFS** | 8GB+ | Fast | Enterprise, Dedup | ✗ Too memory hungry |
| **BTRFS** | 2GB+ | Fast | Snapshots, CoW | ✓ Perfect balance |
| **EXT4** | <1GB | Fastest | Simple, Stable | ✓ If no advanced features needed |

**Winner:** BTRFS (best feature/resource ratio)

### Torrent Client
| Client | RAM | CPU | Features | Docker Support |
|--------|-----|-----|----------|----------------|
| **Transmission** | 50MB | 2% | Minimal | Excellent |
| **qBittorrent** | 100MB | 5% | Full-featured | Excellent |
| **Deluge** | 150MB+ | 10%+ | Plugins | Good |

**Winner:** qBittorrent (best feature/efficiency balance)

### Media Server
| Server | HW Transcode Cost | Privacy | Features | Zimaboard Fit |
|--------|-------------------|---------|----------|---------------|
| **Jellyfin** | Free | 100% | Good | ✓ Perfect |
| **Plex** | $250 | 70% | Excellent | ✓ If you pay |
| **Emby** | $120 | 90% | Good | ✓ Middle ground |

**Winner:** Jellyfin (free HW transcoding, open source)

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           INTERNET                                       │
│                      (Untrusted Network)                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Router/Firewall     │
                    │   - NAT               │
                    │   - Port forwarding   │
                    └───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Mullvad VPN  │    │  Reverse Proxy   │    │  Direct Access   │
│ (Gluetun)    │    │  (Optional)      │    │  (Trusted LAN)   │
│              │    │                  │    │                  │
│ - qBittorrent│    │  Nginx/Traefik   │    │ - All services   │
│ - Prowlarr   │    │  + HTTPS/SSL     │    │ - No encryption  │
│ - autobrr    │    │  + Auth (OAuth)  │    │ - HTTP only      │
└──────────────┘    └──────────────────┘    └──────────────────┘
      │                       │                       │
      │ Torrent traffic       │ Web traffic           │ Internal only
      │ (encrypted)           │ (HTTPS)               │ (no encryption needed)
      ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DOCKER NETWORK                                   │
│                      172.20.0.0/16 (isolated)                            │
└─────────────────────────────────────────────────────────────────────────┘
      │                                                           │
      ▼                                                           ▼
[Public trackers]                                        [Media servers]
[Indexers]                                               [Internal access only]

Security Layers:
1. VPN: All torrent traffic encrypted, IP hidden
2. Firewall: Only necessary ports exposed
3. Network isolation: Containers on separate subnet
4. Authentication: Web UIs password-protected
5. HTTPS: Reverse proxy encrypts web traffic (if exposed)
6. SSH keys: No password authentication to host
```

---

## Scalability & Future Expansion

### Current Capacity (Zimaboard)
- **Containers:** 10-15 (with 8GB RAM)
- **Simultaneous transcodes:** 3-5x 1080p or 1-2x 4K
- **Storage:** 2x SATA (RAID1 up to 2TB+ per drive)
- **Network:** 1Gbps bottleneck

### Expansion Options

#### Option 1: Add NAS for Storage
```
Zimaboard (Compute) ──────────► NAS (Storage)
- Runs Docker containers        - BTRFS/ZFS pool
- Jellyfin, *arr apps            - 4-8 drive RAID
- 16GB RAM upgrade               - 10GbE connection
```

#### Option 2: Proxmox Cluster
```
Zimaboard #1 ──┐
               ├─► Proxmox Cluster
Zimaboard #2 ──┤   - HA capabilities
               │   - VM migration
Zimaboard #3 ──┘   - Shared storage
```

#### Option 3: Dedicated Transcoding Server
```
Zimaboard (Management) ──────────► Server (Transcoding)
- *arr stack                       - Intel QuickSync or
- qBittorrent                      - NVIDIA GPU
- Jellyfin backend                 - Jellyfin frontend
                                   - 32GB RAM
```

#### Option 4: Offload to Cloud
```
Zimaboard (Local) ──────────► Cloud VPS (Remote)
- Media storage               - TubeArchivist
- Jellyfin                    - Backup storage
- *arr automation             - Encrypted sync
```

---

## Performance Benchmarks (Expected)

### Network Throughput
- **Download:** 110-120 MB/s (Gigabit Ethernet limit)
- **Upload (seeding):** 110-120 MB/s
- **Jellyfin stream:** 20-40 MB/s per 1080p client
- **Max simultaneous streams:** 3-4 before saturating network

### Storage I/O
- **BTRFS RAID1 (SSD):** 100-150 MB/s read, 80-120 MB/s write
- **BTRFS RAID1 (HDD):** 80-120 MB/s read, 60-90 MB/s write
- **Random I/O (SQLite):** 5000+ IOPS (SSD), 100-200 IOPS (HDD)

### Transcoding Capacity (Intel Quick Sync)
| Resolution | Codec | Simultaneous Streams |
|------------|-------|----------------------|
| 4K → 1080p | H.264 | 1-2 streams |
| 4K → 1080p | H.265 | 1 stream |
| 1080p → 720p | H.264 | 3-5 streams |
| 1080p → 480p | H.264 | 5-7 streams |

### Power Consumption
| Scenario | Power Draw |
|----------|------------|
| Idle | 6-8W |
| Downloading (1 torrent) | 8-10W |
| Transcoding (1x 1080p) | 10-12W |
| Max load (download + transcode) | 15-20W |
| **Annual cost** (24/7 at $0.12/kWh) | **$10-20/year** |

---

## Maintenance Schedule

### Daily (Automated)
- ✓ Watchtower checks for container updates
- ✓ *arr apps check for new releases
- ✓ qBittorrent seeds completed torrents

### Weekly (Manual)
- Check disk space: `df -h /mnt/storage`
- Review failed downloads in *arr apps
- Clear old completed downloads

### Monthly (Manual)
- Update all containers: `docker compose pull && docker compose up -d`
- BTRFS scrub: `btrfs scrub start /mnt/storage`
- Review logs for errors: `docker compose logs --tail=100`
- Backup appdata: `tar -czf backup.tar.gz /mnt/storage/appdata`

### Quarterly (Manual)
- Review storage usage trends
- Update Proxmox host: `apt update && apt dist-upgrade`
- Test restore from backup
- Audit user accounts and permissions

### Annually (Manual)
- Review and update VPN subscription
- Check drive SMART status: `smartctl -a /dev/sda`
- Consider drive replacement if approaching failure
- Review security settings and passwords

---

This architecture provides a complete, production-ready media stack optimized for the Zimaboard's constraints while maintaining flexibility for future expansion.

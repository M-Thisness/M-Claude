# Media Stack Quick Reference Card

## Service URLs and Ports

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| qBittorrent | http://IP:8080 | admin / adminadmin |
| Prowlarr | http://IP:9696 | No auth (set up manually) |
| Sonarr | http://IP:8989 | No auth (set up manually) |
| Radarr | http://IP:7878 | No auth (set up manually) |
| Lidarr | http://IP:8686 | No auth (set up manually) |
| Readarr | http://IP:8787 | No auth (set up manually) |
| Mylar3 | http://IP:8090 | No auth (set up manually) |
| Whisparr | http://IP:6969 | No auth (set up manually) |
| Jellyfin | http://IP:8096 | Set during first run |
| Jellyseerr | http://IP:5055 | Login via Jellyfin |
| Audiobookshelf | http://IP:13378 | Set during first run |
| Podgrab | http://IP:8083 | No auth |
| TubeArchivist | http://IP:8082 | Set in .env file |
| IPFS Gateway | http://IP:8081 | Read-only |
| Homepage | http://IP:3000 | No auth |
| autobrr | http://IP:7474 | Set during first run |

## Docker Compose Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart specific service
docker compose restart jellyfin

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f qbittorrent

# Update all containers
docker compose pull
docker compose up -d

# Remove everything (including volumes - DANGEROUS!)
docker compose down -v

# Check resource usage
docker stats

# Check disk usage
docker system df
```

## Common Maintenance Tasks

### Check VPN Status
```bash
# Get VPN IP address
docker exec gluetun wget -qO- ifconfig.me

# Should NOT show your real IP
curl ifconfig.me  # Compare with above
```

### Restart Networking Stack
```bash
# If downloads stop working
docker compose restart gluetun qbittorrent prowlarr
```

### Clear qBittorrent Cache
```bash
docker exec qbittorrent rm -rf /config/qBittorrent/cache/*
docker compose restart qbittorrent
```

### Rebuild Jellyfin Library
```bash
# Via API (adjust URL)
curl -X POST "http://IP:8096/Library/Refresh?api_key=YOUR_API_KEY"

# Or via dashboard: Dashboard → Scan All Libraries
```

### BTRFS Maintenance
```bash
# Check filesystem health
btrfs filesystem show /mnt/storage

# Balance (defragment)
btrfs balance start /mnt/storage

# Scrub (find and fix errors)
btrfs scrub start /mnt/storage
btrfs scrub status /mnt/storage

# Check compression ratio
compsize /mnt/storage

# View disk usage by subvolume
btrfs filesystem du -s /mnt/storage/*
```

### Backup Configuration
```bash
# Backup all app configs
tar -czf backup-$(date +%F).tar.gz /mnt/storage/appdata/

# Restore
tar -xzf backup-2025-01-16.tar.gz -C /
```

## Troubleshooting Commands

### Check Container Health
```bash
# All containers status
docker ps -a

# Restart unhealthy container
docker compose restart <service-name>

# View container details
docker inspect <container-name>
```

### Network Debugging
```bash
# Test connectivity between containers
docker exec sonarr ping gluetun
docker exec radarr curl http://gluetun:8080

# Check container IPs
docker network inspect media-stack_media_network
```

### Disk Space Issues
```bash
# Check disk usage
df -h /mnt/storage

# Find large files
du -sh /mnt/storage/* | sort -rh | head -10

# Clean Docker cache
docker system prune -a

# Clean old downloads
find /mnt/storage/downloads/complete -type f -mtime +7 -delete
```

### Permission Issues
```bash
# Fix ownership (run on host)
chown -R 1000:1000 /mnt/storage

# Fix permissions
chmod -R 775 /mnt/storage

# Check current permissions
ls -la /mnt/storage/
```

## Configuration File Locations

| Service | Config Path |
|---------|-------------|
| Docker Compose | /opt/media-stack/docker-compose.yml |
| Environment Vars | /opt/media-stack/.env |
| qBittorrent | /mnt/storage/appdata/qbittorrent/ |
| Sonarr | /mnt/storage/appdata/sonarr/ |
| Radarr | /mnt/storage/appdata/radarr/ |
| Jellyfin | /mnt/storage/appdata/jellyfin/ |
| All Configs | /mnt/storage/appdata/ |

## API Keys

Retrieve API keys for integration:

```bash
# Sonarr
docker exec sonarr cat /config/config.xml | grep -oP '(?<=<ApiKey>).*(?=</ApiKey>)'

# Radarr
docker exec radarr cat /config/config.xml | grep -oP '(?<=<ApiKey>).*(?=</ApiKey>)'

# Prowlarr
docker exec prowlarr cat /config/config.xml | grep -oP '(?<=<ApiKey>).*(?=</ApiKey>)'

# Or find in UI: Settings → General → API Key
```

## Performance Tuning

### Reduce RAM Usage
Edit docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 256M  # Reduce for each service
```

### Disable Auto-Start (Run On-Demand)
```bash
# Remove specific service from auto-start
docker compose stop tubearchivist
docker compose rm tubearchivist

# Start manually when needed
docker compose up -d tubearchivist
```

### Limit qBittorrent Bandwidth
qBittorrent UI → Options → Speed:
- Global upload: 1000 KB/s (adjust as needed)
- Global download: 10000 KB/s
- Alt speed limits: Enable scheduler for night hours

## Network Diagram

```
Internet
    ↓
[Router]
    ↓
[Zimaboard - Proxmox]
    ↓
[LXC Container - Docker]
    ├── Gluetun (VPN) ← qBittorrent, Prowlarr, autobrr (through VPN)
    │
    ├── Sonarr ↔ Prowlarr ↔ qBittorrent
    ├── Radarr ↔ Prowlarr ↔ qBittorrent
    ├── Lidarr ↔ Prowlarr ↔ qBittorrent
    ├── Readarr ↔ Prowlarr ↔ qBittorrent
    ├── Mylar3 ↔ Prowlarr ↔ qBittorrent
    │
    ├── Jellyfin → Reads /media
    ├── Audiobookshelf → Reads /audiobooks, /podcasts
    ├── TubeArchivist → Writes /youtube
    │
    ├── Jellyseerr ↔ Sonarr, Radarr
    └── Homepage → Dashboard for all services

Data Flow:
1. User requests via Jellyseerr
2. Sonarr/Radarr searches via Prowlarr
3. qBittorrent downloads via Gluetun (VPN)
4. *arr apps move to /media (instant hardlink)
5. Jellyfin scans and serves media
```

## Security Checklist

- [ ] Changed default qBittorrent password
- [ ] VPN killswitch enabled (Gluetun handles this)
- [ ] IPFS API (port 5001) NOT exposed to internet
- [ ] Jellyfin admin password set
- [ ] All *arr apps have authentication enabled
- [ ] SSH key-based auth only (no password login)
- [ ] Firewall configured (only expose necessary ports)
- [ ] Regular backups scheduled
- [ ] BTRFS scrub scheduled monthly
- [ ] Watchtower monitoring container updates

## Update Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Docker containers | Weekly | `docker compose pull && docker compose up -d` |
| LXC system packages | Monthly | `apt update && apt upgrade` |
| Proxmox host | Monthly | `apt update && apt dist-upgrade` |
| BTRFS scrub | Monthly | `btrfs scrub start /mnt/storage` |
| Configuration backup | Weekly | `tar -czf backup.tar.gz /mnt/storage/appdata` |
| Check logs | Weekly | `docker compose logs --tail=100` |

## Resource Monitoring

```bash
# Real-time resource usage
docker stats

# Disk I/O
iostat -x 1

# Network usage
iftop

# System overview
htop

# Check Quick Sync usage (Jellyfin transcoding)
intel_gpu_top  # Install: apt install intel-gpu-tools
```

## Emergency Recovery

### If entire stack is broken:
```bash
# Stop everything
docker compose down

# Check for errors
docker compose config

# Start one service at a time
docker compose up -d gluetun
docker compose logs gluetun
docker compose up -d qbittorrent
# etc...
```

### If disk is full:
```bash
# Find large files
du -sh /mnt/storage/* | sort -rh | head -20

# Clean Docker
docker system prune -a -f

# Clean old downloads
rm -rf /mnt/storage/downloads/complete/*

# Clean Jellyfin cache
rm -rf /mnt/storage/appdata/jellyfin/cache/*
```

### If container won't start:
```bash
# Check logs
docker logs <container-name>

# Remove and recreate
docker compose rm -f <service-name>
docker compose up -d <service-name>

# Nuclear option: rebuild from image
docker compose pull <service-name>
docker compose up -d --force-recreate <service-name>
```

---

## Quick Start (TL;DR)

1. Install Proxmox on Zimaboard
2. Setup BTRFS RAID1: `mkfs.btrfs -d raid1 /dev/sda /dev/sdb`
3. Create Ubuntu LXC with Docker
4. Mount storage: `mp0: /mnt/storage,mp=/mnt/storage`
5. Copy docker-compose.yml and .env
6. `docker compose up -d`
7. Configure services via web UIs
8. Request content → Watch on Jellyfin!

**First-time setup:** ~4 hours
**Daily maintenance:** 0 minutes (automated)
**Monthly maintenance:** ~1 hour (updates, backups)

---

For detailed setup, see: MEDIA-STACK-SETUP-GUIDE.md

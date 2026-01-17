# Zimaboard HomeLab Resource Analysis

## Executive Summary

This document provides a comprehensive resource analysis for the proposed Zimaboard HomeLab setup. The analysis reveals that **the full stack as designed requires approximately 28-34GB of RAM**, which **exceeds the Zimaboard's 16GB capacity by 175-212%**.

**Critical Recommendation:** This setup requires careful resource management, selective service deployment, and aggressive optimization to fit within the 16GB constraint.

---

## Hardware Specifications

### Zimaboard Configuration

| Component | Specification | Notes |
|-----------|---------------|-------|
| **CPU** | Intel Celeron N3450 | 4 cores, 4 threads @ 1.1-2.7 GHz (Burst) |
| **Architecture** | x86-64 (Apollo Lake) | 14nm process, TDP 6W |
| **RAM** | 16GB LPDDR4 | Non-upgradeable, shared with iGPU |
| **Graphics** | Intel HD Graphics 500 | Shares system RAM (iGPU buffer: ~512MB) |
| **Storage** | eMMC + 2x SATA III | SATA limited to ~550 MB/s combined |
| **Network** | 2x Onboard 2.5GbE + 4x PCIe 2.5GbE | Total 6 ports |
| **PCIe** | 1x PCIe 2.0 x4 slot | Used for 4-port NIC |
| **Thermal** | Passive cooling | Fanless, thermal throttling possible |

### Effective Resources After System Overhead

| Resource | Total | System Reserved | **Available for Workloads** |
|----------|-------|-----------------|------------------------------|
| RAM | 16GB | 1.5GB (Proxmox + kernel + iGPU) | **~14.5GB** |
| CPU | 4 cores @ 2.7GHz | ~0.5 core (system) | **~3.5 cores** |
| Disk I/O | ~550 MB/s (SATA) | - | Limited by mechanical drives |
| Network | 15 Gbps aggregate | - | Limited by CPU packet processing |

---

## Service-by-Service Resource Requirements

### 🔧 Infrastructure Services (Always Running)

#### Proxmox VE Host
- **RAM:** 1.5GB (host OS, kernel, management)
- **CPU:** 0.3-0.5 cores (idle: 5-10%, monitoring overhead)
- **Disk:** 50GB (Proxmox OS)
- **Priority:** Critical

---

### 🌐 Network Services (Phase 1)

#### 1. Suricata IDS/IPS
- **RAM:** 4-6GB (pattern matching, flow tracking for 6 interfaces)
- **CPU:** 1.5-2 cores (DPI processing at 2.5GbE speeds)
- **Disk:** 20GB (rules, logs)
- **Network:** Monitors all bridge traffic
- **Priority:** High
- **Notes:** Most resource-intensive network service. Can be tuned down.

**Optimization Options:**
```yaml
# Reduced configuration for 16GB system
Rule sets: Essential only (~5,000 rules vs 30,000+)
Flow timeout: 30s (vs 60s default)
Workers: 2 (vs 4)
RAM usage: ~2-3GB (vs 4-6GB)
```

#### 2. ntopng Traffic Monitor
- **RAM:** 2-3GB (flow data, historical stats, GeoIP)
- **CPU:** 0.5-1 core (packet analysis)
- **Disk:** 50GB (historical data, RRD databases)
- **Priority:** Medium
- **Notes:** Can be replaced with lighter alternatives (iftop, vnStat)

**Lightweight Alternative:**
```yaml
Service: vnStat + InfluxDB + Grafana
RAM: ~800MB total
CPU: 0.2 cores
Trade-off: Less detailed real-time analysis
```

#### 3. Deskflow KVM Server
- **RAM:** 256-512MB
- **CPU:** 0.1-0.2 cores (input event processing)
- **Network:** <1 Mbps
- **Priority:** High (user experience)

#### 4. PipeWire Audio Router
- **RAM:** 512MB-1GB
- **CPU:** 0.2-0.5 cores (audio mixing, encoding)
- **Network:** ~12 Mbps per stream (uncompressed)
- **Latency:** 10-20ms target
- **Priority:** High (user experience)

**Network Services Subtotal:**
- **Baseline (all services):** 7.3-10.5GB RAM, 2.5-3.7 cores
- **Optimized (reduced Suricata):** 5.1-7.5GB RAM, 2.0-2.9 cores
- **Minimal (no IDS, lightweight monitoring):** 1.3-2.5GB RAM, 0.5-1.2 cores

---

### 💾 Storage & Media Stack (Phase 2)

#### LXC Container: Docker Host - Media
- **Container Overhead:** 512MB
- **Total Allocation:** 10GB RAM, 4 CPU cores

**Services Running Inside:**

| Service | RAM | CPU | Disk | Priority |
|---------|-----|-----|------|----------|
| **Jellyfin** | 2-3GB | 0.5-1.5 (transcoding: up to 3) | 100GB cache | High |
| **Sonarr** | 512MB | 0.1 | 10GB | Medium |
| **Radarr** | 512MB | 0.1 | 10GB | Medium |
| **Lidarr** | 512MB | 0.1 | 10GB | Low |
| **Readarr** | 512MB | 0.1 | 10GB | Low |
| **Prowlarr** | 256MB | 0.1 | 5GB | Medium |
| **qBittorrent + VPN** | 512MB-1GB | 0.2-0.5 | 20GB | Medium |
| **Jellyseerr** | 256MB | 0.1 | 5GB | Low |
| **Audiobookshelf** | 512MB | 0.2 | 10GB | Medium |
| **TubeArchivist** | 3-4GB (Elasticsearch!) | 1-2 | 500GB+ | Low |

**Media Stack Subtotal:**
- **Full Stack:** 9-12GB RAM, 2-6 cores (transcoding)
- **Without TubeArchivist:** 6-8GB RAM, 1-4 cores
- **Core Only (Jellyfin + 1 *arr):** 3-4GB RAM, 0.7-2 cores

#### NAS (OpenMediaVault LXC)
- **RAM:** 1GB
- **CPU:** 0.2-0.5 cores (file serving, Samba/NFS)
- **Disk:** Direct SATA passthrough (2x drives, BTRFS RAID1)
- **Priority:** High

---

### 🧠 Knowledge Stack (Phase 3)

#### LXC Container: Docker Host - Knowledge
- **Container Overhead:** 512MB
- **Total Allocation:** 6GB RAM, 2 CPU cores

**Services Running Inside:**

| Service | RAM | CPU | Disk | Priority |
|---------|-----|-----|------|----------|
| **Silverbullet** | 256-512MB | 0.1-0.2 | 10GB | High |
| **Paperless-ngx** | 2-3GB (OCR processing) | 0.5-1 | 50GB | High |
| **PostgreSQL** | 512MB-1GB | 0.2-0.5 | 20GB | High |
| **Redis** | 256MB | 0.1 | 1GB | Medium |
| **Tika** (optional) | 1-2GB | 0.5 | 2GB | Low |
| **Gotenberg** (optional) | 512MB-1GB | 0.2-0.5 | 2GB | Low |

**Knowledge Stack Subtotal:**
- **Full Stack (with Tika/Gotenberg):** 4.5-7.5GB RAM, 1.6-2.9 cores
- **Core Only (without Tika/Gotenberg):** 3-4.5GB RAM, 0.9-1.9 cores
- **Minimal (Silverbullet only):** 256-512MB RAM, 0.1-0.2 cores

---

### 🏠 IoT & Automation (Phase 4)

#### LXC Container: Docker Host - IoT
- **Container Overhead:** 512MB
- **Total Allocation:** 4GB RAM, 2 CPU cores

**Services Running Inside:**

| Service | RAM | CPU | Disk | Priority |
|---------|-----|-----|------|----------|
| **Home Assistant** | 1-2GB | 0.3-0.8 | 20GB | Critical |
| **Mosquitto MQTT** | 128-256MB | 0.1 | 1GB | High |
| **BirdNET-Go** | 512MB-1GB | 0.2-0.5 | 10GB | Low |
| **Grafana** | 512MB-1GB | 0.2-0.5 | 10GB | Medium |
| **InfluxDB** (optional) | 1-2GB | 0.3-0.6 | 50GB | Medium |

**IoT Stack Subtotal:**
- **Full Stack (with InfluxDB):** 3.2-6.3GB RAM, 1.1-2.5 cores
- **Without InfluxDB:** 2.2-4.3GB RAM, 0.8-1.9 cores
- **Minimal (HA + MQTT only):** 1.1-2.3GB RAM, 0.4-0.9 cores

#### Alternative: Home Assistant OS (VM)
- **RAM:** 4GB allocated
- **CPU:** 2 cores
- **Disk:** 32GB
- **Trade-off:** Easier add-ons, but higher overhead (hypervisor)

---

### 🔒 Security Scanning (Phase 4)

#### Nessus VM (Resource Limited)
- **RAM:** 4GB (limited to prevent host impact)
- **CPU:** 2 cores (limited to 50% CPU cap)
- **Disk:** 50GB
- **Priority:** Low (scheduled scans only)
- **Notes:** **Only run during maintenance windows**

**Resource Limiting Configuration:**
```bash
# VM Resource Limits in Proxmox
cores: 2
memory: 4096
cpulimit: 1  # Limit to 1 full core (50% of 2 cores)
balloon: 2048  # Can balloon down to 2GB

# Nessus Scan Configuration
Max concurrent checks: 5 (default: 10)
Network timeout: 5s
Max host scan: 5 simultaneous
Scan schedule: 2 AM - 6 AM only
```

---

### 🐦 Citizen Science (Phase 5)

#### BirdNET-Go (included in IoT stack)
- Already counted above
- **RAM:** 512MB-1GB
- **CPU:** 0.2-0.5 cores (real-time inference)
- **Disk:** 10GB (SQLite database, audio samples)
- **Priority:** Low

---

## Total Resource Requirements

### 📊 Scenario Analysis

#### 🔴 **Scenario 1: Full Stack (All Services)**
**Not Recommended - Exceeds Capacity**

| Component | RAM | CPU Cores |
|-----------|-----|-----------|
| Proxmox Host | 1.5GB | 0.5 |
| Network Services | 7.3-10.5GB | 2.5-3.7 |
| Media Stack (full) | 9-12GB | 2-6 |
| Knowledge Stack (full) | 4.5-7.5GB | 1.6-2.9 |
| IoT Stack (full) | 3.2-6.3GB | 1.1-2.5 |
| Nessus VM | 4GB | 2 |
| **TOTAL** | **29.5-41.8GB** ❌ | **9.7-17.6 cores** ❌ |
| **vs Available** | **14.5GB** | **3.5 cores** |
| **Shortfall** | **-15GB to -27GB** | **-6 to -14 cores** |

**Verdict:** Impossible without external compute nodes.

---

#### 🟡 **Scenario 2: Optimized Stack (Recommended)**
**Fits Within Constraints with Trade-offs**

| Component | RAM | CPU Cores |
|-----------|-----|-----------|
| Proxmox Host | 1.5GB | 0.5 |
| Network (optimized IDS, vnStat) | 3.5GB | 1.5 |
| Media (no TubeArchivist, selective *arr) | 6GB | 1.5 |
| Knowledge (no Tika/Gotenberg) | 3.5GB | 1.2 |
| IoT (HA + MQTT + BirdNET) | 2.5GB | 1.0 |
| Nessus (scheduled, not always on) | 0GB* | 0 |
| **TOTAL** | **17GB** ⚠️ | **5.7 cores** ⚠️ |
| **vs Available** | **14.5GB** | **3.5 cores** |
| **Shortfall** | **-2.5GB** | **-2.2 cores** |

*Nessus runs on-demand, other services suspended during scans.

**Required Optimizations:**
1. Disable Jellyfin hardware transcoding (use direct play only)
2. Limit *arr apps to 2-3 (Sonarr + Radarr only)
3. Use lightweight monitoring (vnStat vs ntopng)
4. Reduce Suricata to essential rules
5. Aggressive swap configuration (8GB swap on SSD)

**Verdict:** Possible but requires careful tuning.

---

#### 🟢 **Scenario 3: Minimal Viable Stack**
**Comfortably Fits - Best for Zimaboard**

| Component | RAM | CPU Cores |
|-----------|-----|-----------|
| Proxmox Host | 1.5GB | 0.5 |
| Network (Deskflow + Audio only) | 1GB | 0.4 |
| Media (Jellyfin + Sonarr + qBit) | 4GB | 1.2 |
| Knowledge (Silverbullet + Paperless) | 3GB | 1.1 |
| IoT (Home Assistant + MQTT) | 1.5GB | 0.5 |
| NAS (OMV) | 1GB | 0.3 |
| **TOTAL** | **12GB** ✅ | **4 cores** ✅ |
| **vs Available** | **14.5GB** | **3.5 cores** |
| **Headroom** | **+2.5GB** | **-0.5 cores** |

**Trade-offs:**
- ❌ No IDS/IPS (Suricata)
- ❌ No comprehensive traffic monitoring (ntopng)
- ❌ Limited media automation (1-2 *arr apps)
- ❌ No advanced document processing (Tika/Gotenberg)
- ❌ No TubeArchivist
- ❌ No Nessus
- ✅ All core functionality preserved
- ✅ Stable and responsive

**Verdict:** **Recommended starting point**. Add services incrementally.

---

## Performance Bottlenecks

### 🔴 Critical Bottlenecks

#### 1. **RAM Limitation (Most Critical)**
- **Issue:** 16GB is insufficient for full stack
- **Impact:** Swapping → performance degradation → potential OOM kills
- **Mitigation:**
  - Aggressive memory limits per container
  - Zram/zswap for compressed swap
  - Memory balloon drivers
  - Service prioritization (OOM scores)

#### 2. **CPU Performance (Celeron N3450)**
- **Issue:** Low single-thread performance (~2.7 GHz burst)
- **Impact:**
  - Jellyfin transcoding: 0.2-0.5x real-time (720p max)
  - Suricata: Packet drops at >1 Gbps aggregate
  - OCR processing: Slow document ingestion
- **Mitigation:**
  - Direct play only (no transcoding)
  - Limit Suricata to essential rules
  - Batch OCR processing overnight

#### 3. **Disk I/O (SATA + Mechanical Drives)**
- **Issue:** Limited IOPS (~100-150 for HDDs)
- **Impact:**
  - Slow Docker image pulls
  - Jellyfin thumbnail generation
  - Database query performance
- **Mitigation:**
  - Use SSD for Proxmox OS and databases
  - HDD for media storage only
  - Adjust Docker logging (json-file with rotation)
  - Disable unnecessary access time updates (`noatime`)

#### 4. **Network CPU Overhead**
- **Issue:** 6x 2.5GbE interfaces = high interrupt load
- **Impact:** CPU cycles spent on packet processing
- **Mitigation:**
  - Enable multi-queue (ethtool -L)
  - MSI-X interrupt distribution
  - Disable offloading for bridges (GRO, GSO, TSO)

---

## Optimization Strategies

### 🎯 Memory Optimization

#### 1. **Container Memory Limits (Docker)**
```yaml
# Example: Jellyfin with hard limit
services:
  jellyfin:
    mem_limit: 2g
    mem_reservation: 1g
    memswap_limit: 3g  # Allow 1GB swap
```

#### 2. **LXC Memory Limits (Proxmox)**
```bash
# In container config (/etc/pve/lxc/<ID>.conf)
memory: 8192
swap: 4096
```

#### 3. **Kernel Memory Management**
```bash
# /etc/sysctl.conf
vm.swappiness=10              # Prefer RAM over swap
vm.vfs_cache_pressure=50      # Balance cache vs swap
vm.dirty_ratio=10             # Write cache tuning
vm.dirty_background_ratio=5
```

#### 4. **Zram Compressed Swap**
```bash
# Install zram-tools
apt install zram-tools

# /etc/default/zramswap
ALGO=lz4           # Fast compression
PERCENT=50         # 50% of RAM = 8GB compressed swap
```

**Effective RAM:** 16GB physical + ~4-6GB compressed swap = **~20-22GB usable**

---

### ⚡ CPU Optimization

#### 1. **CPU Pinning (NUMA Awareness)**
```bash
# Pin critical services to specific cores
# LXC config:
cores: 2
cpulimit: 2
cpuunits: 2048  # Higher priority (default: 1024)
```

#### 2. **Process Priority (nice/ionice)**
```yaml
# docker-compose.yml
services:
  jellyfin:
    cpu_shares: 2048      # High priority
  tubarchivist:
    cpu_shares: 512       # Low priority
    blkio_weight: 100     # Low I/O priority
```

#### 3. **Governor Tuning**
```bash
# Set CPU governor to performance (vs powersave)
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
```

---

### 💿 Disk I/O Optimization

#### 1. **Filesystem Tuning**
```bash
# BTRFS mount options for media storage
/dev/sda1 /mnt/storage btrfs noatime,compress=zstd:3,space_cache=v2 0 0

# Ext4 for databases
/dev/sdb1 /var/lib/docker ext4 noatime,data=ordered,barrier=0 0 0
```

#### 2. **I/O Scheduler**
```bash
# For SSDs: none or mq-deadline
echo none > /sys/block/sda/queue/scheduler

# For HDDs: bfq (better for mixed workloads)
echo bfq > /sys/block/sdb/queue/scheduler
```

#### 3. **Docker Logging Limits**
```yaml
# docker-compose.yml (global)
x-logging: &default-logging
  driver: json-file
  options:
    max-size: 10m
    max-file: 3
```

---

### 🌐 Network Optimization

#### 1. **Multi-Queue NICs**
```bash
# Enable 4 queues per interface (already in /etc/network/interfaces)
ethtool -L enp2s0 combined 4
```

#### 2. **Interrupt Affinity**
```bash
# Distribute NIC interrupts across cores
# /etc/rc.local
for i in $(grep eth /proc/interrupts | cut -d: -f1); do
  echo 2 > /proc/irq/$i/smp_affinity
done
```

#### 3. **Network Buffer Tuning**
```bash
# /etc/sysctl.conf
net.core.rmem_max=134217728       # 128MB receive buffer
net.core.wmem_max=134217728       # 128MB send buffer
net.ipv4.tcp_rmem=4096 87380 67108864
net.ipv4.tcp_wmem=4096 65536 67108864
```

---

## Resource Monitoring

### 📈 Essential Monitoring Commands

#### Real-Time Overview
```bash
# Quick resource snapshot
htop

# Per-container memory
docker stats

# LXC container resources
pct list
pct status <ID>

# Network throughput
iftop -i vmbr0
```

#### Historical Analysis
```bash
# CPU usage over time
sar -u 1 60

# Memory pressure
sar -r 1 60

# Disk I/O
iostat -x 1 60

# Network I/O
sar -n DEV 1 60
```

### 🚨 Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| RAM Usage | >80% (12.8GB) | >90% (14.5GB) | Kill lowest priority service |
| CPU Load (1m) | >3.0 | >4.0 | Throttle background tasks |
| Disk I/O Wait | >20% | >40% | Pause downloads/scans |
| Swap Usage | >2GB | >4GB | Add zram, kill services |
| CPU Temp | >70°C | >80°C | Thermal throttling imminent |

### Automated Monitoring Setup

```bash
# Install monitoring tools
apt install sysstat iotop iftop htop glances

# Enable sysstat
systemctl enable sysstat
systemctl start sysstat

# Use Glances for web-based monitoring
glances -w  # Access at http://proxmox-ip:61208
```

---

## Deployment Recommendations

### 🎯 Phase-Based Rollout

#### **Phase 0: Foundation (Week 1)**
Deploy minimal infrastructure:
1. Proxmox network configuration
2. NAS setup (BTRFS RAID1)
3. Basic monitoring (htop, glances)

**Resources:** ~3GB RAM, 1 core

---

#### **Phase 1: Core Services (Week 2-3)**
Deploy essential services:
1. Deskflow KVM
2. PipeWire audio router
3. Home Assistant + MQTT
4. Silverbullet notes

**Resources:** ~6GB RAM, 1.5 cores
**Cumulative:** ~9GB RAM, 2.5 cores

---

#### **Phase 2: Media (Week 4-5)**
Add media services:
1. Jellyfin (direct play only)
2. Sonarr + Radarr (choose 1-2 *arr apps)
3. qBittorrent + VPN
4. Audiobookshelf

**Resources:** +4GB RAM, +1.5 cores
**Cumulative:** ~13GB RAM, 4 cores ⚠️ *Near limit*

---

#### **Phase 3: Knowledge (Week 6-7)**
Add document management:
1. Paperless-ngx (without Tika/Gotenberg initially)
2. PostgreSQL
3. Redis

**Resources:** +3GB RAM, +1 core
**Cumulative:** ~16GB RAM, 5 cores ❌ *Exceeds capacity*

**Required Action:** Enable 8GB zram swap before this phase.

---

#### **Phase 4: Advanced (Optional)**
Only add if resources permit:
1. Suricata IDS (optimized)
2. BirdNET-Go
3. Grafana dashboards
4. TubeArchivist (requires disabling other services)
5. Nessus (on-demand only)

**Resources:** +2-6GB RAM per service
**Strategy:** One at a time, monitor stability

---

### 🛡️ Failure Modes & Mitigation

| Failure Scenario | Symptoms | Mitigation |
|------------------|----------|------------|
| **OOM (Out of Memory)** | Services killed, system hangs | Enable zram, reduce limits, prioritize services |
| **CPU Saturation** | High load, slow response | CPU limits, process nice values, disable transcoding |
| **Disk I/O Bottleneck** | Slow queries, timeouts | Separate SSD/HDD workloads, reduce logging |
| **Thermal Throttling** | CPU freq drops to 1.1GHz | Improve airflow, reduce load, thermal paste |
| **Network Packet Loss** | Drops in Suricata/ntopng | Reduce DPI, use flow sampling, fewer interfaces |

---

## Alternative Architectures

### 🔀 Option 1: Hybrid Cloud
**Offload heavy services to external resources:**

- **Keep on Zimaboard:**
  - Network services (Deskflow, PipeWire, Home Assistant)
  - NAS (local storage)
  - Silverbullet (lightweight notes)

- **Offload to Cloud/Other Hardware:**
  - Jellyfin transcoding (use Tautulli + Plex Cloud)
  - TubeArchivist → YouTube Premium + yt-dlp on NAS
  - Nessus → Managed vulnerability scanning service
  - Paperless OCR → Separate Raspberry Pi or cloud instance

**Resource Savings:** ~10GB RAM, 2-3 cores

---

### 🔀 Option 2: Tiered Storage Strategy
**Use external NAS for media, Zimaboard for compute:**

- **Zimaboard:** Docker services, databases, caching
- **External NAS (Synology, TrueNAS):** Media files, backups
- **Connection:** 2.5GbE direct link

**Benefit:** Reduces Zimaboard disk I/O, frees SATA ports

---

### 🔀 Option 3: Legion as Compute Node
**Use Legion Pro 7i for heavy workloads:**

- **Zimaboard:** Router, networking, Home Assistant, lightweight services
- **Legion (docked):** Jellyfin, *arr stack, Paperless, TubeArchivist, LLM
- **Communication:** 2.5GbE direct link (vmbr2)

**Benefit:** Leverage Legion's superior CPU/RAM (32-64GB+)

**Setup:**
```bash
# On Legion: Install Docker, run media/knowledge stacks
# On Zimaboard: Install lightweight frontend proxies
```

---

## Conclusion

### ✅ Feasibility Assessment

| Stack Scenario | Feasible? | Conditions |
|----------------|-----------|------------|
| **Full Stack** | ❌ No | Requires 28-42GB RAM (176-263% over budget) |
| **Optimized Stack** | ⚠️ Barely | Requires zram, aggressive limits, careful tuning |
| **Minimal Stack** | ✅ Yes | Comfortable with 2.5GB headroom |

### 🎯 Final Recommendations

1. **Start with Minimal Stack** (Scenario 3)
   - Deploy core services first
   - Monitor resource usage for 1-2 weeks
   - Incrementally add services

2. **Enable Zram Immediately**
   - Provides ~4-6GB additional compressed swap
   - Essential for running >12GB workloads

3. **Aggressive Resource Limits**
   - Hard memory limits on all containers
   - CPU shares to prioritize interactive services
   - OOM score adjustment to protect critical services

4. **Leverage Legion for Heavy Lifting**
   - Use Zimaboard as network hub/router
   - Run Jellyfin, Paperless OCR, TubeArchivist on Legion
   - Direct 2.5GbE link between Zimaboard and Legion

5. **Avoid Running Everything Simultaneously**
   - Schedule Nessus scans during maintenance windows
   - Pause downloads during media playback
   - Batch OCR processing overnight

6. **Monitor Continuously**
   - Install Glances for web-based monitoring
   - Set up alerts for RAM >90%, Load >4.0
   - Weekly review of resource trends

### 💡 Long-Term Strategy

If workload demands grow beyond Zimaboard's capacity:

1. **Add Compute Node:** Repurpose old laptop/desktop as secondary Docker host
2. **Upgrade to Mini PC:** Beelink/Minisforum with 64GB RAM (~$600)
3. **Hybrid Architecture:** Keep Zimaboard for networking, add dedicated media server

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Author:** Claude (Sonnet 4.5)
**Target Hardware:** Zimaboard 16GB with PCIe 4x 2.5GbE
